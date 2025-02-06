import pygame
import random
import math
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from collections import Counter
from Ai import *


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

oppenent_win=0
player_win=0

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
    elif hand == opponent_hand:
        hand_pos = 3
        if not revealing_cards:
            card_image = pygame.image.load(f"card-back.jpg")
    elif hand == community_cards:
        hand_pos = 6
    else:
        print("bruh (check display_card)")

    if card.image:
        # Get original dimensions of image #
        #original_width, original_height = card.image.get_size()

        # Calculate new dimensions #
        #card_width = original_width * 0.15
        #card_height = original_height * 0.15

        card_width = 120
        card_height = 180

        scaled_image = pygame.transform.scale(card_image, (card_width, card_height))

        spacing = 20
        total_width = total_cards * card_width + (total_cards - 1) * spacing
        start_x = (screen_width - total_width) // 2
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

playercount = 2 # can be changed later if we want to add more players without needing to code in #
bet_turn = 1
def bet_phase():
    global prev_bet, last_player, bet_turn, round_complete, in_raise
    # 0 is neutral, 1 is player, 2 is AI #
    prev_bet = 0
    in_raise = False
    last_player = playercount
    round_complete = False
    while not round_complete and not player_lost and not AI_lost:
        render_chips()
        if bet_turn == 1:
            player_turn()
            print("player turn")
        else:
            # AI turn to be added #
            AI_turn()
            print("ai turn")
        print("past both turns")
        if bet_turn != last_player:
            bet_turn = (bet_turn % playercount) + 1
        else:
            round_complete = True

    print("Betting round complete")

def player_turn():
    global buttons, raise_button, fold_button, call_button, check_button, cancel_button, confirm_button,in_raise,bet_turn, all_in, running, playerturn_running,prev_bet
    # display buttons#
    print("Player has: $" + str(player_money))
    print("Previous bet is",prev_bet)
    if in_raise:
        delete_button(screen,confirm_button)
        delete_button(screen,cancel_button)
        delete_slider(973, 575, 300, 50)
        delete_slider(1090, 645, 80, 50)
    fold_button = Button(1200, 700, 100, 50, "Fold", Fold)
    buttons = [fold_button]
    in_raise = False
    if not all_in:
        raise_button = Button(1075, 700, 100, 50, "Raise", Raise)
        buttons.append(raise_button)
    if prev_bet > 0:
        delete_button(screen,check_button)
        call_button = Button(950, 700, 100, 50, "Call", Call)
        print("call button called")
        buttons.append(call_button)
        pygame.display.flip()
    else:
        check_button = Button(950, 700, 100, 50, "Check", Check)
        buttons.insert(0, check_button)
    playerturn_running=True
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
                        playerturn_running=False
            elif event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
        
def AI_turn(action, bet_amount):
    global bet_turn, last_player, opponent_money, prev_bet, pot, AI_lost, clear_text, phase

    print("AI turn")
    clear_text = pygame.Rect(1000, 180, 250, 60)
    pygame.draw.rect(screen, (0, 128, 0), clear_text)
    
    if action == "raise":
        raise_amount = min(bet_amount, opponent_money)  # Ensure AI doesn't bet more than it has
        prev_bet = raise_amount
        pot += raise_amount
        opponent_money -= raise_amount
        last_player -= 1
        display_text(screen, f"AI raises {raise_amount}", False, (1000, 200), 50)
    
    elif action == "bet":
        bet_value = min(bet_amount, opponent_money)  # Ensure AI doesn't bet more than it has
        prev_bet = bet_value
        pot += bet_value
        opponent_money -= bet_value
        display_text(screen, f"AI bets {bet_value}", False, (1000, 200), 50)
    
    elif action == "check":
        display_text(screen, "AI checks", False, (1000, 200), 50)
    
    elif action == "call":
        call_amount = min(prev_bet, opponent_money)  # Call the previous bet
        pot += call_amount
        opponent_money -= call_amount
        display_text(screen, f"AI calls {call_amount}", False, (1000, 200), 50)
    
    elif action == "fold":
        print("AI folds")
        display_text(screen, "AI folds", False, (1000, 200), 50)
        pygame.display.flip()
        AI_lost = True
        phase = "showdown"
        pygame.time.wait(2500)
        Showdown()
    
    else:
        print("Invalid action specified")


