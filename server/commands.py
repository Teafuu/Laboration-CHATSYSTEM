from server import objects


def join_channel(user, msg, channels, users):
    channel = msg[1]
    if channel in channels:
        if channel in user.channel:  # Case 1. if channel already joined
            server_alert(user, ['SERVER', '<Channel already joined>'])
        else:  # Case 2. join channel
            user.channel.append(channel)
            channels[channel].members.append(user)
            server_alert(user, ['SERVER', f'<{channel} joined. MOTD: {channels[channel].topic}>'])
            server_alert(user, [channel, f'<{user.id} has joined>'])
            return
    else:  # Case 3. create new channel
        server_alert(user, ['SERVER', '<Channel has been created>'])  # create new chnnael
        channels[channel] = objects.Channel(channel, user)
        user.channel.append(channel)


def part_channel(user, msg, channels, users):
    channel_name = msg[1]
    if channel_exists(channel_name, user):
        leave_channel(user, channel_name, channels)


def leave_channel(user, channel_name, channels):
    if user in channels[channel_name].operators:
        channels[channel_name].operators.remove(user)
        if user == channels[channel_name].admin:  # Case 1. If sole member
            if len(channels[channel_name].members) <= 1:
                server_alert(user, ['SERVER', '<Channel removed>'])
                channels[channel_name].members.remove(user)
                channels.pop(channel_name)
                user.channel.remove(channel_name)
            else:
                for _usr in channels[channel_name].members:
                    if _usr != user:  # Case 2. if admin lave channel
                        server_alert(user, ['SERVER', f'<You have left {channel_name}>'])
                        server_alert(user, [channel_name, f'<{user.id} has left the channel>'])
                        channels[channel_name].admin = _usr
                        channels[channel_name].operators.append(_usr)
                        server_alert(_usr, [user.id, f'You are now the admin of {channel_name}'])
                        channels[channel_name].members.remove(user)
                        user.channel.remove(channel_name)
                        return
    else:  # Case 3. If members
        server_alert(user, [channel_name, f'<{user.id} has left the channel>'])
        server_alert(user, ['SERVER', f'<You left {channel_name}>'])
        channels[channel_name].members.remove(user)
        user.channel.remove(channel_name)


def change_nick(user, msg, channels, users):
    nickname = msg[1]
    if nickname not in users:
        for channel_name in user.channel:  # Broadcast to user's channel(s)
            server_alert(user, [channel_name, f'<{user.id} has changed nickname to {nickname}>'])
        users[nickname] = users.pop(user.id)
        users[nickname].id = nickname
        server_alert(user, ['SERVER', f'<Your nickname is now {user.id}>'])
    else:
        server_alert(user, ['SERVER', '<Nickname taken>'])


def list_all_channels(user, msg, channels, users):
    if channels:
        msg_to_send = f'All channels ({len(channels)}):\n'
        for channel_name in sorted(channels):
            msg_to_send += f'{"":9}{channel_name}\n'
        server_alert(user, ['SERVER', msg_to_send])
    else:
        server_alert(user, ['SERVER', '<No existing channels>'])


def list_user_channels(user, msg, channels, users):
    if user.channel:
        msg_to_send = f'Channels joined ({len(user.channel)}):\n'
        for channel in user.channel:
            # msg_to_send += f'{channel}\n'
            msg_to_send += f'{"":9}{channel}+\n' if user == channels[channel].admin else f'{"":9}{channel}\n'
        server_alert(user, ['SERVER', msg_to_send])
    else:
        server_alert(user, ['SERVER', '<No channels joined>'])


def display_online_users(user, msg, channels, users):
    if users:
        msg_to_send = f'All online users ({len(users)}):\n'
        for member in sorted(users, key=lambda x: x.casefold()):
            # msg_to_send += f'{"":9}{member}\n' if member != user.id else f'{"":9}{color.BOLD}{member}{color.END}\n'
            msg_to_send += f'{"":9}{member}\n'
        server_alert(user, ['SERVER', msg_to_send])
    else:
        server_alert(user, ['SERVER', '<No online users>'])


