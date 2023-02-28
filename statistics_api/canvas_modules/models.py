from django.db import models


# Create your models here.

class Module(models.Model):
    canvas_id = models.CharField(max_length=80)
    course_id = models.CharField(max_length=80)
    name = models.CharField(max_length=512)
    published = models.BooleanField()
    position = models.IntegerField()


class ModuleItem(models.Model):
    canvas_id = models.CharField(max_length=80)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="module_items")
    title = models.CharField(max_length=512)
    position = models.IntegerField()
    url = models.URLField(max_length=255)
    type = models.CharField(max_length=80)
    published = models.BooleanField(blank=True, null=True)
    completion_type = models.CharField(max_length=255)


class FinnishMarkCount(models.Model):
    module_item = models.ForeignKey(ModuleItem, on_delete=models.CASCADE, related_name="user_groups")
    group_id = models.CharField(max_length=80)
    group_name = models.CharField(max_length=512)
    count = models.IntegerField(default=0)


class FinnishedStudent(models.Model):
    module_item = models.ForeignKey(ModuleItem, on_delete=models.CASCADE, related_name="students")
    user_id = models.CharField(max_length=80, blank=True, null=True)
    completed = models.BooleanField()
