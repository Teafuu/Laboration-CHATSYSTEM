import objects

def join_channel(user, channelName, channels):
    if user.channel is not None:  # implement hierarchy operator check, add alert for leaving
        channels[user.channel].members.remove(user)

    for channel in channels: # checking if existing channel
        if channelName[1] in channel: # joining existing channel
            user.channel = channelName[1]
            channels[channelName[1]].members.append(user)

            server_alert(user, [user.id, ' joined.'])
            return
    # create new chnnael
    server_alert(user,['SERVER','channel has been created.'], '#')
    channels[channelName[1]] = objects.Channel(channelName[1], user)
    user.channel = channelName[1]

def server_alert(user, msg,type = ''):
    user.queue.append((type + msg[0], msg[1]))