def list_users(user, msg, channels, users):  # Non-alphabetic, fix later
    channel_name = msg[1]
    if channel_exists(channel_name, user):
        msg_to_send = f'Members of {channel_name}\n{"":9}+{channels[channel_name].admin.id}\n'  # Text & admin
        # msg_to_send += f'{"":9}{channels[channel_name].admin.id}\n'
        for op in sorted([o.id for o in channels[channel_name].operators], key=lambda x: x.casefold()):
            if op != channels[channel_name].admin.id:
                msg_to_send += f'{"":9}@{op}\n'
        for member in sorted([m.id for m in channels[channel_name].members if m not in channels[channel_name].operators], key=lambda x: x.casefold()):
            msg_to_send += f'{"":9}{member}\n'
        server_alert(user, ['SERVER', msg_to_send])


def list_commands(user, msg, channels, users):
    msg_to_send = f'\n{"Usage":<36}{"Description"}\n{"-" * 5:<36}{"-" * 11}\n'
    for command in sorted(commands):
        msg_to_send += f'/{command + " " + commands[command][1]:<35}{commands[command][2]}\n'
    server_alert(user, ['SERVER', msg_to_send])


def kick_user(user, msg, channels, users):
    channel_name, receiver, reason = msg[1], msg[2], ' '.join(msg[3:])
    if channel_exists(channel_name, user):
        if check_operator(user, channels[channel_name]):  # check permission
            if user == users.get(receiver):
                server_alert(user, ['SERVER', '<You cannot kick yourself>'])
            elif user != channels[channel_name].admin and users.get(receiver) in channels[channel_name].operators:
                server_alert(user, ['SERVER', '<Permission denied>'])
            elif users.get(receiver) in channels[channel_name].members and users[receiver] != channels[channel_name].admin:
                channels[channel_name].operators.remove(users[receiver]) if users.get(receiver) in channels[channel_name].operators else None
                channels[channel_name].members.remove(users[receiver])
                server_alert(user, ['SERVER', f'<You have kicked {receiver}>'])  # To admin
                server_alert(users[receiver], [f'+{user.id}' if user == channels[channel_name].admin else f'@{user.id}', f'You have been kicked from {channel_name} by the following reason: {reason}'])  # to kicked
                server_alert(user, [channel_name, f'<{receiver} has been kicked>'])  # To channel
                users[receiver].channel.remove(channel_name)
            else:
                server_alert(user, ['SERVER', '<Invalid user>'])


def whisper_user(user, msg, channels, users):  # rewrite: if receiver[0] == #: ... else: # private message
    receiver, msg = msg[1], ' '.join(msg[2:])
    if receiver in user.channel:  # Case 1. Broadcast
        server_alert(user, [receiver, f'<{user.id}> {msg}'])
    elif receiver in users:  # Case 2. Private message
        server_alert(users[receiver], [user.id, msg])
    elif receiver in channels and receiver not in user.channel:  # channel not joined
        server_alert(user, ['SERVER', f'<Channel {receiver} not joined>'])
    elif receiver[0] != '#' and receiver not in users:  # Case 4. Invalid user
        server_alert(user, ['SERVER', f'<User {receiver} does not exist>'])
    else:  # Case 5. Invalid channel
        server_alert(user, ['SERVER', f'<Channel {receiver} does not exist>'])


def change_topic(user, msg, channels, users):
    channel_name, topic = msg[1], ' '.join(msg[2:])
    if channel_exists(channel_name, user) and check_operator(user, channels[channel_name]):
        channels[channel_name].topic = topic
        server_alert(user, ['SERVER', f'<Topic has been changed to: {channels[channel_name].topic}>'])  # to user
        server_alert(user, [channel_name, f'<Topic has been changed to: {channels[channel_name].topic}>'])  # to channel


