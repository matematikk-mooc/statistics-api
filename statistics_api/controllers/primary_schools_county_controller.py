from collections import defaultdict
from typing import Tuple, Dict, List, Set

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from statistics_api.clients.kpas_client import KpasClient
from statistics_api.definitions import CATEGORY_CODE_INFORMATION_DICT
from statistics_api.models.course_observation import CourseObservation
from statistics_api.utils.calculate_enrollment_percentage_category import calculate_enrollment_percentage_category
from statistics_api.utils.get_org_nrs_enrollment_counts_and_teacher_counts import \
    get_org_nrs_enrollment_counts_and_teacher_counts
from statistics_api.utils.url_parameter_parser import get_url_parameters_dict, ENROLLMENT_PERCENTAGE_CATEGORIES_KEY, \
    NR_OF_DATES_LIMIT_KEY, SHOW_SCHOOLS_KEY, END_DATE_KEY, START_DATE_KEY


@require_http_methods(["GET"])
def county_primary_school_statistics(request: WSGIRequest, county_id: int, canvas_course_id: int) -> HttpResponse:
    url_parameters_dict = get_url_parameters_dict(request)
    start_date, end_date, show_schools, \
    nr_of_dates_limit, enrollment_percentage_categories = (url_parameters_dict[
                                                               START_DATE_KEY],
                                                           url_parameters_dict[
                                                               END_DATE_KEY],
                                                           url_parameters_dict[
                                                               SHOW_SCHOOLS_KEY],
                                                           url_parameters_dict[
                                                               NR_OF_DATES_LIMIT_KEY],
                                                           url_parameters_dict[
                                                               ENROLLMENT_PERCENTAGE_CATEGORIES_KEY])

    kpas_client = KpasClient()
    schools_in_county = kpas_client.get_schools_by_county_id(county_id)
    county: [Dict] = kpas_client.get_county(county_id)
    county_name, county_organization_number = (county["Navn"], int(county["OrgNr"]))

    # Retrieving the {nr_of_most_recent_dates} most recent observations of Canvas LMS course with
    # canvas ID {canvas_course_id} ordered by date descending.
    course_observations = CourseObservation.objects.filter(canvas_id=canvas_course_id, date_retrieved__gte=start_date,
                                                           date_retrieved__lte=end_date).order_by(
        f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_dates_limit]

    if show_schools:
        return get_individual_school_data_for_county(course_observations, county_id, county_name,
                                                     county_organization_number, schools_in_county,
                                                     enrollment_percentage_categories)
    else:
        return get_municipality_aggregated_school_data_for_county(course_observations, county_id, county_name,
                                                                  county_organization_number, schools_in_county,
                                                                  enrollment_percentage_categories)


def get_individual_school_data_for_county(course_observations: Tuple[CourseObservation], county_id: int,
                                          county_name: str, county_organization_number: int,
                                          schools_in_county: Tuple[Dict],
                                          enrollment_percentage_categories: Set[int]) -> JsonResponse:
    organization_number_to_school_name_mapping = {}

    for school in schools_in_county:
        if school['ErSkole'] == 1 and school['ErGrunnSkole'] == 1:
            organization_number_to_school_name_mapping[school['OrgNr']] = school['Navn']

    json_response: List = []
    county_schools_org_nrs = tuple([str(k) for k in organization_number_to_school_name_mapping.keys()])

    for course_observation in course_observations:
        course_observation: CourseObservation

        # Retrieving tuples like (organization_number, members_count, teacher_count) for all matching
        # rows.

        org_nrs_enrollment_counts_and_teacher_counts = get_org_nrs_enrollment_counts_and_teacher_counts(
            county_schools_org_nrs, course_observation.pk)

        names_org_nrs_enrollment_counts_and_teacher_counts = []

        county_enrollment_count = 0
        county_teacher_count = 0

        for org_nr, enrollment_count, teacher_count in org_nrs_enrollment_counts_and_teacher_counts:
            county_enrollment_count += enrollment_count
            county_teacher_count += teacher_count

            enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

            if enrollment_percentage_category in enrollment_percentage_categories:
                school_dict = {
                    "name": organization_number_to_school_name_mapping[org_nr],
                    "organization_number": org_nr,
                    "enrollment_percentage_category": enrollment_percentage_category
                }
                names_org_nrs_enrollment_counts_and_teacher_counts.append(school_dict)

        names_org_nrs_enrollment_counts_and_teacher_counts.sort(key=lambda d: d["name"])

        county_enrollment_percentage_category = calculate_enrollment_percentage_category(county_enrollment_count,
                                                                                         county_teacher_count)

        course_observation_json = {
            "date": course_observation.date_retrieved,
            "county_name": county_name,
            "county_id": county_id,
            "county_organization_number": county_organization_number,
            "enrollment_percentage_category": county_enrollment_percentage_category,
            "schools": names_org_nrs_enrollment_counts_and_teacher_counts
        }

        json_response.append(course_observation_json)

    return JsonResponse({**CATEGORY_CODE_INFORMATION_DICT, **{"Result": json_response}})


