from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from statistics_api.analytics.models import CanvasAnalytics
# Create your views here.

@api_view(('GET',))
def course_analytics(self, request, course_id: int):
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    if from_date and to_date:
        queryset = CanvasAnalytics.objects.filter(course_id=course_id, date__gte=from_date, date__lte=to_date)
    elif from_date:
        queryset = CanvasAnalytics.objects.filter(course_id=course_id, date__gte=from_date)
    elif to_date:
        queryset = CanvasAnalytics.objects.filter(course_id=course_id, date__lte=to_date)
    else:
        queryset = CanvasAnalytics.objects.filter(course_id=course_id)
    queryset = queryset.order_by('-date')
    serializer = CanvasAnalyticsSerializer(queryset, many=True)
    return Response(serializer.data)



class CanvasAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanvasAnalytics
        fields = '__all__'
