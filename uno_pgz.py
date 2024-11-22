import pgzrun
from random import shuffle, choice
from itertools import product, repeat, chain
from threading import Thread
from time import sleep
from constants import COLORS, ALL_COLORS, NUMBERS, SPECIAL_CARD_TYPES
from constants import COLOR_CARD_TYPES, BLACK_CARD_TYPES, CARD_TYPES
from pgzero.actor import Actor


class UnoCard:
    def __init__(self, color, card_type) -> None:
        self._validate(color, card_type)
        self._color = color
        self.card_type = card_type
        self.temp_color = None
        self.sprite = Actor('{}_{}'.format(color, card_type))
        
    def __repr__(self) -> str:
        return'<UnoCard object: {} {}>'.format(self.color, self.card_type)
    
    def __str__(self) -> str:
        return '{} {}'.format(self.color_short, self.card_type_short)
    
    def __format__(self, f) -> str:
        if f == 'full':
            return'{}{}'.format(self.color, self.card_type)
        else:
            return str(self)
        
    def __eq__(self, other) -> bool:
        return self.color == other.color and self.card_type == other.card_type
    
    def _validate(self, color, card_type):
        if color not in ALL_COLORS:
            raise ValueError('Invalid color')
        if color == 'black' and card_type not in BLACK_CARD_TYPES:
            raise ValueError('Invalid card type')
        if color != 'black' and card_type not in COLOR_CARD_TYPES:
            raise ValueError('Invalid card type')
        

    @property
    def color(self):
        return self.temp_color if self.temp_color else self._color
    
    @color.setter
    def color(self, value):
        self._color = value
    
    @property
    def color_short(self):
        return self.color[0].upper()
    
    @property
    def card_type_short(self):
        if self.card_type in ('skip', 'reverse', 'wildcard'):
            return self.card_type[0].upper()
        else:
            return self.card_type
        
    
    @property
    def temp_color(self):
        return self._temp_color
    
    @temp_color.setter
    def temp_color(self, color):
        if color is not None:
            if color not in COLORS:
                raise ValueError('Invalid color')
        self._temp_color = color
        
    def playable(self, other):
        return (
            self._color == other.color or
            self.card_type == other.card_type or
            other.color == 'black'
        )
        

class UnoPlayer:
    def __init__(self, cards, player_id=None) -> None:
        if len(cards) !=7:
            raise ValueError(
                'Invalid player: must be initalised with 7 UnoCards'
            )
        if not all(isinstance(card, UnoCard) for card in cards):
            raise ValueError(
                'Invalid player: cards must all be UnoCard object'
            )
        self.hand = cards
        self.player_id = player_id
        
    def __repr__(self) -> str:
        if self.player_id is not None:
            return '<UnoPlayer object: player {}>'.format(self.player_id)
        else:
            return '<UnoPlayer object>'
        
    def __str__(self) -> str:
        if self.player_id is not None:
            return str(self.player_id)
        else:
            return repr(self)
    
    def can_play(self, current_card):
        return any(current_card.playable(card) for card in self.hand)
    

class ReversibleCycle:
    def __init__(self, iterable) -> None:
        self._item = list(iterable)
        self._pos = None
        self._reverse = False
        
    def __next__(self):
        if self.pos is None:
            self.pos = 0 if not self._reverse else -1
        else:
            self.pos = (self.pos + self._delta) % len(self._item)
        return self._item[self.pos]
    
    @property
    def _delta(self):
        return -1 if self._reverse else 1
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        self._pos = value % len(self._item)

    def reverse(self):
        self._reverse = not self._reverse
    

