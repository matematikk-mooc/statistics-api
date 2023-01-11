# import logging
# import sys
# import datetime

# from django.core.management import BaseCommand
# from django.db import transaction

# from statistics_api.clients.canvas_api_client import CanvasApiClient
# from statistics_api.definitions import CANVAS_ACCOUNT_ID
# from statistics_api.quizzes.models import QuestionStatistics, QuizStatistics, Answer, AnswerSet, SubmissionStatistics, \
#     AnswerUserGroup, OpenAnswerResponse
# from statistics_api.canvas_users.models import CanvasUser


# class Command(BaseCommand):

#     def handle(self, *args, **options):
#         logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#         logger = logging.getLogger()
#         api_client = CanvasApiClient()
#         canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
#         courses = api_client.get_courses(canvas_account_id=canvas_account_id)
#         for course in courses:
#             course_id = course.get('id')
#             if course_id == 360:
#                 continue
#             course_user_groups = CanvasUser.objects.all().filter(course_id=course_id)
#             quizzes = api_client.get_quizzes_in_course(course_id)
#             for quiz in quizzes:
#                 quiz_id = quiz.get('id')
#                 self.fetch_statistics_from_single_quiz(api_client, course_id, quiz_id, course_user_groups)

#     @transaction.atomic
#     def fetch_statistics_from_single_quiz(self, api_client, course_id, quiz_id, course_user_groups):
#         response = api_client.get_quiz_statistics(course_id, quiz_id)
#         if response is None:
#             return
#         quiz_metadata = api_client.get_quiz_metadata(course_id, quiz_id)
#         quiz_data = response['quiz_statistics'][0]
#         statistics_object, created = QuizStatistics.objects.update_or_create(
#             canvas_course_id=course_id,
#             canvas_quiz_id=quiz_id,
#             defaults={
#                 'canvas_id': quiz_data.get('id'),
#                 'title': quiz_metadata.get('title')})

#         question_data = quiz_data['question_statistics']
#         open_answers = []
#         for question in question_data:
#             question_object, created = QuestionStatistics.objects.update_or_create(
#                 canvas_id=question.get('id'),
#                 defaults={
#                     'question_type': question.get('question_type'),
#                     'question_text': question.get('question_text'),
#                     'responses': question.get('responses'),
#                     'quiz_statistics': statistics_object})

#             if 'answer_sets' in question:
#                 answer_sets = question['answer_sets']
#                 self.parse_answer_sets(answer_sets, question_object, course_user_groups)

#             if 'answers' in question:
#                 answers = question['answers']
#                 self.parse_answers(answers, question_object, course_user_groups)
#             question_type = question.get("question_type")
#             if question_type == "essay_question":
#                 qid = question.get("id")
#                 open_answers.append(int(qid))

#         submission_object = quiz_data['submission_statistics']
#         SubmissionStatistics.objects.update_or_create(
#             quiz_statistics=statistics_object,
#             defaults={
#                 'unique_count': submission_object.get('unique_count')})

#         if quiz_metadata.get("assignment_id") and len(open_answers) > 0:
#             self.get_open_answers(api_client, course_id, course_user_groups, quiz_metadata.get("assignment_id"),
#                                   open_answers)

#     def parse_answer_sets(self, answer_sets, question_object, course_user_groups):
#         for answer_set in answer_sets:
#             answer_set_object, created = AnswerSet.objects.update_or_create(
#                 canvas_id=answer_set.get('id'),
#                 defaults={
#                     'text': answer_set.get('text'),
#                     'question_statistics': question_object})
#             answers = answer_set['answers']
#             self.parse_answers(answers, answer_set_object, course_user_groups)

#     def parse_answers(self, answers, parent_object, course_user_groups):
#         if isinstance(parent_object, AnswerSet):
#             for answer in answers:
#                 answer_obj, created = Answer.objects.update_or_create(
#                     canvas_id=answer.get('id'),
#                     answer_sets=parent_object,
#                     defaults={
#                         'text': answer.get('text'),
#                         'responses': answer.get('responses')})
#                 self.map_responses_to_groups(answer.get('user_ids'), answer_obj, course_user_groups)

#         if isinstance(parent_object, QuestionStatistics):
#             for answer in answers:
#                 answer_obj, created = Answer.objects.update_or_create(
#                     canvas_id=answer.get('id'),
#                     question_statistics=parent_object,
#                     defaults={
#                         'text': answer.get('text'),
#                         'responses': answer.get('responses')})
#                 self.map_responses_to_groups(answer['user_ids'], answer_obj, course_user_groups)

#     def map_responses_to_groups(self, users, answer_obj, course_user_groups):
#         groups_count = []
#         for user in users:
#             groups = course_user_groups.filter(canvas_user_id=user)
#             if groups is None or len(groups) == 0:
#                 continue
#             for group in groups:
#                 count = [count for count in groups_count if count["group_id"] == getattr(group, "group_id")]
#                 if len(count) > 0:
#                     count[0]["count"] += 1
#                 else:
#                     groups_count.append(
#                         {"group_id": getattr(group, "group_id"), "group_name": getattr(group, "group_name"),
#                          "count": 1})

#         for user_group in groups_count:
#             AnswerUserGroup.objects.update_or_create(
#                 group_id=user_group["group_id"],
#                 answer=answer_obj,
#                 defaults={
#                     "group_name": user_group["group_name"],
#                     "count": user_group["count"]
#                 })

#     def get_open_answers(self, api_client, course_id, course_user_groups, assignment_id, essay_questions):
#         submissions = api_client.get_submissions_in_quiz(course_id, assignment_id)
#         yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
#         latest_submissions = [submission for submission in submissions if
#                               self.get_submitted_date(submission.get("submitted_at")) > yesterday]
#         for submission in latest_submissions:
#             user_id = submission.get("user_id")
#             submitted_time = self.get_submitted_date(submission.get("submitted_at"))
#             groups = course_user_groups.filter(canvas_user_id=user_id)
#             for history in submission.get("submission_history"):
#                 questions = history.get("submission_data")
#                 oa_questions = [question for question in questions if question["question_id"] in essay_questions]
#                 for question in oa_questions:
#                     db_question = QuestionStatistics.objects.get(canvas_id=question.get("question_id"))
#                     if not groups:
#                         OpenAnswerResponse.objects.create(
#                             question_statistics=db_question,
#                             answer=question.get("text"),
#                             submission_time=submitted_time,
#                             group_id="0000",
#                             group_name="no_group"
#                         )
#                     else:
#                         for group in groups:
#                             OpenAnswerResponse.objects.create(
#                                 question_statistics=db_question,
#                                 answer=question.get("text"),
#                                 submission_time=submitted_time,
#                                 group_id=getattr(group, "group_id"),
#                                 group_name=getattr(group, "group_name")
#                             )

#     def get_submitted_date(self, submitted_at):
#         if submitted_at is None:
#             return datetime.datetime.strptime("2000-01-01T00:00:00Z", '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z')
#         return datetime.datetime.strptime(submitted_at, '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z')
