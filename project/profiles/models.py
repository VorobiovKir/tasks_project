from __future__ import unicode_literals

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Profile(models.Model):
    """Profile model

    Add information for User's model

    Extends:
        django.db.models.Model

    Variables:
        user {int} -- OneToOne field for main User model
        slug {str} -- Unique name of User
        activation_key {str[HASH]} -- hash key for confirm email
        key_expires {str[date]} -- date for activation key
        age {int} -- User's age
        phonenum {str} -- User's phonenumber

    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=224, unique=True)
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=datetime.date.today())
    age = models.IntegerField(null=True, blank=True)
    phonenum = models.CharField(max_length=124, null=True, blank=True)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile:detail', kwargs={'slug': self.slug})
