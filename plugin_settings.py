from utils import models, setting_handler
from journal import models as journal_models

PLUGIN_NAME = 'Commission Articles'
DESCRIPTION = 'Allows editors to commission articles.'
AUTHOR = 'Andy Byers'
VERSION = '0.1'
SHORT_NAME = 'commission'
DISPLAY_NAME = 'commission'
MANAGER_URL = 'commission_index'
JANEWAY_VERSION = "1.3.6"


def get_self():
    plugin, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        display_name=DISPLAY_NAME,
        enabled=True,
        defaults={'version': VERSION}
    )
    return plugin


def install():
    new_plugin, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        display_name=DISPLAY_NAME,
        enabled=True,
        press_wide=True,
        defaults={'version': VERSION}
    )

    setting, c = models.PluginSetting.objects.get_or_create(
        name='commission_article',
        plugin=new_plugin,
        types='rich-text',
        pretty_name='Commission Article Email',
        description='Email text for sending an article commission.',
        is_translatable=True)

    email_setting = '''<p>Dear {{ article.owner.full_name }},</p>

<p>We are requesting that you complete the submission of the article "{{ article.title|safe }}".</p>

<p><a href="{% journal_url 'submit_info' article.pk %}">{% journal_url 'submit_info' article.pk %}</a></p>

<p>Regards,</p>

{{ request.user.signature|safe }}
    '''

    for journal in journal_models.Journal.objects.all():

        setting_handler.save_plugin_setting(
            new_plugin,
            'commission_article',
            email_setting,
            journal,
        )

    if created:
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        print('Plugin {0} is already installed.'.format(PLUGIN_NAME))


def hook_registry():
    return {
        'journal_admin_nav_block': {'module': 'plugins.commission.hooks',
                                    'function': 'admin_hook'},
    }
