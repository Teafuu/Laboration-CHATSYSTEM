from config import HEADER_SIZE


class ThreadState:
    def __init__(self):
        self.running = True


def send_buf(socket, message):
    msg_len = str(len(message)).rjust(HEADER_SIZE, '0')
    print(msg_len)
    socket.send(msg_len.encode())
    socket.send(message.encode())


def read_buf(socket):
    while True:
        try:
            msg_len = socket.recv(HEADER_SIZE).decode()
            data = socket.recv(int(msg_len)).decode()
            return data if data else None
        except:
            return None


