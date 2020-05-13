from server import objects


def join_channel(user, msg, channels, users): # doesn't like spaced channels
    for channel in channels: # checking if existing channel
        if msg[1] in channel: # joining existing channel
            if msg[1] in user.channel:
                return
            user.channel.append(msg[1]  )
            channels[msg[1]].members.append(user)
            server_alert(user, ["SERVER", ' MOTD: ' + channels[msg[1]].topic],':')
            server_alert(user, ['SERVER', user.id + ' joined.'], ('#' + msg[1] + " "))
            return
    # create new chnnael
    server_alert(user,['SERVER','channel has been created.'], ':')
    channels[msg[1]] = objects.Channel(msg[1], user)
    user.channel.append(msg[1])


def server_alert(user, msg, type = ''):
    user.queue.append((type + msg[0], msg[1]))


def part_channel(user, msg, channels, users):
    if message_param_check(user, msg, 2):
        if msg[1] in user.channel:
            leave_channel(user, msg[1], channels)

def leave_channel(user, channelName, channels):
    if user in channels[channelName].operators:
        channels[channelName].operators.remove(user)
        if user == channels[channelName].admin:
            if len(channels[channelName].members) <= 1:
                server_alert(user, ['SERVER', ' server removed.'], ':')
                channels[channelName].members.remove(user)
                channels.pop(channelName)
                user.channel.remove(channelName)
            else:
                for _usr in channels[channelName].members:
                    if _usr != user:
                        server_alert(user, ['SERVER', user.id + ' left.'], ('#' + channelName + " "))
                        channels[channelName].admin = _usr
                        channels[channelName].operators.append(_usr)
                        server_alert(_usr, [user.id, ' you are now administartor.'], ':')
                        channels[channelName].members.remove(user)
                        user.channel.remove(channelName)
    else:
        server_alert(user, ['SERVER',  user.id + ' left.'], ('#' + channelName + " "))
        server_alert(user, ['SERVER', ' you left'], ':')
        channels[channelName].members.remove(user)
        user.channel.remove(channelName)


def change_nick(user, msg, channels, users):
    if msg[1] in users:
        server_alert(user, ['SERVER', ' nick taken.'], ':')
    else:
        for channelName in user.channel:
            server_alert(user, ['SERVER', user.id + ' has changed his nick to: ' + msg[1]], ('#' + channelName + " "))
        users[msg[1]] = users.pop(user.id)
        users[msg[1]].id = msg[1]
        server_alert(user, ['SERVER', ' nick has been changed.'], ':')


def list_channels(user, msg, channels, users):
    server_alert(user,['SERVER',channels.keys()], ':')

def list_users(user, msg, channels, users):
    if user.channel is not None:
        if message_param_check(user, msg, 2):
            if channel_exists(channels, msg[1], user):
                server_alert(user,['SERVER',channels[msg[1]].members], ':')


def list_commands(user, msg, channels, users):
    print("is running\n")
    msg_to_send = "\n"
    for command in commands:
        msg_to_send += command +" " + commands[command][1] + "\n"
    server_alert(user,['SERVER', msg_to_send], ':')

def kick_user(user, msg, channels, users):
    if message_param_check(user, msg, 3):
        channelName, receiver, msg = msg[1], msg[2], ' '.join(msg[3:])
        if channel_exists(channels, channelName, user):
            if check_operator(user, channels[channelName]): # check permission
                for u in channels[channelName].members: # iterate through everyone in the channel
                    if receiver == u.id and users[receiver] != channels[channelName].admin: # removes user from appropriate channel
                        channels[channelName].members.remove(users[receiver])
                        server_alert(users[receiver], ['SERVER', receiver + ' has been kicked'], ('#' + channelName + " "))
                        server_alert(users[receiver], [user.id, "You have been kicked by the following reason: " + msg], ':')
                        users[receiver].channel.remove(channelName)
                        return
                server_alert(user, ['SERVER', 'User does not exist'], ':')

def whisper_user(user, msg, channels, users):
    if message_param_check(user, msg, 2):
        receiver, msg = msg[1], ' '.join(msg[2:])

        if receiver[0] == '#' and receiver[1:] in user.channel:
            server_alert(user, [receiver + ' ' + user.id, msg])
            return
        else:
            if receiver in users:
                server_alert(users[receiver], [user.id, msg], ':')
                return

def change_topic(user, msg, channels, users):
    if message_param_check(user, msg, 2):
        channelName = msg[1]
        if channel_exists(channels, channelName, user):
            if check_operator(user, channels[channelName]):
                channels[msg[1]].topic = ' '.join(msg[2:])
                server_alert(user, ['SERVER', 'Topic has been changed succesfully'], ':')
                server_alert(user, ['SERVER', 'Topic has been changed to: ' + channels[msg[1]].topic], ('#' + channelName + " "))

def add_operator(user, msg, channels, users): # need to fix
    if message_param_check(user, msg, 3):
        channelName = msg[1]
        if check_operator(user, channels[channelName]):
            channels[channelName].operators.append(users[msg[2]])
            server_alert(users[msg[2]], ['SERVER', 'You have been added as operator.'], ':')

def remove_operator(user, msg, channels, users): # need to fix
    if message_param_check(user, msg, 2):
        channelName = msg[1]
        if check_operator(user, channels[channelName]) and channels[channelName].admin.id != msg[1]:
            channels[channelName].operators.append(msg[1])
            server_alert(users[msg[1]], ['SERVER', 'You have been removed as operator'], ':')

def check_operator(user, channel):
    for op in channel.operators:
        if user.id == op.id:
            return True
    server_alert(user, ['SERVER', 'Invalid permissions'], ':')
    return False

def quit_server(user, msg, channels, users): # need to fix
    server_alert(user, ['SERVER', user.id + " has quit."])
    users[user.id].connected = False
    del users[user.id]

def channel_exists(channels, channelName, user):
    if channelName in channels.keys():
        return True
    server_alert(user, ['SERVER', 'channel does not exist.'], ':')
    return False

def message_param_check(user, msg, limit):
    if len(msg) < limit:
        server_alert(user, ['SERVER', 'Invalid parameters'], ':')
        return False
    return True

def display_user_channels(user, msg, channels, users):
    server_alert(user, ['SERVER', user.channel], ':')

def display_online_users(user, msg, channels, users):
    server_alert(user, ['SERVER', users.keys()], ':')


commands = {'/help' : (list_commands,"Commands"),
            '/join': (join_channel, "[Channel Name]"),
            '/part' : (part_channel, "[Channel Name"),
            '/kick' : (kick_user,"[Server] [Nickname]"),
            '/list' : (list_users,"[Server]"),
            '/channels' : (list_channels,"Displays all servers"),
            '/w' : (whisper_user,"#[Server] or [Nickname] + [message]"),
            '/nick': (change_nick,"[New Nickname"),
            '/op' : (add_operator,"[Server] [Nickname]"),
            '/unop' : (remove_operator,"[Server] [Nickname]"),
            '/topic' : (change_topic,"[Server] [Topic]"),
            '/quit' : (quit_server,"Quits application"),
            '/joined' : (display_user_channels,"Displays your servers"),
            '/online' : (display_online_users, "Displays all users")}