def render_chips():
    clear_chips = pygame.Rect(0, 0, 350, 1500)
    pygame.draw.rect(screen, (0,128,0), clear_chips)
    display_text(screen, "Player Chips", player_money, (100,800))
    display_text(screen, "Opponents Chips", opponent_money, (100,250))
    display_text(screen, "Pot", pot, (100, 550))
    display_chips(player_money, 180, 700)
    display_chips(opponent_money, 180, 150)
    display_chips(pot, 180, 450)

def move_to_next_phase():
    global phase, bet_turn, player_lost
    render_chips()
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
    global pot, player_money, bet_turn
    pot += prev_bet
    player_money -= prev_bet
    print(player_money)
    print(pot)
    print("Call")

def Raise():
    global prev_bet, last_player, pot, player_money, in_raise, buttons, raise_button,check_button,call_button,fold_button, cancel_button, confirm_button, all_in
    #Have slider to define amount#
    in_raise=True
    slider = Slider(screen, 973, 575, 300, 50, min=prev_bet, max=player_money, step=1, onRelease=bet_checkfunc)
    output = TextBox(screen, 1090, 645, 80, 50, fontSize=30)
    output.disable()

    confirm_button = Button(1015, 700, 100, 50, "Confirm", ConfirmRaise)
    cancel_button = Button(1135, 700, 100, 50, "Cancel", player_turn)

    delete_button(screen,raise_button)
    if prev_bet == 0:
        delete_button(screen,check_button)
    else:
        delete_button(screen,call_button)
    delete_button(screen,fold_button)
    buttons = [confirm_button, cancel_button]
    
    print("The Current Pot is: " + str(pot))
    
    while in_raise:
        amount=min
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
        amount=slider.getValue()

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
    bet_check+=1
    delete_slider(973, 575, 300, 50)
    delete_slider(1090, 645, 80, 50)
    delete_button(screen,confirm_button)
    delete_button(screen,cancel_button)
    print(pot)

def Fold():
    global player_lost, phase
    print("Fold")
    player_lost = True
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
    display_hand(opponent_hand)
    ResolveGame()

    #checkwin()

def ResolveGame():
    global opponent_money, player_money, pot, revealing_cards, playerturn_running, player_lost, AI_lost
    try:
        delete_button(screen, call_button)
    except NameError:
        delete_button(screen, check_button)
    delete_button(screen, fold_button)
    delete_button(screen, raise_button)
    try:
        pygame.draw.rect(screen, (0, 128, 0), clear_text)
    except NameError:
        pass
    if not AI_lost and compare_hands(player_hand+ community_cards, opponent_hand + community_cards) == "Opponent wins!":
        player_lost = True
    if player_lost:
        opponent_money += pot
    else:
        player_money += pot
    pot = 0
    while revealing_cards:
        if player_lost:
            display_text(screen, "Opponent wins!", False, (1000, 200), 50)
        elif AI_lost:
            display_text(screen, "Player wins!", False, (1000, 200), 50)
        else:
            display_text(screen, compare_hands(player_hand + community_cards, opponent_hand + community_cards), False, (1000, 200), 50)
        if player_money > 0 and opponent_money > 0:
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
                if next_round_button.is_hovered(mouse_pos):
                    next_round_button.handle_click(mouse_pos)
                    print("Button")
                    if revealing_cards:
                        playerturn_running = False
                        revealing_cards = False
        pygame.display.flip()

oppenent_win=0
player_win=0


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
    global oppenent_win,player_win
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
            oppenent_win+=1
            return "Opponent wins!"
        else:
            player_win+=1
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
opponent_money = initial_money
def play_round():
    global player_hand, opponent_hand, community_cards, deck, phase, revealing_cards, all_in, running, player_lost, AI_lost
    deck = create_deck()
    load_card_images(deck)
    random.shuffle(deck)
    player_hand = []
    opponent_hand = []
    community_cards = []
    print("round starting...")
    screen.fill((0, 128, 0))
    phase = "pre-flop"
    revealing_cards = False
    all_in = False
    player_lost = False
    AI_lost = False
    draw_hand(2, deck, player_hand)
    draw_hand(2, deck, opponent_hand)
    while running:
        screen.fill((0, 128, 0))
        display_hand(player_hand)
        display_hand(opponent_hand)
        display_hand(community_cards)
        render_chips()
        pygame.display.flip()
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
        while phase != "showdown":
            bet_phase()
            move_to_next_phase()
        pygame.display.flip()
        pygame.time.Clock().tick(60)

play_round()

pygame.quit()