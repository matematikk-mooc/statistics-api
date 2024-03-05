from django.test import TestCase
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
import json as JSON
from statistics_api.canvas_modules.models import Module, ModuleItem, FinnishedStudent, FinnishMarkCount

class ModuleTestCase(TestCase):
    def setUp(self):
        self.module_1 = Module.objects.create(
            canvas_id="123",
            course_id="456",
            name="Test Module 1",
            published=True,
            position=1
        )
        self.module_item_1 = ModuleItem.objects.create(
            canvas_id="789",
            module=self.module_1,
            title="Test Module Item 1",
            position=1,
            url="http://example.com",
            type="type",
            published=True,
            completion_type="type"
        )

        self.module_item_2 = ModuleItem.objects.create(
            canvas_id="987",
            module=self.module_1,
            title="Test Module Item 2",
            position=2,
            url="http://example.com",
            type="type",
            published=True,
            completion_type="type"
        )

        self.module_item_3 = ModuleItem.objects.create(
            canvas_id="654",
            module=self.module_1,
            title="Test Module Item 3",
            position=3,
            url="http://example.com",
            type="type",
            published=True,
            completion_type="type"
        )


        self.finnish_mark_count1 = FinnishMarkCount.objects.create(
            module_item=self.module_item_1,
            group_id="group1",
            group_name="Group Name 1",
            count=5
        )

        self.finnish_mark_count2 = FinnishMarkCount.objects.create(
            module_item=self.module_item_1,
            group_id="group2",
            group_name="Group Name 2",
            count=3
        )

        self.finnished_student123_789 = FinnishedStudent.objects.create(
            module_item=self.module_item_1,
            user_id="user123",
            completed=True,
            completedDate="2022-01-01"
        )

        self.finnished_student123_987 = FinnishedStudent.objects.create(
            module_item=self.module_item_2,
            user_id="user123",
            completed=True,
            completedDate="2022-01-01"
        )

        self.finnished_student_123_654 = FinnishedStudent.objects.create(
            module_item=self.module_item_3,
            user_id="user123",
            completed=True,
            completedDate="2022-02-03"
        )

        self.finnished_student234_789 = FinnishedStudent.objects.create(
            module_item=self.module_item_1,
            user_id="user234",
            completed=True,
            completedDate="2022-01-01"
        )

        self.finnished_student234_987 = FinnishedStudent.objects.create(
            module_item=self.module_item_2,
            user_id="user234",
            completed=True,
            completedDate="2022-01-01"
        )

    def test_module_creation(self):
        self.assertEqual(self.module_1.canvas_id, "123")
        self.assertEqual(self.module_1.course_id, "456")
        self.assertEqual(self.module_1.name, "Test Module 1")
        self.assertTrue(self.module_1.published)
        self.assertEqual(self.module_1.position, 1)
        self.assertEqual(Module.objects.all().count(), 1)

    def test_module_item_creation(self):
        self.assertEqual(self.module_item_1.canvas_id, "789")
        self.assertEqual(self.module_item_1.module, self.module_1)
        self.assertEqual(self.module_item_1.title, "Test Module Item 1")
        self.assertEqual(self.module_item_1.position, 1)
        self.assertEqual(self.module_item_1.url, "http://example.com")
        self.assertEqual(self.module_item_1.type, "type")
        self.assertTrue(self.module_item_1.published)
        self.assertEqual(self.module_item_1.completion_type, "type")
        self.assertEqual(ModuleItem.objects.all().count(), 3)

    def test_finnish_mark_count_creation(self):
        self.assertEqual(self.finnish_mark_count.module_item, self.module_item_1)
        self.assertEqual(self.finnish_mark_count.group_id, "group_id")
        self.assertEqual(self.finnish_mark_count.group_name, "Group Name 1")
        self.assertEqual(self.finnish_mark_count.count, 5)
        self.assertEqual(FinnishMarkCount.objects.all().count(), 1)

    def test_finnished_student_creation(self):
        self.assertEqual(self.finnished_student123_789.module_item, self.module_item_1)
        self.assertEqual(self.finnished_student123_789.user_id, "user123")
        self.assertTrue(self.finnished_student123_789.completed)
        self.assertEqual(self.finnished_student123_789.completedDate, "2022-01-01")
        self.assertEqual(FinnishedStudent.objects.all().count(), 5)

    def test_module_statistics_with_group(self):
        url = reverse('module_statistics', args=('456', ))
        response = self.client.get(url, {'group': 'group_id'})
        self.assertEqual(response.status_code, 200)
        result = JSON.loads(response.content)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['canvas_id'], '123')
        self.assertEqual(result)

    def test_module_statistics_without_group(self):
        url = reverse('module_statistics', args=('456', ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        result = JSON.loads(response.content)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['canvas_id'], '123')

    def test_module_item_total_count(self):
        url = reverse('module_item_total_count', args=('456', ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        result = JSON.loads(response.content)
        #Expecting two users to have completed module item 789
        self.assertEqual(result[0]['module_items'][0]['canvas_id'], '789')
        self.assertEqual(result[0]['module_items'][0]['total_completed'], 2)

        #Expecting one user to have completed module item 654
        self.assertEqual(result[0]['module_items'][2]['canvas_id'], '654')
        self.assertEqual(result[0]['module_items'][2]['total_completed'], 1)

    def test_module_completed_per_date_count(self):
        url = reverse('module_completed_per_date_count', args=('123',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        result = JSON.loads(response.content)
        #Expecting one user to have completed whole module 1, user123 completed last item in module on 2022-02-03
        #User234 is missing completion of one item in the module therefore should not be counted here.
        self.assertEqual(result[0][0], "2022-02-03")
        self.assertEqual(result[0][1], 1)