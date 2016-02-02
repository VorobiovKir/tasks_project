from django.views.generic import ListView, FormView, DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator

from .models import Task
from .forms import TaskForm


class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'tasks/list.html'
    login_url = reverse_lazy('auth:login')

    # @method_decorator(login_required(login_url='/auth/login/'))
    # def dispatch(self, request, *args, **kwargs):
    #     return super(MainView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        if self.request.user.groups.filter(name='experts').exists():
            return Task.objects.filter(expert=self.request.user)
        elif self.request.user.groups.filter(name='super_experts').exists():
            return Task.objects.all()
        elif self.request.user.groups.filter(name='customers').exists():
            return Task.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        return context


class TaskCreateView(LoginRequiredMixin, FormView):
    form_class = TaskForm
    template_name = 'tasks/form_task.html'
    success_url = reverse_lazy('tasks:list')
    login_url = reverse_lazy('auth:login')

    def form_valid(self, form, *args, **kwargs):
        new_task = form.save(commit=False)
        new_task.author = self.request.user
        new_task.expert_id = 1
        new_task.save()
        return super(TaskCreateView, self).form_valid(form)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/detail.html'
    login_url = reverse_lazy('auth:login')
