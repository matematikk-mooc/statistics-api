from django.test import TestCase

from statistics_api.models.course_observation import CourseObservation
from statistics_api.services.course_service import compute_total_nr_of_students_for_course_observation


class CountyControllerBaseTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(CountyControllerBaseTest, cls).setUpClass()

        cls.COUNTY_ID = 15
        distinct_course_observation_canvas_ids = [i[CourseObservation.canvas_id.field.name] for i in
                                                  CourseObservation.objects.values(
                                                      CourseObservation.canvas_id.field.name).distinct()]

        most_recent_observations_for_courses = []

        for course_canvas_id in distinct_course_observation_canvas_ids:
            most_recent_course_observation = CourseObservation.objects.filter(canvas_id=course_canvas_id).order_by(
                f"-{CourseObservation.date_retrieved.field.name}")[0]
            most_recent_observations_for_courses.append(most_recent_course_observation)

        c: CourseObservation
        most_recent_observation_of_course_with_most_members = max(most_recent_observations_for_courses,
                                                                  key=lambda
                                                                      c: compute_total_nr_of_students_for_course_observation(
                                                                      c))

        cls.CANVAS_COURSE_ID = most_recent_observation_of_course_with_most_members.canvas_id