from datetime import timedelta

from django.db import models
from django.utils import timezone

from utils import setting_handler


def author_decision_choices():
    return (
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )


class CommissionedArticle(models.Model):
    article = models.ForeignKey(
        'submission.Article',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    journal = models.ForeignKey(
        'journal.Journal',
        null=True,
        on_delete=models.SET_NULL,
    )
    commissioning_editor = models.ForeignKey(
        'core.Account',
        null=True,
        on_delete=models.SET_NULL,
    )
    commissioned_author = models.ForeignKey(
        'core.Account',
        null=True,
        related_name='commissioned_author',
        on_delete=models.SET_NULL,
    )
    commissioned = models.DateTimeField(default=timezone.now)
    message_sent = models.DateTimeField(null=True, blank=True)
    additional_information = models.TextField(
        blank=True,
        null=True,
        help_text='Add any information you want to provide to the author '
                  'on the accept/decline page.'
    )
    author_decision = models.CharField(
        null=True,
        blank=True,
        max_length=20,
        choices=author_decision_choices(),
    )
    author_decision_date = models.DateTimeField(null=True, blank=True)
    author_decision_editor_check = models.BooleanField(
        default=False,
    )
    deadline = models.DateField(
        blank=True,
        null=True,
    )
    reminder_before_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The date and time the before deadline reminder is sent.',
    )
    reminder_after_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The date and time the after deadline reminder is sent.',
    )

    def status(self):
        if self.author_decision_editor_check:
            return 'Archived'
        if self.check_expiry():
            return 'Expired'
        elif self.author_decision == 'accept':
            return 'Author accepted request'
        elif self.author_decision == 'declined':
            return 'Author declined request'
        elif self.message_sent and not self.author_decision:
            return 'Request sent'
        else:
            return 'Awaiting response from author'

    def reminder_before_date(self):
        reminder_before_days = setting_handler.get_setting(
            'plugin:commission',
            'commission_reminder_before',
            self.article.journal,
        ).processed_value

        dt = self.deadline - timedelta(days=reminder_before_days)

        if dt < timezone.now().date():
            return 'This date has now passed.'
        return dt

    def reminder_after_date(self):
        reminder_after_days = setting_handler.get_setting(
            'plugin:commission',
            'commission_reminder_after',
            self.article.journal,
        ).processed_value

        dt = self.deadline + timedelta(days=reminder_after_days)
        if dt < timezone.now().date():
            return 'This date has now passed.'
        return dt

    def check_expiry(self):
        expiry_days = setting_handler.get_setting(
            'plugin:commission',
            'commission_expiry_days',
            self.article.journal,
        ).processed_value
        if (self.deadline + timedelta(days=expiry_days)) < timezone.now().date():
            return True
        return False


class CommissionTemplate(models.Model):
    name = models.CharField(
        max_length=255,
    )
    section = models.ForeignKey(
        'submission.Section',
        on_delete=models.CASCADE,
    )
    template = models.TextField()
    subject = models.CharField(max_length=255)

    def __str__(self):
        return self.name
