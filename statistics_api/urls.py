"""statistics_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.urls import re_path as url
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.shortcuts import redirect

from statistics_api.controllers.high_schools_county_controller import county_high_school_statistics_by_county_id
from statistics_api.controllers.primary_schools_controller import municipality_primary_school_statistics, \
    county_primary_school_statistics
from statistics_api.controllers.version_controller import get_software_version
from statistics_api.enrollment_activity.views import EnrollmentActivityViewSet
from statistics_api.controllers.course_controller import course, course_count
from statistics_api.controllers.group_category_controller import group_category, group_category_count
from statistics_api.history.views import user_history, user_history_on_context, context_history, user_aggregated_history
from statistics_api.matomo.views import visits_statistics, page_statistics, course_pages_statistics
from statistics_api.canvas_modules.views import module_statistics, module_item_total_count, module_completed_per_date_count
from statistics_api.total_students.views import total_students_course, get_total_students_course_current, get_total_students_all_current

router = DefaultRouter()
router.register(r"user_activity", EnrollmentActivityViewSet, basename="enrollment_activity")


urlpatterns = [
    url(r'^api/statistics/(\d+)/?$', course),
    url(r'^api/statistics/(\d+)/count$', course_count),
    url(r'^api/statistics/groupCategory/(\d+)$', group_category),
    url(r'^api/statistics/groupCategory/(\d+)/count$', group_category_count),
    url(r'^api/statistics/primary_schools/municipality/(\d+)/course/(\d+)$', municipality_primary_school_statistics),
    url(r'^api/statistics/primary_schools/county/(\d+)/course/(\d+)$', county_primary_school_statistics),
    url(r'^api/statistics/high_schools/county/(\d+)/course/(\d+)$', county_high_school_statistics_by_county_id),
    url(r'^api/statistics/user/(\d+)/history$', user_history, name="user_history"),
    url(r'^api/statistics/user/(\d+)/context/(\d+)/history$', user_history_on_context, name="user_history_on_context"),
    url(r'^api/statistics/context/(\d+)/history$', context_history, name="context_history"),
    url(r'^api/statistics/user/(\d+)/history/aggregated$', user_aggregated_history, name="user_aggregated_history"),
    url(r'^api/statistics/visits/$', visits_statistics, name="visits_statistics"),
    url(r'^api/statistics/pages/$', page_statistics, name="page_statistics"),
    url(r'^api/statistics/course/(\d+)/pages/$', course_pages_statistics, name="course_pages_statistics"),


    url(r'^api/statistics/course/(\d+)/modules$', module_statistics, name="module_statistics"),
    url(r'^api/statistics/course/(\d+)/modules/count$', module_item_total_count, name="module_item_total_count"),
    url(r'^api/statistics/modules/(\d+)/per_date$', module_completed_per_date_count, name="module_completed_per_date_count"),

    url(r'^api/total_students/(\d+)$', total_students_course, name="total_students_course"),
    url(r'^api/total_students/current$', get_total_students_all_current, name="get_total_students_all_current"),
    url(r'^api/total_students/current/(\d+)$', get_total_students_course_current, name="get_total_students_course_current"),


    url(r'^version/?$', get_software_version),

    path("api/statistics/", include(router.urls)),
    path("", lambda req: redirect('api/statistics', permanent=False)),

]
