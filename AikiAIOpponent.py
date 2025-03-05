import random
from poker_utils import create_deck, draw_card, draw_hand, get_hand_rank, get_card_values

class BayesianOpponentModel:
    def __init__(self, name):
        self.opponents = {}
        self.name = name
        self.history = {"fold": 0, "check": 0, "call": 0, "raise": 0}
        self.current_hand_actions = {"fold": 0, "check": 0, "call": 0, "raise": 0}
        self.last_action = None
        self.showdown_hands = []

        #Opponent profiling
        self.total_preflop = 0
        self.folds_preflop = 0
        self.total_bet_amount = 0
        
        self.tightness = 0.5 #0 = Loose, 1 = Tight
        self.aggression = 0.5 #0 = Passive, 1 = Aggressive
        self.bluff_freq = 0.5 #0 = Honest, 1 = Frequent Bluffer

    def track_action(self, action, phase):
        if action in self.history:
            self.history[action] += 1
            self.current_hand_actions[action] += 1
            self.last_action = action
        if phase == "pre-flop":
            self.total_preflop += 1
            if action == "fold":
                self.folds_preflop += 1

    def analyze_showdown(self, hand, community_cards):
        if hand is None or community_cards is None:
            return
        hand_rank, final_hand_values = get_hand_rank(hand + community_cards)
        personal_hand_values = sorted(get_card_values(hand), reverse=True)
        self.showdown_hands.append((hand_rank, final_hand_values))
        if self.current_hand_actions["raise"] > 0:
            bluff_factor = 0.0
            match hand_rank:
                case 1:
                    bluff_factor += 0.2
                case 2:
                    bluff_factor += 0.05
                case 3:
                    bluff_factor -= 0.02
                case 4:
                    bluff_factor -= 0.05
                case _:
                    bluff_factor -= 0.1
            for value in personal_hand_values:
                if value <= 10:
                    bluff_factor += round(0.1/value, 2)
                else:
                    bluff_factor -= 0.01*(value-10)
            self.bluff_freq = max(min(1.0, self.bluff_freq + bluff_factor), 0.0)

    def update_playstyle(self):
        if self.total_preflop > 0:
            self.tightness = self.folds_preflop / self.total_preflop
        
        total_actions = sum(self.history.values())
        if total_actions > 0:
            self.aggression = self.history["raise"] / total_actions
        
        return self

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

def make_decision(hand, community_cards, opponent_model, game_state):
    win_probability = monte_carlo_simulation(hand, community_cards)
    opponent_profile = opponent_model.update_playstyle()

    pot_size = game_state["pot"]
    prev_bet = game_state["prev_bet"]
    player_money = game_state["player_money"]
    ai_money = game_state["ai_money"]

    actions = {"fold": 0.0, "check": 0.0, "call": 0.0, "raise": 0.0}

    # Initial decision making based on monte carlo win percentage #
    if win_probability < 0.3:
        actions["fold"] = 0.6
        actions["check"] = 0.3
        actions["call"] = 0.1
        actions["raise"] = 0.0
    elif win_probability < 0.5:
        actions["fold"] = 0.3
        actions["check"] = 0.4
        actions["call"] = 0.2
        actions["raise"] = 0.1
    elif win_probability < 0.7:
        actions["fold"] = 0.0
        actions["check"] = 0.3
        actions["call"] = 0.4
        actions["raise"] = 0.3
    else:
        actions["fold"] = 0.0
        actions["check"] = 0.1
        actions["call"] = 0.3
        actions["raise"] = 0.6
    
    # Adjust for Bayesian opponent model #
    if opponent_profile.tightness > 0.65:
        if opponent_model.last_action == "raise":
            actions["fold"] *= 1.3
            actions ["raise"] *= 0.7
        elif opponent_model.last_action == "call":
            actions["fold"] *= 1.1
            actions["raise"] *= 0.9
        else:
            actions["raise"] *= 1.2
    elif opponent_profile.tightness < 0.35:
        actions["fold"] *= 0.8

    if opponent_profile.aggression > 0.65:
        actions["call"] *= 1.2
        actions["fold"] *= 0.9
        if opponent_model.last_action == "check":
            actions["raise"] *= 1.2
    elif opponent_profile.aggression < 0.35:
        actions["raise"] *= 1.1
        if opponent_model.last_action == "raise":
            actions["fold"] *= 1.2
    
    if opponent_profile.bluff_freq > 0.65:
        actions["call"] *= 1.2
        actions["raise"] *= 1.1
        actions["fold"] *= 0.7
    elif opponent_profile.bluff_freq < 0.35:
        actions["call"] *= 0.8
        actions["fold"] *= 1.2
    

    # Adjustments based on pot size #
    effective_stack = min(player_money, ai_money)
    if effective_stack < pot_size * 0.5:
        actions["raise"] *= 0.6
        actions["call"] *= 1.2
    elif effective_stack > pot_size * 3:
        actions["raise"] *= 1.2
        actions["call"] *= 1.2
        actions["fold"] *= 0.8

    if pot_size + prev_bet == 0:
        pot_odds = 0
    else:
        pot_odds = (prev_bet / (pot_size + prev_bet))
    if win_probability > pot_odds:
        actions["call"] *= 1.3
    else:
        actions["fold"] *= 1.3

    # Disqualify actions when appropriate #
    if prev_bet == 0:
        actions["fold"] = 0
        actions["call"] = 0

    best_action = max(actions, key=actions.get)
    bet_size = 0

    if best_action == "raise":
        max_bet = min(game_state["player_money"], game_state["ai_money"])
        if win_probability < 0.4:
            base_bet = effective_stack * 0.2 # Small bet for weaker hands
        elif win_probability < 0.6:
            base_bet = effective_stack * 0.3  # Medium bet for decent hands
        else:
            base_bet = effective_stack * 0.5  # Large bet for strong hands
    
        # Adjust for opponent tendencies
        if opponent_model.tightness > 0.65:  # Tight opponents fold to large bets
            base_bet *= 1.2
        elif opponent_model.tightness < 0.35:  # Loose opponents call more
            base_bet *= 0.8

        bet_amount = min(base_bet, max_bet)
        bet_size = round(bet_amount)

    print(actions)

    return best_action, bet_size