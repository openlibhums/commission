
from django.contrib import messages

from utils import setting_handler, render_template
from plugins.commission import plugin_settings
from core import models


def render_commission_email(request, commissioned_article):
    setting = setting_handler.get_plugin_setting(
        plugin_settings.CommissionPlugin.get_self(),
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
