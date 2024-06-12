from collections import defaultdict
from typing import Tuple, Dict, List
from rest_framework.decorators import api_view

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from statistics_api.course_info.utils import Utils
from statistics_api.clients.kpas_client import KpasClient
from statistics_api.controllers.models.KpasSchool import KpasSchool
from statistics_api.course_info.models import CourseObservation
from statistics_api.course_info.models import School
from statistics_api.utils.url_parameter_parser import get_url_parameters_dict, \
    NR_OF_DATES_LIMIT_KEY, SHOW_SCHOOLS_KEY, END_DATE_KEY, START_DATE_KEY
from statistics_api.utils.utils import get_target_year, get_closest_matching_year

@api_view(['GET'])
def municipality_primary_school_statistics(request: WSGIRequest, municipality_id: int, canvas_course_id: int):
    kpas_client = KpasClient()
    schools_in_municipality = kpas_client.get_schools_by_municipality_id(municipality_id)
    municipality = kpas_client.get_municipality(municipality_id)
    if not municipality:
        return HttpResponseNotFound()
    municipality_name, municipality_organization_number = (municipality["Navn"], int(municipality["OrgNr"]))

    url_parameters_dict = get_url_parameters_dict(request)
    response = get_individual_school_data(
        canvas_course_id, municipality_id,
        municipality_name,
        municipality_organization_number,
        schools_in_municipality,
        url_parameters_dict
    )

    def map_municipality_keywords(municipality: dict):
        return {
            "date": municipality['date'],
            "municipality_name": municipality['unit_name'],
            "municipality_id": municipality['unit_id'],
            "municipality_organization_number": municipality['organization_number'],
            "total_course_member_count": municipality['total_course_member_count'],
            "total_school_teacher_count": municipality['total_school_teacher_count'],
            "schools": municipality['schools']
        }

    json_response = list(map(map_municipality_keywords, response))
    return JsonResponse({"Result": json_response})


@api_view(['GET'])
def county_primary_school_statistics(request, county_id: int, canvas_course_id: int) -> HttpResponse:
    kpas_client = KpasClient()
    schools_in_county = kpas_client.get_schools_by_county_id(county_id)
    county = kpas_client.get_county(county_id)
    if not county:
        return HttpResponseNotFound()
    county_name, county_organization_number = (county["Navn"], int(county["OrgNr"]))

    url_parameters_dict = get_url_parameters_dict(request)
    show_schools = url_parameters_dict[SHOW_SCHOOLS_KEY]
    if show_schools:
        response = get_individual_school_data(
            canvas_course_id, county_id, county_name,
            county_organization_number, schools_in_county,
            url_parameters_dict
        )

        def map_county_keywords(county: dict):
            return {
                "date": county['date'],
                "county_name": county['unit_name'],
                "county_id": county['unit_id'],
                "county_organization_number": county['organization_number'],
                "total_course_member_count": county['total_course_member_count'],
                "total_school_teacher_count": county['total_school_teacher_count'],
                "schools": county['schools']
            }

        json_response = list(map(map_county_keywords, response))
        return JsonResponse({"Result": json_response})

    else:
        return get_municipality_aggregated_school_data_for_county(
            canvas_course_id, county_id, county_name,
            county_organization_number, schools_in_county,
            url_parameters_dict
        )


def filter_and_map_to_kpas_schools(schools):
    organization_number_to_school_name_mapping = {}

    for school in schools:
        if school['ErSkole'] == 1 and school['ErGrunnSkole'] == 1:
            organization_number_to_school_name_mapping[school['OrgNr']] = KpasSchool(
                organization_number=school['OrgNr'],
                name=school['FulltNavn'],
                latitude=school['Breddegrad'],
                longitude=school['Lengdegrad'],
            )

    return organization_number_to_school_name_mapping


def retrieve_course_observations(canvas_course_id: int, url_parameters_dict: dict):
    start_date = url_parameters_dict[START_DATE_KEY]
    end_date = url_parameters_dict[END_DATE_KEY]
    nr_of_dates_limit = url_parameters_dict[NR_OF_DATES_LIMIT_KEY]

    return CourseObservation.objects.filter(
        canvas_id=canvas_course_id,
        date_retrieved__gte=start_date,
        date_retrieved__lte=end_date
    ).order_by(f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_dates_limit]


def get_teacher_count_by_year() -> tuple:
    return tuple([int(school['year']) for school in School.objects.values('year').distinct()])


