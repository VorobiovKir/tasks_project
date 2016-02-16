import logging
import hashlib
import random
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth import (login as app_login,
                                 logout as app_logout)
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, RedirectView

from .forms import AuthenticationForm, RegistrationForm

from generic.functions.create_log_for_superuser import prepare_and_create_log
from generic.functions.send_email import SendEmailClass

from profiles.models import Profile


"""Variable for logging site"""
LOGGER = logging.getLogger(__name__)


class LoginView(FormView):
    """Login View

        View allows User loggining, if User successfully login
    he redirect on {tasks:list} (Main page)

    Extends:
        django.views.generic.FormView

    Variables:
        template_name {str} -- template
        success_url {str} -- url if User successfully login
        form_class {obj} -- form for view

    """
    form_class = AuthenticationForm
    template_name = 'authorization/login.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        app_login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)


class RegisterView(FormView):
    """Registration View

        View allows User registration. If User successfully registration
    in profile.models.profile create new field with User's slug, activation key
    and expire day of this key. View generate activation key and send his on
    User Email for confirmed.

    Extends:
        django.views.generic.FormView

    Variables:
        template_name {str} -- template
        success_url {str} -- url if User successfully registrated
        form_class {obj} -- form for view

    Methods:
        form_valid -- Save User, Create Profile[slug],
            Generate activation key and expire date for confirm email.
            Send on User's email confirm letter

    """
    form_class = RegistrationForm
    template_name = 'authorization/registration.html'
    success_url = reverse_lazy('tasks:list')

    def generate_activation_key(self, user_info):
        """Generate activation key

            Methods generate activation key for confirmed User's email.
        Generate with 'SHA1' technology and User Information

        Arguments:
            user_info {str} -- something information from User for
        generate key

        Returns:
            [str[HASH]] -- HASH string

        """
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        return hashlib.sha1(salt + user_info).hexdigest()

    def generate_key_expires(self, term_days):
        """Generate Expire Key Date

        Generate Date when activation key doesn't be worked

        Arguments:
            term_days {int} -- count day where activation key doesn't be
                worked

        Returns:
            [string] -- date

        """
        return datetime.datetime.today() + datetime.timedelta(term_days)

    def form_valid(self, form):
        """Form Valid

        If form valid User save in database with his profile.
        Generate Activation key with expire date.
        For User's email sended confirmation letter

        Return:
            Redirect

        """
        form.save()

        user_email = form.cleaned_data['email']

        activation_key = self.generate_activation_key(user_email)
        key_expires = self.generate_key_expires(settings.KEY_EXPIRE_TERM)

        user = User.objects.get(email=user_email)
        user.groups.add(Group.objects.get(name='customers'))

        slug = self.create_slug(user)

        new_profile = Profile(
            user=user,
            activation_key=activation_key,
            key_expires=key_expires,
            slug=slug
        )
        new_profile.save()

        email_data = {
            'username': user.username,
            'activation_key': activation_key
        }

        email = SendEmailClass(
            subject=_('Account Confirmation'),
            sender=settings.EMAIL_HOST_USER,
            to=settings.EMAIL_SUPERUSERS,
            template=settings.EMAIL_TEMPLATES['confirmation'],
            data=email_data
        )
        email.send()

        return render(
            self.request,
            settings.REGISTRATION_TEMPLATES['thanks'],
            context={
                'username': user.username,
                'email': user.email
            }
        )

    def create_slug(self, user, new_slug=None):
        """Create User's slug

        If slug unique -- return slug
        Else create new slug

        Arguments:
            user {obj} -- User

        Keyword Arguments:
            new_slug {str} -- slug (default: {None})

        Returns:
            [str] -- unique slug

        """
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
    """Logout View

    If User is authenticated doing log out User from site

    Extends:
        django.views.generic.RedirectView

    Variables:
        url {str} -- redirect if success logout

    """
    url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            app_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class ConfirmEmailView(RedirectView):
    """Confirmation Email

    If confirmation key and expire date are valid User's status
    is active = True

    Extends:
        django.views.generic.RedirectView

    """
    def get(self, request, activation_key, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('tasks:list'))
        user_profile = get_object_or_404(Profile,
                                         activation_key=activation_key)

        if user_profile.key_expires < timezone.now():
            # generate new key and date and send to email
            LOGGER.error(_("User expires date less than now"))

        user = user_profile.user
        user.is_active = True
        user.save()

        prepare_and_create_log(4, '', user.profile.slug, '')

        messages.success(self.request,
                         _('Your activate you account, please login'))
        return redirect(reverse('auth:login'))
