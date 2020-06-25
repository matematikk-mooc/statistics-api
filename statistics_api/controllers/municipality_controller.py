from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from statistics_api.clients.kpas_client import KpasClient
from statistics_api.models.course_observation import CourseObservation
from statistics_api.utils.query_maker import get_org_nrs_enrollment_counts_and_teacher_counts_query


@require_http_methods(["GET"])
def municipality_statistics(request: WSGIRequest, municipality_id: int, canvas_course_id: int):
    try:
        nr_of_most_recent_dates: int = int(request.GET.get('nr_of_dates', 1))
    except ValueError:
        return HttpResponseBadRequest(f"Invalid parameter value.")

    kpas_client = KpasClient()
    schools_in_municipality = kpas_client.get_schools_by_municipality_id(municipality_id)

    organization_number_to_school_name_mapping = {}

    for school in schools_in_municipality:
        if school['ErSkole'] == 1 and school['ErGrunnSkole'] == 1:
            organization_number_to_school_name_mapping[school['OrgNr']] = school['Navn']

    # Retrieving the {nr_of_most_recent_dates} most recent observations of Canvas LMS course with
    # canvas ID {canvas_course_id} ordered by date descending.
    course_observations = CourseObservation.objects.filter(canvas_id=canvas_course_id).order_by(
        f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_most_recent_dates]

    if not course_observations:
        return HttpResponseNotFound(f"Could not find course with specified canvas ID.")

    json_response = []

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
