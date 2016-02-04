from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify
# from django.utils.translation import ugettext_lazy as _


class Status(models.Model):
    """docstring for Status"""
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Statuses'


class Task(models.Model):

    '''
        Slug create from title ??????????
    '''

    author = models.ForeignKey(User, related_name='author')
    title = models.CharField(max_length=128)
    description = models.TextField()
    start_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    expect_date = models.DateField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.ForeignKey(Status, default=1, related_name='status')
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
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    tasks = models.ForeignKey(Task)

    def __unicode__(self):
        return '%s...' % (self.text[:20])

    class Meta:
        ordering = ['create_date']


def content_file_name(instance, filename):
    return '/'.join(['files', instance.tasks.slug, filename])


class File(models.Model):
    file = models.FileField(upload_to=content_file_name)
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    author = models.ForeignKey(User)
    tasks = models.ForeignKey(Task)

    def __unicode__(self):
        return self.file

    class Meta:
        ordering = ['create_date']


# SIGNALS for create Unique Slug
def create_slug(instance, new_slug=None):
    if instance.title not in ['create', 'file_create']:
        slug = slugify(instance.title)
    else:
        slug = slugify('task')
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
