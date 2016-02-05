from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset


class RegistrationForm(UserCreationForm):
    """docstring for RegistrationForm"""

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


class AuthenticationForm(AuthenticationForm):
    """AuthenticationForm"""

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
