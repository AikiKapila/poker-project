import random
from pokergame import create_deck, draw_card, draw_hand, get_hand_rank

class BayesianOpponentModel:
    def __init__(self, name):
        self.name = name
        self.history = {"fold": 0, "check": 0, "call": 0, "raise": 0}

        #Opponent profiling
        self.hands_seen_preflop = 0
        self.hands_played_preflop = 0
        
        self.tightness = 0.5 #0 = Loose, 1 = Tight
        self.aggression = 0.5 #0 = Passive, 1 = Aggressive
        self.bluff_freq = 0.5 #0 = Honest, 1 = Frequent Bluffer
    
    def update_playstyle(self):
        pass

def monte_carlo_simulation(ai_hand, community_cards, num_opponents=3, num_simulations=10000):
    wins = 0
    total_simulations = num_simulations

    # Simulate "num_simulations" games
    for _ in range(total_simulations):
        # Randomly shuffle remaining deck
        deck = create_deck()
        deck = remove_known_cards(deck, ai_hand + community_cards)
        random.shuffle(deck)

        #Deal community cards
        simulated_community_cards = community_cards.copy()
        while len(simulated_community_cards) < 5:
            draw_card(deck, simulated_community_cards)
    
        #Deal random hands to opponents
        simulated_opponent_hands = []
        for i in range(num_opponents):
            opponent_hand = []
            draw_hand(2, deck, opponent_hand)
            simulated_opponent_hands.append(opponent_hand)

        #Evaluate outcome
        won_all = True
        ai_rank, ai_values = get_hand_rank(ai_hand)
        for opponent in range(num_opponents):
            opponent_rank, opponent_values = get_hand_rank(simulated_opponent_hands[opponent])
            if opponent_rank > ai_rank or (opponent_rank==ai_rank and opponent_values > ai_values):
                won_all = False
                break
        if won_all:
            wins += 1
    
    return wins / num_simulations

def remove_known_cards(deck, known_cards):
    remaining_deck = set(deck) - set(known_cards)
    return list(remaining_deck)

