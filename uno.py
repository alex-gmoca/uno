import random
from termcolor import colored

COLORS = ['red', 'green', 'yellow', 'blue']

def uniqueid():
    seed = random.getrandbits(32)
    while True:
       yield seed
       seed += 1

class Card():
    def __init__(self, color, number, action):
        unique_sequence = uniqueid()
        self.id = next(unique_sequence)
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
    def __init__(self, name):
        self.name = name
        self.cards = []

    def get_current_cards(self):
        return self.cards

    def play_card(self, current_card, playable_card):
        try:
            if self.cards[playable_card].color is None and self.cards[playable_card].number is None:
                return self.cards.pop(playable_card)
            if self.cards[playable_card].number is None and current_card.color == self.cards[playable_card].color:
                return self.cards.pop(playable_card)
            if current_card.color == self.cards[playable_card].color or current_card.number == self.cards[playable_card].number:
                return self.cards.pop(playable_card)
            else:
                print('Invalid Play')
                return False
        except IndexError:
            print('Invalid option')
            return False

def start_game():
    end_game = False
    jugadores = PlayerTurns()
    while True:
        try:
            num_jug = int(input('How many players?: '))
        except(ValueError):
            print('Invalid option.')
        else:
            if num_jug > 1:
                break
    for j in range(0, num_jug):
        jug_name = input(f'Name of player {j+1}: ')
        jugadores.add_player(Player(jug_name))
    turnos = iter(jugadores)
    cartas = Deck()
    cartas_a_repartir = cartas.deal_cards(jugadores.number_of_players())
    for jugador in range(0,jugadores.number_of_players()):
        jugadores.data[jugador].cards = cartas_a_repartir.pop()
    current_player = next(turnos)
    while(not end_game):
        card_drawed = None
        print('Current card: ')
        print(cartas.get_current_card())
        print('---------------')
        print(f"{current_player.name}'s turn:")
        current_player_cards = current_player.get_current_cards()
        for x in range(0,len(current_player_cards)):
            print(f'{x}. {current_player_cards[x]}')
        print(f'{x+1}. Draw a card')
        valid_play = False
        while not valid_play:
            try:
                play = int(input("Pick a card: "))
            except ValueError:
                #not proud of this
                play = 100000000000
            if play == x+1:
                card_drawed = cartas.draw_a_card()
                if card_drawed:
                    current_player.cards.append(card_drawed)
                    valid_play = True
            else:
                the_card = current_player.play_card(cartas.get_current_card(),play)
                if the_card:
                    if the_card.action and 'Change' in the_card.action:
                        while True:
                            try:
                                color_change = int(input("Choose a color: \n\r0. red\n\r1. green\n\r2. yellow\n\r3. blue\n\r"))
                                the_card.color = COLORS[color_change]
                            except(ValueError, IndexError):
                                print('Invalid option.')
                            else:
                                break
                    cartas.update_current_card(the_card)
                    valid_play = True
        if len(current_player.get_current_cards()) == 0:
            end_game = True
            winner = current_player
        print('\n\r')
        print('\n\r')
        if card_drawed:
            current_player = next(turnos)
        elif cartas.get_current_card().action == 'Change color':
            current_player = next(turnos)
        elif cartas.get_current_card().action == 'Reverse':
            jugadores.change_direction(turnos)
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
    print(f'The winner is {winner.name}!')

start_game()




