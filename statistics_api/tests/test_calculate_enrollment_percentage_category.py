from unittest import TestCase

from statistics_api.utils.calculate_enrollment_percentage_category import calculate_enrollment_percentage_category


class Test(TestCase):

    def test_calculate_enrollment_percentage_category_twenty_percent_should_return_category_1(self):
        enrollment_count = 20
        teacher_count = 100

        enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

        self.assertEqual(1, enrollment_percentage_category)

    def test_calculate_enrollment_percentage_category_fifty_percent_should_return_category_2(self):
        enrollment_count = 50
        teacher_count = 100

        enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

        self.assertEqual(3, enrollment_percentage_category)

    def test_calculate_enrollment_percentage_category_hundredandten_percent_should_return_category_5(self):
        enrollment_count = 110
        teacher_count = 100

        enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

        self.assertEqual(5, enrollment_percentage_category)

    def test_calculate_enrollment_percentage_category_over_twenty_percent_should_return_category_2(self):
        enrollment_count = 2001
        teacher_count = 10000

        enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

        self.assertEqual(2, enrollment_percentage_category)