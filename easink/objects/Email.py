from djangoProject.utils import email_utils


class Email:
    def __init__(self, email_address, subject, content, replyTo=None):
        self.email_address = email_address
        self.subject = subject
        self.content = content
        self.replyTo = replyTo

    def send(self):
        email_utils.sendMail(self.email_address, self.subject, self.content)