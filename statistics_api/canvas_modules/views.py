from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from statistics_api.canvas_modules.models import FinnishMarkCount, Module, ModuleItem, FinnishedStudent
from django.db.models import Prefetch, Count, Q, Sum


# Create your views here.

@api_view(('GET',))
def module_statistics(request, course_id: int):
    group = request.GET.get('group')
    if group:
        query = Module.objects.filter(course_id=course_id).prefetch_related(
            Prefetch(
                'module_items__user_groups',
                queryset=FinnishMarkCount.objects.filter(group_id=group)
            )
        )
    else:
        query = Module.objects.all().filter(course_id=course_id)
    result = ModuleSerializer(query, many=True)
    return Response(result.data)


@api_view(('GET',))
def module_item_total_count(self, course_id: int):
    query = Module.objects.all().filter(course_id=course_id).prefetch_related(
        Prefetch(
            'module_items__students',
            queryset=FinnishedStudent.objects.all().filter(completed=True)
        )
    )

    result = ModuleTotalCountSerializer(query, many=True)
    return Response(result.data)


class FinnishMarkCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinnishMarkCount
        fields = (
            'group_id',
            'group_name',
            'count'
        )
        depth = 1


class ModuleItemSerializer(serializers.ModelSerializer):
    user_groups = FinnishMarkCountSerializer(many=True)

    class Meta:
        model = ModuleItem
        fields = (
            'canvas_id',
            'title',
            'position',
            'url',
            'type',
            'completion_type',
            'user_groups',
        )
        depth = 1


class ModuleSerializer(serializers.ModelSerializer):
    module_items = ModuleItemSerializer(many=True)

    class Meta:
        model = Module
        fields = (
            'canvas_id',
            'course_id',
            'name',
            'position',
            'module_items'
        )
        depth = 1


class ModuleItemTotalCountSerializer(serializers.ModelSerializer):
    total_completed = serializers.SerializerMethodField()

    @staticmethod
    def get_total_completed(obj):
        return obj.students.count()

    class Meta:
        model = ModuleItem
        fields = (
            'canvas_id',
            'title',
            'position',
            'url',
            'type',
            'completion_type',
            'total_completed',
        )
        depth = 1


class ModuleTotalCountSerializer(serializers.ModelSerializer):
    module_items = ModuleItemTotalCountSerializer(many=True)

    class Meta:
        model = Module
        fields = (
            'canvas_id',
            'course_id',
            'name',
            'position',
            'module_items'
        )
        depth = 1
