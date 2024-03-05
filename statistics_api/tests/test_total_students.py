from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import json as JSON

from statistics_api.total_students.models import TotalStudents

class TestTotalStudents(TestCase):
    def setUp(self):

        self.total_students = TotalStudents.objects.create(
            course_id="123",
            total_students=54
        )
        TotalStudents.objects.create(
            course_id="456",
            total_students=60
        )
        TotalStudents.objects.create(
            course_id="789",
            total_students=60
        )


    def test_total_students_object_created(self):
        self.assertTrue(isinstance(self.total_students, TotalStudents))
        self.assertEqual(self.total_students.course_id, "123")
        self.assertEqual(self.total_students.total_students, 54)
        self.assertEqual(self.total_students.date, timezone.now().date())

    def test_total_students_count(self):
        total_students_count = TotalStudents.objects.count()
        self.assertEqual(total_students_count, 3)

    def test_total_students_course(self):
        url = reverse('total_students_course', args=(123, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        result_response_c123 = JSON.loads(response.content)
        self.assertEqual(len(result_response_c123), 1)


    def test_get_total_students_course_current(self):
        url = reverse('get_total_students_course_current', args=(123, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Expecting entry for today for course 123 has 54 total students
        result_response = JSON.loads(response.content)
        self.assertEqual(result_response['total_students'], 54)

    def test_get_total_students_all_current(self):
        url = reverse('get_total_students_all_current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        result_response = JSON.loads(response.content)
        #Expecting list of 3 as there is 3 unique courses registrerd with data for today
        self.assertEqual(len(result_response), 3)