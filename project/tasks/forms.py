import datetime

from django import forms
from django.conf import settings
from django.core.validators import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout, ButtonHolder, Submit
from crispy_forms.helper import FormHelper

from .models import Task, Comment, File


class CSVForm(forms.Form):
    date_from = forms.DateField()
    date_to = forms.DateField()

    def __init__(self, *args, **kwargs):
        super(CSVForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_tag = False
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'date_from',
            'date_to',
            StrictButton('Get CSV', type='submit', css_class='btn-default'),
        )

    def clean(self):
        cleaned_data = super(CSVForm, self).clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        if date_from > date_to:
            raise ValidationError(_('Date to must be in future'),
                                  code=_('invalid'))


class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            'title',
            'description',
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button')
            )
        )

    class Meta:
        model = Task
        fields = ['title', 'description']


class ExpectDateForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['expect_date', ]

    def clean_expect_date(self):
        expect_date = self.cleaned_data.get('expect_date')

        if expect_date:
            if expect_date < datetime.date.today():
                raise forms.ValidationError(_('Expect Date must be in future'),
                                            code=_('invalid'))
        else:
            raise forms.ValidationError(_('Expect Date empty'),
                                        code=_('invalid'))
        return expect_date


class FileForm(forms.ModelForm):

    class Meta:
        model = File
        fields = ['file', ]

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            if len(file.name.split('.')) == 1:
                raise forms.ValidationError(_('File type is not supported'),
                                            code=_('invalid'))

            if file.content_type in settings.TASK_UPLOAD_FILE_TYPES:
                if file._size > settings.TASK_UPLOAD_FILE_MAX_SIZE:
                    raise forms.ValidationError(
                        _('Please keep filesize under %s. Current filesize %s')
                        % (filesizeformat(
                            settings.TASK_UPLOAD_FILE_MAX_SIZE),
                            filesizeformat(file._size)), code=_('invalid'))
            else:
                raise forms.ValidationError(_('File type is not supported'),
                                            code=_('invalid'))

        return file


class CommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_errors = True
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'text'
        )

    class Meta:
        model = Comment
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4, 'placeholder': _('Type the comment...')}),
        }
