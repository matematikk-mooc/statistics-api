from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from statistics_api.matomo.models import Visits


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

class VisitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visits
        fields = '__all__'
