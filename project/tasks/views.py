from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Task


class MainView(ListView):
    template_name = 'tasks/list.html'

    def get_queryset(self):
        if self.request.user.groups.filter(name='experts').exists():
            queryset = Task.objects.filter(expert=self.request.user)
        elif self.request.user.groups.filter(name='super_experts').exists():
            queryset = Task.objects.all()
        elif self.request.user.groups.filter(name='customers').exists():
            queryset = Task.objects.filter(author=self.request.user)

        print self.request.user.is_authenticated()
        return queryset
