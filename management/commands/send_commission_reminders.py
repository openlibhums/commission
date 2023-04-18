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

    return models.CommissionedArticle.objects.filter(
        article__journal=journal,
        article__date_submitted__isnull=True,
        message_sent__isnull=False,
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

    return models.CommissionedArticle.objects.filter(
        article__journal=journal,
        article__date_submitted__isnull=True,
        message_sent__isnull=False,
        author_decision_editor_check=False,
        deadline=date,
        reminder_after_sent__isnull=True,
    )


class Command(BaseCommand):

    def handle(self, *args, **options):
        journals = journal_models.Journal.objects.filter(code='olh')

        for journal in journals:
            print(f"Processing {journal.name}")
            before = get_before_due_date_commissions(journal)
            after = get_after_due_date_commissions(journal)

            print(f"{before.count()} reminders for upcoming due dates and "
                  f"{after.count()} reminders for overdue commissions.")

            request = Request()
            request.journal = journal
            request.site_type = journal

            for ca in before:
                path = reverse(
                    'commissioned_author_decision',
                    kwargs={
                        'commissioned_article_id': ca.pk,
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
                rendered_template = render_template.get_requestless_content(
                    context=context,
                    journal=journal,
                    template='commission_reminder_before_email',
                    group_name='plugin:commission',
                )
                notify_helpers.send_email_with_body_from_user(
                    request,
                    'Commissioned Article Reminder',
                    ca.commissioned_author.email,
                    rendered_template,
                )
                ca.reminder_before_sent = timezone.now()
                ca.save()
                print(f"Message sent to {ca.commissioned_author.full_name()}")

            for ca in after:
                path = reverse(
                    'commissioned_author_decision',
                    kwargs={
                        'commissioned_article_id': ca.pk,
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
                rendered_template = render_template.get_requestless_content(
                    context=context,
                    journal=journal,
                    template='commission_reminder_after_email',
                    group_name='plugin:commission',
                )
                notify_helpers.send_email_with_body_from_user(
                    request,
                    'Commissioned Article Reminder',
                    ca.commissioned_author.email,
                    rendered_template,
                )
                ca.reminder_after_sent = timezone.now()
                ca.save()
                print(f"Message sent to {ca.commissioned_author.full_name()}")