def add_operator(user, msg, channels, users):
    channel_name, receiver = msg[1], ' '.join(msg[2:])
    if channel_exists(channel_name, user):  # check channel
        if user != channels[channel_name].admin:  # check admin
            server_alert(user, ['SERVER', '<Permission denied>'])
        elif users.get(receiver) not in channels[channel_name].members:  # check user
            server_alert(user, ['SERVER', '<Invalid user>'])
        else:
            if user.id == receiver:  # admin admin
                server_alert(user, ['SERVER', '<You are already admin>'])
            elif users[receiver] in channels[channel_name].operators:  # already op
                server_alert(user, ['SERVER', '<User already operator>'])
            else:
                channels[channel_name].operators.append(users[receiver])
                server_alert(user, ['SERVER', f'<Operator privilege assigned to {receiver}>'])  # to admin
                server_alert(users[receiver], [f'@{user.id}', f'You have been added as operator of {channel_name}'])  # to op
                server_alert(user, [channel_name, f'<{receiver} is now an operator>'])  # to channel


def remove_operator(user, msg, channels, users):
    channel_name, receiver = msg[1], ' '.join(msg[2:])
    if channel_exists(channel_name, user):  # check channel
        if user != channels[channel_name].admin:  # check admin
            server_alert(user, ['SERVER', '<Permission denied>'])
        # elif users.get(receiver) not in channels[channel_name].members:  # check user
        elif receiver not in users:  # check user
            server_alert(user, ['SERVER', '<Invalid user>'])
        else:
            if user.id == receiver:  # /unop admin
                server_alert(user, ['SERVER', '<You are the admin>'])
            elif users[receiver] not in channels[channel_name].operators:  # not op
                server_alert(user, ['SERVER', '<User is not operator>'])
            else:
                channels[channel_name].operators.remove(users[receiver])
                server_alert(user, ['SERVER', f'<Operator privilege removed from {receiver}>'])  # to admin
                server_alert(users[receiver], [f'+{user.id}', f'You have been removed as operator of {channel_name}'])  # to op
                server_alert(user, [channel_name, f'<{receiver} has been removed as operator>'])  # to channel


def quit_server(user, msg, channels, users):  # need to fix
    server_alert(user, ['SERVER', f'{user.id} has quit'])
    while len(user.channel) > 0:
        leave_channel(user, user.channel[0], channels)
    users[user.id].connected = False
    del users[user.id]


def check_operator(user, channel):
    if user in channel.operators:
        return True
    server_alert(user, ['SERVER', '<Invalid permissions>'])
    return False


def channel_exists(channel_name, user, prompt=None):
    if channel_name in user.channel:
        return True
    server_alert(user, ['SERVER', f'<{prompt}>']) if prompt else server_alert(user, ['SERVER', '<Invalid channel>'])
    return False


def server_alert(user, msg):
    user.queue.append((msg[0], msg[1]))


commands = {'help': (list_commands, '', "Shows this message"),
            'join': (join_channel, "#<channel>", 'Join existing channel, else create new channel'),
            'part': (part_channel, "#<channel>", 'Leave channel'),
            'kick': (kick_user, "#<channel> <nick> <reason>", 'Kick user, reason optional (Admin/op)'),
            'list': (list_users, "#<channel>", 'List channel members, admin/op denoted by +/@'),
            'channels': (list_all_channels, '', "List all channels"),
            'msg': (whisper_user, "#<channel> or <nick> <message>", 'Send message to user or channel'),
            'nick': (change_nick, "<nick>", 'Change nickname, must be unique'),
            'op': (add_operator, "#<channel> <nick>", 'Assign user operator privilege (Admin)'),
            'unop': (remove_operator, "#<channel> <nick>", 'Remove user operator privilege (Admin)'),
            'topic': (change_topic, "#<channel> <topic>", 'Assign or change channel topic (Admin/op)'),
            'quit': (quit_server, '', "Quits application", 'Quit server'),
            'joined': (list_user_channels, '', "List joined channels, admin denoted by +"),
            'online': (display_online_users, '', "List all users")}
