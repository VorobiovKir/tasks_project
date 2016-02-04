from django.views.generic import ListView, FormView, TemplateView, UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator

from .models import Task
from .forms import TaskForm, CommentForm, FileForm, ExpectDateForm


class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'tasks/list.html'
    login_url = reverse_lazy('auth:login')

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


class TaskDetailView(TemplateView):

    template_name = 'tasks/detail.html'
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        obj = get_object_or_404(Task, slug=slug)
        if self.request.user not in [obj.expert, obj.author]:
            raise Http404
        else:
            return super(TaskDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        slug = kwargs.pop('slug')
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['object'] = get_object_or_404(Task, slug=slug)

        # if expect date == null !!!!!!!!!!!!!!!!!!!!!!
        if context['object'].status.name == 'pending' and \
                context['object'].expert == self.request.user:
            context['must_setup_expect_date'] = True

        # if context['object'].status == 'pending' and self.request.user.has_perm('experts'):
        #     print 'you are expert and you must set UP expect date'

        context['form_comment'] = CommentForm(self.request.POST or None)
        context['form_file'] = FileForm()
        context['form_expect_date'] = ExpectDateForm()

        comments = context['object'].comment_set.all()
        paginator = Paginator(comments, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            context['comments'] = paginator.page(page)
        except PageNotAnInteger:
            context['comments'] = paginator.page(1)
        except EmptyPage:
            context['comments'] = paginator.page(paginator.num_pages)

        return context

    def post(self, request, slug, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            new_comment.tasks = get_object_or_404(Task, slug=slug)
            new_comment.save()
        else:
            return self.render_to_response(self.get_context_data(slug=slug))
        return redirect(reverse('tasks:detail', kwargs={'slug': slug}))


class FileCreateView(LoginRequiredMixin, FormView):
    form_class = FileForm
    login_url = reverse_lazy('auth:login')

    def dispatch(self, *args, **kwargs):
        self.refer = self.request.META.get('HTTP_REFERER', '/')
        if self.refer == '/':
            raise Http404
        return super(FileCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        new_file = form.save(commit=False)
        new_file.author = self.request.user
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        slug = self.refer.split('/')[-2]
        new_file.tasks = get_object_or_404(Task, slug=slug)
        new_file.save()
        return redirect(self.refer)

    def form_invalid(self, form, *args, **kwargs):
        return redirect(self.refer)


class ExpectDateUpdateView(UpdateView):
    model = Task
    form_class = ExpectDateForm

    def dispatch(self, *args, **kwargs):
        self.refer = self.request.META.get('HTTP_REFERER', '/')
        if self.refer == '/':
            raise Http404
        return super(ExpectDateUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        expect_date = form.save(commit=False)
        expect_date.status_id = 3
        expect_date.save()
        return redirect(self.refer)

    def form_invalid(self, form, *args, **kwargs):
        print 'invalid'
        return redirect(self.refer)
