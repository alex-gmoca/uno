import random
import select
import socket
from termcolor import colored

COLORS = ['red', 'green', 'yellow', 'blue']
HEADER_LENGTH = 10

server = "the server ip"
port = 5555
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server, port))
server_socket.listen()
sockets_list = [server_socket]

class Card():
    def __init__(self, color, number, action):
        self.color = color
        self.number = number
        self.action = action
        
    def __repr__(self):
        if self.number or self.number == 0:
            return colored(f'{self.number}',self.color)
        elif self.color:
            return colored(f'{self.action}',self.color)
        else:
            return colored(f'{self.action}','cyan')

class Deck():
    def __init__(self):
        self.current_card = None
        self.cards = []
        self.pile = []
        for color in COLORS:
            self.cards.append(Card(color,0, None))
            for x in range(1,10):
                self.cards.append(Card(color, x, None))
                self.cards.append(Card(color, x, None))
            for x in range(0,2):
                self.cards.append(Card(color, None, 'Take 2'))
                self.cards.append(Card(color, None, 'Reverse'))
                self.cards.append(Card(color, None, 'Skip'))
        for x in range(0,4):
            self.cards.append(Card(None, None, 'Change color'))
            self.cards.append(Card(None, None, 'Take 4 Change Color'))
        random.shuffle(self.cards)

    def how_many_cards(self):
        return len(self.cards)

    def draw_a_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            self.cards = self.pile
            random.shuffle(self.cards)
            self.pile = []
            return self.cards.pop()

    def deal_cards(self, number_of_players):
        player_cards = []
        for x in range(0,number_of_players):
            player_cards.append(self.cards[0:7])
            self.cards = self.cards[7:]
        self.current_card = self.cards.pop()
        while self.current_card.number is None:
            self.add_card_to_pile(self.current_card)
            self.current_card = self.cards.pop()
        return player_cards

    def get_current_card(self):
        return self.current_card
    
    def add_card_to_pile(self, card):
        if card.action and 'Change' in card.action:
            card.color = None
        self.pile.append(card)
    
    def update_current_card(self, card):
        self.add_card_to_pile(self.current_card)
        self.current_card = card

class PlayerIterator:
    def __init__(self, players):
       self._players = players
       self._index = 0

    def __next__(self):
        if self._players.direction:
            if self._index >= len(self._players.data):
                self._index = 0
            result = self._players.data[self._index]
            self._index += 1
            return result
        else:
            if self._index < 0:
                self._index = len(self._players.data)-1
            result = self._players.data[self._index]
            self._index -= 1
            return result

    def whos_next(self):
        aux = self._index
        if self._players.direction:    
            if self._index >= len(self._players.data):
                aux = 0
            result = self._players.data[aux]
            return result
        else:
            if self._index < 0:
                aux = len(self._players.data)-1
            result = self._players.data[aux]
            return result

class PlayerTurns():
    def __init__(self):
        self.data = []
        self.direction = True
    
    def add_player(self, player):
        self.data.append(player)
    
    def number_of_players(self):
        return len(self.data)

    def change_direction(self, iterator):
        self.direction = not self.direction
        if self.direction:
            iterator._index += 2
        else:
            iterator._index -= 2

    def __iter__(self):
        return PlayerIterator(self)

class Player():
    def __init__(self, name, player_socket):
        self.name = name
        self.cards = []
        self.socket = player_socket

    def how_many_cards_left(self):
        return len(self.cards)

    def get_current_cards(self):
        return self.cards

    def play_card(self, current_card, playable_card):
        try:
            #actions with no color
            if self.cards[playable_card].number is None and self.cards[playable_card].color is None: 
                return self.cards.pop(playable_card)
            #actions with the same color
            if self.cards[playable_card].number is None and current_card.color == self.cards[playable_card].color:
                return self.cards.pop(playable_card)
            #sameaction different color
            if self.cards[playable_card].number is None and current_card.action == self.cards[playable_card].action:
                return self.cards.pop(playable_card)
            #normal numbers
            if self.cards[playable_card].number is not None:
                if current_card.color == self.cards[playable_card].color or current_card.number == self.cards[playable_card].number:
                    return self.cards.pop(playable_card)
            else:
                return False
        except IndexError:
            return False

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except Exception as e:
        print(e)
        return False

