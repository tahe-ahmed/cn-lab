import chat_protocol
import socket
import threading

MAX_WAIT_TIME = 5
HOST = ("0.0.0.0", 1234)

def check_newline(s: str):
    return ~('\n' in s)

def __main__():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(HOST)

    session = chat_protocol.SessionData()
    session.soc = server

    while 1:
        ui = input("Username: ")
        session.username = ui.removesuffix('\n')
        session.HELLO_FROM(ui.removesuffix('\n'))
        r = session.soc.recv(2048).decode("utf-8")
        if r.startswith("HELLO"):
            print("Login successful!")
            break
        elif r == "BUSY\n":
            print("Maximum user-count reached!")
            session.soc.close()
            session.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            session.soc.connect(HOST)
        elif r == "IN-USE\n":
            print("Username already in use!")
            session.soc.close()
            session.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            session.soc.connect(HOST)
        else:
            print(f"Error occurred: received unknown message \"{r}\"")
            return

    t = threading.Thread(target=session.receive)
    t.daemon = True
    t.start()
    

    while 1:
        ui = input()
        if ui == "!quit":
            break
        elif ui == "!who":
            session.LIST()
        elif ui.startswith('@'):
            args = ui.rsplit(' ', 1)
            if len(args) != 2:
                print(f"Unknown command \"{ui}\"")
                continue
            if ~check_newline(args[0]):
                print(f"Error: destination username cannot contain new-line, front-slash or backslash (\"username: {ui}\")")
                continue
            if ~check_newline(args[1]):
                print(f"Error: message cannot contain new-line, front-slash or backslash (\"message: {ui}\")")
                continue
            if len(args[1]) == 0:
                print("Cannot send empty message")
                continue
            session.SEND(args[0][1:], args[1])
        else:
            print(f"Unknown command \"{ui}\"")

    session.soc.close()
    
    

if __name__ == '__main__':
    __main__()