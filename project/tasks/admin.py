from django.contrib import admin

from .models import Comment, Status, Task


admin.site.register(Comment)
admin.site.register(Status)
admin.site.register(Task)
