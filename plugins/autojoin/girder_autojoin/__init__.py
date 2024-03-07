from pathlib import Path

from girder import events
from girder.models.group import Group
from girder.models.setting import Setting
from girder.plugin import GirderPlugin, registerPluginStaticContent

from .settings import PluginSettings


def userCreated(event):
    """
    Check auto join rules when a new user is created. If a match is found,
    add the user to the group with the specified access level.
    """
    user = event.info
    email = user.get('email').lower()
    rules = Setting().get(PluginSettings.AUTOJOIN)
    for rule in rules:
        if rule['pattern'].lower() not in email:
            continue
        group = Group().load(rule['groupId'], force=True)
        if group:
            Group().addUser(group, user, rule['level'])


class AutojoinPlugin(GirderPlugin):
    DISPLAY_NAME = 'Auto Join'

    def load(self, info):
        events.bind('model.user.save.created', 'autojoin', userCreated)

        registerPluginStaticContent(
            plugin='autojoin',
            css=['/style.css'],
            js=['/girder-plugin-autojoin.umd.cjs'],
            staticDir=Path(__file__).parent / 'web_client' / 'dist',
            tree=info['serverRoot'],
        )
