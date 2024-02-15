from rest_framework import serializers
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view

from statistics_api.matomo.models import Visits, PageStatistics


# Create your views here.

def filterTimeFrame(queryset, from_date, to_date):
    if from_date:
        queryset = queryset.filter(date__gte=from_date)
    if to_date:
        queryset = queryset.filter(date__lte=to_date)
    return queryset

@api_view(('GET',))
def visits_statistics(request):
    try:
        queryset = Visits.objects.all()
        queryset = filterTimeFrame(queryset, request.GET.get('from', None), request.GET.get('to', None))
        result = VisitsSerializer(queryset, many=True)
        return Response(result.data)
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        return Response({'error': 'An unexpected error occurred'}, status=500)

@api_view(('GET',))
def page_statistics(request):
    try:
        queryset = PageStatistics.objects.all()
        queryset = filterTimeFrame(queryset, request.GET.get('from', None), request.GET.get('to', None))
        result = PageStatisticsSerializer(queryset, many=True)
        return Response(result.data)
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        return Response({'error': 'An unexpected error occurred'}, status=500)

@api_view(('GET',))
def course_pages_statistics(request, canvas_course_id: int):
    try:
        queryset = PageStatistics.objects.all().filter(canvas_course_id = canvas_course_id)
        queryset = filterTimeFrame(queryset, request.GET.get('from', None), request.GET.get('to', None))
        result = PageStatisticsSerializer(queryset, many=True)
        return Response(result.data)
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        return Response({'error': 'An unexpected error occurred'}, status=500)


class VisitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visits
        fields = '__all__'



class PageStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageStatistics
        fields= '__all__'