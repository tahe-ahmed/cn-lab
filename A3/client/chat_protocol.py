import socket

class SessionData:
    soc: socket
    username: str

    def HELLO_FROM(self, name: str):
        self.soc.send(f"HELLO-FROM {name}\n".encode("utf-8"))

    def HELLO(self, name: str):
        if name == self.username:
            print("Login successful!")

    def LIST(self):
        self.soc.send("LIST\n".encode("utf-8"))

    def LIST_OK(self, names: list[str]):
        print(f"Currently active users:")
        for name in names:
            print(f"{name}")

    def SEND(self, user: str, msg: str):
        self.soc.send(f"SEND {user} {msg}\n".encode("utf-8"))

    def SEND_OK(self):
        pass

    def BAD_DEST_USER(self):
        print("Couldn't send message: target user is not online!")

    def DELIVERY(self, user: str, msg: str):
        if user != self.username:
            print(f"[{user}] {msg}")

    def IN_USE(self):
        print("Couldn't connect to server: username is already in use!")

    def BUSY(self):
        print("Couldn't connect to server: maximum number of user is already online.")

    def BAD_RQST_HDR(self):
        print("An error occurred: BAD_RQST_HDR")

    def BAD_RQST_BODY(self):
        print("An error occurred: BAD_RQST_BODY")

    def process_received(self, data: bytes):
        msg = data.decode("utf-8")
        args = msg.rsplit(' ', -1)

        if len(args) == 0:
            print("Received empty message")
            return False

        for i in range(0, len(args)):
            args[i] = args[i].removesuffix('\n')

        match args[0]:
            case "HELLO":
                self.HELLO(args[1])
            case "LIST-OK":
                self.LIST_OK(args[1].rsplit(',', -1))
            case "SEND-OK":
                self.SEND_OK()
            case "BAD-DEST-USER":
                self.BAD_DEST_USER()
            case "DELIVERY":
                self.DELIVERY(args[1], args[2])
            case "IN-USE":
                self.IN_USE()
            case "BUSY":
                self.BUSY()
            case "BAD-RQST-HDR":
                self.BAD_RQST_HDR()
            case "BAD-RQST-BODY":
                self.BAD_RQST_BODY()
            case default:
                if len(msg) != 0:
                    print(f"Unknown message: {msg}")
                return False
        return True

    def receive(self):
        buffer = bytearray(0)
        buffer_max = 4096
        with self.soc:
            try:
                while 1:
                    data = self.soc.recv(512)
                    if not data:
                        print("Connection closed!")
                        break
                    else:
                        for b in data:
                            buffer.append(b)
                        if len(buffer) > buffer_max:
                            print(f"Warning: received message was too large ({len(buffer)} bytes). Message discarded")
                            buffer.clear()
                        elif b'\n' in buffer:
                            for msg in buffer.rsplit(b'\n', -1):
                                self.process_received(msg)
                            buffer.clear()
                
            except ConnectionAbortedError:
                return
        
