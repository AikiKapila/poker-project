import pygame
import random
import math
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from collections import Counter


# Pygame Set Up #
pygame.init()
screen_width = 1400
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Poker Game')
        
def display_text(screen, text, value, coordinates, font_size=24, color=(255, 255, 255)):
    """
    Displays text with a value on the Pygame screen.

    Args:
        screen: The Pygame display surface.
        text (str): The label or text to display.
        value (any): The value to display alongside the text.
        coordinates (tuple): The (x, y) position to render the text.
        font: A Pygame font object.
        color (tuple): RGB color of the text (default is white).
    """
    font = pygame.font.Font(None, font_size)
    
    # Combine the text and value
    if value != False:
        full_text = f"{text}: {value}"
    else:
        full_text = f"{text}"
    # Render the text
    text_surface = font.render(full_text, True, color)
    # Get the rectangle of the text surface
    text_rect = text_surface.get_rect()
    # Set the rectangle's top-left corner to the given coordinates
    text_rect.topleft = coordinates
    # Blit the text surface onto the screen
    screen.blit(text_surface, text_rect)

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

opponent_win = 0
player_win = 0

# Attaching Card Images to Names #
def load_card_images(cards):
    for card in cards:
        card_image_file = f"{card.n}_{card.s}.png"
        try:
            card.image = pygame.image.load(card_image_file)
        except pygame.error as e:
            print(f"Error loading image {card_image_file}: {e}")

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

def display_card(card, index, total_cards, hand):
    global revealing_cards
    card_image = card.image
    if hand == player_hand:
        hand_pos = 9
        hand_x = 0
        hand_rotated = False
    elif hand == opponent_hands[0]:
        hand_pos = 3
        hand_x = 0
        hand_rotated = True
        if not revealing_cards:
            card_image = pygame.image.load(f"card-back.jpg")
    elif hand == opponent_hands[1]:
        hand_pos = 3
        hand_x = 500
        hand_rotated = False
        if not revealing_cards:
            card_image = pygame.image.load(f"card-back.jpg")
    elif hand == opponent_hands[2]:
        hand_pos = 6
        hand_x = 500
        hand_rotated = True
        if not revealing_cards:
            card_image = pygame.image.load(f"card-back.jpg")
    elif hand == community_cards:
        hand_pos = 6
        hand_x = 0
        hand_rotated = False

    else:
        print("bruh (check display_card)")

    if card.image:
        card_width = 120
        card_height = 180

        scaled_image = pygame.transform.scale(card_image, (card_width, card_height))

        spacing = 20
        total_width = total_cards * card_width + (total_cards - 1) * spacing
        start_x = (screen_width - total_width) // 2 + hand_x
        x_position = start_x + index * (card_width + spacing)
        y_position = screen_height * hand_pos // 10 - card_height

        # Debugging #
        #print(f"Card {card.n}{card.s} at position ({x_position}, {y_position})")

        screen.blit(scaled_image, (x_position, y_position))

def display_hand(hand):
    for index, card in enumerate(hand):
        display_card(card, index, len(hand), hand)

def display_chips(pile, x, y):
    chips = pygame.image.load(f"pile-of-chips.webp")
    original_width, original_height = chips.get_size()
    chips_width = original_width * 0.15
    chips_height = original_height * 0.15
    scaled_image = pygame.transform.scale(chips, (chips_width, chips_height))
    rows = 1
    while (rows * (rows + 1)) // 2 * 100 <= pile:
        rows += 1
    rows -= 1

    # Draw pyramid
    current_row = rows
    chips_placed = 0
    while current_row > 0:
        for i in range(current_row + 1):
            if chips_placed < math.ceil(pile / 100):
                offset_x = x + ((current_row-1) * chips_width / 4) - (i * (chips_width/2))
                offset_y = y - ((rows-current_row) * (chips_height/2))
                screen.blit(scaled_image, (offset_x, offset_y))
                chips_placed += 1
            else:
                break
        current_row -= 1

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 3)  # Border
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                    self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def handle_click(self, mouse_pos):
        global turn_complete
        if self.rect.collidepoint(mouse_pos) and self.action:
            self.action()
            
def delete_button(screen, button):
    global buttons
    if button in buttons:
        buttons.remove(button)
    button.active = False
    pygame.draw.rect(screen, (0, 128, 0), button.rect)
    pygame.display.update(button.rect)

