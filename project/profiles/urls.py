from django.conf.urls import url

from .views import ProfileDetailView

urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$', ProfileDetailView.as_view(), name='detail'),
]
