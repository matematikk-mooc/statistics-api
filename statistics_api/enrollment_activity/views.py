from django.utils.datetime_safe import datetime
from rest_framework import viewsets, serializers
from rest_framework.response import Response

# Create your views here.
from statistics_api.enrollment_activity.models import EnrollmentActivity


class EnrollmentActivityViewSet(viewsets.ViewSet):
    """
    A enrollment ViewSet for listing or retrieving enrollment activity.
    """

    def list(self, request):
        queryset = EnrollmentActivity.objects.all()
        serializer = EnrollmentActivitySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = EnrollmentActivity.objects.all().filter(course_id=pk)
        serializer = EnrollmentActivitySerializer(queryset, many=True)
        return Response(serializer.data)


class EnrollmentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentActivity
        fields = [
            "id",
            "course_id",
            "course_name",
            "active_users_count",
            "activity_date",
        ]
