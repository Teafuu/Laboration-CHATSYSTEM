# Laboration-CHATSYSTEM


Users är en dictionary med klassen User()
    def __init__(self, uid, sock):
        self.id = uid # nick name
        self.socket = sock # socket
        self.queue = [] # messagee queue
        self.connected = True
        self.channel = None # channel name
används för att komma åt väsentlig data.

Channels är en dictionary med Kanaler '
  def __init__(self, channelName, user):
        self.id = channelName # channel name
        self.admin = user # current useradmin
        self.members = [user] # user list
        self.operators = [user] # operator list
        self.topic = ""
  används för att komma åt användare i en kanal.


Alla COMMANDS kräver 4 argument 
    for command in commands:
        if msg_list[0] == command:
            commands[command](users[nick], msg_list, channels, users)
            return

users[nick] = är själva User instansen
msg_list = medelandet som användare har skickat in som är splittar ['/w','argument1','hej',] etc..
channels = dictionary för alla kanal instanser
users = dictionary för alla user instanser.
