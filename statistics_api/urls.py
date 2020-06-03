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

from django.conf.urls import url

from statistics_api.controllers.course_controller import course, course_count
from statistics_api.controllers.group_category_controller import group_category, group_category_count

urlpatterns = [
    url(r'^api/statistics/(\d+)/$', course),
    url(r'^api/statistics/(\d+)/count$', course_count),
    url(r'^api/statistics/groupCategory/(\d+)$', group_category),
    url(r'^api/statistics/groupCategory/(\d+)/count$', group_category_count),
]