#slider # Link to slider code explained: https://pygamewidgets.readthedocs.io/en/latest/widgets/slider/
bet_check=0
amount=0
def bet_checkfunc(value):
    global bet_check
    bet_check = value

def delete_slider(x,y,width,height): #delete slider with given coords of slider(can be used for textbox)
    # Assuming the slider's position and size are known:
    slider_rect = pygame.Rect(x-50, y-10, width+100, height+50)  # Replace with your slider's actual position and size
    expanded_slider_rect = slider_rect.inflate(100, 100)  # Increase the width and height to cover the circles

    pygame.draw.rect(screen, (0, 128, 0), slider_rect)  # Fill the slider area with the background color
    pygame.display.update()  # Update the display
# Button Actions #

# Betting #

playercount = 4  # Changed to 4 (player + 3 AI opponents)
bet_turn = 1
def bet_phase():
    global prev_bet, last_player, bet_turn, round_complete, in_raise, ai_folded
    # 1 is player, 2-4 are AI opponents
    prev_bet = 0
    in_raise = False
    last_player = playercount
    active_players = sum(1 for folded in ai_folded if not folded) + (0 if player_lost else 1)
    
    if active_players <= 1:
        round_complete = True
        return
        
    round_complete = False
    while not round_complete and not player_lost and not all(ai_folded):
        render_chips()
        
        # Skip folded players
        while bet_turn > 1 and bet_turn <= playercount and ai_folded[bet_turn-2]:
            bet_turn = (bet_turn % playercount) + 1
            
        if bet_turn == 1 and not player_lost:
            player_turn()
            print("player turn")
        else:
            # AI turn for the current AI player
            AI_turn(bet_turn-2)  # -2 because AI indices are 0-2 but bet_turn is 2-4
            print(f"AI {bet_turn-1} turn")
            
        print("past turn")
        
        # Check if we've completed a full round
        if bet_turn != last_player:
            bet_turn = (bet_turn % playercount) + 1
        else:
            round_complete = True

    print("Betting round complete")

def player_turn():
    global buttons, raise_button, fold_button, call_button, check_button, cancel_button, confirm_button, in_raise, bet_turn, all_in, running, playerturn_running, prev_bet
    # display buttons#
    print("Player has: $" + str(player_money))
    print("Previous bet is", prev_bet)
    if in_raise:
        delete_button(screen, confirm_button)
        delete_button(screen, cancel_button)
        delete_slider(973, 575, 300, 50)
        delete_slider(1090, 645, 80, 50)
    fold_button = Button(1200, 700, 100, 50, "Fold", Fold)
    buttons = [fold_button]
    in_raise = False
    if not all_in:
        raise_button = Button(1075, 700, 100, 50, "Raise", Raise)
        buttons.append(raise_button)
    if prev_bet > 0:
        delete_button(screen, check_button)
        call_button = Button(950, 700, 100, 50, "Call", Call)
        print("call button called")
        buttons.append(call_button)
        pygame.display.flip()
    else:
        check_button = Button(950, 700, 100, 50, "Check", Check)
        buttons.insert(0, check_button)
    playerturn_running = True
    while playerturn_running:
        for button in buttons:
            button.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("mousebuttondown")
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.is_hovered(mouse_pos):
                        button.handle_click(mouse_pos)
                        print("Button")
                        playerturn_running = False
            elif event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
        
