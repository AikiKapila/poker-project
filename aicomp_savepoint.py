#this is aicomp_beta
import random
import pygame
from collections import Counter

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
        if max(values) == 14 and min(values) == 10:  # Royal flush check
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
    
    return 0  # No significant draws

def monte_carlo_simulation(player_hand, community_cards, deck, num_simulations=1000):
    wins = 0
    for _ in range(num_simulations):
        # Simulate remaining community cards
        simulated_community = community_cards.copy()
        remaining_deck = [card for card in deck if card not in player_hand + community_cards]
        random.shuffle(remaining_deck)
        simulated_community += remaining_deck[:5 - len(community_cards)]

        # Simulate opponent's hand
        opponent_hand = remaining_deck[5 - len(community_cards):7 - len(community_cards)]

        # Compare hands
        player_rank, _ = get_hand_rank(player_hand + simulated_community)
        opponent_rank, _ = get_hand_rank(opponent_hand + simulated_community)
        if player_rank > opponent_rank:
            wins += 1
        elif player_rank == opponent_rank:
            wins += 0.5  # Split pot

    return wins / num_simulations  # Probability of winning


def eai_decision(opponent_hand, community_cards, prev_bet, opponent_money, deck):
    """
    Makes a decision for the AI player based on current game state.
    Returns a tuple of (action, bet_amount)
    """
    print("AI deciding...")
    ai_hand_rank, _ = get_hand_rank(opponent_hand + community_cards)
    win_probability = monte_carlo_simulation(opponent_hand, community_cards, deck)

    # Determine action and bet amount based on hand strength and win probability
    action = "fold"
    bet_amount = 0
    
    if win_probability > 0.7:  # Strong hand
        action = "raise"
        bet_amount = min(opponent_money, max(50, prev_bet * 2))
    elif win_probability > 0.5:  # Decent hand
        if prev_bet > 0:
            action = "call"
            bet_amount = prev_bet
        else:
            action = "check"
    elif win_probability > 0.3 and random.random() > 0.5:  # Weak hand with chance
        if prev_bet > 0:
            action = "call"
            bet_amount = prev_bet
        else:
            action = "check"

    return action, bet_amount
    