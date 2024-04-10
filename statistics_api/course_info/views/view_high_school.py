from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseServerError
from statistics_api.course_info.utils import Utils

from statistics_api.clients.kpas_client import KpasClient
from statistics_api.definitions import CATEGORY_CODE_INFORMATION_DICT
from statistics_api.course_info.models import County
from statistics_api.course_info.models import CourseObservation
from statistics_api.utils.url_parameter_parser import get_url_parameters_dict, START_DATE_KEY, END_DATE_KEY \
    , NR_OF_DATES_LIMIT_KEY
from statistics_api.utils.utils import filter_high_schools, calculate_enrollment_percentage_category, \
    get_closest_matching_year, get_target_year


def county_high_school_statistics_by_county_id(request, county_id, canvas_course_id) -> HttpResponse:

    url_parameters_dict = get_url_parameters_dict(request)

    start_date, end_date, nr_of_dates_limit = (
        url_parameters_dict[START_DATE_KEY],
        url_parameters_dict[END_DATE_KEY],
        url_parameters_dict[NR_OF_DATES_LIMIT_KEY],
    )

    kpas_client = KpasClient()
    schools_in_county = kpas_client.get_schools_by_county_id(county_id)
    county = kpas_client.get_county(county_id)
    if not county:
        return HttpResponseNotFound()
    county_name, county_organization_number = (county["Navn"], int(county["OrgNr"]))

    high_schools_in_county = filter_high_schools(schools_in_county)
    school_org_nrs = tuple([str(school["OrgNr"]) for school in high_schools_in_county])

    course_observations = CourseObservation.objects.filter(
        canvas_id=canvas_course_id,
        date_retrieved__gte=start_date,
        date_retrieved__lte=end_date).order_by(
            f"-{CourseObservation.date_retrieved.field.name}"
        )[:nr_of_dates_limit]

    json_response = []

    db_counties = County.objects.filter(county_id__exact=int(county_id))

    year_to_db_county_mapping = {}

    for db_county in db_counties:
        year_to_db_county_mapping[db_county.year] = db_county

    teacher_count_available_years = tuple([key for key in year_to_db_county_mapping.keys()])

    for course_observation in course_observations:

        target_year = get_target_year(course_observation.date_retrieved)

        try:
            closest_matching_year = get_closest_matching_year(teacher_count_available_years, target_year)
            county_teacher_count = year_to_db_county_mapping[closest_matching_year].number_of_teachers
        except ValueError:
            return HttpResponseServerError()

        course_observation: CourseObservation

        county_enrollment_count = 0

        org_nrs_and_enrollment_counts = Utils.get_org_nrs_and_enrollment_counts(
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
