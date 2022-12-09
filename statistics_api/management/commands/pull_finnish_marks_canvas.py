import datetime
from threading import Thread

from django.core.management import BaseCommand
from statistics_api.canvas_modules.models import Module, ModuleItem, FinnishedStudent, FinnishMarkCount
from statistics_api.canvas_users.models import CanvasUser
from statistics_api.definitions import CANVAS_ACCOUNT_ID
from django.db.models import F

from statistics_api.clients.canvas_api_client import CanvasApiClient


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("command pull_finnish_marks_canvas started")
        api_client = CanvasApiClient()
        canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
        courses = api_client.get_courses(canvas_account_id)
        midle_index = len(courses) // 2
        first_half = courses[:midle_index]
        second_half = courses[midle_index:]
        threads = [Thread(target=self.parse_courses, args=(api_client, first_half)),
                   Thread(target=self.parse_courses, args=(api_client, second_half))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        print("command pull_finnish_marks_canvas completed")

    def parse_courses(self, api_client, courses):
        for course in courses:
            course_id = course.get('id')
            if course_id == 360:
                continue
            self.course_modules(api_client, course)

    def course_modules(self, api_client, course):
        course_id = course.get("id")
        modules = api_client.get_course_modules(course_id)
        students = api_client.get_course_students_recently_active(course_id)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        students_active_yesterday = [item for item in students if
                                     self.get_last_active_date(item.get("last_login")) >= yesterday]

        for module in modules:
            if not module.get("published"):
                continue
            module_id = module.get("id")
            module_object, created = Module.objects.update_or_create(
                canvas_id=module_id,
                course_id=course_id,
                defaults={
                    "name": module.get("name"),
                    "published": module.get("published"),
                    "position": module.get("position")
                })

            for student in students_active_yesterday:
                student_id = student.get("id")
                finnish_marks = api_client.get_finnish_mark_per_student(course_id, module_id, student_id)
                if finnish_marks is None:
                    print("student completed?")
                    self.student_completed_course(api_client, course_id, student_id, module_id, module_object)
                else:
                    self.parse_module_items(module_object, finnish_marks, student_id, course_id, False)

    def student_completed_course(self, api_client, course_id, user_id, module_id, module_object):
        completed = api_client.get_student_completed(course_id, user_id)
        if completed is []:
            return
        module_items = api_client.get_course_module_items(course_id, module_id)
        self.parse_module_items(module_object, module_items, user_id, course_id, True)

    def parse_module_items(self, module_object, module_items, user_id, course_id, completed_course):
        for item in module_items:
            if item.get("completion_requirement"):
                if not completed_course and not item["completion_requirement"].get("completed"):
                    continue
                module_item, created = ModuleItem.objects.get_or_create(
                    canvas_id=item.get("id"),
                    defaults={
                        "module": module_object,
                        "title": item.get("title"),
                        "position": item.get("position"),
                        "url": item.get("url"),
                        "type": item.get("type"),
                        "published": item.get("published"),
                        "completion_type": item["completion_requirement"].get("type")
                    }
                )
                student, createdStudent = FinnishedStudent.objects.get_or_create(user_id=user_id,
                                                                                 module_item=module_item,
                                                                                 defaults={"completed": True})
                if createdStudent:
                    self.count_groups(user_id, course_id, module_item)

    def count_groups(self, student_id, course_id, module_item):
        groups = CanvasUser.objects.filter(canvas_user_id=student_id, course_id=course_id)
        if not groups:
            FinnishMarkCount.objects.get_or_create(
                module_item=module_item,
                group_id="0000",
                defaults={
                    "group_name": "no_group"
                }
            )
            FinnishMarkCount.objects.filter(module_item=module_item, group_id="0000").update(count=F("count") + 1)
        else:
            for group in groups:
                FinnishMarkCount.objects.get_or_create(
                    module_item=module_item,
                    group_id=getattr(group, "group_id"),
                    defaults={
                        "group_name": getattr(group, "group_name")
                    }
                )
                FinnishMarkCount.objects.filter(module_item=module_item, group_id=getattr(group, "group_id")).update(
                    count=F("count") + 1)

    def get_last_active_date(self, last_login):
        if last_login is None:
            return datetime.datetime.strptime("2000-01-01T00:00:00Z", '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z')
        return datetime.datetime.strptime(last_login, '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z')
