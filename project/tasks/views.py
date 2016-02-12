import csv
import datetime
import logging

from django.views.generic import ListView, FormView, TemplateView, UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.utils.encoding import smart_str

from .models import Task
from .forms import TaskForm, CommentForm, FileForm, ExpectDateForm, CSVForm
from .make_statistic import log_super_action


logger = logging.getLogger(__name__)


class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'tasks/list.html'
    login_url = reverse_lazy('auth:login')

    def get_queryset(self, *args, **kwargs):
        if self.request.user.groups.filter(pk=2).exists():
            return Task.objects.filter(expert=self.request.user)
        elif self.request.user.groups.filter(pk=3).exists():
            return Task.objects.all()
        elif self.request.user.groups.filter(pk=1).exists():
            return Task.objects.filter(author=self.request.user)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)

        if self.request.user.groups.filter(name='super').exists():
            if context['object_list']:
                context['can_get_csv'] = True
                context['form_csv'] = CSVForm(self.request.POST or None)

        context['task'] = {
            'pending': [],
            'in_proccess': [],
            'closed': [],
            'other': [],
        }

        for obj in context['object_list']:
            if obj.status.name == 'pending':
                context['task']['pending'].append(obj)
            elif obj.status.name == 'in process':
                context['task']['in_proccess'].append(obj)
            elif obj.status.name == 'closed':
                context['task']['closed'].append(obj)
            else:
                context['task']['other'].append(obj)

        return context


class TaskCreateView(PermissionRequiredMixin, FormView):
    form_class = TaskForm
    template_name = 'tasks/form_task.html'
    success_url = reverse_lazy('tasks:list')

    permission_required = 'tasks.add_task'
    raise_exception = True
    login_url = reverse_lazy('auth:login')

    def form_valid(self, form, *args, **kwargs):
        new_task = form.save(commit=False)
        new_task.author = self.request.user
        new_task.expert_id = 3
        new_task.save()
        # send_mail(
        #     'Subject here',
        #     'Here is the message.',
        #     settings.EMAIL_HOST_USER,
        #     ['kvorobiov89@gmail.com'],
        #     fail_silently=False
        # )

        log_super_action(
            1,
            new_task.author.profile.slug,
            new_task.slug,
            ''
        )
        logger.error(_("User expires date less than now"))
        messages.success(self.request, _('Task successfully created!'))

        return super(TaskCreateView, self).form_valid(form)


