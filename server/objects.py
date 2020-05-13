class User:
    def __init__(self, uid, sock):
        self.id = uid # nick name
        self.socket = sock # socket
        self.queue = [] # messagee queue
        self.connected = True
        self.channel = [] # channel name
        self.attempts = 0


class Channel:
    def __init__(self, channelName, user):
        self.id = channelName # channel name
        self.admin = user # current useradmin
        self.members = [user] # user list
        self.operators = [user] # operator list
        self.topic = ""
