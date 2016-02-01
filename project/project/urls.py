from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('authorization.urls', namespace='auth')),
    url(r'^main/', include('tasks.urls', namespace='tasks')),
]
