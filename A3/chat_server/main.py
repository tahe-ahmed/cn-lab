import threading
import select
import socket
import uuid
import chat_protocol

MAX_USERS = 64
IP = '127.0.0.1'
PORT = 1234
LENGTH = 4000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))

server_socket.listen(MAX_USERS)
print(f"the server is running and listening on port {PORT}")

username_to_uuid = {}
uuid_to_socket = {}

def poll_clients():
    while 1:
        read_sockets, _, in_error = select.select(list(uuid_to_socket.values()), [], [])
        for _uuid, _socket in read_sockets:
        
            if _socket == server_socket:
                client_socket, client_IP = server_socket.accept()
            
                uuid_to_socket[uuid.uuid4()] = client_socket

                print(f"New connection port : {client_IP}")
            else:
                threading.Thread(target=chat_protocol.receive, args=(_uuid, _socket)).start()

        

t = threading.Thread(target=poll_clients)
t.daemon = True
t.start()