def AI_turn(ai_index):
    global bet_turn, last_player, opponent_money, prev_bet, pot, ai_folded, clear_text, phase
    
    # Return if this AI has already folded
    if ai_folded[ai_index]:
        return
    
    print(f"AI {ai_index+1} turn")
    clear_text = pygame.Rect(1000, 300, 250, 60)
    pygame.draw.rect(screen, (0, 128, 0), clear_text)
    
    # Evaluate AI's hand
    ai_best_hand = opponent_hands[ai_index] + community_cards
    hand_rank, values = get_hand_rank(ai_best_hand)
    
    # Each AI has different playing styles/strategies
    ai_risk_level = ai_personalities[ai_index]
    
    # If there's no previous bet, AI will check or raise
    if prev_bet == 0:
        # Aggressive AI raises more often
        if hand_rank >= 3 - ai_risk_level:  # AI with higher risk level raises with weaker hands
            # Raise with strong hands if no one has bet yet
            raise_multiplier = 0.3 + (ai_risk_level * 0.1)  # Aggressive AI raises higher
            raise_amount = min(int(opponent_money[ai_index] * raise_multiplier), opponent_money[ai_index])
            prev_bet = raise_amount
            pot += raise_amount
            opponent_money[ai_index] -= raise_amount
            last_player = bet_turn - 1 if bet_turn > 1 else playercount
            display_text(screen, f"AI {ai_index+1} raises {raise_amount}", False, (1000, 300), 50)
        else:
            # Otherwise, AI checks with weak hands
            display_text(screen, f"AI {ai_index+1} checks", False, (1000, 300), 50)

    # If there's a previous bet, AI can call, raise, or fold based on its hand and personality
    elif prev_bet > 0:
        # Different threshold for raising based on personality
        raise_threshold = 5 - ai_risk_level
        
        if hand_rank >= raise_threshold:  # Strong hands
            # Determine whether to raise or just call based on hand strength and personality
            if random.random() < (0.3 + ai_risk_level * 0.1):  # More aggressive AIs raise more often
                raise_multiplier = 0.2 + (ai_risk_level * 0.15)
                raise_amount = min(int(prev_bet * (1 + raise_multiplier)), opponent_money[ai_index])
                
                # Make sure the raise is valid
                if raise_amount > prev_bet and raise_amount <= opponent_money[ai_index]:
                    prev_bet = raise_amount
                    pot += raise_amount
                    opponent_money[ai_index] -= raise_amount
                    last_player = bet_turn - 1 if bet_turn > 1 else playercount
                    display_text(screen, f"AI {ai_index+1} raises to {raise_amount}", False, (1000, 300), 50)
                else:
                    # If can't raise properly, just call
                    call_amount = min(prev_bet, opponent_money[ai_index])
                    pot += call_amount
                    opponent_money[ai_index] -= call_amount
                    display_text(screen, f"AI {ai_index+1} calls {call_amount}", False, (1000, 300), 50)
            else:
                # Call with decent hands
                call_amount = min(prev_bet, opponent_money[ai_index])
                pot += call_amount
                opponent_money[ai_index] -= call_amount
                display_text(screen, f"AI {ai_index+1} calls {call_amount}", False, (1000, 300), 50)
        
        elif hand_rank >= 2 - ai_risk_level:  # Decent hands (threshold depends on personality)
            # Call with decent hands
            if prev_bet <= opponent_money[ai_index]:
                call_amount = prev_bet
            else:
                call_amount = opponent_money[ai_index]
            pot += call_amount
            opponent_money[ai_index] -= call_amount
            display_text(screen, f"AI {ai_index+1} calls {call_amount}", False, (1000, 300), 50)
        
        else:  # Weak hand, AI will fold
            # Bluff chance based on personality
            bluff_chance = 0.05 + (ai_risk_level * 0.1)  # More aggressive AIs bluff more
            
            if random.random() < bluff_chance:
                # Decide to bluff and call
                call_amount = min(prev_bet, opponent_money[ai_index])
                pot += call_amount
                opponent_money[ai_index] -= call_amount
                display_text(screen, f"AI {ai_index+1} calls {call_amount}", False, (1000, 300), 50)
            else:
                # Fold
                print(f"AI {ai_index+1} folds")
                display_text(screen, f"AI {ai_index+1} folds", False, (1000,300), 50)
                pygame.display.flip()
                ai_folded[ai_index] = True
                
                # Check if only one player remains
                active_players = sum(1 for folded in ai_folded if not folded) + (0 if player_lost else 1)
                if active_players <= 1:
                    phase = "showdown"
                    pygame.time.wait(1500)
                    Showdown()

def render_chips():
    clear_chips = pygame.Rect(0, 0, 350, 1500)
    pygame.draw.rect(screen, (0, 128, 0), clear_chips)
    
    # Player chips
    display_text(screen, "Player Chips", player_money, (100, 800))
    display_chips(player_money, 180, 700)
    
    # AI opponents chips
    for i in range(3):
        y_pos = 100 + i * 100
        display_text(screen, f"AI {i+1} Chips", opponent_money[i], (100, y_pos))
        display_chips(opponent_money[i], 180, y_pos - 50)
    
    # Pot
    display_text(screen, "Pot", pot, (100, 550))
    display_chips(pot, 180, 450)

