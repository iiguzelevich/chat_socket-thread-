import os
import socket
import select
import sys
from dotenv import load_dotenv

load_dotenv()

server_address = (os.getenv('HOST'), int(os.getenv('PORT')))
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_server.bind(server_address)
socket_server.listen()

FOR_READ = []
FOR_WRITE = []

FOR_READ.append(socket_server)
BUFFER = {}
name_list = {}

try:
    while True:
        read_ready, write_ready, err_ready = select.select(
            FOR_READ, FOR_WRITE, [], 0
        )
        for r in read_ready:
            if r is socket_server:
                client_connection, client_address = r.accept()
                print(f'connection: {client_connection}')
                client_connection.setblocking(False)
                FOR_READ.append(client_connection)

                names = [
                    n for n in FOR_READ
                    if n is not client_connection and n is not socket_server
                ]
                greetMsg = (
                        f'hello user!\r\n users online: {str(len(names))}\n'
                )
                client_connection.send(greetMsg.encode())

            else:
                data = r.recv(1024)
                data = data.decode('utf-8')
                identifier = r.fileno()

                if data.split(':')[0] == '-my_name':
                    name_user = data[data.index(':')+1:]
                    name_list[identifier] = name_user.strip()
                elif data.strip() == '_exit':
                    for sock in FOR_READ:
                        if sock is r:
                            FOR_READ.remove(sock)
                            sock.close()
                else:
                    BUFFER[identifier] = data

                    for sock in FOR_READ:
                        if sock is not r and sock is not socket_server:
                            FOR_WRITE.append(sock)

        for w in write_ready:
            data = BUFFER[identifier]
            if data.strip():
                if identifier in name_list:
                    name = name_list.get(identifier)
                    data = (f'\r{name} >>> ' + data).encode('utf-8')
                else:
                    data = (f'{identifier} >>> ' + data).encode('utf-8')
                w.send(data)

            if w in FOR_WRITE:
                FOR_WRITE.remove(w)

except KeyboardInterrupt:
    socket_server.close()
    sys.exit()
