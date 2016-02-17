from django.test import TestCase
from django.contrib.auth.models import User

from .forms import RegistrationForm


class RegistrationFormTestCase(TestCase):

    user_Foo = {
        'username': 'foo',
        'email': 'foo@foo.com',
        'password': 'foo',
    }

    def test_email_correct(self):
        user = {
            'username': 'user',
            'password1': 'user',
            'password2': 'user',
        }

        incorect_emails = [
            '',
            'something.com',
            'something@some'
            'something@some.'
            'something@.',
            'something@some.c'
        ]

        for email in incorect_emails:
            user['email'] = email
            form = RegistrationForm(user)
            self.assertFalse(form.is_valid())

        form = RegistrationForm(user)
        self.assertFalse(form.is_valid())

    def test_email_duplicate(self):
        User.objects.create(**self.user_Foo)
        user_other = {
            'username': 'other',
            'email': 'foo@foo.com',
            'password1': 'other',
            'password2': 'other',
        }
        form = RegistrationForm(user_other)
        self.assertFalse(form.is_valid())

    def test_username_duplicate(self):
        result = False
        User.objects.create(**self.user_Foo)
        user_other = {
            'username': 'foo',
            'email': 'other@other.com',
            'password': 'other',
        }
        try:
            User.objects.create(**user_other)
        except:
            result = True

        self.assertTrue(result)
