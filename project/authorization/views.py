import logging

from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import FormView, RedirectView
from django.contrib.auth import authenticate, login as app_login
from django.contrib.auth import logout as app_logout
from django.contrib.auth.models import Group
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import hashlib
import random
import datetime

from profiles.models import Profile
from .forms import AuthenticationForm, RegistrationForm


logger = logging.getLogger(__name__)


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
        form.save()

        email = form.cleaned_data['email']
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(salt + email).hexdigest()
        key_expires = datetime.datetime.today() + datetime.timedelta(7)

        user = User.objects.get(email=email)
        user.groups.add(Group.objects.get(name='customers'))

        slug = self.create_slug(user)

        new_profile = Profile(
            user=user,
            activation_key=activation_key,
            key_expires=key_expires,
            slug=slug
        )

        new_profile.save()

        htmly = get_template('addition_page/email_confirmation.html')
        d = Context({
            'username': user.username,
            'activation_key': activation_key
        })
        text_content = htmly.render(d)

        subject = 'Account confirmation'
        from_email = settings.EMAIL_HOST_USER
        to = ['kvorobiov89@gmail.com']

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(text_content, 'text/html')

        msg.send()

        return render(
            self.request,
            'authorization/registration_need_confirm.html',
            context={
                'username': user.username,
                'email': email
            }
        )

        # return super(RegisterView, self).form_valid(form)

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


class ConfirmEmailView(RedirectView):
    def get(self, request, activation_key, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('tasks:list'))
        user_profile = get_object_or_404(Profile,
                                         activation_key=activation_key)

        if user_profile.key_expires < timezone.now():
            # generate new key and date and send to email
            logger.error(_("User expires date less than now"))

        user = user_profile.user
        user.is_active = True
        user.save()

        return redirect(reverse('tasks:list'))
