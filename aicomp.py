import random
import pygame
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from collections import Counter
from pokergame import *

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))

# Global variables
player_money = 1000
opponent_money = 1000
pot = 0
bet_turn = 1  # 1 for player, 2 for AI
prev_bet = 0
phase = "pre-flop"
player_hand = []
opponent_hand = []
community_cards = []
all_in = False
revealing_cards = False
player_lost = False
AI_lost = False
bet_check = 0
playerturn_running = True

# Card class to handle individual cards

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

oppenent_win=0
player_win=0

# Function to make deck #
def create_deck():
    suits = ['H', 'D', 'C', 'S']
    deck = [Card(number, suit) for suit in suits for number in range(1, 13)]
    return deck

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

    if is_flush_hand and is_straight_hand:
        if max(values) == 14 and min(values) == 10:  # Royal flush check
            return 10, values
        return 9, values  # Straight Flush

    if most_common[0][1] == 4:
        return 8, values  # Four of a kind
    try:
        if most_common[0][1] == 3 and most_common[1][1] == 2:
            return 7, values  # Full house
    except IndexError:
        pass

    if is_flush_hand:
        return 6, sorted(values, reverse=True)  # Flush
    if is_straight_hand:
        return 5, sorted(values, reverse=True)  # Straight
    if most_common[0][1] == 3:
        return 4, values  # Three of a kind
    try:
        if most_common[0][1] == 2 and most_common[1][1] == 2:
            return 3, values  # Two pair
    except IndexError:
        pass
    if most_common[0][1] == 2:
        return 2, values  # One pair
    return 1, sorted(values, reverse=True)  # High card

def compare_hands(hand1, hand2):
    rank1, values1 = get_hand_rank(hand1)
    rank2, values2 = get_hand_rank(hand2)
    
    if rank1 > rank2:
        return "Player wins!"
    elif rank2 > rank1:
        return "Opponent wins!"
    else:
        if values1 > values2:
            return "Player wins!"
        elif values2 > values1:
            return "Opponent wins!"
        else:
            return "It's a tie!"

# AI decision-making functions
def ai_decision():
    global pot, player_money, opponent_money, bet_turn, all_in, prev_bet
    full_hand = opponent_hand + community_cards
    ai_hand_rank, ai_hand_values = get_hand_rank(full_hand)

    if ai_hand_rank >= 7:
        action = "raise"
    elif ai_hand_rank == 6:
        action = "call" if random.random() > 0.3 else "raise"
    elif ai_hand_rank == 5:
        action = "call" if random.random() > 0.4 else "raise"
    elif ai_hand_rank == 4:
        action = "call" if random.random() > 0.5 else "raise"
    elif ai_hand_rank == 3:
        action = "call" if random.random() > 0.6 else "raise"
    elif ai_hand_rank == 2:
        action = "call" if random.random() > 0.7 else "fold"
    else:
        action = "fold"

    if action == "raise":
        raise_amount = calculate_ai_raise(ai_hand_rank)
        if raise_amount > opponent_money:
            raise_amount = opponent_money
            all_in = True
        pot += raise_amount
        opponent_money -= raise_amount
        prev_bet = raise_amount
    elif action == "call":
        if prev_bet <= opponent_money:
            opponent_money -= prev_bet
            pot += prev_bet
    elif action == "fold":
        AI_lost = True
        phase = "showdown"
        Showdown()

    bet_turn = 1  # Switch to player's turn
    return action

def calculate_ai_raise(hand_rank):
    if hand_rank == 9: 
        return 200
    elif hand_rank == 8: 
        return 150
    elif hand_rank == 7: 
        return 100
    elif hand_rank == 6: 
        return 75
    elif hand_rank == 5: 
        return 50
    elif hand_rank == 4: 
        return 40
    elif hand_rank == 3: 
        return 30
    elif hand_rank == 2: 
        return 20
    else:
        return 0

# Game functions
def bet_phase():
    global bet_turn
    if bet_turn == 1:
        # Player's turn (Implement player's betting logic here)
        pass
    elif bet_turn == 2:
        ai_decision()

def move_to_next_phase():
    global phase
    if phase == "pre-flop":
        phase = "flop"
    elif phase == "flop":
        phase = "turn"
    elif phase == "turn":
        phase = "river"
    elif phase == "river":
        phase = "showdown"

def Showdown():
    global revealing_cards
    revealing_cards = True
    display_hand(opponent_hand)
    print(compare_hands(player_hand + community_cards, opponent_hand + community_cards))
    ResolveGame()

def ResolveGame():
    global opponent_money, player_money, pot, revealing_cards, playerturn_running, player_lost, AI_lost
    if player_lost:
        opponent_money += pot
    else:
        player_money += pot
    pot = 0
    while revealing_cards:
        if player_lost:
            print("Opponent wins!")
        elif AI_lost:
            print("Player wins!")
        else:
            print(compare_hands(player_hand + community_cards, opponent_hand + community_cards))
        if player_money > 0 and opponent_money > 0:
            print("Next Round button...")
        else:
            print("Game Over")
            if player_money == 0:
                print("You lost")
            else:
                print("You won")
        break  # End the game

# Main game loop
def play_round():
    global player_hand, opponent_hand, community_cards, deck, phase, revealing_cards, all_in, running, player_lost, AI_lost
    deck = create_deck()
    random.shuffle(deck)
    player_hand = [Card("spades", 5), Card("hearts", 9)]  # Sample hands
    opponent_hand = [Card("diamonds", 12), Card("clubs", 11)]
    community_cards = [Card("spades", 7), Card("hearts", 8), Card("diamonds", 10)]
    print("Round starting...")
    phase = "pre-flop"
    revealing_cards = False
    all_in = False
    player_lost = False
    AI_lost = False

    while running:
        bet_phase()
        move_to_next_phase()
        print("Moving to next phase...")
        ResolveGame()

# Start the round
play_round()

# Quit Pygame when done
pygame.quit()
