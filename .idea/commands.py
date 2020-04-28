import objects

def join_channel(user, msg, channels, users):
    if user.channel is not None:  # implement hierarchy operator check, add alert for leaving
        part_channel(user, msg, channels, users)

    for channel in channels: # checking if existing channel
        if msg[1] in channel: # joining existing channel
            user.channel = msg[1]
            channels[msg[1]].members.append(user)
            server_alert(user, ["SERVER", ' MOTD: ' + channels[msg[1]].topic],'#')
            server_alert(user, [user.id, ' joined.'])
            return
    # create new chnnael
    server_alert(user,['SERVER','channel has been created.'], '#')
    channels[msg[1]] = objects.Channel(msg[1], user)
    user.channel = msg[1]

def server_alert(user, msg, type = ''):
    user.queue.append((type + msg[0], msg[1]))

def part_channel(user, msg, channels, users):
    if user in channels[user.channel].operators:
        channels[user.channel].operators.remove(user)
        if user == channels[user.channel].admin:
            if len(channels[user.channel].members) <= 1:
                server_alert(user, [user.id, ' server removed.'], '#')
                channels[user.channel].members.remove(user)
                channels.pop(user.channel)
                user.channel = None
            else:
                for _usr in channels[user.channel].members:
                    if _usr != user:
                        channels[_usr.channel].admin = _usr
                        channels[_usr.channel].operators.append(_usr)
                        server_alert(_usr, [user.id, ' you are now administartor.'], '#')
                        channels[user.channel].members.remove(user)
                        user.channel = None
    else:
        server_alert(user, [user.id, ' left.'], '#')
        channels[user.channel].members.remove(user)
        user.channel = None

def change_nick(user, msg, channels, users):
    server_alert(user, ['SERVER', user.id + ' has changed his nick to: ' + msg[1]], '')
    users[msg[1]] = users.pop(user.id)
    users[msg[1]].id = msg[1]
    server_alert(user, ['SERVER', ' nick has been changed.'], '#')


def list_channels(user, msg, channels, users):
    server_alert(user,['SERVER',channels.keys()], '#')

def list_users(user, msg, channels, users):
    if user.channel is not None:
        server_alert(user,['SERVER',channels[user.channel].members], '#')

def list_commands(user, msg, channels, users):
    msg_to_send = "\n"
    for command in commands:
        msg_to_send += command + "\n"
    server_alert(user,['SERVER', msg_to_send], '#')


def kick_user(user, msg, channels, users):
    receiver, msg = msg[1], ' '.join(msg[2:])
    if check_operator(user, channels[user.channel]): # check permission
        for u in channels[user.channel].members: # iterate through everyone in the channel
            if receiver == u.id and users[receiver] != channels[user.channel].admin: # removes user from appropriate channel
                channels[user.channel].members.remove(users[receiver])
                server_alert(users[receiver], ['SERVER', receiver + 'has been kicked'])
                server_alert(users[receiver], [user.id, msg], '#')
                users[receiver].channel = None
                return

        server_alert(user, ['SERVER', 'User does not exist'], '#')


def whisper_user(user, msg, channels, users):
    receiver, msg = msg[1], ' '.join(msg[2:])

    for u in users:
        if receiver == u:  # If user doesn't exist
            server_alert(users[receiver], [user.id, msg], '#')
            return

def change_topic(user, msg, channels, users):
    if check_operator(user, channels[user.channel]):
        channels[user.channel].topic = ' '.join(msg[1:])
        server_alert(user, ['SERVER', 'Topic has been changed succesfully'], '#')
        server_alert(user, ['SERVER', 'Topic has been changed to: ' + channels[user.channel].topic], '')

def add_operator(user, msg, channels, users):
    if check_operator(user, channels[user.channel]):
        channels[user.channel].operators.append(users[msg[1]])
        server_alert(users[msg[1]], ['SERVER', 'You have been added as operator.'], '#')

def remove_operator(user, msg, channels, users):
    if check_operator(user, channels[user.channel]) and channels[user.channel].admin.id != msg[1]:
        channels[user.channel].operators.append(msg[1])
        server_alert(users[msg[1]], ['SERVER', 'You have been removed as operator'], '#')

def check_operator(user, channel):
    for op in channel.operators:
        if user.id == op.id:
            return True
    server_alert(user, ['SERVER', 'Invalid permissions'], '#')
    return False

def quit_server(user, msg, channels, users):
    server_alert(user, ['SERVER', user.id + " has quit."])
    users[user.id].connected = False
    del users[user.id]

commands = {'/help' : list_commands,
            '/join': join_channel,
            '/part' : part_channel,
            '/kick' : kick_user,
            '/list' : list_users,
            '/channels' : list_channels,
            '/w' : whisper_user,
            '/nick': change_nick,
            '/op' : add_operator,
            '/unop' : remove_operator,
            '/topic' : change_topic,
            '/quit' : quit_server}
