from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset


class RegistrationForm(UserCreationForm):
    """ Registration Form

    Registration form for new user. Use Crispy forms.

    Model:
        django.contrib.auth.models.User

    Extends:
        django.contrib.auth.forms.UserCreationForm

    Variables:
        email {string} -- required, unique, user email
        username {string} -- user name
        password1 {string} -- user password
        password2 {string} -- confirmed user password

    Methods:
        clean_email -- raise error if email not unique
        save -- make user.is_active = False

    """
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.html5_required = True
        self.helper.form_show_errors = True
        self.helper.form_tag = False
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'
        self.helper.layout = Layout(
            Fieldset(
                'Registration',
                'email',
                'username',
                'password1',
                'password2'
            ),
        )

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Duplicate email'))
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        if commit:
            user.is_active = False
            user.save()
        return user


class AuthenticationForm(AuthenticationForm):
    """ Authentication Form

    Authentication form for user. Use Crispy forms.

    Model:
        django.contrib.auth.models.User

    Extends:
        django.contrib.auth.forms.AuthenticationForm

    Variables:
        username {string} -- user name
        password {string} -- user password

    """
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.html5_required = True
        self.helper.form_show_errors = True
        self.helper.form_tag = False
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'
        self.helper.layout = Layout(
            Fieldset(
                'Sign in',
                'username',
                'password',
            ),
        )

    class Meta:
        model = User
        fields = ['username', 'password']
