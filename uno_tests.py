import pytest
from uno import *


with pytest.raises(TypeError):
    card = UnoCard()

with pytest.raises(TypeError):
    card = UnoCard('black')

with pytest.raises(ValueError):
    card = UnoCard('purple', 'ace')

with pytest.raises(ValueError):
    card = UnoCard('red', 'ace')

with pytest.raises(ValueError):
    card = UnoCard('purple', 1)

with pytest.raises(ValueError):
    card = UnoCard('red', 'wildcard')

with pytest.raises(ValueError):
    card = UnoCard('black', 1)



card1 = UnoCard('red', 0)
assert repr(card1) == '<UnoCard object: red 0>'
card2 = UnoCard('red', 1)
assert repr(card2) == '<UnoCard object: red 1>'
assert card1 != card2
assert card1.color == card2.color
assert card1.card_type != card2.card_type
card3 = UnoCard('red', 0)
assert card1 == card3



card1 = UnoCard('red', 1)

card2 = UnoCard('red', 1)
assert card1.playable(card2)
card2 = UnoCard('red', 2)
assert card1.playable(card2)
card2 = UnoCard('red', 'skip')
assert card1.playable(card2)
card2 = UnoCard('green', 1)
assert card1.playable(card2)
card2 = UnoCard('green', 1)
assert card1.playable(card2)
card2 = UnoCard('red', 1)
assert card1.playable(card2)
card2 = UnoCard('black', 'wildcard')
assert card1.playable(card2)
card2 = UnoCard('black', '+4')
assert card1.playable(card2)



card1 = UnoCard('red', 1)

card2 = UnoCard('green', 2)
assert not card1.playable(card2)
card2 = UnoCard('blue', 9)
assert not card1.playable(card2)
card2 = UnoCard('yellow', 'skip')
assert not card1.playable(card2)



card1 = UnoCard('black', 'wildcard')
card1.temp_color = 'red'

card2 = UnoCard('red', 1)
assert card1.playable(card2)
card2 = UnoCard('red', 'skip')
assert card1.playable(card2)
card2 = UnoCard('black', 'wildcard')
assert card1.playable(card2)



card1 = UnoCard('black', 'wildcard')
card1.temp_color = 'red'

card2 = UnoCard('green', 1)
assert not card1.playable(card2)

card2 = UnoCard('green', 'skip')
assert not card1.playable(card2)



with pytest.raises(TypeError):
    game = UnoGame()

with pytest.raises(ValueError):
    game = UnoGame(1)

with pytest.raises(ValueError):
    game = UnoGame('foo')

card = UnoCard('red', 1)
with pytest.raises(ValueError):
    game = UnoGame(card)

with pytest.raises(ValueError):
    game = UnoGame(16)



cards = []
with pytest.raises(ValueError):
    player = UnoPlayer(cards)

cards = range(7)
with pytest.raises(ValueError):
    player = UnoPlayer(cards)

cards = [UnoCard('red', 0)]
with pytest.raises(ValueError):
    player = UnoPlayer(cards)

cards = [
    ('red', 0),
    ('red', 1),
    ('yellow', 0),
    ('yellow', 2),
    ('blue', 0),
    ('blue', 1),
]
uno_cards = [UnoCard(color, card_type) for color, card_type in cards]
uno_cards.append(1)
with pytest.raises(ValueError):
    player = UnoPlayer(cards)

cards = [
    ('red', 0),
    ('red', 1),
    ('yellow', 0),
    ('yellow', 2),
    ('blue', 0),
    ('blue', 1),
    ('black', 'wildcard'),
    ('black', '+4'),
]
uno_cards = [UnoCard(color, card_type) for color, card_type in cards]
with pytest.raises(ValueError):
    player = UnoPlayer(cards)



cards = [
    ('red', 0),
    ('red', 1),
    ('yellow', 0),
    ('yellow', 2),
    ('blue', 0),
    ('blue', 1),
    ('black', 'wildcard'),
]
uno_cards = [UnoCard(color, card_type) for color, card_type in cards]
player = UnoPlayer(uno_cards)



