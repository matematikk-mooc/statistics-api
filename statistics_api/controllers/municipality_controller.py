from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from statistics_api.clients.kpas_client import KpasClient
from statistics_api.definitions import CATEGORY_CODE_INFORMATION_DICT
from statistics_api.models.course_observation import CourseObservation
from statistics_api.utils.calculate_enrollment_percentage_category import calculate_enrollment_percentage_category
from statistics_api.utils.get_org_nrs_enrollment_counts_and_teacher_counts import \
    get_org_nrs_enrollment_counts_and_teacher_counts
from statistics_api.utils.query_maker import get_org_nrs_enrollment_counts_and_teacher_counts_query, \
    get_org_nrs_enrollment_counts_and_teacher_counts_for_unregistered_schools_query
from statistics_api.utils.url_parameter_parser import get_url_parameters_dict, START_DATE_KEY, END_DATE_KEY, \
    NR_OF_DATES_LIMIT_KEY, ENROLLMENT_PERCENTAGE_CATEGORIES_KEY


@require_http_methods(["GET"])
def municipality_statistics(request: WSGIRequest, municipality_id: int, canvas_course_id: int):
    url_parameters_dict = get_url_parameters_dict(request)
    start_date, end_date, nr_of_dates_limit, enrollment_percentage_categories = (url_parameters_dict[
                                                                                     START_DATE_KEY],
                                                                                 url_parameters_dict[
                                                                                     END_DATE_KEY],
                                                                                 url_parameters_dict[
                                                                                     NR_OF_DATES_LIMIT_KEY],
                                                                                 url_parameters_dict[
                                                                                     ENROLLMENT_PERCENTAGE_CATEGORIES_KEY])

    kpas_client = KpasClient()
    schools_in_municipality = kpas_client.get_schools_by_municipality_id(municipality_id)
    municipality = kpas_client.get_municipality(municipality_id)
    municipality_name, municipality_organization_number = (municipality["Navn"], int(municipality["OrgNr"]))

    organization_number_to_school_name_mapping = {}

    for school in schools_in_municipality:
        if school['ErSkole'] == 1 and school['ErGrunnSkole'] == 1:
            organization_number_to_school_name_mapping[school['OrgNr']] = school['Navn']

    # Retrieving the {nr_of_most_recent_dates} most recent observations of Canvas LMS course with
    # canvas ID {canvas_course_id} ordered by date descending.
    course_observations = CourseObservation.objects.filter(canvas_id=canvas_course_id, date_retrieved__gte=start_date,
                                                           date_retrieved__lte=end_date).order_by(
        f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_dates_limit]

    json_response = []
    municipality_schools_org_nrs = tuple([str(k) for k in organization_number_to_school_name_mapping.keys()])

    municipality_enrollment_count = 0
    municipality_teacher_count = 0

    for course_observation in course_observations:
        course_observation: CourseObservation

        # Retrieving tuples like (organization_number, members_count, teacher_count) for all matching
        # schools.
        org_nrs_enrollment_counts_and_teacher_counts = get_org_nrs_enrollment_counts_and_teacher_counts(
            municipality_schools_org_nrs, course_observation.pk)

        names_org_nrs_enrollment_counts_and_teacher_counts = []

        for org_nr, enrollment_count, teacher_count in org_nrs_enrollment_counts_and_teacher_counts:
            enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

            municipality_enrollment_count += enrollment_count
            municipality_teacher_count += teacher_count

            if enrollment_percentage_category in enrollment_percentage_categories:
                school_dict = {
                    "name": organization_number_to_school_name_mapping[org_nr],
                    "organization_number": org_nr,
                    "enrollment_percentage_category": enrollment_percentage_category
                }
                names_org_nrs_enrollment_counts_and_teacher_counts.append(school_dict)

        names_org_nrs_enrollment_counts_and_teacher_counts.sort(key=lambda d: d["name"])

        municipality_enrollment_percentage_category = calculate_enrollment_percentage_category(
            municipality_enrollment_count, municipality_teacher_count)

        course_observation_for_municipality_json = {
            "date": course_observation.date_retrieved,
            "municipality_name": municipality_name,
            "municipality_id": municipality_id,
            "municipality_organization_number": municipality_organization_number,
            "enrollment_percentage_category": municipality_enrollment_percentage_category,
            "schools": names_org_nrs_enrollment_counts_and_teacher_counts
        }

        json_response.append(course_observation_for_municipality_json)

    return JsonResponse({**CATEGORY_CODE_INFORMATION_DICT, **{"Result": json_response}})
