# Coding: utf8
import os, sys
file_dir = os.path.dirname('/Users/thomasliu/IntelliJProjects/ADS2/Laboration-CHATSYSTEM/utils')
sys.path.append(file_dir)

from utils.base import *
from utils.config import *
import socket, threading, time
from server import commands
from server import objects


class Server:
    def __init__(self, ip=""):
        self.HOST = ip
        self.channels = {}
        self.users = {}
        self.client_threads = []

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen(QUEUE_SIZE)
        self.s.settimeout(TIMEOUT)

        self.state = ThreadState()
        self.t_input = threading.Thread(target=self.input_thread)
        self.t_send = threading.Thread(target=self.client_send)
        self.t_ping = threading.Thread(target=self.ping_thread)

        self.t_ping.start()
        self.t_send.start()
        self.t_input.start()

# TODO_: part 1 & 2
    def client_handle(self, c_sock, c_addr):
        c_sock.settimeout(TIMEOUT)
        # Read the first message from the client # and use this as the nickname/username

        nick = read_buf(c_sock)
        user = objects.User(nick, c_sock)

        if nick not in self.users:
            self.users[nick] = user
            send_buf(user.socket, "#SERVER you are connected!")
        else:
            send_buf(user.socket, "#SERVER nick taken, use /nick [name] to reconnect.")

        print('ALERT::User {} at {}'.format(user.id, c_addr))
        while self.state.running and user.connected:
            msg = read_buf(c_sock)
            if not msg:
                continue
            user.attempts = 0
            self.command_handle(user.id, user, msg)
        c_sock.close()

    def command_handle(self, nick, user, msg):
        msg = msg.replace('\n', '')
        msg_list = msg.split(':')
        print('msg:', msg)
        print('msg_list:', msg_list)
        if msg_list:
            if nick in self.users and user is not self.users[nick]:
                if len(msg_list) > 1 and msg_list[0] == "nick":
                    self.users[msg_list[1]] = user
                    user.id = msg_list[1]
                    send_buf(user.socket, "#SERVER you are connected!")
            else:
                for cmd in commands.commands:
                    if msg_list[0] == cmd:
                        commands.commands[cmd][0](self.users[nick], msg_list, self.channels, self.users)
                        return
                self.users[nick].queue.append((user.id, msg))

# TODO_: part 2.1
    def client_send(self):
        while self.state.running:
            disconnected_users = []
            time.sleep(0.05)
            for nick in self.users:
                queue = self.users[nick].queue
                if queue:
                    print('this is queue:', queue)
                while len(queue) > 0:
                    sender, msg = queue.pop(0)
                    message = '<{}> {}'.format(sender, msg)

                    try:
                        if '#' not in sender:  # private message
                            send_buf(self.users[nick].socket, message)
                        elif '#' in sender:  # channel message
                            for member in self.channels[sender].members:  # message to everyone
                                if member.id != nick:
                                    send_buf(self.users[member.id].socket, message)
                    except Exception as e:
                        print("ERROR: ", e)
                        self.users[nick].attempts += 1
                        if self.users[nick].attempts > 9:
                            disconnected_users.append(self.users[nick])

            for nick in disconnected_users:
                print('ALERT::{} disconnected'.format(nick))
                self.users[nick].socket.close()
                del self.users[nick]

    def ping_thread(self):
        while self.state.running:
            time.sleep(PING_FREQ)
            for nick in self.users:
                self.users[nick].queue.append(('!PING', ''))

    def input_thread(self):
        input("Server started, press Enter top stop.\n")
        self.state.running = False

    def run(self):
        while self.state.running:
            try:
                c_sock, c_addr = self.s.accept()
                c_thread = threading.Thread(target=self.client_handle, args=(c_sock, c_addr))
                self.client_threads.append((c_thread, c_addr))
                c_thread.start()
            except Exception as e:
                print("Error: ", e)

    def quit(self):
        self.t_input.join()
        self.t_send.join()
        self.t_ping.join()

        for t, addr in self.client_threads:
            t.join()
            print("Thread for address {} stopped".format(addr))
        print("Client threads stopped")
        self.s.close()


if __name__ == '__main__':
    myServer = Server(input("Enter IP-address"))
    myServer.run()