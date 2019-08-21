from utils import models

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

    if created:
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        print('Plugin {0} is already installed.'.format(PLUGIN_NAME))


def hook_registry():
    return {
        'journal_admin_nav_block': {'module': 'plugins.commission.hooks',
                                    'function': 'admin_hook'},
    }
