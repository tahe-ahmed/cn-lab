import uuid
import socket
import main

def HELLO_FROM(name: str, soc_id: uuid.UUID):
    if len(main.username_to_uuid) == main.MAX_USERS:
        BUSY(soc_id)
    elif not name in main.username_to_uuid:
        main.username_to_uuid[name] = soc_id
        HELLO(name, soc_id)
    else:
        IN_USE(soc_id)

def HELLO(name: str, soc_id: uuid.UUID):
    main.uuid_to_socket[soc_id].send(f"HELLO {name}\n".encode("utf-8"))

def LIST(soc_id: uuid.UUID):
    LIST_OK(main.username_to_uuid.keys, soc_id)

def LIST_OK(names: list[str], soc_id: uuid.UUID):
    if len(names) == 1:
        main.uuid_to_socket[soc_id].send(f"LIST-OK {names[0]}".encode("utf-8"))
    else:
        str = f"LIST-OK {names[0]}"
        for name in names[1:]:
            str += f", {name}"
        str += '\n'
        main.uuid_to_socket[soc_id].send(str.encode("utf-8"))

def SEND(username: str, msg: str, soc_id: uuid.UUID):
    dest = main.username_to_uuid[username]
    if not dest:
        BAD_DEST_USER(soc_id)
    else:
        for _usr, _uuid in main.username_to_uuid:
            if _uuid == soc_id:
                SEND_OK(soc_id)
                DELIVERY(_usr, msg, dest)


def SEND_OK(soc_id: uuid.UUID):
    main.uuid_to_socket[soc_id].send("SEND-OK\n".encode("utf-8"))

def BAD_DEST_USER(soc_id: uuid.UUID):
    main.uuid_to_socket[soc_id].send("BAD-DEST-USER\n".encode("utf-8"))

def DELIVERY(username: str, msg: str, soc_id: uuid.UUID):
    main.uuid_to_socket[soc_id].send(f"DELIVERY {username} {msg}\n".encode("utf-8"))

def IN_USE(soc_id: uuid.UUID):
    main.uuid_to_socket[soc_id].send("IN-USE\n".encode("utf-8"))

def BUSY(soc_id: uuid.UUID):
    main.uuid_to_socket[soc_id].send("BUSY\n".encode("utf-8"))

def BAD_RQST_HDR(soc_id: uuid.UUID):
    main.uuid_to_socket[soc_id].send("BAD-RQST-HDR\n".encode("utf-8"))

def BAD_RQST_BODY(soc_id: uuid.UUID):
    main.uuid_to_socket[soc_id].send("BAD-RQST-BODY\n".encode("utf-8"))

def process_received(_uuid: uuid.UUID, data: bytes):
    msg = data.decode("utf-8")
    args = msg.rsplit(' ', -1)

    if len(args) == 0:
        print("Received empty message")
        return False

    for i in range(0, len(args)):
        args[i] = args[i].removesuffix('\n')

    match args[0]:
        case "HELLO-FROM":
            HELLO_FROM(args[1], _uuid)
        case "LIST":
            LIST(_uuid)
        case "SEND":
            SEND(args[1], args[2], _uuid)
        case default:
            pass

def receive(_uuid: uuid.UUID, _socket: socket):
    buffer = bytearray(0)
    buffer_max = 4096
    with _socket:
        try:
            while 1:
                data = _socket.recv(512)
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