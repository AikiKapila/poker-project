import random
from collections import Counter

# CARD CREATION #
class Card:
    def __init__(self, number, suit, image=None):
        match number:
            case 1:
                self.n = "A"
            case 11:
                self.n = "J"
            case 12:  
                self.n = "Q"
            case 13:
                self.n = "K"
            case _:
                self.n = number
        self.s = suit
        self.image = image

# Function to make deck #
def create_deck():
    suits = ['H', 'D', 'C', 'S']
    deck = [Card(number, suit) for suit in suits for number in range(1, 13)]
    return deck

# Function to draw a card from the deck #
def draw_card(deck, hand):
    if deck:
        hand.append(deck[0])
        deck.pop(0)
    else:
        return None  # Return None if the deck is empty

def draw_hand(draw_num, deck, hand):
    for i in range(draw_num):
        draw_card(deck, hand)

# Hand evaluation functions
def get_card_values(cards):
    values = []
    for card in cards:
        if card.n == "A":
            values.append(14)
        elif card.n == "K":
            values.append(13)
        elif card.n == "Q":
            values.append(12)
        elif card.n == "J":
            values.append(11)
        else:
            values.append(card.n)
    return values


def is_flush(cards):
    return len(set(card.s for card in cards)) == 1

def is_straight(cards):
    values = sorted(get_card_values(cards))
    return values == list(range(values[0], values[0] + 5))

def get_hand_rank(cards):
    values = get_card_values(cards)
    counts = Counter(values)
    most_common = counts.most_common()
    
    is_flush_hand = is_flush(cards)
    is_straight_hand = is_straight(cards)

    # Check for straight flush (flush + straight)
    if is_flush_hand and is_straight_hand:
        if max(values) == 14 and min(values) == 10:  # Royal flush check (Ace high straight flush)
            return 10, values  # Royal Flush
        return 9, values  # Straight Flush

    # Check for four of a kind
    if most_common[0][1] == 4:
        return 8, values

    # Full house: Three of a kind + pair
    try:
        if most_common[0][1] == 3 and most_common[1][1] == 2:
            return 7, values
    except IndexError:
        pass

    # Flush
    if is_flush_hand:
        return 6, sorted(values, reverse=True)

    # Straight
    if is_straight_hand:
        return 5, sorted(values, reverse=True)

    # Three of a kind
    if most_common[0][1] == 3:
        return 4, values

    # Two pair
    try:
        if most_common[0][1] == 2 and most_common[1][1] == 2:
            return 3, values
    except IndexError:
        pass

    # One pair
    if most_common[0][1] == 2:
        return 2, values

    # High card
    return 1, sorted(values, reverse=True)