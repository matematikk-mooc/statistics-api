from rest_framework import serializers
from rest_framework.response import Response
from django.http import JsonResponse

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.quizzes.models import Answer, QuestionStatistics, QuizStatistics, SubmissionStatistics

# Create your views here.


def quiz_statistics(self, course_id: int, quiz_id: int):
    api_client = CanvasApiClient()
    response = api_client.get_quiz_statistics(course_id, quiz_id)
    quiz_data = response['quiz_statistics'][0]
    statistics_object = QuizStatistics.objects.create(canvas_course_id=course_id, canvas_quiz_id=quiz_id, canvas_id=quiz_data['id'])
    question_data = quiz_data['question_statistics']
    for question in question_data:
        question_object = QuestionStatistics.objects.create(canvas_id=question['id'], question_type=question['question_type'], question_text=question['question_text'], responses=question['responses'], quiz_statistics=statistics_object)
        answer_data = question['answers']
        for answer in answer_data:
           Answer.objects.create(canvas_id=answer['id'], text=answer['text'], responses=answer['responses'], question_statistics=question_object)
    submission_object = quiz_data['submission_statistics']
    SubmissionStatistics.objects.create(unique_count=submission_object['unique_count'], quiz_statistics=statistics_object)
    #query = QuizStatistics.objects.all().filter(canvas_quiz_id=quiz_id)
    #result = QuizStatisticsSerializer(query, many=True)
    #return Response(result.data)
    return JsonResponse({'result' : quiz_data})


class QuizStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizStatistics
        fields = (
            'id',
            'canvas_course_id',
            'canvas_quiz_id',
            'canvas_id',
            'question_statistics',
            'submission_statistics'
        )
        depth = 1
