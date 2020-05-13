from utils.base import *
from utils.config import *
import socket, threading, time
import winsound


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
        self.t1 = threading.Thread(target=self.send_thread, args="")
        self.t2 = threading.Thread(target=self.recv_thread)

        for t in [self.t1, self.t2]:
            t.start()

    def send_thread(self, _msg):
        while self.state.running:
            try:
                send_buf(self.s, _msg)
                return
            except:
                self.state.running = False
            time.sleep(5)

    def recv_thread(self):
        while self.state.running:
            msg = read_buf(self.s)
            if msg:
                winsound.Beep(100, 100)
                winsound.Beep(100, 200)
                print('\n', msg)
                self.interface.receive_message(msg)

    def stop_client(self):
        self.t1.join()
        self.t2.join()
        self.s.close()