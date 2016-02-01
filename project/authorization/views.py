from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, RedirectView
from django.contrib.auth import authenticate, login as app_login
from django.contrib.auth import logout as app_logout
from django.contrib.auth.models import Group

from .forms import AuthenticationForm, RegistrationForm


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'authorization/login.html'
    success_url = reverse_lazy('tasks:main')

    def form_valid(self, form):
        app_login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)


class RegisterView(FormView):
    form_class = RegistrationForm
    template_name = 'authorization/registration.html'
    success_url = reverse_lazy('tasks:main')

    def form_valid(self, form):
        user = form.save()
        user.groups.add(Group.objects.get(name='customers'))
        new_user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        app_login(self.request, new_user)
        return super(RegisterView, self).form_valid(form)


class LogoutView(RedirectView):
    url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            app_logout(request)

        return super(LogoutView, self).get(request, *args, **kwargs)