def send_message(client_socket, message):
    try:
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
    except Exception as e:
        print(e)
        return False

def start_game():
    end_game = False
    jugadores = PlayerTurns()
    clients = {}
    while True:
        try:
            num_jug = int(input('How many players?: '))
        except(ValueError):
            print('Invalid option.')
        else:
            if num_jug > 1:
                break
    while len(clients) < num_jug:
        print('Waiting for players to join ...')
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if user is False:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('New player has entered {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
                jugadores.add_player(Player(user['data'].decode('utf-8'), client_socket))
    turnos = iter(jugadores)
    cartas = Deck()
    cartas_a_repartir = cartas.deal_cards(jugadores.number_of_players())
    for jugador in range(0,jugadores.number_of_players()):
        jugadores.data[jugador].cards = cartas_a_repartir.pop()
    current_player = next(turnos)
    while(not end_game):
        card_drawed = None
        #envia a todos la carta actual y de quien es el turno
        for client_socket in clients:
            send_message(client_socket, 'Current card:')
            send_message(client_socket, '--------------------')
            send_message(client_socket, f'|{cartas.get_current_card().__repr__():^27}|')
            send_message(client_socket, '--------------------')
            send_message(client_socket, f"{current_player.name}'s turn, {current_player.how_many_cards_left()} cards left... Next turn will be {turnos.whos_next().name}")
            current_player_cards = current_player.get_current_cards()
        #envia al jugador del turno sus cartas y la notificacion de q es su turno
        send_message(current_player.socket, '0. Draw a card')
        for x in range(0,len(current_player_cards)):
            send_message(current_player.socket, f'{x+1}. {current_player_cards[x].__repr__()}')
        valid_play = False
        while not valid_play:
            send_message(current_player.socket, '-play-')
            play = receive_message(current_player.socket)
            play = int(play['data'])
            if play == 0:
                card_drawed = cartas.draw_a_card()
                if card_drawed:
                    current_player.cards.append(card_drawed)
                    valid_play = True
                    for client_socket in clients:
                        if client_socket != current_player.socket:
                            send_message(client_socket, f'{current_player.name} draw a card!')
            else:
                the_card = current_player.play_card(cartas.get_current_card(),play-1)
                if the_card:
                    if the_card.action and 'Change' in the_card.action:
                        color_text = colored("0. red\n\r",'red')
                        color_text += colored("1. green\n\r",'green')
                        color_text += colored("2. yellow\n\r",'yellow')
                        color_text += colored("3. blue\n\r",'blue')
                        color_text += "Choose a color: "
                        send_message(current_player.socket, '-color-' + color_text)
                        send_message(current_player.socket, color_text)
                        color_change = receive_message(current_player.socket)
                        color_change = int(color_change['data'])
                        the_card.color = COLORS[color_change]
                    cartas.update_current_card(the_card)
                    valid_play = True
                else:
                    send_message(current_player.socket, 'Invalid play/option.')
        if len(current_player.get_current_cards()) == 0:
            end_game = True
            winner = current_player
        if card_drawed:
            current_player = next(turnos)
        elif cartas.get_current_card().action == 'Change color':
            current_player = next(turnos)
        elif cartas.get_current_card().action == 'Reverse':
            jugadores.change_direction(turnos)
            current_player = next(turnos)
            if num_jug == 2:
                current_player = next(turnos)    
        elif cartas.get_current_card().action == 'Skip':
            current_player = next(turnos)
            current_player = next(turnos)
        elif cartas.get_current_card().action and 'Take' in cartas.get_current_card().action:
            current_player = next(turnos)
            punishment = cartas.get_current_card().action.split()
            for i in range(0, int(punishment[1])):
                card_drawed = cartas.draw_a_card()
                if card_drawed:
                    current_player.cards.append(card_drawed)
            current_player = next(turnos)
        else:
            current_player = next(turnos)
        #print(f'la pila: {cartas.pile}')
    for client_socket in clients:
        send_message(client_socket, 'Current card:')
        send_message(client_socket, '--------------------')
        send_message(client_socket, f'|{cartas.get_current_card().__repr__():^27}|')
        send_message(client_socket, '--------------------')
        send_message(client_socket, f'The winner is {winner.name}!!')
        send_message(client_socket, '-end-')
start_game()







