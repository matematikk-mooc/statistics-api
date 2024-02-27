from django.test import TestCase
from django.utils import timezone
from statistics_api.history.models import History

class TestHistoryModels(TestCase):
    def setUp(self):
        History.objects.create(
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

    def test_history_object(self):
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
        self.assertEqual(history.count(), 4)
        history_user1 = History.objects.filter(canvas_userid='1')
        self.assertEqual(history_user1.count(), 1)
        history_user2 = History.objects.filter(canvas_userid='2')
        self.assertEqual(history_user2.count(), 2)
        history_nonExistingUser = History.objects.filter(canvas_userid='99')
        self.assertEqual(history_nonExistingUser.count(), 0)

    def test_history_timeframe(self):
        history = History.objects.all()
        self.assertEqual(history.count(), 4)
        history_timeframeToday = History.objects.filter(visited_at__date=timezone.now().date())
        self.assertEqual(history_timeframeToday.count(), 2)
        self.assertEqual(history_timeframeToday[0].canvas_userid, '1')
        self.assertEqual(history_timeframeToday[1].canvas_userid, '2')
        historybetween190224_today = History.objects.filter(visited_at__range=["2024-02-19 00:00:00", timezone.now()])
        self.assertEqual(historybetween190224_today.count(), 3)
        self.assertEqual(historybetween190224_today[0].canvas_userid, '1')
        self.assertEqual(historybetween190224_today[1].canvas_userid, '2')
        self.assertEqual(historybetween190224_today[2].canvas_userid, '3')