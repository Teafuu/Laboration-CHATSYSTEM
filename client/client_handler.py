from utils.base import *
from utils.config import *

import socket, threading, time

# import winsound

commands = {'/help': 0, '/join': 1, '/part': 1, '/kick': 3, '/list': 1, '/channels': 0, '/msg': 2,
            '/nick': 1, '/op': 2, '/unop': 2, '/topic': 2, '/quit': 0, '/joined': 0}


def format_check(msg):
    if len(msg.split()) > 0:
        cmd, para = msg.split()[0], msg.split()[1:]
        if cmd in commands and len(para) == commands.get(cmd):
            _msg = msg.split()
            parsed_msg = ':'.join([_msg[0][1:]] + _msg[1:])
            print('format check parsed_msg:', parsed_msg)
            return True, parsed_msg
    print('Syntax error!')
    return False, None


class Client:
    def __init__(self, nick, address, _interface=None):
        self.nickname = nick
        self.ip = address
        self.interface = _interface
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.s.settimeout(TIMEOUT)
        self.s.connect((self.ip, PORT))
        send_buf(self.s, self.nickname)

        self.state = ThreadState()
        self.t1 = threading.Thread(target=self.send_thread)
        self.t2 = threading.Thread(target=self.recv_thread)

        for t in [self.t1, self.t2]:
            t.start()

    def send_thread(self, _msg=None):
        while self.state.running:
            try:
                if _msg:
                    send_buf(self.s, _msg)
                return
                    # else:
                    #     print('Syntax error!')
            except:
                self.state.running = False
            time.sleep(5)

    def recv_thread(self):
        while self.state.running:
            msg = read_buf(self.s)
            if msg:
                # winsound.Beep(100, 100)
                # winsound.Beep(100, 200)

                if self.interface:
                    self.interface.receive_message(msg)
                else:
                    print(msg, "\n")

    def stop_client(self):
        self.t1.join()
        self.t2.join()
        self.s.close()

    def run(self):
        while True:
            msg = input('>> ')
            # if msg != '\n' and msg != '' and format_check(msg):
            check, parsed_msg = format_check(msg)
            # if format_check(msg):
            if check:
                # _msg = msg.split()
                # parsed_msg = ':'.join([_msg[0][1:]] + _msg[1:])
                print('run parsed_msg:', parsed_msg)
                self.send_thread(parsed_msg)


name = input('enter name: ')
myClient = Client(name, "127.0.0.1")
myClient.run()