def get_municipality_aggregated_school_data_for_county(course_observations: Tuple[CourseObservation],
                                                       county_id: int, county_name: str,
                                                       county_organization_number: int,
                                                       schools_in_county: Tuple[Dict],
                                                       enrollment_percentage_categories: Set[int]) -> JsonResponse:
    municipality_number_to_list_of_school_org_nrs_mapping: Dict[str, List[str]] = defaultdict(list)
    municipality_number_to_name_mapping: Dict[str, str] = {}
    all_schools_in_county_org_nrs: List[str] = []

    for school in schools_in_county:
        if school['ErSkole'] == 1 and school['ErGrunnSkole'] == 1 and school['Navn'].find("Utgått ") == -1:
            municipality_number_to_list_of_school_org_nrs_mapping[school['Kommunenr']].append(school['OrgNr'])
            all_schools_in_county_org_nrs.append(school['OrgNr'])

    kpas_client = KpasClient()
    municipalities_in_county = kpas_client.get_municipalities_by_county_id(county_id)

    for municipality in municipalities_in_county:
        municipality_number_to_name_mapping[municipality['Kommunenr']] = municipality['Navn']

    json_response: List = []

    for course_observation in course_observations:
        course_observation: CourseObservation

        # Retrieving tuples like (organization_number, members_count, teacher_count) for all matching
        # schools.
        org_nrs_enrollment_counts_and_teacher_counts = get_org_nrs_enrollment_counts_and_teacher_counts(
            tuple(all_schools_in_county_org_nrs), course_observation.pk)

        school_org_nr_to_enrollment_and_teacher_count_mapping: Dict[str, Tuple[int, int]] = {}
        municipality_dicts: List = []

        county_enrollment_count = 0
        county_teacher_count = 0

        for org_nr, enrollment_count, teacher_count in org_nrs_enrollment_counts_and_teacher_counts:
            school_org_nr_to_enrollment_and_teacher_count_mapping[org_nr] = (enrollment_count, teacher_count)

        for municipality_nr in municipality_number_to_list_of_school_org_nrs_mapping.keys():
            municipality_school_org_nrs = municipality_number_to_list_of_school_org_nrs_mapping[municipality_nr]

            municipality_enrollment_count = sum([school_org_nr_to_enrollment_and_teacher_count_mapping[org_nr][
                                                     0] if school_org_nr_to_enrollment_and_teacher_count_mapping.get(
                org_nr) else 0 for org_nr in municipality_school_org_nrs])

            municipality_teacher_count = sum(
                [school_org_nr_to_enrollment_and_teacher_count_mapping[org_nr][1] if
                 school_org_nr_to_enrollment_and_teacher_count_mapping.get(org_nr) else 0 for org_nr in
                 municipality_school_org_nrs])

            county_enrollment_count += municipality_enrollment_count
            county_teacher_count += municipality_teacher_count

            enrollment_percentage_category = calculate_enrollment_percentage_category(municipality_enrollment_count,
                                                                                      municipality_teacher_count)
            if enrollment_percentage_category in enrollment_percentage_categories:
                municipality_dict = {
                    "name": municipality_number_to_name_mapping[municipality_nr],
                    "municipality_nr": municipality_nr,
                    "enrollment_percentage_category": enrollment_percentage_category
                }

                municipality_dicts.append(municipality_dict)

        municipality_dicts.sort(key=lambda d: d["name"])

        county_enrollment_percentage_category = calculate_enrollment_percentage_category(county_enrollment_count,
                                                                                         county_teacher_count)

        course_observation_for_municipality_json = {
            "date": course_observation.date_retrieved,
            "county_name": county_name,
            "county_id": county_id,
            "county_organization_number": county_organization_number,
            "enrollment_percentage_category": county_enrollment_percentage_category,
            "municipalities": municipality_dicts
        }

        json_response.append(course_observation_for_municipality_json)

    return JsonResponse({**CATEGORY_CODE_INFORMATION_DICT, **{"Result": json_response}})
