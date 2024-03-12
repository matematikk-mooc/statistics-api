from typing import Tuple, Dict

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseServerError

from statistics_api.clients.db_client import DatabaseClient
from statistics_api.clients.kpas_client import KpasClient
from statistics_api.definitions import CATEGORY_CODE_INFORMATION_DICT
from statistics_api.course_info.models import County
from statistics_api.course_info.models import CourseObservation
from statistics_api.utils.url_parameter_parser import get_url_parameters_dict, START_DATE_KEY, END_DATE_KEY, \
    SHOW_SCHOOLS_KEY, NR_OF_DATES_LIMIT_KEY, ENROLLMENT_PERCENTAGE_CATEGORIES_KEY
from statistics_api.utils.utils import filter_high_schools, calculate_enrollment_percentage_category, \
    get_closest_matching_prior_year_to_target_year, get_target_year_for_course_observation_teacher_count


def county_high_school_statistics_by_county_id(request: WSGIRequest, county_id: int,
                                               canvas_course_id: int) -> HttpResponse:
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
    if not county:
        return HttpResponseNotFound()
    county_name, county_organization_number = (county["Navn"], int(county["OrgNr"]))

    high_schools_in_county: Tuple[Dict] = filter_high_schools(schools_in_county)
    school_org_nrs: Tuple[str] = tuple([str(school["OrgNr"]) for school in high_schools_in_county])

    course_observations = CourseObservation.objects.filter(canvas_id=canvas_course_id, date_retrieved__gte=start_date,
                                                           date_retrieved__lte=end_date).order_by(
        f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_dates_limit]

    json_response = []

    db_counties = County.objects.filter(county_id__exact=int(county_id))

    # Need a data structure to look up county teacher count by year, so that each course_observation can be mapped
    # accordingly in O(1) time.
    year_to_db_county_mapping: Dict[int, County] = {}

    for db_county in db_counties:
        year_to_db_county_mapping[db_county.year] = db_county

    teacher_count_available_years = tuple([y for y in year_to_db_county_mapping.keys()])

    for course_observation in course_observations:

        target_year = get_target_year_for_course_observation_teacher_count(course_observation.date_retrieved)

        try:
            closest_matching_year = get_closest_matching_prior_year_to_target_year(teacher_count_available_years, target_year)
            county_teacher_count = year_to_db_county_mapping[closest_matching_year].number_of_teachers
        except ValueError:
            return HttpResponseServerError()

        course_observation: CourseObservation

        # Retrieving tuples like (organization_number, members_count, teacher_count) for all matching
        # rows.

        county_enrollment_count: int = 0

        org_nrs_and_enrollment_counts = DatabaseClient.get_org_nrs_and_enrollment_counts(
            school_org_nrs, course_observation.pk)

        for org_nr, enrollment_count in org_nrs_and_enrollment_counts:
            county_enrollment_count += enrollment_count  # Looping through the schools, calculating total enrollment in entire county

        county_enrollment_percentage_category = calculate_enrollment_percentage_category(county_enrollment_count,
                                                                                         county_teacher_count)

        course_observation_json = {
            "date": course_observation.date_retrieved,
            "county_name": county_name,
            "county_id": county_id,
            "county_organization_number": county_organization_number,
            "enrollment_percentage_category": county_enrollment_percentage_category,
        }

        json_response.append(course_observation_json)

    return JsonResponse({**CATEGORY_CODE_INFORMATION_DICT, **{"Result": json_response}})
