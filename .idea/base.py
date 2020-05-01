from config import HEADER_SIZE


class ThreadState:
    def __init__(self):
        self.running = True


def send_buf(socket, message):
    msg_to_send = message.encode()
    msg_len = str(len(msg_to_send)).rjust(HEADER_SIZE, '0')
    socket.send(msg_len.encode())
    socket.send(msg_to_send)


def read_buf(socket):
    while True:
        try:
            msg_len = socket.recv(HEADER_SIZE).decode()
            data = socket.recv(int(msg_len)).decode()
            return data if data else None
        except:
            return None


