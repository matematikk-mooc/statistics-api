from django.db import models

# Create your models here.

class Visits(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    visits = models.IntegerField()
    unique_visitors = models.IntegerField()
