from utils import plugins
from utils.install import update_settings

PLUGIN_NAME = 'Commission Articles'
DESCRIPTION = 'Allows editors to commission articles.'
AUTHOR = 'Andy Byers'
VERSION = '0.1'
SHORT_NAME = 'commission'
DISPLAY_NAME = 'commission'
MANAGER_URL = 'commission_index'
JANEWAY_VERSION = "1.3.10"


class CommissionPlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = PLUGIN_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME

    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = "1.4.0"

    is_workflow_plugin = False


def install():
    CommissionPlugin.install()
    update_settings(
        file_path='plugins/commission/install/settings.json',
    )


def hook_registry():
    return {
        'journal_admin_nav_block': {'module': 'plugins.commission.hooks',
                                    'function': 'admin_hook'},
    }
