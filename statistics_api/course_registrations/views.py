from django.shortcuts import render

# Create your views here.

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from statistics_api.course_registrations.models import DailyRegistrations
from datetime import date, timedelta
from django.db.models import Sum



# Create your views here.

@api_view(('GET',))
def course_groups(request, course_id: int):
    period = request.GET.get('period')
    yesterday = date.today() - timedelta(days=1)
    if period == 'day':
        query = DailyRegistrations.objects.filter(course_id=course_id, date=yesterday)
        result = DailyRegistrationsSerializer(query, many=True)
        return Response({"start_date" : yesterday, "end_date": yesterday, "result" : result.data})
    elif period == 'week':
        start_date = date.today() - timedelta(days=7)
        query = DailyRegistrations.objects.filter(course_id=course_id, date__range=[start_date, yesterday]).values('group_id', 'group_name').annotate(registrations=Sum('registrations'))
        result = DailyRegistrationsSerializer(query, many=True)
        return Response({"start_date": start_date, "end_date" : yesterday, "result" : result.data })
    elif period == 'month':
        start_date = date.today() - timedelta(days=30)
        query = DailyRegistrations.objects.filter(course_id=course_id, date__range=[start_date, yesterday]).values('group_id', 'group_name').annotate(registrations=Sum('registrations'))
        result = DailyRegistrationsSerializer(query, many=True)
        return Response({"start_date": start_date, "end_date" : yesterday, "result" : result.data })
    else:
        return Response({"error": "Invalid period parameter value"}, status=400)

@api_view(('GET',))
def course_groups_leaders(request, course_id: int):
    period = request.GET.get('period')
    yesterday = date.today() - timedelta(days=1)
    if period == 'day':
        query = DailyRegistrations.objects.filter(course_id=course_id, date=yesterday, group_name__startswith='Skoleleder')
        result = DailyRegistrationsSerializer(query, many=True)
        return Response({"start_date" : yesterday, "end_date": yesterday, "result" : result.data})
    elif period == 'week':
        start_date = date.today() - timedelta(days=7)
        query = DailyRegistrations.objects.filter(course_id=course_id, date__range=[start_date, yesterday], group_name__startswith='Skoleleder').values('group_id', 'group_name').annotate(registrations=Sum('registrations'))
        result = DailyRegistrationsSerializer(query, many=True)
        return Response({"start_date": start_date, "end_date" : yesterday, "result" : result.data })
    elif period == 'month':
        start_date = date.today() - timedelta(days=30)
        query = DailyRegistrations.objects.filter(course_id=course_id, date__range=[start_date, yesterday], group_name__startswith='Skoleleder').values('group_id', 'group_name').annotate(registrations=Sum('registrations'))
        result = DailyRegistrationsSerializer(query, many=True)
        return Response({"start_date": start_date, "end_date" : yesterday, "result" : result.data })
    else:
        return Response({"error": "Invalid period parameter value"}, status=400)

class DailyRegistrationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRegistrations
        fields = (
            'group_id',
            'group_name',
            'registrations',
        )
        depth = 1
