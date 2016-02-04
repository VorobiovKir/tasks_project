from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('authorization.urls', namespace='auth')),
    url(r'^main/', include('tasks.urls', namespace='tasks')),
    url(r'^profile/', include('profiles.urls', namespace='profile')),
    url(r'^$', RedirectView.as_view(
            pattern_name='tasks:list', permanent=False)),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
