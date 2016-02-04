from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
# from crispy_forms.bootstrap import Field

from .models import Task, Comment


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description']


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