def move_to_next_phase():
    global phase, bet_turn, player_lost, ai_folded
    render_chips()
    
    active_players = sum(1 for folded in ai_folded if not folded) + (0 if player_lost else 1)
    if active_players <= 1:
        Showdown()
        phase = "showdown"
        return
        
    if phase == "pre-flop":
        Flop()
        phase = "post-flop"
        bet_turn = 1
        player_lost = False
    elif phase == "river":
        Showdown()
        phase = "showdown"
    else:
        community_rect = pygame.Rect(450, 350, 500, 200)
        pygame.draw.rect(screen, (0, 128, 0), community_rect)
        if phase == "post-flop":
            Turn()
            phase = "turn"
            bet_turn = 1
        elif phase == "turn":
            River()
            phase = "river"
            bet_turn = 1
    print(phase)
    pygame.display.flip()

def Check():
    global bet_turn, pot
    pot += 0
    print("Check")
    if bet_turn == last_player:
        move_to_next_phase()

def Call():
    global pot, player_money, bet_turn, prev_bet
    call_amount = min(prev_bet, player_money)  # Can only call what you have
    pot += call_amount
    player_money -= call_amount
    print(f"Player calls {call_amount}")
    print(f"Player money: {player_money}")
    print(f"Pot: {pot}")

def Raise():
    global prev_bet, last_player, pot, player_money, in_raise, buttons, raise_button, check_button, call_button, fold_button, cancel_button, confirm_button, all_in
    #Have slider to define amount#
    in_raise = True
    slider = Slider(screen, 973, 575, 300, 50, min=prev_bet, max=player_money, step=1, onRelease=bet_checkfunc)
    output = TextBox(screen, 1090, 645, 80, 50, fontSize=30)
    output.disable()

    confirm_button = Button(1015, 700, 100, 50, "Confirm", ConfirmRaise)
    cancel_button = Button(1135, 700, 100, 50, "Cancel", player_turn)

    delete_button(screen, raise_button)
    if prev_bet == 0:
        delete_button(screen, check_button)
    else:
        delete_button(screen, call_button)
    delete_button(screen, fold_button)
    buttons = [confirm_button, cancel_button]
    
    print("The Current Pot is: " + str(pot))
    
    while in_raise:
        amount = min
        slider.draw()
        output.setText(slider.getValue())
        output.draw()
   
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()
        output.setText(slider.getValue())
        amount = slider.getValue()

        pygame_widgets.update(events)
        pygame.display.update()
        for button in buttons:
            button.draw(screen)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.is_hovered(mouse_pos):
                        button.handle_click(mouse_pos)

    print(pot)
    if amount == player_money:
        all_in = True
    prev_bet = amount
    player_money -= amount
    pot += amount
    if bet_turn == 1:
        last_player = playercount
    else:
        last_player = bet_turn - 1
    print("Raise")
    print(amount)

def ConfirmRaise():
    global bet_check, in_raise, bet_turn, all_in
    in_raise = False
    bet_check += 1
    delete_slider(973, 575, 300, 50)
    delete_slider(1090, 645, 80, 50)
    delete_button(screen, confirm_button)
    delete_button(screen, cancel_button)
    print(pot)

def Fold():
    global player_lost, phase
    print("Fold")
    player_lost = True
    
    # Check if only one player remains
    active_players = sum(1 for folded in ai_folded if not folded)
    if active_players <= 1:
        phase = "showdown"
        Showdown()

def Flop():
    global bet_turn
    draw_hand(3, deck, community_cards)
    display_hand(community_cards)
    bet_turn = 0

def Turn():
    global bet_turn
    draw_card(deck, community_cards)
    display_hand(community_cards)
    bet_turn = 0

def River():
    global bet_turn
    draw_card(deck, community_cards)
    display_hand(community_cards)
    bet_turn = 0

def Showdown():
    global revealing_cards
    # Win conditions #
    revealing_cards = True
    
    # Show all AI hands that haven't folded
    for i in range(3):
        if not ai_folded[i]:
            display_hand(opponent_hands[i])
    
    ResolveGame()