class TaskDetailView(LoginRequiredMixin, TemplateView):

    template_name = 'tasks/detail.html'
    paginate_by = 5

    login_url = reverse_lazy('auth:login')

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        obj = get_object_or_404(Task, slug=slug)
        if self.request.user not in [obj.expert, obj.author]:
            if not request.user.groups.filter(name='super').exists():
                raise Http404

        return super(TaskDetailView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        slug = kwargs.pop('slug')
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['object'] = get_object_or_404(Task, slug=slug)

        if context['object'].status.id == 1 and \
                context['object'].expert == self.request.user:
            if not context['object'].expect_date:
                context['must_setup_expect_date'] = True

        if context['object'].status.id in [3, 6] and \
                context['object'].expert == self.request.user:
            context['must_resolved'] = True

        if context['object'].status.id == 4 and \
                context['object'].author == self.request.user:
            context['must_accept_task'] = True

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
            new_comment.tasks = get_object_or_404(Task, slug=slug)
            new_comment.save()

            log_super_action(
                2,
                new_comment.author.profile.slug,
                new_comment.tasks.slug,
                2
            )

            messages.success(self.request, _('Comment successfully added!'))
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
        # !!!
        slug = self.refer.split('/')[-2]
        new_file.tasks = get_object_or_404(Task, slug=slug)
        new_file.save()

        log_super_action(
            2,
            new_file.author.profile.slug,
            new_file.tasks.slug,
            4
        )
        messages.success(self.request, _('File successfully added!'))
        return redirect(self.refer)

    def form_invalid(self, form, *args, **kwargs):
        return redirect(self.refer)


class ExpectDateUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = ExpectDateForm
    login_url = reverse_lazy('auth:login')

    def dispatch(self, *args, **kwargs):
        self.refer = self.request.META.get('HTTP_REFERER', '/')
        if self.refer == '/':
            raise Http404
        if not self.request.user.groups.filter(name='experts').exists():
            raise Http404
        return super(ExpectDateUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        expect_date = form.save(commit=False)
        expect_date.status_id = 3
        expect_date.save()
        messages.success(self.request, _('Expect date successfully added!'))
        return redirect(self.refer)

    def form_invalid(self, form, *args, **kwargs):
        return redirect(self.refer)


class ResolveTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', ]
    login_url = reverse_lazy('auth:login')

    def dispatch(self, *args, **kwargs):
        self.refer = self.request.META.get('HTTP_REFERER', '/')
        if self.refer == '/':
            raise Http404
        if not self.request.user.groups.filter(name='experts').exists():
            raise Http404
        return super(ResolveTaskUpdateView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.request.POST.get('resolved_task'):
            object = self.get_object()
            if object.status_id in [3, 6]:
                object.status_id = 4
                object.save()
                messages.success(
                    self.request, _('Status successfully changed!'))
        return redirect(self.refer)


class AcceptTaskPerformanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', ]
    login_url = reverse_lazy('auth:login')

    def dispatch(self, *args, **kwargs):
        self.refer = self.request.META.get('HTTP_REFERER', '/')
        if self.refer == '/':
            raise Http404
        if not self.request.user.groups.filter(name='customers').exists():
            raise Http404
        return super(AcceptTaskPerformanceUpdateView, self).dispatch(
            *args, **kwargs)

    def post(self, *args, **kwargs):
        object = self.get_object()
        if object.status_id == 4:
            if self.request.POST.get('accept_task'):
                object.status_id = 5
                object.end_date = datetime.datetime.now()
                object.save()

                log_super_action(
                    3,
                    object.author.profile.slug,
                    object.slug,
                    ''
                )
            if self.request.POST.get('reopen_task'):
                object.status_id = 6
                object.save()
            messages.success(self.request, _('Status successfully changed!'))

        return redirect(self.refer)


class GetCsvView(LoginRequiredMixin, FormView):
    form_class = CSVForm
    login_url = reverse_lazy('auth:login')

    def dispatch(self, *args, **kwargs):
        self.refer = self.request.META.get('HTTP_REFERER', '/')
        if self.refer == '/':
            raise Http404
        if not self.request.user.groups.filter(name='super').exists():
            raise Http404
        return super(GetCsvView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        queryset = Task.objects.filter(start_date__range=(
            datetime.datetime.combine(date_from, datetime.time.min),
            datetime.datetime.combine(date_to, datetime.time.max)
        ))

        if not queryset:
            messages.warning(self.request,
                             _('''In this period we haven't any tasks '''))
            return redirect(self.refer)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename=%s_%s:%s.csv' % ('tasks', date_from, date_to)

        writer = csv.writer(response, csv.excel)
        # BOM (optional...Excel needs it to open UTF-8 file properly)
        response.write(u'\ufeff'.encode('utf8'))
        writer.writerow([
            smart_str(u"ID"),
            smart_str(u"Author"),
            smart_str(u"Expert"),
            smart_str(u"Title"),
            smart_str(u"Description"),
            smart_str(u"Start_date"),
            smart_str(u"Expect_date"),
            smart_str(u"End_date"),
            smart_str(u"Status"),
        ])
        for obj in queryset:
            writer.writerow([
                smart_str(obj.pk),
                smart_str(obj.author),
                smart_str(obj.expert),
                smart_str(obj.title),
                smart_str(obj.description),
                smart_str(obj.start_date),
                smart_str(obj.expect_date),
                smart_str(obj.end_date),
                smart_str(obj.status),
            ])

        return response

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request,
                       _('''Please, check dates'''))
        return redirect(self.refer)
