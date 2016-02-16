from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


class SendEmailClass(object):

    def __init__(self, subject, sender, to, template, data=None):
        self.subject = subject
        self.sender = sender
        self.to = to
        self.template = template
        self.data = data
        self.mimetype = 'text/html'

    def get_rendered_template(self):
        if self.data is not None:
            return get_template(self.template).render(self.data)
        else:
            return self.template

    def send(self):
        msg = EmailMultiAlternatives(
            self.subject,
            self.get_rendered_template(),
            self.sender,
            self.to
        )
        msg.attach_alternative(self.get_rendered_template(), self.mimetype)
        msg.send()
