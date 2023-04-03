from utils import plugins
from utils.install import update_settings

PLUGIN_NAME = 'Commission Articles'
DESCRIPTION = 'Allows editors to commission articles.'
AUTHOR = 'Open Library of Humanities'
VERSION = '0.1'
SHORT_NAME = 'commission'
DISPLAY_NAME = 'Commission'
MANAGER_URL = 'commission_index'
JANEWAY_VERSION = "1.5.0"
IS_WORKFLOW_PLUGIN = False


class CommissionPlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME

    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = JANEWAY_VERSION

    is_workflow_plugin = IS_WORKFLOW_PLUGIN


def install():
    CommissionPlugin.install()
    update_settings(
        file_path='plugins/commission/install/settings.json'
    )


def hook_registry():
    return {
        'journal_admin_nav_block': {'module': 'plugins.commission.hooks',
                                    'function': 'admin_hook'},
    }
