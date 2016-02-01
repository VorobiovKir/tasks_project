from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# from django.utils.translation import ugettext_lazy as _
# from django.text.utils import slugify
from django.db.models.signals import pre_save


class Status(models.Model):
    """docstring for Status"""
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Statuses'


class Task(models.Model):
    author = models.ForeignKey(User, related_name='author')
    title = models.CharField(max_length=128)
    description = models.TextField()
    start_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    expect_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.ForeignKey(Status, default='pending')
    expert = models.ForeignKey(User, related_name='expert')
    slug = models.SlugField(max_length=124, unique=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-pk']


class Comment(models.Model):
    author = models.ForeignKey(User)
    text = models.TextField()
    is_watch = models.BooleanField(default=False)
    tasks = models.ForeignKey(Task)

    def __unicode__(self):
        return '%s...' % (self.text[:15])


# SIGNALS for create Unique Slug
def create_slug(instance, new_slug=None):
    # if instance.name not in ['create', 'delete']:
    #     slug = slugify(instance.name)
    # else:
    #     slug = slugify('unknown')
    if new_slug is not None:
        slug = new_slug
    qs = Task.objects.filter(slug=slug).order_by('-pk')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().pk)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Task)
