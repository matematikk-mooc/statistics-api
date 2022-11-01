import datetime
from django.core.management import BaseCommand
from statistics_api.canvas_modules.models import Module, ModuleItem, FinnishedStudent, FinnishMarkCount
from statistics_api.canvas_users.models import CanvasUser
from statistics_api.definitions import CANVAS_ACCOUNT_ID
from django.db.models import F

from statistics_api.clients.canvas_api_client import CanvasApiClient


class Command(BaseCommand):

    def handle(self, *args, **options):
        api_client = CanvasApiClient()
        canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
        courses = api_client.get_courses(canvas_account_id)
        for course in courses:
            self.course_modules(api_client, course)

    def course_modules(self, api_client, course):
        course_id = course.get("id")
        modules = api_client.get_course_modules(course_id)
        students = api_client.get_course_students_recently_active(course_id)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        students_active_yesterday = [item for item in students if self.get_last_active_date(item.get("last_login")) >= yesterday ]

        for module in modules:
            module_id = module.get("id")
            module_obj, created = Module.objects.update_or_create(
            canvas_id = module_id,
            course_id = course_id,
            defaults={
                "name" : module.get("name"),
                "published" : module.get("published"),
                "position" : module.get("position")
            })

            for student in students_active_yesterday:
                student_id = student.get("id")
                finnish_marks = api_client.get_finnish_mark_per_student(course_id, module_id, student_id)
                if finnish_marks is None:
                    continue
                for finnish_mark in finnish_marks:
                    if finnish_mark.get("completion_requirement") is not None and finnish_mark["completion_requirement"].get("completed"):
                        item_id = finnish_mark.get("id")
                        module_item, created = ModuleItem.objects.get_or_create(
                        canvas_id = item_id,
                        defaults={
                            "module" : module_obj,
                            "title" : finnish_mark.get("title"),
                            "position" : finnish_mark.get("position"),
                            "url" : finnish_mark.get("url"),
                            "type" : finnish_mark.get("type"),
                            "published" : finnish_mark.get("published"),
                            "completion_type" : finnish_mark["completion_requirement"].get("type")
                        })
                        stud, createdStudent = FinnishedStudent.objects.get_or_create(user_id = student_id, module_item = module_item, defaults={"completed" : True})
                        if createdStudent:
                            self.count_groups(student_id, course_id, module_item)


    def count_groups(self, student_id, course_id, module_item):
        groups = CanvasUser.objects.filter(canvas_user_id=student_id, course_id = course_id)
        if not groups:
            FinnishMarkCount.objects.get_or_create(
                module_item = module_item,
                group_id = "0000",
                defaults={
                    "group_name" : "no_group"
                }
            )
            FinnishMarkCount.objects.filter(module_item = module_item, group_id="0000").update(count=F("count") + 1)
        else:
            for group in groups:
                FinnishMarkCount.objects.get_or_create(
                    module_item = module_item,
                    group_id = getattr(group, "group_id"),
                    defaults={
                        "group_name" : getattr(group, "group_name")
                    }
                )
                FinnishMarkCount.objects.filter(module_item = module_item, group_id = getattr(group, "group_id")).update(count=F("count") + 1)

    def get_last_active_date(self, last_login):
        if last_login is None:
            return datetime.datetime.strptime("2000-01-01T00:00:00Z", '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z')
        return datetime.datetime.strptime(last_login, '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z')