from django import forms
from django.core.urlresolvers import reverse

from sentry.plugins import Plugin
from sentry.utils.http import absolute_uri
from sentry_xmpp.bot import SentryNotificationBot

import sentry_xmpp
import logging

log = logging.getLogger(__name__)


class XMPPOptionsForm(forms.Form):
    jid = forms.CharField()
    password = forms.CharField(required=False)
    nick = forms.CharField()
    room = forms.CharField()

    room_password = forms.CharField(required=False)


class XMPPMessage(Plugin):
    author = 'Christopher Proto'
    author_url = 'http://chrispro.to/projects/sentry-xmpp'
    title = 'XMPP'
    conf_title = 'XMPP'
    conf_key = 'xmpp'
    version = sentry_xmpp.VERSION
    project_conf_form = XMPPOptionsForm

    BASE_MAXIMUM_MESSAGE_LENGTH = 400

    def is_configured(self, project):
        return all(self.get_option(k, project) for k in ('jid', 'nick'))

    @staticmethod
    def get_group_url(group):
        return absolute_uri(reverse('sentry-group', args=[
            group.team.slug,
            group.project.slug,
            group.id,
            ]))

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        if not is_new or not self.is_configured(event.project):
            return
        link = self.get_group_url(group)
        message = event.message.replace('\n', ' ').replace('\r', ' ')
        message_format = '[%s] %s (%s)'
        max_message_length = (
            self.BASE_MAXIMUM_MESSAGE_LENGTH
            - len(link)
            - len(event.server_name)
            - len(message_format.replace('%s', '')) # No of brackets/spaces
        )
        if len(message) > max_message_length:
            message = message[0:max_message_length-3] + '...'

        message = message_format % (event.server_name, message, link)
        self.send_payload(event.project, message)

    def send_payload(self, project, message):
        jid = self.get_option('jid', project)
        password = self.get_option('password', project)
        nick = self.get_option('nick', project)
        room = self.get_option('room', project)
        room_password = self.get_option('room_password', project)

        xmpp = SentryNotificationBot(jid, password, room, nick, message, room_password)
        xmpp.register_plugin('xep_0030')  # Service Discovery
        xmpp.register_plugin('xep_0045')  # Multi-User Chat
        xmpp.register_plugin('xep_0199')  # XMPP Ping

        if xmpp.connect():
            xmpp.process(block=False)
        else:
            log.error("XMPP Bot was unable to make a connection", *(jid, password, nick, room))
