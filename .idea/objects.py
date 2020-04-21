class User:
    def __init__(self, uid, sock):
        self.id = uid
        self.socket = sock
        self.queue = []
        self.connected = True
        self.channel = None

class Channel:
    def __init__(self, channelName, _admin):
        self.id = channelName
        self.admin = _admin
        self.members = [_admin]
        self.operators = []
