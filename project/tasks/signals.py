from django.db.models.signals import pre_save
from django.utils.text import slugify
from .models import Task


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
