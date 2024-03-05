from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import json as JSON
from statistics_api.history.models import History


class TestHistoryModels(TestCase):
    def setUp(self):
        History.objects.create(
            id=1,
            canvas_userid='1',
            context_id=123,
            context_type="Course",
            asset_code="wiki_page_1234",
            visited_at=timezone.now(),
            visited_url="http://example.com",
            interaction_seconds=60,
            asset_readable_category="wiki",
            asset_name="Example Wiki",
            asset_icon="icon",
            context_name="Example Course"
        )
        History.objects.create(
            id=2,
            canvas_userid='2',
            context_id=456,
            context_type="Course",
            asset_code="wiki_page_5678",
            visited_at=timezone.now(),
            visited_url="http://example.com",
            interaction_seconds=60,
            asset_readable_category="wiki",
            asset_name="Example Wiki",
            asset_icon="icon",
            context_name="Example Course"
        )
        History.objects.create(
            id=3,
            canvas_userid='2',
            context_id=789,
            context_type="Course",
            asset_code="wiki_page_91011",
            visited_at="2024-02-01 13:00:00",
            visited_url="http://example.com",
            interaction_seconds=60,
            asset_readable_category="wiki",
            asset_name="Example Wiki",
            asset_icon="icon",
            context_name="Example Course"
        )
        History.objects.create(
            id=4,
            canvas_userid='3',
            context_id=123,
            context_type="Course",
            asset_code="wiki_page_1234",
            visited_at="2024-02-20 13:00:00",
            visited_url="http://example.com",
            interaction_seconds=60,
            asset_readable_category="wiki",
            asset_name="Example Wiki",
            asset_icon="icon",
            context_name="Example Course"
        )
        History.objects.create(
            id=5,
            canvas_userid='3',
            context_id=123,
            context_type="Course",
            asset_code="wiki_page_1234",
            visited_at="2024-02-18 13:00:00",
            visited_url="http://example.com",
            interaction_seconds=120,
            asset_readable_category="wiki",
            asset_name="Example Wiki",
            asset_icon="icon",
            context_name="Example Course"
        )

    def tearDown(self):
        pass


    # Tests for the history model

    def test_history_object_created(self):
        history = History.objects.get(id=1)
        self.assertEqual(history.canvas_userid, '1')
        self.assertEqual(history.context_id, 123)
        self.assertEqual(history.context_type, "Course")
        self.assertEqual(history.asset_code, "wiki_page_1234")
        self.assertEqual(history.visited_at.date(), timezone.now().date())
        self.assertEqual(history.visited_url, "http://example.com")
        self.assertEqual(history.interaction_seconds, 60)
        self.assertEqual(history.asset_readable_category, "wiki")
        self.assertEqual(history.asset_name, "Example Wiki")
        self.assertEqual(history.asset_icon, "icon")
        self.assertEqual(history.context_name, "Example Course")

    def test_history_object_count(self):
        history = History.objects.all()
        self.assertEqual(history.count(), 5)
        history_user1 = History.objects.filter(canvas_userid='1')
        self.assertEqual(history_user1.count(), 1)
        history_user2 = History.objects.filter(canvas_userid='2')
        self.assertEqual(history_user2.count(), 2)
        history_nonExistingUser = History.objects.filter(canvas_userid='99')
        self.assertEqual(history_nonExistingUser.count(), 0)

    def test_history_timeframe(self):
        history_timeframeToday = History.objects.filter(visited_at__date=timezone.now().date())
        self.assertEqual(history_timeframeToday.count(), 2)
        self.assertEqual(history_timeframeToday[0].canvas_userid, '1')
        self.assertEqual(history_timeframeToday[1].canvas_userid, '2')

        historybetween190224_today = History.objects.filter(visited_at__range=["2024-02-19 00:00:00", timezone.now()])
        self.assertEqual(historybetween190224_today.count(), 3)
        self.assertEqual(historybetween190224_today[0].canvas_userid, '1')
        self.assertEqual(historybetween190224_today[1].canvas_userid, '2')
        self.assertEqual(historybetween190224_today[2].canvas_userid, '3')

    # Tests for the history views

    def test_user_history(self):
        client = Client()
        response_u1 = client.get(reverse('user_history', args=('1',)))
        self.assertEqual(response_u1.status_code, 200)
        # Expecting a list of one object as there is one history object for user 1
        result_u1 = JSON.loads(response_u1.content)
        self.assertEqual(len(result_u1), 1)

        response_u2 = client.get(reverse('user_history', args=('2',)))
        self.assertEqual(response_u2.status_code, 200)
        # Expecting a list of two objects as there are two history objects for user 2
        result_u2 = JSON.loads(response_u2.content)
        self.assertEqual(len(result_u2), 2)

    def test_user_history_on_context(self):
        client = Client()
        response_u1c123 = client.get(reverse('user_history_on_context', args=('1', 123)))
        self.assertEqual(response_u1c123.status_code, 200)
        # Expecting a list of one object as there is one history object for user 1 in context 123
        result_u1c123 = JSON.loads(response_u1c123.content)
        self.assertEqual(len(result_u1c123), 1)

        response_u2c456 = client.get(reverse('user_history_on_context', args=('2', 456)))
        self.assertEqual(response_u2c456.status_code, 200)
        # Expecting a list of one object as there is one history object for user 2 in context 456
        result_u2c456 = JSON.loads(response_u2c456.content)
        self.assertEqual(len(result_u2c456), 1)


    def test_context_history(self):
        client = Client()
        response_c123 = client.get(reverse('context_history', args=(123,)))
        self.assertEqual(response_c123.status_code, 200)
        # Expecting there to be three visits to context 123
        result_c123 = JSON.loads(response_c123.content)
        self.assertEqual(result_c123['Result'][0]['visits'], 3)

        response_c456 = client.get(reverse('context_history', args=(456,)))
        self.assertEqual(response_c456.status_code, 200)
        # Expecting there to be one visit to context 456
        result_c456 = JSON.loads(response_c456.content)
        self.assertEqual(result_c456['Result'][0]['visits'], 1)

    def test_context_history_not_found(self):
        client = Client()
        response_c321 = client.get(reverse('context_history', args=(321,)))
        self.assertEqual(response_c321.status_code, 404)

    def test_user_aggregated_history(self):
        client = Client()
        response_u1 = client.get(reverse('user_aggregated_history', args=('1',)))
        self.assertEqual(response_u1.status_code, 200)
        # Expecting a list of one object as there is one history object for user 1
        result_u1 = JSON.loads(response_u1.content)
        self.assertEqual(len(result_u1['Result']), 1)
        # User 1 has one visit with a total of 60 seconds
        self.assertEqual(result_u1['Result'][0]['visits'], 1)
        self.assertEqual(result_u1['Result'][0]['time_spent_seconds'], 60)

        response_u2 = client.get(reverse('user_aggregated_history', args=('2',)))
        self.assertEqual(response_u2.status_code, 200)
        # Expecting a list of two object as there is two contexts visited by user 2
        result_u2 = JSON.loads(response_u2.content)
        self.assertEqual(len(result_u2['Result']), 2)

        response_u3 = client.get(reverse('user_aggregated_history', args=('3',)))
        self.assertEqual(response_u3.status_code, 200)
        # Expecting a list of one object as user 3 has wisiited one context twice
        result_u3 = JSON.loads(response_u3.content)
        self.assertEqual(len(result_u3['Result']), 1)
        # User 3 has two visit with a total of 180 seconds
        self.assertEqual(result_u3['Result'][0]['visits'], 2)
        self.assertEqual(result_u3['Result'][0]['time_spent_seconds'], 180)

    def test_user_aggregated_history_not_found(self):
        client = Client()
        response_u99 = client.get(reverse('user_aggregated_history', args=('99',)))
        # Expecting a 404 response as there is no history for user 99
        self.assertEqual(response_u99.status_code, 404)