rc = ReversibleCycle(range(3))
a = next(rc)
assert a == 0
a = next(rc)
assert a == 1
a = next(rc)
assert a == 2
a = next(rc)
assert a == 0
a = next(rc)
assert a == 1
a = next(rc)
assert a == 2
rc.reverse()
a = next(rc)
assert a == 1
a = next(rc)
assert a == 0
rc.reverse()
a = next(rc)
assert a == 1

rc = ReversibleCycle(range(3))
rc.reverse()
a = next(rc)
assert a == 2
a = next(rc)
assert a == 1

rc = ReversibleCycle(range(3))
rc.reverse()
rc.reverse()
a = next(rc)
assert a == 0
a = next(rc)
assert a == 1



for n in range(2, 16):
    game = UnoGame(n)
    assert len(game.players) == n
    for player in game.players:
        assert isinstance(player, UnoPlayer)
        assert len(player.hand) == 7
    assert len(game.deck) == 108 - 7*n
    assert len(game.deck) > 1



game = UnoGame(2)
assert isinstance(game.current_card, UnoCard)
assert game.is_active
assert game.current_player == game.players[0]
assert game.winner is None



game = UnoGame(5, random=False)

player_0 = game.players[0]
player_1 = game.players[1]
player_2 = game.players[2]
player_3 = game.players[3]
player_4 = game.players[4]

assert game.current_player == player_0
assert game.current_card == UnoCard('yellow', 1)
assert game.winner is None
assert player_0.can_play(game.current_card)

with pytest.raises(ValueError):
    game.play(player="bob", card=0)

with pytest.raises(ValueError):
    
    game.play(player=1, card=0)

with pytest.raises(ValueError):
    
    game.play(player=0, card=0)

assert player_0.hand[1] == UnoCard('red', 1)

game.play(player=0, card=1)
assert len(player_0.hand) == 6
assert game.current_card == UnoCard('red', 1)
assert game.is_active
game.play(player=1, card=0)
game.play(player=2, card=0)
game.play(player=3, card=0)

assert len(player_4.hand) == 9
assert game.current_player == player_0

with pytest.raises(ValueError):
    game.play(player=4, card=1)

game.play(player=0, card=0)
game.play(player=1, card=0)
game.play(player=2, card=0)
game.play(player=3, card=0)
assert game.current_player == player_0

game.play(player=0, card=0)
game.play(player=1, card=0)
game.play(player=2, card=0)
game.play(player=3, card=0)
assert game.current_player == player_2

game.play(player=2, card=0)
game.play(player=1, card=0)
game.play(player=0, card=0)
game.play(player=4, card=0)
game.play(player=3, card=1)

assert not game.current_player.can_play(game.current_card)
assert game.current_player == player_2
player_2_hand_size_before = len(player_2.hand)
game.play(player=2, card=None)
player_2_hand_size_after = len(player_2.hand)
assert player_2_hand_size_after == player_2_hand_size_before + 1

game.play(player=1, card=None)
game.play(player=0, card=None)
player_3_hand_size_before = len(player_3.hand)
game.play(player=4, card=7, new_color='yellow')
player_3_hand_size_after = len(player_3.hand)
assert game.current_player == player_3
assert game.current_card._color == 'yellow'
assert player_3_hand_size_after == player_3_hand_size_before
game.play(player=3, card=1)

with pytest.raises(ValueError):
    game.play(player=2, card=3)

player_1_hand_size_before = len(player_1.hand)
game.play(player=2, card=3, new_color='red')
player_1_hand_size_after = len(player_1.hand)
assert game.current_player == player_0
assert game.current_card._color == 'red'
assert player_1_hand_size_after == player_1_hand_size_before + 4

game.play(player=0, card=0)
game.play(player=4, card=0)
game.play(player=3, card=1)
game.play(player=2, card=None)
game.play(player=1, card=0)
game.play(player=0, card=0)
game.play(player=4, card=None)
assert game.winner is None
game.play(player=3, card=0)
assert len(player_3.hand) == 0
assert not game.is_active
assert game.winner == player_3

with pytest.raises(ValueError):
    game.play(player=2, card=0)

with pytest.raises(ValueError):
    game.play(player=1, card=0)