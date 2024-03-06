from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from statistics_api.matomo.models import Visits, PageStatistics
import json as JSON

class TestMatomo(TestCase):
    def setUp(self):
        Visits.objects.create(
            date=timezone.now(),
            visits=100,
            unique_visitors=50,
            unique_visitors_new=30,
            unique_visitors_returning=20,
            visits_new=70,
            visits_returning=30,
            bounce_count_new=10,
            bounce_count_returning=5,
            sum_visit_length_new=1000,
            sum_visit_length_returning=800,
            actions_new=300,
            actions_returning=20,
            max_actions_new=10,
            max_actions_returning=8,
            bounce_rate_new='20%',
            bounce_rate_returning='5%',
            avg_time_on_site_new=20,
            avg_time_on_site_returning=25,
            actions_per_visit_new=3.5,
            actions_per_visit_returning=4.0
        )
        PageStatistics.objects.create(
            date=timezone.now(),
            canvas_course_id="123",
            label="Test Page",
            visits=100,
            sum_time_spent=5000,
            average_time_spent=50,
            unique_visitors=50,
            url="https://example.com/",
            bounce_rate="10%",
            exit_rate="20%",
            exit_visits=20,
            entry_visits=30,
            segment="Test Segment"
        )
        PageStatistics.objects.create(
            date=timezone.now() - timedelta(3),
            canvas_course_id="123",
            label="Test Page",
            visits=100,
            sum_time_spent=5000,
            average_time_spent=50,
            unique_visitors=50,
            url="https://example.com/",
            bounce_rate="10%",
            exit_rate="20%",
            exit_visits=20,
            entry_visits=30,
            segment="Test Segment"
        )
        PageStatistics.objects.create(
            date=timezone.now(),
            canvas_course_id="456",
            label="Test Page",
            visits=100,
            sum_time_spent=5000,
            average_time_spent=50,
            unique_visitors=50,
            url="https://example.com/",
            bounce_rate="10%",
            exit_rate="20%",
            exit_visits=20,
            entry_visits=30,
            segment="Test Segment"
        )


    def test_visits_model(self):
        visit = Visits.objects.all().first()
        self.assertEqual(visit.visits, 100)
        self.assertEqual(visit.unique_visitors, 50)
        self.assertEqual(visit.unique_visitors_new, 30)
        self.assertEqual(visit.unique_visitors_returning, 20)
        self.assertEqual(visit.visits_new, 70)
        self.assertEqual(visit.visits_returning, 30)
        self.assertEqual(visit.bounce_count_new, 10)
        self.assertEqual(visit.bounce_count_returning, 5)
        self.assertEqual(visit.sum_visit_length_new, 1000)
        self.assertEqual(visit.sum_visit_length_returning, 800)
        self.assertEqual(visit.actions_new, 300)
        self.assertEqual(visit.actions_returning, 20)
        self.assertEqual(visit.max_actions_new, 10)
        self.assertEqual(visit.max_actions_returning, 8)
        self.assertEqual(visit.bounce_rate_new, '20%')
        self.assertEqual(visit.bounce_rate_returning, '5%')
        self.assertEqual(visit.avg_time_on_site_new, 20)
        self.assertEqual(visit.avg_time_on_site_returning, 25)
        self.assertEqual(visit.actions_per_visit_new, 3.5)
        self.assertEqual(visit.actions_per_visit_returning, 4.0)

    def test_page_statistics_model(self):
        pagestat =  PageStatistics.objects.all().first()
        self.assertEqual(pagestat.date, timezone.now().date())
        self.assertEqual(pagestat.canvas_course_id, "123")
        self.assertEqual(pagestat.label, "Test Page")
        self.assertEqual(pagestat.visits, 100)
        self.assertEqual(pagestat.sum_time_spent, 5000)
        self.assertEqual(pagestat.average_time_spent, 50)
        self.assertEqual(pagestat.unique_visitors, 50)
        self.assertEqual(pagestat.url, "https://example.com/")
        self.assertEqual(pagestat.bounce_rate, "10%")
        self.assertEqual(pagestat.exit_rate, "20%")
        self.assertEqual(pagestat.exit_visits, 20)
        self.assertEqual(pagestat.entry_visits, 30)
        self.assertEqual(pagestat.segment, "Test Segment")

    def test_visits_statistics(self):
        client = Client()
        url = reverse('visits_statistics')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)


    def test_page_statistics(self):
        client = Client()
        url = reverse('page_statistics')
        response = client.get(url)
        result = JSON.loads(response.content)
        self.assertEqual(response.status_code, 200)
        #Expecting 3 as there are 3 page_stats added to the db
        self.assertEqual(len(result), 3)


    def test_course_pages_statistics(self):
        client = Client()
        url = reverse('course_pages_statistics', args=('123',))
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        result = JSON.loads(response.content)
        #Expecting 2 as there are 2 page_stats for course 123
        self.assertEqual(len(result), 2)


    def test_visits_statistics_invalid_date(self):
        # Testing if an invalid date range returns a 400 error
        url = reverse('visits_statistics')
        client = Client()
        response = client.get(f'{url}?from=01-01-2023&to=02-01-2023')
        self.assertEqual(response.status_code, 400)

    def test_page_stats_timeframe(self):
        client = Client()
        url  = reverse('page_statistics')
        response = client.get(url, {'from' : (timezone.now()-timedelta(1)).date(), 'to' : timezone.now().date()})
        self.assertEqual(response.status_code, 200)
        result = JSON.loads(response.content)
        #Expecting two of the page stats to fit the timeframe
        self.assertEqual(len(result), 2)
