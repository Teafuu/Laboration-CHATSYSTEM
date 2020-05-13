from tkinter import *
from client import client_handler as c


class ClientPage(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.title("Chat Isaac")
        self.iconbitmap("icon.ico")
        self.geometry("700x400+0+0")
        self.resizable(False, False)

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in {StartPage}:
            page_name = F.__name__
            if page_name not in self.frames:
                self.frames[page_name] = eval(page_name)(container, self)
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        self.protocol("WM_DELETE_WINDOW", self.quit_func)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def quit_func(self):
        self.destroy()


class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.config(bg="#34495E")
        self.nickname = ""
        self.ip = ""
        self.parent = parent

        self.server_ip = Entry(self, textvariable=vars, width=30)
        server_ip_label = Label(self, text="Address", font=("Courier", 14), bg="#34495E")
        self.server_nickname = Entry(self, textvariable=vars, width=30)

        server_nickname_label = Label(self, text="Nickname", font=("Courier", 14), bg="#34495E")
        server_name = Label(self, text="Welcome to Chat Isaac", font=("Courier", 30, "bold"), bg="#34495E")
        connect_button = Button(self, text="Connect", bg="#6d9bc9", command=self.joining)

        self.grid_rowconfigure(0, minsize=100)
        self.grid_rowconfigure(2, minsize=50)
        self.grid_columnconfigure(0, minsize=100)

        server_name.grid(row=1, column=1, columnspan=2)
        server_ip_label.grid(row=3, column=1)
        self.server_ip.grid(row=3, column=2)
        server_nickname_label.grid(row=4, column=1)
        self.server_nickname.grid(row=4, column=2)
        connect_button.grid(row=5, column=2)

    def joining(self):
        self.nickname = self.server_nickname.get()
        self.ip = self.server_ip.get()

        frame = ChatPage(parent=self.parent, controller=self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()


class ChatPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        bg = "#34495E"
        self.controller = controller
        self.config(bg=bg)
        self.client = c.Client(controller.nickname, controller.ip, self)


        container = Frame(self, bg=bg)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        right_frame = Frame(container, width=220, height=340, bg="white", highlightbackground=bg, highlightthickness=10)
        right_frame.pack(side="right", anchor="nw")
        right_frame.pack_propagate(0)

        left_frame = Frame(container, width=480, height=340, bg="white", highlightbackground=bg, highlightthickness=10)
        left_frame.pack(side="left", anchor="ne")
        left_frame.pack_propagate(0)

        scrollbar = Scrollbar(left_frame)
        self.chat = Listbox(left_frame, height=10, width=50, font=("Courier", 8), yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.chat.pack(side=LEFT, fill=BOTH, expand=TRUE)

        input_frame = Frame(self, width=480, height=70, bg="white", highlightbackground=bg, highlightthickness=10)
        input_frame.pack(side="left", anchor="se")
        input_frame.pack_propagate(0)

        self.input_field = Entry(input_frame, textvariable=vars, width=76)
        self.input_field.bind('<Return>', self.send_message)
        self.input_field.pack()

        name_label = Label(self, text=controller.nickname,  font=("Courier", 8), bg="#34495E", fg="white")
        connected_label = Label(self, text="Connected: " + controller.ip, font=("Courier", 6), bg="#34495E")
        connected_label.pack(side="right", anchor="sw")
        name_label.pack(side="right", anchor="sw")

    def send_message(self, event):
        msg = self.input_field.get()

        if len(msg) >= 1:
            self.client.send_thread(msg)
            _msg = msg.split(" ")
            if _msg[0] == '/w':
                self.chat.insert(END, "to {}> {}".format(_msg[1], ' '.join(_msg[2:])) + "\n")
            self.chat.see(END)
            self.input_field.delete(0, 'end')

    def receive_message(self, msg):
        for _msg in msg.split('\n'):
            self.chat.insert(END, _msg + '\n')
        self.chat.see(END)


if __name__ == '__main__':
    app = ClientPage()
    app.mainloop()


