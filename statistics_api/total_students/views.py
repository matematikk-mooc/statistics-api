from django.shortcuts import render
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from statistics_api.total_students.models import TotalStudents
import datetime

# Create your views here.
@api_view(('GET',))
def total_students_course(request, course_id: int):
    try:
        queryset = TotalStudents.objects.all().filter(course_id = course_id)
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
        queryset = queryset.order_by('-date')
        result = TotalStudentsSerializer(queryset, many=True)
        return Response(result.data)
    except TotalStudents.DoesNotExist:
        return None

@api_view(('GET',))
def get_total_students_course_current(request, course_id: int):
    try:
        date = datetime.date.today()
        queryset = TotalStudents.objects.get(course_id=course_id, date=date)
        result = TotalStudentsSerializer(queryset)
        return Response(result.data)
    except TotalStudents.DoesNotExist:
        return None

@api_view(('GET',))
def get_total_students_all_current(request):
    try:
        date = datetime.date.today()
        queryset = TotalStudents.objects.filter(date=date)
        result = TotalStudentsSerializer(queryset, many=True)
        return Response(result.data)
    except TotalStudents.DoesNotExist:
        return None


class TotalStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalStudents
        fields = '__all__'