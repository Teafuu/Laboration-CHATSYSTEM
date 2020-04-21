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

def part_channel(user, channelName, channels, users):
    server_alert(user, [user.id, ' left.'], '#')
    channels[user.channel].members.remove(user)
    user.channel = None

def change_nick(user, msg, channels, users):
    print("NOT YET IMPLEMENTED")

def list_channels(user, msg, channels, users):
    server_alert(user,['SERVER',channels], '#')

def list_users(user, msg, channels, users):
    if user.channel != none:
        server_alert(user,['SERVER',channels[user.channel].members], '#')

def kick_user(user, msg, channels, users):
    receiver, msg = msg[1], ' '.join(msg[2:])
    if check_operator(user, channels[user.channel]):
        for u in channels[user.channel].members:
            if receiver == u.id:
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

def remove_operator(user, msg, channels, users):
    server_alert(user, ['SERVER', user.id + " has quit."])
    del users[user.id]
