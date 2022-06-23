import logging
import sys

from django.core.management import BaseCommand
from django.db import transaction

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.definitions import CANVAS_ACCOUNT_ID
from statistics_api.quizzes.models import QuestionStatistics, QuizStatistics, Answer, AnswerSet, SubmissionStatistics

class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        api_client = CanvasApiClient()
        canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
        courses = api_client.get_courses(canvas_account_id=canvas_account_id)
        for course in courses:
            course_id = course.get('id')
            quizzes = api_client.get_quizzes_in_course(course_id)
            for quiz in quizzes:
                quiz_id = quiz.get('id')
                self.fetch_statistics_from_single_quiz(api_client, course_id, quiz_id)
        #Temp:
        #self.fetch_statistics_from_single_quiz(api_client, 502, 2720)

    @transaction.atomic
    def fetch_statistics_from_single_quiz(self, api_client, course_id, quiz_id):
        response = api_client.get_quiz_statistics(course_id, quiz_id)
        if response is None:
            return
        quiz_data = response['quiz_statistics'][0]
        statistics_object, created = QuizStatistics.objects.update_or_create(
            canvas_course_id=course_id,
            canvas_quiz_id=quiz_id,
            defaults={'canvas_id' : quiz_data.get('id')})

        question_data = quiz_data['question_statistics']
        for question in question_data:
            question_object, created = QuestionStatistics.objects.update_or_create(
                canvas_id=question.get('id'),
                defaults={
                    'question_type' : question.get('question_type'),
                    'question_text' : question.get('question_text'),
                    'responses' : question.get('responses'),
                    'quiz_statistics' : statistics_object})

            if 'answer_sets' in question:
                answer_sets = question['answer_sets']
                self.parse_answer_sets(answer_sets, question_object)

            if 'answers' in question:
                answers = question['answers']
                self.parse_answers(answers, question_object)

        submission_object = quiz_data['submission_statistics']
        SubmissionStatistics.objects.update_or_create(
            quiz_statistics=statistics_object,
            defaults={
                'unique_count' : submission_object.get('unique_count')})

    def parse_answer_sets(self, answer_sets, question_object):
        for answer_set in answer_sets:
            answer_set_object, created =  AnswerSet.objects.update_or_create(
                canvas_id = answer_set.get('id'),
                defaults={
                    'text': answer_set.get('text'),
                    'question_statistics' : question_object})
            answers = answer_set['answers']
            self.parse_answers(answers, answer_set_object)

    def parse_answers(self, answers, parent_object):
        if isinstance(parent_object, AnswerSet):
            for answer in answers:
                Answer.objects.update_or_create(
                    canvas_id=answer.get('id'),
                    answer_sets=parent_object,
                    defaults={
                        'text' : answer.get('text'),
                        'responses' : answer.get('responses')})

        if isinstance(parent_object, QuestionStatistics):
            for answer in answers:
                Answer.objects.update_or_create(
                    canvas_id=answer.get('id'),
                    question_statistics=parent_object,
                    defaults={
                        'text' : answer.get('text'),
                        'responses' : answer.get('responses')})
