from django.conf.urls import url

from .views import (TaskListView, TaskCreateView,
                    TaskDetailView, FileCreateView,
                    ExpectDateUpdateView, ResolveTaskUpdateView,
                    AcceptTaskPerformanceUpdateView, GetCsvView)

urlpatterns = [
    url(r'^$', TaskListView.as_view(), name='list'),
    url(r'^create/$', TaskCreateView.as_view(), name='create'),
    url(r'^file_create/$', FileCreateView.as_view(), name='file_create'),
    url(r'^get_csv/$', GetCsvView.as_view(), name='get_csv'),
    url(r'^(?P<slug>[\w-]+)/$', TaskDetailView.as_view(), name='detail'),
    url(r'^(?P<slug>[\w-]+)/expect_date_change/$',
        ExpectDateUpdateView.as_view(), name='expect_date_change'),
    url(r'^(?P<slug>[\w-]+)/resolve/$',
        ResolveTaskUpdateView.as_view(), name='resolve_task'),
    url(r'^(?P<slug>[\w-]+)/accept/$',
        AcceptTaskPerformanceUpdateView.as_view(), name='accept_task'),
]
