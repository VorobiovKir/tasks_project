import csv

from django.contrib import admin
from django.utils.encoding import smart_str
from django.http import HttpResponse

from .models import Comment, Status, Task


def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=mymodel.csv'
    writer = csv.writer(response, csv.excel)
    # BOM (optional...Excel needs it to open UTF-8 file properly)
    response.write(u'\ufeff'.encode('utf8'))
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"Title"),
        smart_str(u"Description"),
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.title),
            smart_str(obj.description),
        ])
    return response
export_csv.short_description = u"Export CSV"


class TaskModelAdmin(admin.ModelAdmin):
    actions = [export_csv]


admin.site.register(Comment)
admin.site.register(Status)
admin.site.register(Task, TaskModelAdmin)
