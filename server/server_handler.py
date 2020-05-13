# Coding: utf8

from utils.base import *
from utils.config import *
import socket, threading, time
from server import commands
from server import objects

HOST = input("Host IP: ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(QUEUE_SIZE)
s.settimeout(TIMEOUT)
state = ThreadState()

channels = {}
users = {}


# TODO_: part 1 & 2
def client_handle(c_sock, c_addr, state):  # to be implemented
    c_sock.settimeout(TIMEOUT)
    # Read the first message from the client # and use this as the nickname/username

    nick = read_buf(c_sock)
    user = objects.User(nick, c_sock)

    if nick not in users:
        users[nick] = user
        send_buf(user.socket, "#SERVER you are connected!")
    else:
        send_buf(user.socket, "#SERVER nick taken, use /nick [name] to reconnect.")

    print('ALERT::User {} at {}'.format(user.id, c_addr))
    while state.running and user.connected:
        msg = read_buf(c_sock)
        if not msg:
            continue
        command_handle(user.id, user, msg)
    c_sock.close()


def command_handle(nick, user, msg):
    msg = msg.replace('\n','')
    msg_list = msg.split()

    if nick in users and user is not users[nick]:
        if len(msg_list) > 1 and msg_list[0] == "/nick":
            users[msg_list[1]] = user
            user.id = msg_list[1]
            send_buf(user.socket, "#SERVER you are connected!")
    else:
        for command in commands.commands:
            if msg_list[0] == command:
                commands.commands[command][0](users[nick], msg_list, channels, users)
                return
        users[nick].queue.append((user.id, msg))


# TODO_: part 2.1
def client_send(state):
    """Send all unsent messages with a delay of 0.05 seconds"""
    while state.running:
        disconnected_users = []
        time.sleep(0.05)
        for nick in users:
            queue = users[nick].queue
            if queue:
                print('this is queue:', queue)
            while len(queue) > 0:
                sender, msg = queue.pop(0)
                message = '{}> {}'.format(sender, msg)
                try:
                    if ":" in message[0]: # private message
                        send_buf(users[nick].socket, message)
                    else: # channel message
                        for _usr in channels[message.split(' ')[0][1:]].members: # message      to everyone
                            if _usr.id != nick:
                                send_buf(users[_usr.id].socket, message)
                except:
                    pass
      #   for nick in disconnected_users:
        #     print('ALERT::{} disconnected'.format(nick))
          #   users[nick].c.close()
            # del users[nick]


# TODO_: part 2.2
def ping_thread(state):
    """Send PING message to users every PING_FREQ seconds"""
    while state.running:
        time.sleep(PING_FREQ)
        for nick in users:
            users[nick].queue.append(('SERVER', 'PING'))


def input_thread(state):
    stop = input("Server started, press Enter top stop.\n")
    state.running = False


# TODO_: part 3
t_input = threading.Thread(target=input_thread, args=(state,))
t_send = threading.Thread(target=client_send, args=(state,))
t_ping = threading.Thread(target=ping_thread, args=(state,))

t_ping.start()
t_send.start()
t_input.start()


# TODO_: part 3
client_threads = []
while state.running:
    try:
        c_sock, c_addr = s.accept()
        c_thread = threading.Thread(target=client_handle, args=(c_sock, c_addr, state))
        client_threads.append((c_thread, c_addr))
        c_thread.start()
    except:
        pass


# TODO: part 4
print("Exiting, waiting for threads")

t_input.join()
print("Input thread stopped")

t_send.join()
print("Send thread stopped")

t_ping.join()
print("Ping thread stopped")

for t, addr in client_threads:
    t.join()
    print("Thread for address {} stopped".format(addr))
print("Client threads stopped")

s.close()
print("Socket closed")
