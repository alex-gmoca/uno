import socket
import errno
import json
import sys

HEADER_LENGTH = 10

username = input("what's your name? ")
server = " the server ip"
port = 5555
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server, port))
client_socket.setblocking(False)
username = username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)
print('Waiting for other players.')
while True:
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode('utf-8').strip())
        message = (client_socket.recv(message_length).decode('utf-8'))
        if '-color-' in message:
            while True:
                try:
                    color_change = int(input(message[7:]))
                except(ValueError, IndexError):
                    print('Invalid option.')
                else:
                    color = str(color_change)
                    color = color.encode('utf-8')
                    color_header = f"{len(color):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(color_header + color)
                    break
        elif message == '-play-':
            sys.stdout.write('\a')
            play = ''
            try:
                play = int(input("Pick a card: "))
            except ValueError:
                #not proud of this
                play = 100000000000
            play = str(play)
            play = play.encode('utf-8')
            play_header = f"{len(play):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(play_header + play)
        elif message == '-end-':
            print('Thanks for playing')
            sys.exit()
        else:
            print(f'{message}')
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue
    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()