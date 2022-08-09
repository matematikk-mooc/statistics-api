from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from statistics_api.quizzes.models import Answer, AnswerSet, QuestionStatistics, QuizStatistics, SubmissionStatistics

# Create your views here.

@api_view(('GET',))
def quiz_statistics(self, course_id: int, quiz_id: int):
    query = QuizStatistics.objects.all().filter(canvas_course_id=course_id, canvas_quiz_id=quiz_id)
    result = QuizStatisticsSerializer(query, many=True)
    return Response(result.data)

@api_view(('GET',))
def course_quizzes_statistics(self, course_id: int):
    query = QuizStatistics.objects.all().filter(canvas_course_id=course_id)
    result = QuizStatisticsSerializer(query, many=True)
    return Response(result.data)

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'id',
            'canvas_id',
            'text',
            'responses'
        )
        depth = 1

class AnswerSetSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    class Meta:
        model = AnswerSet
        fields = (
            'id',
            'canvas_id',
            'text',
            'answers'
        )
        depth = 1

#class OpenAnswerResponseSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = OpenAnswerResponse
#        fields = (
#            'id',
#            'answer'
#        )
#        depth = 1

class QuestionStatisticsSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, required=False)
    answer_sets = AnswerSetSerializer(many=True)
    class Meta:
        model = QuestionStatistics
        fields = (
            'id',
            'canvas_id',
            'question_type',
            'question_text',
            'responses',
            'answers',
            'answer_sets',
        )
        depth = 1

class SubmissionStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionStatistics
        fields = (
            'id',
            'unique_count'
        )
        depth = 1

class QuizStatisticsSerializer(serializers.ModelSerializer):
    question_statistics = QuestionStatisticsSerializer(many=True)
    submission_statistics = SubmissionStatisticsSerializer(many=True)
    class Meta:
        model = QuizStatistics
        fields = (
            'id',
            'canvas_course_id',
            'canvas_quiz_id',
            'title',
            'canvas_id',
            'question_statistics',
            'submission_statistics'
        )
        depth = 1
