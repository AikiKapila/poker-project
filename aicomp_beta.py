#this is aicomp_beta
import random
import pygame
from pokergame import get_hand_rank, opponent_hand, community_cards, prev_bet, opponent_money


def eai_decision(opponent_hand, community_cards, prev_bet, opponent_money):
    """
    Makes a decision for the AI player based on current game state.
    Returns a tuple of (action, bet_amount)
    """
    print("AI deciding...")
    ai_hand_rank, _ = get_hand_rank(opponent_hand + community_cards)

    # Determine action and bet amount based on hand strength and previous bet
    action = "fold"
    bet_amount = 0
    
    if prev_bet > 1:
        if ai_hand_rank >= 7:  # Strong hand (Full house or better)
            action = "raise"
            bet_amount = min(opponent_money, max(50, prev_bet * 2))
        elif ai_hand_rank >= 4:  # Decent hand (Three of a kind or better)
            action = "call"
            bet_amount = prev_bet
        elif ai_hand_rank >= 2 and random.random() > 0.5:  # Weak hand with chance
            action = "call"
            bet_amount = prev_bet
    else:
        if ai_hand_rank >= 7:
            action = "raise"
            bet_amount = min(opponent_money, 50)
        elif ai_hand_rank >= 4:
            action = "check"
        elif ai_hand_rank >= 2 and random.random() > 0.5:
            action = "check"
    
    return action, bet_amount