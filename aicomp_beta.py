import random
import pygame
from collections import Counter
from pokergame import *  # Keeping your original game intact

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


# Card class
class Card:
    def __init__(self, number, suit):
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


# Create deck function
def create_deck():
    suits = ['H', 'D', 'C', 'S']
    return [Card(number, suit) for suit in suits for number in range(1, 14)]


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
        return 9, values  # Straight Flush

    if most_common[0][1] == 4:
        return 8, values  # Four of a Kind

    if len(most_common) >= 2 and most_common[0][1] == 3 and most_common[1][1] == 2:
        return 7, values  # Full House

    if is_flush_hand:
        return 6, sorted(values, reverse=True)  # Flush

    if is_straight_hand:
        return 5, sorted(values, reverse=True)  # Straight

    if most_common[0][1] == 3:
        return 4, values  # Three of a Kind

    if len(most_common) >= 2 and most_common[0][1] == 2 and most_common[1][1] == 2:
        return 3, values  # Two Pair

    if most_common[0][1] == 2:
        return 2, values  # One Pair

    return 1, sorted(values, reverse=True)  # High Card


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


def ai_decision():
    global pot, opponent_money, bet_turn, prev_bet, all_in
    print("AI deciding...")
    ai_hand_rank, _ = get_hand_rank(opponent_hand + community_cards)

    action = "fold"
    if ai_hand_rank >= 7:
        action = "raise"
    elif ai_hand_rank >= 4:
        action = "call"
    elif ai_hand_rank >= 2 and random.random() > 0.5:
        action = "call"

    if action == "raise":
        raise_amount = min(opponent_money, 50)
        pot += raise_amount
        opponent_money -= raise_amount
        prev_bet = raise_amount
        print("AI raises by", raise_amount)
    elif action == "call":
        call_amount = min(opponent_money, prev_bet)
        pot += call_amount
        opponent_money -= call_amount
        print("AI calls", call_amount)
    else:
        print("AI folds")
        global AI_lost
        AI_lost = True
        return "fold"

    bet_turn = 1  # Back to player turn


def bet_phase():
    global bet_turn, player_money, pot
    if bet_turn == 1:
        print("Player's turn...")
        # Simulating player action for now
        player_bet = 50
        if player_bet <= player_money:
            player_money -= player_bet
            pot += player_bet
            print(f"Player bets ${player_bet}")
        bet_turn = 2
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
    print("Moving to next phase:", phase)


def resolve_game():
    print("Game Over")
    if player_lost:
        print("Opponent wins the game!")
    elif AI_lost:
        print("Player wins the game!")
    else:
        print(compare_hands(player_hand + community_cards, opponent_hand + community_cards))


def play_round():
    global player_hand, opponent_hand, community_cards, phase, bet_turn
    deck = create_deck()
    random.shuffle(deck)
    player_hand = random.sample(deck, 2)
    opponent_hand = random.sample(deck, 2)
    community_cards = random.sample(deck[4:], 5)
    phase = "pre-flop"
    print("Round starting...")

    running = True
    while running:
        bet_phase()
        move_to_next_phase()
        if phase == "showdown":
            resolve_game()
            running = False


# Start the round
play_round()
pygame.quit()
