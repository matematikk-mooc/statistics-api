from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from statistics_api.enrollment_activity.views import EnrollmentActivityViewSet
import json as JSON


from statistics_api.enrollment_activity.models import EnrollmentActivity
class TestEnrollmentActivity(TestCase):

    def setUp(self):
        yesterday = timezone.now() - timedelta(1)
        weekago = timezone.now() - timedelta(7)
        EnrollmentActivity.objects.create(
            id=1,
            course_id=123,
            course_name="Test course 1",
            active_users_count=3,
            activity_date=yesterday,
        )
        EnrollmentActivity.objects.create(
            id=2,
            course_id=456,
            course_name="Test course 2",
            active_users_count=4,
            activity_date=yesterday,
        )
        EnrollmentActivity.objects.create(
            id=3,
            course_id=789,
            course_name="Test course 3",
            active_users_count=2,
            activity_date=weekago,
        )
        EnrollmentActivity.objects.create(
            id=4,
            course_id=456,
            course_name="Test course 2",
            active_users_count=9,
            activity_date=weekago,
        )

    def tearDown(self):
        pass

    def test_enrollment_activities_was_created(self):
        allActivities = EnrollmentActivity.objects.all()
        self.assertEqual(allActivities.count(), 4)
        firstActivity = EnrollmentActivity.objects.get(id=1)
        self.assertEqual(firstActivity.course_id, 123)
        self.assertEqual(firstActivity.course_name, "Test course 1")
        self.assertEqual(firstActivity.active_users_count, 3)
        self.assertEqual(firstActivity.activity_date.date(), (timezone.now()-timedelta(1)).date())

    def test_enrollment_activity_timeframe(self):
        fromDate = timezone.now()-timedelta(5)
        toDate = timezone.now()
        filteredActivities = EnrollmentActivity.objects.filter(activity_date__range=[fromDate, toDate])
        self.assertEqual(filteredActivities.count(), 2)

    def test_enrollment_activity_course(self):
        client = Client()
        retriveCourse123 = client.get(reverse('enrollment_activity-detail', kwargs={'pk': 123}))
        result_retriveCourse123 = JSON.loads(retriveCourse123.content)
        self.assertEqual(retriveCourse123.status_code, 200)
        self.assertEqual(len(result_retriveCourse123), 1)
        self.assertEqual(result_retriveCourse123[0]["active_users_count"], 3)
        retriveCourse456 = client.get(reverse('enrollment_activity-detail', kwargs={'pk': 456}))
        result_retriveCourse456 = JSON.loads(retriveCourse456.content)
        self.assertEqual(retriveCourse456.status_code, 200)
        self.assertEqual(len(result_retriveCourse456), 2)
        self.assertEqual(result_retriveCourse456[0]["active_users_count"], 4)
        self.assertEqual(result_retriveCourse456[1]["active_users_count"], 9)

    def test_enrollment_activity_courses(self):
        client = Client()
        listCourses = client.get(reverse('enrollment_activity-list'))
        result_listCourses = JSON.loads(listCourses.content)
        self.assertEqual(listCourses.status_code, 200)
        self.assertEqual(len(result_listCourses), 4)

    def test_enrollment_activity_course_timeframe(self):
        url = reverse('enrollment_activity-detail', args=(456, ))
        response_c456 = self.client.get(url, {'from': (timezone.now()-timedelta(5)).date(), 'to': timezone.now().date()})
        self.assertEqual(response_c456.status_code, 200)
        #Expecting only the latest entry for course 456 to be returned
        result_response_c456 = JSON.loads(response_c456.content)
        self.assertEqual(len(result_response_c456), 1)

    def test_enrollment_activity_courses_timeframe(self):
        url = reverse('enrollment_activity-list')
        response = self.client.get(url, {'from': (timezone.now()-timedelta(5)).date(), 'to': timezone.now().date()})
        self.assertEqual(response.status_code, 200)
        #Expecting the two latest entries to be returned
        result_response = JSON.loads(response.content)
        self.assertEqual(len(result_response), 2)


    def test_not_existing_course(self):
        client = Client()
        retrieveCourseNotExisting = client.get(reverse('enrollment_activity-detail', kwargs={'pk': 321}))
        self.assertEqual(retrieveCourseNotExisting.status_code, 200)
        result_retrieveNotExisting = JSON.loads(retrieveCourseNotExisting.content)
        self.assertEqual(result_retrieveNotExisting, [])