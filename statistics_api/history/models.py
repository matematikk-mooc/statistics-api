from django.db import models

# Create your models here.

class History(models.Model):
    id = models.AutoField(primary_key=True)
    canvas_userid = models.CharField(max_length=10)
    asset_code = models.CharField(max_length=255, null=True, blank=True )
    context_id = models.IntegerField(null=True, blank=True)
    context_type = models.CharField(max_length=255, null=True, blank=True)
    visited_at = models.DateTimeField(auto_now_add= False, auto_now=False)
    visited_url = models.URLField(max_length=1024, null=True, blank=True)
    interaction_seconds = models.IntegerField(blank=True, null=True)
    asset_icon = models.CharField(max_length=255, null=True, blank=True)
    asset_readable_category = models.CharField(max_length=255, null=True, blank=True)
    asset_name = models.CharField(max_length=512, null=True, blank=True)
    context_name = models.CharField(max_length=255, null=True, blank=True)
