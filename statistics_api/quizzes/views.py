
# from rest_framework import serializers
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from django.db.models import Prefetch

# from statistics_api.quizzes.models import AnswerUserGroup, Answer, AnswerSet, QuestionStatistics, QuizStatistics, SubmissionStatistics, OpenAnswerResponse

# # Create your views here.
# @api_view(('GET',))
# def quiz_statistics(request, course_id: int, quiz_id: int):
#     groups = request.GET.get('groups')
#     print(groups)
#     if groups:
#         groups = groups.split(',')
#         query = QuizStatistics.objects.filter(
#                 canvas_course_id=course_id,
#                 canvas_quiz_id=quiz_id
#             ).prefetch_related(
#                 Prefetch(
#                     'question_statistics__answers__user_groups',
#                     queryset=AnswerUserGroup.objects.filter(group_id__in=groups)
#                 )
#             ).prefetch_related(
#                 Prefetch(
#                     'question_statistics__open_responses',
#                     queryset=OpenAnswerResponse.objects.filter(group_id__in=groups)
#                 )
#             )
#     else:
#         query = QuizStatistics.objects.filter(
#                 canvas_course_id=course_id,
#                 canvas_quiz_id=quiz_id
#             )
#     result = QuizStatisticsSerializer(query, many=True)
#     return Response(result.data)

# @api_view(('GET',))
# def course_quizzes_statistics(request, course_id: int):
#     groups = request.GET.get('groups')
#     print(groups)
#     if groups:
#         groups = groups.split(',')
#         query = QuizStatistics.objects.filter(
#                 canvas_course_id=course_id
#             ).prefetch_related(
#                 Prefetch(
#                     'question_statistics__answers__user_groups',
#                     queryset=AnswerUserGroup.objects.filter(group_id__in=groups)
#                 )
#             ).prefetch_related(
#                 Prefetch(
#                     'question_statistics__open_responses',
#                     queryset=OpenAnswerResponse.objects.filter(group_id__in=groups)
#                 )
#             )
#     else:
#         query = QuizStatistics.objects.filter(canvas_course_id=course_id)
#     result = QuizStatisticsSerializer(query, many=True)
#     return Response(result.data)

# class AnswerUserGroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AnswerUserGroup
#         fields = (
#             'group_id',
#             'group_name',
#             'count'
#         )
#         depth = 1

# class AnswerSerializer(serializers.ModelSerializer):
#     user_groups = AnswerUserGroupSerializer(many=True)
#     class Meta:
#         model = Answer
#         fields = (
#             'id',
#             'canvas_id',
#             'text',
#             'responses',
#             'user_groups'
#         )
#         depth = 1


# class AnswerSetSerializer(serializers.ModelSerializer):
#     answers = AnswerSerializer(many=True)
#     class Meta:
#         model = AnswerSet
#         fields = (
#             'id',
#             'canvas_id',
#             'text',
#             'answers'
#         )
#         depth = 1

# class OpenAnswerResponseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OpenAnswerResponse
#         fields = (
#             'group_id',
#             'group_name',
#             'submission_time',
#             'answer'
#         )
#         depth = 1


# class QuestionStatisticsSerializer(serializers.ModelSerializer):
#     open_responses = OpenAnswerResponseSerializer(many=True, required=False)
#     answers = AnswerSerializer(many=True, required=False)
#     answer_sets = AnswerSetSerializer(many=True)
#     class Meta:
#         model = QuestionStatistics
#         fields = (
#             'id',
#             'canvas_id',
#             'question_type',
#             'question_text',
#             'responses',
#             'open_responses',
#             'answers',
#             'answer_sets',
#         )
#         depth = 1

# class SubmissionStatisticsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SubmissionStatistics
#         fields = (
#             'id',
#             'unique_count'
#         )
#         depth = 1


# class QuizStatisticsSerializer(serializers.ModelSerializer):
#     question_statistics = QuestionStatisticsSerializer(many=True)
#     submission_statistics = SubmissionStatisticsSerializer(many=True)
#     class Meta:
#         model = QuizStatistics
#         fields = (
#             'id',
#             'canvas_course_id',
#             'canvas_quiz_id',
#             'title',
#             'canvas_id',
#             'question_statistics',
#             'submission_statistics'
#         )
#         depth = 1
