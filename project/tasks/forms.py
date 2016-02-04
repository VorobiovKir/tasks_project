from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import filesizeformat

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
# from crispy_forms.bootstrap import Field

from .models import Task, Comment, File


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description']


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file', ]

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            if len(file.name.split('.')) == 1:
                raise forms.ValidationError(_('File type is not supported'))

            if file.content_type in settings.TASK_UPLOAD_FILE_TYPES:
                print 'content - ', file.content_type
                if file._size > settings.TASK_UPLOAD_FILE_MAX_SIZE:
                    print 'size - ', file._size
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.TASK_UPLOAD_FILE_MAX_SIZE), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('File type is not supported'))

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

    # def clean(self):
    #     cleaned_data = super(CommentForm, self).clean()
    #     text = cleaned_data.get('text', '')
    #     if text == '':
    #         self._errors["text"] = self.error_class(['Pls fill the form'])
    #         print 'error'
