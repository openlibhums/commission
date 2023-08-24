from utils import setting_handler, render_template
from core import models
from plugins.commission import models as commission_models

from django.contrib import messages
from django.shortcuts import reverse


def remove_author_from_article(request, article, author_id):
    try:
        author = models.Account.objects.get(pk=author_id)
    except models.Account.DoesNotExist:
        messages.add_message(
            request,
            messages.WARNING,
            'Author with this ID was not found.'
        )
        return

    if author not in article.authors.all():
        messages.add_message(
            request,
            messages.WARNING,
            'This author is not in the list of authors for this article.'
        )
    else:
        article.authors.remove(author)
        messages.add_message(
            request,
            messages.SUCCESS,
            'Author removed from article.'
        )


def render_commission_email(request, commissioned_article):
    setting = setting_handler.get_setting(
        'plugin:commission',
        'commission_article',
        request.journal,
    )

    context = {
        'article': commissioned_article.article,
        'commissioned_article': commissioned_article,
    }

    template_html = render_template.get_message_content(
        request,
        context,
        setting.value,
        template_is_setting=True,
    )

    return template_html


def get_rendered_templates(request, comm_article):

    rendered_templates = []
    if comm_article.article:

        decision_url = reverse(
            'commissioned_author_decision',
            kwargs={'commissioned_article_id': comm_article.pk}
        )
        context = {
            'url': request.journal.site_url(path=decision_url),
            'commissioned_article': comm_article,
        }
        if comm_article.article:
            section_templates = commission_models.CommissionTemplate.objects.filter(
                section=comm_article.article.section,
                sent_on_acceptance=False,
            )
            for template in section_templates:
                rendered_templates.append(
                    {
                        'template_identifier': template.pk,
                        'template_name': template.name,
                        'content': render_template.get_message_content(
                            request,
                            context,
                            template.template,
                            template_is_setting=True,
                        ),
                    }
                )

        default_template = setting_handler.get_setting(
            'plugin:commission',
            'commission_article',
            request.journal,
        )
        rendered_templates.append(
            {
                'template_identifier': "default",
                'template_name': "Janeway Default Template",
                'content': render_template.get_message_content(
                    request,
                    context,
                    default_template.processed_value,
                    template_is_setting=True,
                ),
            }
        )
    return rendered_templates


def get_settings(journal):
    settings = [
        {
            'name': 'commission_article',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_article',
                journal),
        },
        {
            'name': 'commission_reminder_before',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_reminder_before',
                journal),
        },
        {
            'name': 'commission_reminder_after',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_reminder_after',
                journal),
        },
        {
            'name': 'commission_expiry_days',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_expiry_days',
                journal),
        },
        {
            'name': 'commission_reminder_after_email',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_reminder_after_email',
                journal),
        },
        {
            'name': 'commission_reminder_before_email',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_reminder_before_email',
                journal),
        },
        {
            'name': 'commission_author_decision_made',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_author_decision_made',
                journal),
        },
        {
            'name': 'commission_author_decision_text',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_author_decision_text',
                journal),
        },
        {
            'name': 'commission_submission_deadline_days',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_submission_deadline_days',
                journal),
        },
        {
            'name': 'commission_reminder_after_article_sub_email',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_reminder_after_article_sub_email',
                journal),
        },
        {
            'name': 'commission_reminder_before_article_sub_email',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_reminder_before_article_sub_email',
                journal),
        },
        {
            'name': 'submission_reminder_after',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'submission_reminder_after',
                journal),
        },
        {
            'name': 'submission_reminder_before',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'submission_reminder_before',
                journal),
        },
        {
            'name': 'commission_withdrawn_email',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_withdrawn_email',
                journal),
        },
        {
            'name': 'commission_cc_address',
            'object': setting_handler.get_setting(
                'plugin:commission',
                'commission_cc_address',
                journal),
        }
    ]
    return settings
