from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from statistics_api.matomo.models import Visits, PageStatistics


# Create your views here.

@api_view(('GET',))
def visits_statistics(request):
    queryset = Visits.objects.all()
    from_date = request.GET.get('from', None)
    to_date = request.GET.get('to', None)
    if from_date:
        queryset = queryset.filter(date__gte=from_date)
    if to_date:
        queryset = queryset.filter(date__lte=to_date)
    result = VisitsSerializer(queryset, many=True)
    return Response(result.data)

@api_view(('GET',))
def page_statistics(request):
    queryset = PageStatistics.objects.all()
    from_date = request.GET.get('from', None)
    to_date = request.GET.get('to', None)
    if from_date:
        queryset = queryset.filter(date__gte=from_date)
    if to_date:
        queryset = queryset.filter(date__lte=to_date)
    result = PageStatisticsSerializer(queryset, many=True)
    return Response(result.data)

@api_view(('GET',))
def course_pages_statistics(request, canvas_course_id: int):
    queryset = PageStatistics.objects.all().filter(canvas_course_id = canvas_course_id)
    from_date = request.GET.get('from', None)
    to_date = request.GET.get('to', None)
    if from_date:
        queryset = queryset.filter(date__gte=from_date)
    if to_date:
        queryset = queryset.filter(date__lte=to_date)
    result = PageStatisticsSerializer(queryset, many=True)
    return Response(result.data)


class VisitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visits
        fields = '__all__'



class PageStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageStatistics
        fields= '__all__'