import os
import socket
import threading
import sys

from dotenv import load_dotenv

load_dotenv()

server_address = (os.getenv('HOST'), int(os.getenv('PORT')))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(float(os.getenv('Timeout')))
client_socket.connect(server_address)

sys.stdout.write(
    'enter your name using the command "-my_name:",\n'
    'enter to exit - "_exit"\n')


def cl_send():
    while True:
        for line in sys.stdin:
            if '_exit' == line.rstrip("\n"):
                client_socket.send(line.encode('utf-8'))
                sys.exit()

            elif '-my_name' == line.split(':')[0] and line.split(':')[1]:
                client_socket.send(line.encode('utf-8'))

            else:
                client_socket.send(line.encode('utf-8'))


t = threading.Thread(target=cl_send)
t.start()

while True:
    data = client_socket.recv(1024).decode('utf-8')

    if not data:
        sys.stdout.write('DISCONNECTED\n')
        sys.exit()

    else:
        sys.stdout.write(data)
