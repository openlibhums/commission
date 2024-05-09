from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.shortcuts import reverse

from plugins.commission import models
from utils import setting_handler, render_template, notify_helpers
from journal import models as journal_models
from cron.models import Request


def get_before_due_date_commissions(journal):
    reminder_before_days = setting_handler.get_setting(
        'plugin:commission',
        'commission_reminder_before',
        journal,
    ).processed_value

    date = timezone.now().date() + timedelta(days=reminder_before_days)
    print(f'Target date for before commission due: {date}')

    return models.CommissionedArticle.objects.filter(
        article__journal=journal,
        article__date_submitted__isnull=True,
        message_sent__isnull=False,
        author_decision__isnull=True,
        author_decision_editor_check=False,
        deadline=date,
        reminder_before_sent__isnull=True
    )


def get_after_due_date_commissions(journal):
    reminder_after_days = setting_handler.get_setting(
        'plugin:commission',
        'commission_reminder_after',
        journal,
    ).processed_value

    date = timezone.now().date() - timedelta(days=reminder_after_days)
    print(f'Target date for after commission due: {date}')

    return models.CommissionedArticle.objects.filter(
        article__journal=journal,
        article__date_submitted__isnull=True,
        message_sent__isnull=False,
        author_decision__isnull=True,
        author_decision_editor_check=False,
        deadline=date,
        reminder_after_sent__isnull=True,
    )


def get_before_due_date_submissions(journal):
    reminder_before_days = setting_handler.get_setting(
        'plugin:commission',
        'submission_reminder_before',
        journal,
    ).processed_value

    date = timezone.now().date() + timedelta(days=reminder_before_days)
    print(f'Target date for before submission due: {date}')

    return models.CommissionedArticle.objects.filter(
        article__journal=journal,
        article__date_submitted__isnull=True,
        message_sent__isnull=False,
        author_decision__isnull=False,
        author_decision_editor_check=False,
        submission_deadline=date,
        submission_reminder_before_sent__isnull=True,
    )


def get_after_due_date_submissions(journal):
    reminder_after_days = setting_handler.get_setting(
        'plugin:commission',
        'submission_reminder_after',
        journal,
    ).processed_value

    date = timezone.now().date() - timedelta(days=reminder_after_days)
    print(f'Target date for after submission due: {date}')

    return models.CommissionedArticle.objects.filter(
        article__journal=journal,
        article__date_submitted__isnull=True,
        message_sent__isnull=False,
        author_decision__isnull=False,
        author_decision_editor_check=False,
        submission_deadline=date,
        submission_reminder_after_sent__isnull=True,
    )


def send_before_messages(request, ca, journal, before_or_after):
    if before_or_after == 'before':
        template_name = 'commission_reminder_before_email'
    elif before_or_after == 'after':
        template_name = 'commission_reminder_after_email'
    elif before_or_after == 's_before':
        template_name = 'commission_reminder_before_article_sub_email'
    else:
        template_name = 'commission_reminder_after_article_sub_email'

    if before_or_after in ['before', 'after']:
        path = reverse(
            'commissioned_author_decision',
            kwargs={
                'commissioned_article_id': ca.pk,
            }
        )
    else:
        path = reverse(
            'submit_info',
            kwargs={
                'article_id': ca.article.pk,
            }
        )
    url = journal.site_url(
        path=path,
    )
    context = {
        'commissioned_article': ca,
        'url': url,
        'journal': journal,
    }
    html = render_template.get_requestless_content(
        context=context,
        journal=journal,
        template=template_name,
        group_name='plugin:commission',
    )
    bcc = request.journal.get_setting(
        'plugin:commission',
        'commission_cc_address',
    )
    notify_helpers.send_email_with_body_from_user(
        request,
        'Commissioned Article Reminder',
        ca.commissioned_author.email,
        html,
        bcc=[bcc] if bcc else None,
    )

    if before_or_after == 'before':
        ca.reminder_before_sent = timezone.now()
    elif before_or_after == 'after':
        ca.reminder_after_sent = timezone.now()
    elif before_or_after == 's_after':
        ca.submission_reminder_after_sent = timezone.now()
    elif before_or_after == 's_before':
        ca.submission_reminder_before_sent = timezone.now()

    ca.save()
    print(f"Message {before_or_after} sent to {ca.commissioned_author.full_name()}")


class Command(BaseCommand):

    def handle(self, *args, **options):
        journals = journal_models.Journal.objects.filter(code='olh')

        for journal in journals:
            print(f"Processing {journal.name}")
            before = get_before_due_date_commissions(journal)
            after = get_after_due_date_commissions(journal)
            s_before = get_before_due_date_submissions(journal)
            s_after = get_after_due_date_submissions(journal)

            print(f"{before.count()} reminders for upcoming commission due dates and "
                  f"{after.count()} reminders for overdue commissions.")
            print(f"{s_before.count()} reminders for upcoming submission due dates and "
                  f"{s_after.count()} reminders for overdue submissions.")

            request = Request()
            request.journal = journal
            request.site_type = journal

            for ca in before:
                send_before_messages(request, ca, journal, 'before')

            for ca in after:
                send_before_messages(request, ca, journal, 'after')

            for ca in s_before:
                send_before_messages(request, ca, journal, 's_before')

            for ca in s_after:
                send_before_messages(request, ca, journal, 's_after')



