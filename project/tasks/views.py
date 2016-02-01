from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy

from .models import Task


class MainView(ListView):
    model = Task
    template_name = 'tasks/list.html'

    def get_queryset(self):
        if self.request.user.groups.filter(name='experts').exists():
            queryset = Task.objects.filter(expert=self.request.user)
        elif self.request.user.groups.filter(name='super_expert').exists():
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(autor=self.request.user)
        return queryset
