from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Profile(models.Model):
    '''
        slug == username if username = unique
    '''
    age = models.IntegerField(null=True, blank=True)
    phonenum = models.CharField(max_length=124, null=True, blank=True)
    slug = models.SlugField(max_length=124, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile:detail', kwargs={'slug': self.slug})
