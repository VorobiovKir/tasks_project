from django.conf.urls import url

from .views import (LoginView, RegisterView,
                    LogoutView, ConfirmEmailView)

urlpatterns = [
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^register/', RegisterView.as_view(), name='register'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^confirm/(?P<activation_key>\w+)/$', ConfirmEmailView.as_view(),
        name='confirm_email'),
]
