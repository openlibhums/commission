from datetime import timedelta

from django.db import models
from django.utils import timezone

from utils import setting_handler, notify_helpers, render_template


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
        help_text='The deadline by which the author must accept '
                  'or decline the commission request.',
        verbose_name="Request deadline",
    )
    submission_deadline = models.DateField(
        null=True,
        help_text='The deadline by which the author must submit the article.'
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
    submission_reminder_before_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The date and time the before submission deadline reminder '
                  'is sent.',
    )
    submission_reminder_after_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The date and time the after submission deadline reminder '
                  'is sent.',
    )

    def status(self):
        if self.author_decision_editor_check:
            return 'Archived'
        elif not self.message_sent:
            return 'Notification not sent'
        elif self.author_decision == 'accepted':
            return 'Author accepted request'
        elif self.author_decision == 'declined':
            return 'Author declined request'
        elif self.check_expiry():
            return 'Expired'
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

    def submission_reminder_before_date(self):
        reminder_before_days = setting_handler.get_setting(
            'plugin:commission',
            'submission_reminder_before',
            self.article.journal,
        ).processed_value

        dt = self.deadline - timedelta(days=reminder_before_days)

        if dt < timezone.now().date():
            return 'This date has now passed.'
        return dt

    def submission_reminder_after_date(self):
        reminder_after_days = setting_handler.get_setting(
            'plugin:commission',
            'submission_reminder_after',
            self.article.journal,
        ).processed_value

        dt = self.deadline + timedelta(days=reminder_after_days)
        if dt < timezone.now().date():
            return 'This date has now passed.'
        return dt

    def check_expiry(self):
        if self.article and self.deadline:
            expiry_days = setting_handler.get_setting(
                'plugin:commission',
                'commission_expiry_days',
                self.article.journal,
            ).processed_value
            if (self.deadline + timedelta(days=expiry_days)) < timezone.now().date():
                return True
        return False

    def calculate_submission_deadline(self):
        deadline_days = setting_handler.get_setting(
            'plugin:commission',
            'commission_submission_deadline_days',
            self.article.journal,
        ).processed_value
        return timezone.now().date() + timedelta(days=deadline_days)

    def set_deadline(self):
        self.submission_deadline = self.calculate_submission_deadline()
        self.save()

    def send_author_notification_email(self, request):
        template = CommissionTemplate.objects.filter(
            section=self.article.section,
            sent_on_acceptance=True,
        ).first()
        if template:
            email_context = {
                'commissioned_article': self,
            }
            log_dict = {
                'level': 'Info',
                'action_text': 'Commission Acceptance Notification',
                'types': 'Commission',
                'actor': request.user,
                'target': self.article,
            }
            body = render_template.get_message_content(
                request,
                email_context,
                template.template,
                template_is_setting=True,
            )
            notify_helpers.send_email_with_body_from_user(
                request=request,
                subject=template.subject,
                to=self.commissioned_author.email,
                body=body,
                log_dict=log_dict,
            )


class CommissionTemplate(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="The name of your template"
    )
    section = models.ForeignKey(
        'submission.Section',
        on_delete=models.CASCADE,
        help_text="The section your template is to be used for"
    )
    template = models.TextField()
    subject = models.CharField(max_length=255)
    sent_on_acceptance = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.name
