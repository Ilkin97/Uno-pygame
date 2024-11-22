from random import shuffle, choice
from itertools import product, repeat, chain
from constants import COLORS, ALL_COLORS, NUMBERS, SPECIAL_CARD_TYPES
from constants import COLOR_CARD_TYPES, BLACK_CARD_TYPES, CARD_TYPES


class UnoCard:
    def __init__(self, color, card_type) -> None:
        self._validate(color, card_type)
        self.color = color
        self.card_type = card_type
        self.temp_color = None
        
    def __repr__(self) -> str:
        return '<UnoCard object: {} {}>'.format(self.color, self.card_type)
    
    def __str__(self) -> str:
        return '{}{}'.format(self.color_short, self.card_type_short)
    
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
    def color_short(self):
        return self.color[0].upper()
    
    @property
    def card_type_short(self):
        if self.card_type in ('skip', 'reverse', 'wildcard'):
            return self.card_type[0].upper()
        else:
            return self.card_type
    
    @property
    def _color(self):
        return self.temp_color if self.temp_color else self. color
    
    @property
    def temp_color(self):
        return self._temp_color
    
    @temp_color.setter
    def temp_color(self, color):
        if color is not None:
            if color is not COLORS:
                raise ValueError('Invalid color')
        self._temp_color = color
    
    def playable(self, other):
        return(
            self._color == other.color or
            self.card_type == other.card_type or
            other.color == 'black'
        )


class UnoPlayer:
    def __init__(self, cards, player_id=None) -> None:
        if len(cards) != 7:
            raise ValueError(
                'Invalid player: must be initalised with 7 UnoCards'
            )
        if not all(isinstance(card, UnoCard) for card in cards):
            raise ValueError(
                'Invalid player: cards must all be UnoCards object'
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
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.pos is None:
            self.pos = -1 if self._reverse else 0 
        else:
            self.pos = self.pos + self._delta
        return self._items [self.pos]
    
    @property
    def _delta(self):
        return -1 if self._reverse else 1
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        self._pos = value % len(self._items)
        
    def reverse(self):
        self._reverse = not self._reverse
 
       
class UnoGame:
    def __init__(self, players, random=True) -> None:
        if not isinstance(players, int):
            raise ValueError('Invalid game: players must be integer')
        if not 2 <= players <= 15:
            raise ValueError('Invalid game: must be between 2 and 15 players')

        self.deck = self._create_deck(random)
        self.players = [
            UnoPlayer(self._deal_hand(), n) for n in range(players)
        ]
        self._player_cycle = ReversibleCycle(self.players)
        self._current_player = next(self._player_cycle)  # current yazımı düzeltildi
        self._winner = None

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
        return all(len(player.hand) > 0 for player in self.players)
    
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
            raise ValueError('Game is over')
        
        played_card = _player.hand.pop(card)
        self.deck.append(played_card)
        
        card_color = played_card.color
        card_type = played_card.card_type
        if card_color == 'black':
            self.current_card.temp_color =new_color
            if card_type == '+4':
                next(self)
                self._pick_up(self.current_player, 4)
        elif card_type == 'reverse':
            self._player_cycle._reverse()
        elif card_type == 'skip':
            next(self)
        elif card_type == '+2':
            next(self)
            self._pick_up(self.current_player, 2)
            
        if self.is_active:
            next(self)
        else:
            self_winner = _player
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
        

class AIUnoGame:
    def __init__(self, players) -> None:
        self.game = UnoGame(players)
        self.player = choice(self.game.players)
        self.player_index = self.game.players.index(self.player)
        print('The game begins. You are Player {}.'.format(self.player_index))
        self.print_hand()
        while self.game.is_active:
            print()
            next(self)
            
    def __next__(self):
        game = self.game
        player = game.current_player
        player_id = player.player_id
        current_card = game.current_card
        if player == self.player:
            print('Current card: {}, color: {}'.format(
                game.current_card, game.current_card._color
            ))
            self.print_hand()
            if player.can_play(current_card):
                played = False
                while not played:
                    card_index = int(input('Which card do you wnat to play? >> '))
                    card = player.hand[card_index]
                    if not game.current_card.playable(card):
                        print('Cannot play taht card')
                    else:
                        if card.color == 'black':
                            new_color = input('Which color do you want? >> ')
                        else:
                            new_color = None
                        game.play(player_id, card_index, new_color)
                        played = True
            else:
                print('You cannot play. You must pick up a card.')
                game.play(player_id, card=None)
                self.print_hand()
        elif player.can_play(game.current_card):
            for i, card in enumerate(player.hand):
                if game.current_card.playable(card):
                    if card.color == 'black':
                        new_color = choice(COLORS)
                    else:
                        new_color = None
                    print("Player {} played {}".format(player, card))
                    game.play(player=player_id, card=i, new_color=new_color)
                    break
        else:
            print("Player {} picked up".format(player))
            game.play(player=player_id, card=None)
    
    def print_hand(self):
        print('Your hand: {}'.format(
            ' '.join(str(card) for card in self.player.hand)
        ))