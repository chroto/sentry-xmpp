import sleekxmpp


class SentryNotificationBot(sleekxmpp.ClientXMPP):
    """
    Simple bot that joins a room to notify of log events
    """
    def __init__(self, jid, password, room, nick, message, room_password=None):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.room = room
        self.nick = nick
        self.room_password = room_password
        self.message = message
        self.add_event_handler('session_start', self.start)

    def start(self, event):
        self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        password=self.room_password,
                                        wait=True)
        self.send_message(mto=self.room,
                          mbody=self.message,
                          mtype='groupchat')
        self.disconnect(wait=True)
