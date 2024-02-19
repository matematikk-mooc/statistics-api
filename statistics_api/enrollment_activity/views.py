from rest_framework import viewsets, serializers
from rest_framework.response import Response
from django.core.exceptions import ValidationError

# Create your views here.
from statistics_api.enrollment_activity.models import EnrollmentActivity


class EnrollmentActivityViewSet(viewsets.ViewSet):
    """
    A enrollment ViewSet for listing or retrieving enrollment activity.
    """

    def list(self, request):
        from_date = request.GET.get("from")
        to_date = request.GET.get("to")
        try:
            queryset = self.filter_query(from_date, to_date)
            serializer = EnrollmentActivitySerializer(queryset, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"Error": str(e)}, status=400)
        except Exception as e:
            return Response({"Error": str(e)}, status=500)

    def retrieve(self, request, pk=None):
        from_date = request.GET.get("from")
        to_date = request.GET.get("to")
        try:
            queryset = self.filter_query(from_date, to_date, course_id=pk)
            serializer = EnrollmentActivitySerializer(queryset, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"Error": str(e)}, status=400)
        except Exception as e:
            return Response({"Error": str(e)}, status=500)

    def filter_query(self, from_date, to_date, course_id=None):
        queryset = EnrollmentActivity.objects.all()
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if from_date and to_date:
            queryset = queryset.filter(activity_date__gte=from_date, activity_date__lte=to_date)
        elif from_date:
            queryset = queryset.filter(activity_date__gte=from_date)
        elif to_date:
            queryset = queryset.filter(activity_date__lte=to_date)

        queryset = queryset.order_by('-activity_date')
        return queryset

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