def get_individual_school_data(
        canvas_course_id: int,
        administration_unit_id: int,
        administration_unit_name: str,
        administration_unit_organization_number: int,
        schools_in_county: Tuple[Dict],
        url_parameters_dict: Dict,
) -> list:
    organization_number_to_school_name_mapping = filter_and_map_to_kpas_schools(schools_in_county)
    teacher_count_available_years = get_teacher_count_by_year()

    course_enrollment_stats: List = []
    schools_org_nrs = tuple([str(key) for key in organization_number_to_school_name_mapping.keys()])

    for course_observation in retrieve_course_observations(canvas_course_id, url_parameters_dict):
        course_observation: CourseObservation

        course_member_counts = get_course_member_counts(
            course_observation,
            teacher_count_available_years,
            schools_org_nrs,
            organization_number_to_school_name_mapping
        )
        total_course_member_count, total_school_teacher_count, schools = course_member_counts

        course_enrollment_stats.append({
            "date": course_observation.date_retrieved,
            "unit_name": administration_unit_name,
            "unit_id": administration_unit_id,
            "organization_number": administration_unit_organization_number,
            "total_course_member_count": total_course_member_count,
            "total_school_teacher_count": total_school_teacher_count,
            "schools": schools,
        })

    return course_enrollment_stats

def get_course_member_counts(
    course_observation,
    teacher_count_available_years,
    schools_org_nrs,
    organization_number_to_school_name_mapping
):
    target_year = get_target_year(course_observation.date_retrieved)
    closest_matching_year = get_closest_matching_year(teacher_count_available_years, target_year)
    course_member_counts = Utils.get_course_member_counts(schools_org_nrs, course_observation.pk, closest_matching_year)

    total_course_member_count = 0
    total_school_teacher_count = 0
    schools = []

    for course_member_count_item in course_member_counts:
        total_course_member_count += course_member_count_item["course_member_count"]
        total_school_teacher_count += course_member_count_item["school_teacher_count"]

        school_dict = vars(organization_number_to_school_name_mapping[course_member_count_item["organization_number"]])
        school_dict["course_member_count"] = course_member_count_item["course_member_count"]
        school_dict["school_teacher_count"] = course_member_count_item["school_teacher_count"]
        schools.append(school_dict)

    return total_course_member_count, total_school_teacher_count, schools

def get_municipality_aggregated_school_data_for_county(
    canvas_course_id: int,
    county_id: int, county_name: str,
    county_organization_number: int,
    schools_in_county: Tuple[Dict],
    url_parameters_dict: Dict
) -> JsonResponse:

    json_response = []
    municipality_number_mapping = defaultdict(list)
    municipality_number_to_name_mapping = {}
    all_schools_in_county_org_nrs = []

    for school in schools_in_county:
        if school.get('ErSkole') == 1 and school.get('ErGrunnSkole') == 1 and "Utgått" not in school.get('Navn', ''):
            municipality_number_mapping[school['Kommunenr']].append(school['OrgNr'])
            all_schools_in_county_org_nrs.append(school['OrgNr'])

    teacher_count_available_years = get_teacher_count_by_year()

    kpas_client = KpasClient()
    municipalities_in_county = kpas_client.get_municipalities_by_county_id(county_id)

    for municipality in municipalities_in_county:
        municipality_number_to_name_mapping[municipality['Kommunenr']] = municipality['Navn']

    for course_observation in retrieve_course_observations(canvas_course_id, url_parameters_dict):
        school_mapping = {}
        municipality_dicts = []
        course_observation: CourseObservation
        total_course_member_count = 0
        total_school_teacher_count = 0

        target_year = get_target_year(course_observation.date_retrieved)
        closest_matching_year = get_closest_matching_year(teacher_count_available_years, target_year)
        course_member_counts = Utils.get_course_member_counts(
            tuple(all_schools_in_county_org_nrs),
            course_observation.pk,
            closest_matching_year
        )

        for course_member_count_item in course_member_counts:
            school_mapping[course_member_count_item["organization_number"]] = (course_member_count_item["course_member_count"], course_member_count_item["school_teacher_count"])

        for municipality_nr in municipality_number_mapping.keys():
            municipality_school_org_nrs = municipality_number_mapping[municipality_nr]

            municipality_enrollment_count = sum(school_mapping.get(org_nr, (0, 0))[0] for org_nr in municipality_school_org_nrs)
            total_course_member_count += municipality_enrollment_count

            municipality_teacher_count = sum(school_mapping.get(org_nr, (0, 0))[1] for org_nr in municipality_school_org_nrs)
            total_school_teacher_count += municipality_teacher_count

            municipality_dicts.append({
                "name": municipality_number_to_name_mapping.get(municipality_nr, ''),
                "municipality_nr": municipality_nr,
                "course_member_count": municipality_enrollment_count,
                "school_teacher_count": municipality_teacher_count
            })

        municipality_dicts.sort(key=lambda d: d["name"])
        json_response.append({
            "date": course_observation.date_retrieved,
            "county_name": county_name,
            "county_id": county_id,
            "county_organization_number": county_organization_number,
            "total_course_member_count": total_course_member_count,
            "total_school_teacher_count": total_school_teacher_count,
            "municipalities": municipality_dicts
        })

    return JsonResponse({"Result": json_response})
