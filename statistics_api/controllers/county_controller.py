from collections import defaultdict
from distutils import util
from typing import Tuple, Dict, List

from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from statistics_api.clients.kpas_client import KpasClient
from statistics_api.models.course_observation import CourseObservation
from statistics_api.utils.query_maker import get_org_nrs_enrollment_counts_and_teacher_counts_query
from statistics_api.utils.url_parameter_parser import get_url_parameters


@require_http_methods(["GET"])
def county_statistics(request: WSGIRequest, county_id: int, canvas_course_id: int) -> HttpResponse:
    start_date, end_date, show_schools, nr_of_dates_limit = get_url_parameters(request)

    kpas_client = KpasClient()
    schools_in_county = kpas_client.get_schools_by_county_id(county_id)

    # Retrieving the {nr_of_most_recent_dates} most recent observations of Canvas LMS course with
    # canvas ID {canvas_course_id} ordered by date descending.
    course_observations = CourseObservation.objects.filter(canvas_id=canvas_course_id, date_retrieved__gte=start_date,
                                                           date_retrieved__lte=end_date).order_by(
        f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_dates_limit]

    if show_schools:
        return get_individual_school_data_for_county(course_observations, schools_in_county)
    else:
        return get_municipality_aggregated_school_data_for_county(course_observations, county_id, schools_in_county)


def get_individual_school_data_for_county(course_observations: Tuple[CourseObservation],
                                          schools_in_county: Tuple[Dict]) -> JsonResponse:
    organization_number_to_school_name_mapping = {}

    for school in schools_in_county:
        if school['ErSkole'] == 1 and school['ErGrunnSkole'] == 1:
            organization_number_to_school_name_mapping[school['OrgNr']] = school['Navn']

    json_response: List = []

    for course_observation in course_observations:
        course_observation: CourseObservation

        org_nrs_enrollment_counts_and_teacher_counts_query = get_org_nrs_enrollment_counts_and_teacher_counts_query(
            tuple([int(i) for i in organization_number_to_school_name_mapping.keys()]))

        # Retrieving tuples like (organization_number, members_count, teacher_count) for all matching
        # rows.
        with connection.cursor() as cursor:
            cursor.execute(org_nrs_enrollment_counts_and_teacher_counts_query, [course_observation.pk])
            org_nrs_enrollment_counts_and_teacher_counts = cursor.fetchall()

        names_org_nrs_enrollment_counts_and_teacher_counts = []

        for org_nr, enrollment_count, teacher_count in org_nrs_enrollment_counts_and_teacher_counts:
            school_dict = {
                "name": organization_number_to_school_name_mapping[org_nr],
                "organization_number": org_nr,
                "members_count": enrollment_count,
                "total_teachers_count": teacher_count
            }
            names_org_nrs_enrollment_counts_and_teacher_counts.append(school_dict)

        course_observation_for_municipality_json = {
            "date": course_observation.date_retrieved,
            "schools": names_org_nrs_enrollment_counts_and_teacher_counts
        }

        json_response.append(course_observation_for_municipality_json)

    return JsonResponse({"Result": json_response})


def get_municipality_aggregated_school_data_for_county(course_observations: Tuple[CourseObservation],
                                                       county_id: int,
                                                       schools_in_county: Tuple[Dict]) -> JsonResponse:
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
        if municipality["ErNedlagt"] == False:
            municipality_number_to_name_mapping[municipality['Kommunenr']] = municipality['Navn']

    json_response: List = []

    for course_observation in course_observations:
        course_observation: CourseObservation

        org_nrs_enrollment_counts_and_teacher_counts_query = get_org_nrs_enrollment_counts_and_teacher_counts_query(
            tuple([int(i) for i in all_schools_in_county_org_nrs]))

        # Retrieving tuples like (organization_number, members_count, teacher_count) for all matching
        # rows.
        with connection.cursor() as cursor:
            cursor.execute(org_nrs_enrollment_counts_and_teacher_counts_query, [course_observation.pk])
            org_nrs_enrollment_counts_and_teacher_counts = cursor.fetchall()

        school_org_nr_to_enrollment_and_teacher_count_mapping: Dict[str, Tuple[int, int]] = {}
        municipality_dicts: List = []

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

            municipality_dict = {
                "name": municipality_number_to_name_mapping[municipality_nr],
                "municipality_nr": municipality_nr,
                "members_count": municipality_enrollment_count,
                "total_teachers_count": municipality_teacher_count
            }

            municipality_dicts.append(municipality_dict)

        course_observation_for_municipality_json = {
            "date": course_observation.date_retrieved,
            "municipalities": municipality_dicts
        }

        json_response.append(course_observation_for_municipality_json)

    return JsonResponse({"Result": json_response})
