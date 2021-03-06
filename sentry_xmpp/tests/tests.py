import unittest

from django.conf import settings
import mimic

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                },
            },
        SENTRY_BUFFER='sentry.buffer.base.Buffer',
        SENTRY_BUFFER_OPTIONS={},
        SENTRY_QUOTAS='sentry.quotas.Quota',
        SENTRY_QUOTA_OPTIONS={},
        SENTRY_URL_PREFIX='',
        ROOT_URLCONF='sentry_xmpp.tests.urls',
        INSTALLED_APPS=[
        ]
    )

# This must happen after settings
from sentry_xmpp.plugin import XMPPMessage


class TestXMPPMessage(mimic.MimicTestBase):
    def setUp(self, *args, **kwargs):
        self.mimic = mimic.Mimic()
        super(TestXMPPMessage, self).setUp(*args, **kwargs)

    def get_mock_group_and_event(self, message, new=True, sample=False):
        arbitrary_project = self.mimic.create_mock_anything()
        arbitrary_project.slug = 'alpha' # arbitrary
        arbitrary_group = self.mimic.create_mock_anything()
        arbitrary_group.id = 224 # arbitrary
        arbitrary_group.project = arbitrary_project
        arbitrary_group.team = self.mimic.create_mock_anything()
        arbitrary_group.team.slug = 'whatever'
        arbitrary_server_name = 'beta' # arbitrary

        event = self.mimic.create_mock_anything()
        event.project = arbitrary_project
        event.message = message
        event.server_name = arbitrary_server_name
        return arbitrary_group, event

    def test_clean_passes(self):
        event_is_new = True
        event_is_sample = False
        very_long_message = 'a' * 512

        def set_message(message):
            self.sent_message = message

        def get_message():
            return self.sent_message

        group, event = self.get_mock_group_and_event(very_long_message)

        message = XMPPMessage()

        self.mimic.stub_out_with_mock(message, 'is_configured')
        message.is_configured(mimic.IgnoreArg()).and_return(True)

        self.mimic.stub_out_with_mock(message, 'send_payload')
        message.send_payload = lambda project, message: set_message(message)

        self.mimic.replay_all()

        message.post_process(
            group,
            event,
            event_is_new,
            event_is_sample,
            )

        message = get_message()
        # group_id is in the link, ensure that it is still present
        self.assertTrue(
            str(group.id) in message
        )
        # ensure that server name is still present
        self.assertTrue(
            str(event.server_name) in message
        )
