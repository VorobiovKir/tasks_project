from django.conf.urls import url

from .views import TaskListView, TaskCreateView, TaskDetailView

urlpatterns = [
    url(r'^$', TaskListView.as_view(), name='list'),
    url(r'^create/$', TaskCreateView.as_view(), name='form'),
    url(r'^(?P<slug>[\w-]+)/$', TaskDetailView.as_view(), name='detail'),
]
