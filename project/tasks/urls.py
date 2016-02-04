from django.conf.urls import url

from .views import (TaskListView, TaskCreateView,
                    TaskDetailView, FileCreateView,
                    ExpectDateUpdateView)

urlpatterns = [
    url(r'^$', TaskListView.as_view(), name='list'),
    url(r'^create/$', TaskCreateView.as_view(), name='form'),
    url(r'^file_create/$', FileCreateView.as_view(), name='file_create'),
    url(r'^(?P<slug>[\w-]+)/$', TaskDetailView.as_view(), name='detail'),
    url(r'^(?P<slug>[\w-]+)/expect_date_change/$',
        ExpectDateUpdateView.as_view(), name='expect_date_change'),
]
