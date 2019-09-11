from utils import setting_handler, render_template
from plugins.commission import plugin_settings


def render_commission_email(request, commissioned_article):
    setting = setting_handler.get_plugin_setting(
        plugin_settings.get_self(),
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