class UnoGame:
    def __init__(self, players, random=True) -> None:
        if not isinstance(players, int):
            raise ValueError('Invalid game: players must be integer')
        if not 2 <= players <= 15:
            raise ValueError('Invalid game: must be between 2 and 15 players')
        self.deck = self._create_deck(random=random)
        self.players = [
            UnoPlayer(self._deal_hand(), n) for n in range(players)
        ]
        self._player_cycle = ReversibleCycle(self.players)
        self._current_player = next(self._player_cycle)
        self._winner = None
        self._check_first_card()
        
    def __next__(self):
        self._current_player = next(self._player_cycle)
        
    def _create_deck(self, random):
        color_cards = product(COLORS, COLOR_CARD_TYPES)
        black_cards = product(repeat('black', 4), BLACK_CARD_TYPES)
        all_cards = chain(color_cards, black_cards)
        deck = [UnoCard(color, card_type) for color, card_type in all_cards]
        if random:
            shuffle(deck)
            return deck
        else:
            return list(reversed(deck))
        
    def _deal_hand(self):
        return [self.deck.pop() for i in range(7)]
    
    @property
    def current_card(self):
        return self.deck[-1]
    
    @property
    def is_active(self):
        return all(len(player.hand) > 0 for player in self.players) #burda player idi
    
    @property
    def current_player(self):
        return self._current_player
    
    @property
    def winner(self):
        return self._winner
    
    def play(self, player, card=None, new_color=None):
        if not isinstance(player, int):
            raise ValueError('Invalid player: should be the index number')
        if not 0 <= player < len(self.players):
            raise ValueError('Invalid player: index out of range')
        _player = self.players[player]
        if self.current_player != _player:
            raise ValueError('Invalid player: not their turn')
        if card is None:
            self._pick_up(_player, 1)
            next(self)
            return
        _card = _player.hand[card]
        if not self.current_card.playable(_card):
            raise ValueError(
                'Invalid card: {} not playable on {}'.format(
                    _card, self.current_card
                )
            )
        if _card.color == 'black':
            if new_color not in COLORS:
                raise ValueError(
                    'Invalid new_color: must be red, yellow, green or blue'
                )
        if not self.is_active:
            raise ValueError('GAME OVER')
        
        player_card = _player.hand.pop(card)
        self.deck.append(player_card)
        
        card_color = player_card.color
        card_type = player_card.card_type
        if card_color == 'black':
            self.current_card.temp_color = new_color
            if card_type == '+4':
                next(self)
                self._pick_up(self.current_player, 4)
        elif card_type == 'reverse':
            self._player_cycle.reverse()
        elif card_type == 'skip':
            next(self)
        elif card_type == '+2':
            next(self)
            self._pick_up(self.current_player, 2)
            
        if self.is_active:
            next(self)
        else:
            self._winner =_player
            self._print_winner()
    
    def _print_winner(self):
        if self.winner.player_id:
            winner_name = self.winner.player_id
        else:
            winner_name = self.players.index(self.winner)
        print("Player {} wins!".format(winner_name))
        
    def _pick_up(self, player, n):
        penalty_cards = [self.deck.pop(0) for i in range(n)]
        player.hand.extend(penalty_cards)
        
    def _check_first_card(self):
        if self.current_card.color == 'black':
            color = choice(COLORS)
            self.current_card.temp_color = color
            print("Selected random color for black card: {}".format(color))


class GameData:
    def __init__(self) -> None:
        self.selected_card = None
        self.selected_color = None
        self.color_selected_required = False
        self.log = ''
        
    @property
    def currect_card(self):
        if not self.deck:
            return None
        return self.deck[-1]
    
    @property
    def selected_card(self):
        selected_card = self._selected_card
        self.selected_card = None
        return selected_card
    
    @selected_card.setter
    def selected_card(self,value):
        self._selected_card = value
        
    @property
    def selected_color(self):
        selected_color = self._selected_color
        self.selected_color = None
        return selected_color
    
    @selected_color.setter
    def selected_color(self, value):
        self._selected_color = value
        
        
