class User:
    def __init__(self, uid, sock):
        self.id = uid           # nickname
        self.socket = sock      # socket
        self.queue = []         # message queue
        self.connected = True
        self.channel = []       # channel name
        self.attempts = 0       # ping attempts


class Channel:
    def __init__(self, channelName, user):
        self.id = channelName    # channel name
        self.admin = user        # current user admin
        self.members = [user]    # user list
        self.operators = [user]  # operator list
        self.topic = ""          # Server MOTD
