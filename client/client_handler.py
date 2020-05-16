# Run from terminal
import os, sys
file_dir = os.path.dirname('/Users/thomasliu/IntelliJProjects/ADS2/Laboration-CHATSYSTEM/utils')
sys.path.append(file_dir)

from utils.base import *
from utils.config import *
import socket, threading, time

# import winsound

commands_no_channel = {'/channels': 0, '/help': 0, '/joined': 0, '/online': 0, '/quit': 0, '/nick': 1}
commands_channel = {'/join': 1, '/list': 1, '/part': 1, '/op': 2, '/unop': 2}
commands_sentence = {'/msg': 2, '/topic': 2, '/kick': 3}


def format_check(msg):
    if len(msg.split()) > 0 and msg[0] == '/':
        cmd, para = msg.split()[0], msg.split()[1:]
        if cmd in commands_no_channel and len(para) == commands_no_channel[cmd]:  # Case 1. No channels
            _msg = msg.split()
            parsed_msg = ':'.join([_msg[0][1:]] + _msg[1:])
            return True, parsed_msg
        elif cmd in commands_channel and len(para) == commands_channel[cmd] and para[0][0] == '#':  # Case 2. Channels
            _msg = msg.split()
            parsed_msg = ':'.join([_msg[0][1:]] + _msg[1:])
            return True, parsed_msg
        elif cmd in commands_sentence and len(para) >= commands_sentence[cmd]:  # Case 3. Sentence
            if (cmd == '/topic' or cmd == '/kick') and para[0][0] == '#':
                _msg = msg.split()
                parsed_msg = ':'.join([_msg[0][1:]] + _msg[1:])
                return True, parsed_msg
            elif cmd == '/msg':
                _msg = msg.split()
                parsed_msg = ':'.join([_msg[0][1:]] + _msg[1:])
                return True, parsed_msg
            return False, None
        return False, None
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
            msg = input()
            check, parsed_msg = format_check(msg)
            if check:
                self.send_thread(parsed_msg)
            else:
                print('Client: SYNTAX ERROR!!!')


if __name__ == '__main__':
    name = input('enter name: ')
    myClient = Client(name, "127.0.0.1")
    myClient.run()