game_data = GameData()

    
class AIUnoGame:
    def __init__(self, players) -> None:
        self.game = UnoGame(players)
        self.player = choice(self.game.players)
        self.player_index = self.game.players.index(self.player)
        print('The game begins. You are Player {}'.format(self.player_index))
        
    def __next__(self):
        game = self.game
        player = game.current_player
        player_id = player.player_id
        current_card = game.current_card
        
        if current_card is not None:
            current_card.sprite.pos = (210, 70)
            # current_card.sprite.draw()
        else:
            print("No current card avaliable (deck might be empty).")
            
        if player == self.player:
            player = False
            while not player:
                card_index = None
                while card_index is None:
                    card_index = game_data.selected_card
                new_color = None
                if card_index is not False:
                    card = player.hand[card_index]
                    if not game.current_card.playable(card):
                        game_data.log = 'You cannot play that card'
                        continue
                    else:
                        game_data.log = 'You played card {:full}'.format(card)
                        if card.color == 'black' and len(player.hand) > 1:
                            game_data.color_selected_required = True
                            while new_color is not None: 
                                new_color = game_data.selected_color
                            game_data.log = 'You selected {}'.format(new_color)
            else:
                card_index = None
                game_data.log = 'You picked up'
            game.play(player_id, card_index, new_color)
            player = True
        elif player.can_play(game.current_card):
            for i, card in enumerate(player.hand):
                if game.current_card.playable(card):
                    if card.color == 'black':
                        new_color = choice(COLORS)
                    else:
                        new_color = None
                    game_data.log = "Player {} played {:full}".format(player, card)
                    game.play(player=player_id, card=i, new_color=new_color)
                    break
        else:
            game_data.log = "Player {} picked up".format(player)
            game.play(player=player_id, card=None)
            
            
    def print_hand(self):
        print('Your hand: {}'.format(
            ' '.join(str(card) for card in self.player.hand)
        ))
        
        
# num_players = 3
# game = AIUnoGame(num_players)

def game_loop(self):
    if not isinstance(self, AIUnoGame):
        raise TypeError("Expected an AIUnoGame instance!")
    while self.game.is_active:
        sleep(1)
        next(self)


num_players = 3
game = AIUnoGame(num_players)
game_loop_thread = Thread(target=game_loop, args=(game,))
game_loop_thread.start()

WIDTH = 1200
HEIGHT = 800

deck_img = Actor('back')
color_imgs = {color: Actor(color) for color in COLORS}

try:
    sprite = Actor('back')
except Exception as e:
    print(f"Error loading sprite: {e}")


def draw_deck():
    deck_img.pos = (130, 70)
    if deck_img:
        deck_img.draw()
    else:
        print("Error: deck image is None!")
    
    current_card = game.game.current_card
    if current_card.sprite is not None:
        current_card.sprite.pos = (210, 70)
        current_card.sprite.draw()
    else:
        print("Error: current card sprite is None!")
        
    if game_data.color_selected_required:
        for i, card in enumerate(color_imgs.values()):
            if card:
                card.pos = (290 + i * 80, 70)
                card.draw()
            else:
                print(f"Error: color card {i} is None!")
    elif current_card.color == 'black' and current_card.temp_color is not None:
        color_img = color_imgs[current_card.temp_color]
        if color_img:
            color_img.pos = (290, 70)
            color_img.draw()
        else:
            print("Error: color image not found for black card color!")
        
def draw_players_hands():
    for p, player in enumerate(game.game.players):
        color = 'red' if player == game.game.current_player else 'black'
        text = 'P{} {}'.format(p, 'wins' if game.game.winner == player else '')
        pgzrun.screen.draw.text(text, (0, 300 + p * 130), fontsize=100, color=color)
        for c, card in enumerate(player.hand):
            if player == game.player:
                sprite = card.sprite
            else:
                sprite = Actor('back')
            sprite.pos = (130 + c * 80, 330 + p * 130)
            sprite.draw()
    
def show_log():
    pgzrun.screen.draw.text(game_data.log, midbottom=(WIDTH/2, HEIGHT-50), color='black')
        
def update():
    pgzrun.screen.clear()
    pgzrun.screen.fill((255, 255, 255))
    draw_deck()
    draw_players_hands()
    show_log()
    
def on_mouse_down(pos):
    if game.player == game.game.current_player:
        for card in game.player.hand:
            if card.sprite.collidepoint(pos):
                game_data.selected_card = game.player.hand.index(card)
                print('Selected card {} index {}'.format(card, game.player.hand.index(card)))
        if deck_img.collidepoint(pos):
            game_data.selected_card = False
            print('Selected pick up')
        for color, card in color_imgs.items():
            if card.collidepoint(pos):
                game_data.selected_color = color
                game_data.color_selected_required = False
# pgzrun.go(draw_deck)
# pgzrun.go(draw_players_hands)
# pgzrun.go(show_log)
# pgzrun.go(update)
# pgzrun.go(on_mouse_down)