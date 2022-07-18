from django.db import models

# Create your models here.

class History(models.Model):
    id = models.AutoField(primary_key=True)
    canvas_userid = models.CharField(max_length=10)
    asset_code = models.CharField(max_length=255)
    context_id = models.IntegerField()
    context_type = models.CharField(max_length=255)
    visited_at = models.DateTimeField(auto_now_add= False, auto_now=False)
    visited_url = models.URLField()
    interaction_seconds = models.IntegerField(blank=True, null=True)
    asset_icon = models.CharField(max_length=255)
    asset_readable_category = models.CharField(max_length=255)
    asset_name = models.CharField(max_length=255)
    context_name = models.CharField(max_length=255)