def ResolveGame():
    global opponent_money, player_money, pot, revealing_cards, playerturn_running, player_lost, ai_folded
    
    # Clean up buttons
    try:
        delete_button(screen, call_button)
    except NameError:
        try:
            delete_button(screen, check_button)
        except NameError:
            pass
    try:
        delete_button(screen, fold_button)
        delete_button(screen, raise_button)
    except NameError:
        pass
    
    try:
        pygame.draw.rect(screen, (0, 128, 0), clear_text)
    except NameError:
        pass
    
    # Find the winner
    best_hand_rank = -1
    winner = -1
    winner_text = ""
    
    # Check player hand if not folded
    if not player_lost:
        player_rank, player_values = get_hand_rank(player_hand + community_cards)
        best_hand_rank = player_rank
        winner = 0  # 0 represents player
        winner_text = "Player wins!"
    
    # Check each AI hand that hasn't folded
    for i in range(3):
        if not ai_folded[i]:
            ai_rank, ai_values = get_hand_rank(opponent_hands[i] + community_cards)
            
            # Compare with current best hand
            if winner == -1 or ai_rank > best_hand_rank or (ai_rank == best_hand_rank and ai_values > best_hand_values):
                best_hand_rank = ai_rank
                best_hand_values = ai_values
                winner = i + 1  # 1-3 represents AI 1-3
                winner_text = f"AI {i+1} wins!"
    
    # Distribute pot
    if winner == 0:
        # Player wins
        player_money += pot
    else:
        # AI wins
        opponent_money[winner-1] += pot
    
    pot = 0
    
    while revealing_cards:
        display_text(screen, winner_text, False, (1000, 200), 50)
        
        # Check if game should continue or end
        if player_money > 0 and any(money > 0 for money in opponent_money):
            next_round_button = Button(1075, 700, 200, 50, "Next Round", start_next_round)
            next_round_button.draw(screen)
        else:
            display_text(screen, "Game Over", False, (1000, 800), 50)
            if player_money == 0:
                display_text(screen, "You lost", False, (1000, 600), 50)
            else:
                display_text(screen, "You won", False, (1000, 600), 50)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("mousebuttondown")
                mouse_pos = pygame.mouse.get_pos()
                try:
                    if next_round_button.is_hovered(mouse_pos):
                        next_round_button.handle_click(mouse_pos)
                        print("Button")
                        if revealing_cards:
                            playerturn_running = False
                            revealing_cards = False
                except NameError:
                    pass
        pygame.display.flip()

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

def compare_hands(hand1, hand2):
    global opponent_win, player_win
    rank1, values1 = get_hand_rank(hand1)
    rank2, values2 = get_hand_rank(hand2)
    
    if rank1 > rank2:
        return "Player wins!"
    elif rank2 > rank1:
        return "Opponent wins!"
    else:
        # If same rank, compare by card values
        if values1 > values2:
            return "Player wins!"
        elif values2 > values1:
            opponent_win += 1
            return "Opponent wins!"
        else:
            player_win += 1
            return "It's a tie!"
        
def start_next_round():
    global playerturn_running, revealing_cards, bet_turn
    playerturn_running = False
    revealing_cards = False
    bet_turn = 1
    screen.fill((0, 128, 0))
    print("Starting next round...")
    play_round()

# Main Game Loop #
running = True
# Creating the pot#
initial_money = 1000
pot = 0
player_money = initial_money
# Initialize money for all three AI opponents
opponent_money = [initial_money, initial_money, initial_money]

# Define AI personalities (0 = conservative, 1 = balanced, 2 = aggressive)
ai_personalities = [0, 1, 2]

def play_round():
    global player_hand, opponent_hands, community_cards, deck, phase, revealing_cards
    global all_in, running, player_lost, ai_folded
    
    deck = create_deck()
    random.shuffle(deck)
    load_card_images(deck)
    
    # Reset game state
    player_hand = []
    opponent_hands = [[], [], []]
    community_cards = []
    phase = "pre-flop"
    revealing_cards = False
    all_in = False
    player_lost = False
    ai_folded = [False, False, False]
    
    # Deal initial hands
    draw_hand(2, deck, player_hand)
    for hand in opponent_hands:
        draw_hand(2, deck, hand)
    
    # Display hands
    display_hand(player_hand)
    for hand in opponent_hands:
        display_hand(hand)
    
    # Begin betting rounds
    bet_phase()
    
    pygame.display.flip()

# Main game loop
def main():
    global running, screen
    
    # Initial setup
    screen.fill((0, 128, 0))
    render_chips()
    
    # Start the first round
    play_round()
    
    # Main game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        pygame.display.flip()
    
    pygame.quit()

# Game initialization
if __name__ == "__main__":
    # Set up buttons
    buttons = []
    
    # Small blind and big blind values
    small_blind = 10
    big_blind = 20
    
    # Start the game
    main()