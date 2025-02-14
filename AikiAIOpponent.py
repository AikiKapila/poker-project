import random
from pokergame import create_deck, draw_card, draw_hand, get_hand_rank, get_card_values, phase

class BayesianOpponentModel:
    def __init__(self, name):
        self.name = name
        self.history = {"fold": 0, "check": 0, "call": 0, "raise": 0}
        self.current_hand_actions = {"fold": 0, "check": 0, "call": 0, "raise": 0}
        self.showdown_hands = []

        #Opponent profiling
        self.total_preflop = 0
        self.folds_preflop = 0
        
        self.tightness = 0.5 #0 = Loose, 1 = Tight
        self.aggression = 0.5 #0 = Passive, 1 = Aggressive
        self.bluff_freq = 0.5 #0 = Honest, 1 = Frequent Bluffer
    
    def track_action(self, action):
        if action in self.history:
            self.history[action] += 1
            self.current_hand_actions[action] += 1
        if phase == "pre-flop":
            self.total_preflop += 1
            if action == "fold":
                self.folds_preflop += 1

    def analyze_showdown(self, hand, community_cards):
        hand_rank, final_hand_values = get_hand_rank(hand + community_cards)
        personal_hand_values = sorted(get_card_values(hand), reverse=True)
        self.showdown_hands.append((hand_rank, final_hand_values))
        if self.current_hand_actions["raise"] > 0:
            bluff_factor = 0.0
            match hand_rank:
                case 1:
                    bluff_factor += 0.05
                case 2:
                    bluff_factor += 0.02
                case 3:
                    bluff_factor -= 0.02
                case 4:
                    bluff_factor -= 0.03
                case _:
                    bluff_factor -= 0.05
            for card in hand:
                match personal_hand_values[card]:
                    case x if x <= 10:
                        bluff_factor += round(0.1/x, 2)
                    case x if x > 10:
                        bluff_factor -= 0.01*(x-10)
            self.bluff_freq = max(min(1.0, self.bluff_freq + bluff_factor), 0.0)

    def update_playstyle(self):
        if self.total_preflop > 0:
            self.tightness = self.folds_preflop / self.total_preflop
        
        total_actions = sum(self.history.values())
        if total_actions > 0:
            self.aggression = self.history["raise"] / total_actions

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

