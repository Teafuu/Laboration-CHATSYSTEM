class User:
    def __init__(self, uid, sock):
        self.id = uid # nick namee
        self.socket = sock # socket
        self.queue = [] # messagee queue
        self.connected = True
        self.channel = None # channel name

class Channel:
    def __init__(self, channelName, user):
        self.id = channelName # channel name
        self.admin = user # current useradmin
        self.members = [user] # user list
        self.operators = [user] # operator list
        self.topic = ""
