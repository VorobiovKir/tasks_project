from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, RedirectView
from django.contrib.auth import authenticate, login as app_login
from django.contrib.auth import logout as app_logout
from django.contrib.auth.models import Group
from django.utils.text import slugify
from django.contrib.auth.models import User

from .forms import AuthenticationForm, RegistrationForm

from profiles.models import Profile


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'authorization/login.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        app_login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)


class RegisterView(FormView):
    form_class = RegistrationForm
    template_name = 'authorization/registration.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        user = form.save()
        user.groups.add(Group.objects.get(name='customers'))
        slug = self.create_slug(user)
        # !!!
        Profile.objects.create(slug=slug, user_id=user.id)
        # !!!
        new_user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        app_login(self.request, new_user)
        return super(RegisterView, self).form_valid(form)

    # !!!
    def create_slug(self, user, new_slug=None):
        if user.username not in ['edit']:
            slug = slugify(user.username)
        else:
            slug = slugify('cus_edit')
        if new_slug is not None:
            slug = new_slug
        qs = User.objects.filter(profile__slug=slug).order_by('-pk')
        exists = qs.exists()
        if exists:
            new_slug = '%s-%s' % (slug, qs.first().pk)
            return self.create_slug(user, new_slug=new_slug)
        return slug


class LogoutView(RedirectView):
    url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            app_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
