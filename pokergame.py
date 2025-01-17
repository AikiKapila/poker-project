
import pygame
import random
import math
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox

# Pygame Set Up #
pygame.init()
screen_width = 1400
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Poker Game')

# Chip Creation #
class Pile:
    def __init__(self, size):
        self.size = size

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
        
# Attaching Card Images to Names #
def load_card_images(cards):
    for card in cards:
        card_image_file = f"{card.n}_{card.s}.png"
        try:
            card.image = pygame.image.load(card_image_file)
        except pygame.error as e:
            print(f"Error loading image {card_image_file}: {e}")

def load_pile_images(size):
    pile_images = []
    for i in range(math.ceil(size/100)):
        pile_images.append(f"pile-of-chips.webp")

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
    card_image = card.image
    if hand == player_hand:
        hand_pos = 9
    elif hand == opponent_hand:
        hand_pos = 3
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


# Creating the deck and images and empty player hand #
deck = create_deck()
load_card_images(deck)
random.shuffle(deck)
player_hand = []
opponent_hand = []
community_cards = []
initial_money = 1000
pot = 0
player_money = initial_money
opponent_money = initial_money
player_chips = Pile(player_money)
opponent_chips = Pile(opponent_money)


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
    """
    Disables the given button by setting its active property to False, 
    clearing its area from the screen, and updating the display.
    
    Args:
        screen: The Pygame surface where the button is drawn.
        button: The Button object to be disabled.
    """
    button.active = False  # Mark the button as inactive
    # Clear the button area by filling it with the background color
    pygame.draw.rect(screen, (0, 128, 0), button.rect)  # Replace (0, 128, 0) with your background color
    # Update the display area corresponding to the button
    pygame.display.update(button.rect)
#slider # Link to slider code explained: https://pygamewidgets.readthedocs.io/en/latest/widgets/slider/
bet_check=0
amount=0
def bet_checkfunc(value):
    global bet_check
    bet_check = value

    
# Button Actions #

# Betting #

playercount = 2 # can be changed later if we want to add more players without needing to code in #
bet_turn = 1

def bet_phase():
    global prev_bet, last_player, bet_turn, round_complete
    # 0 is neutral, 1 is player, 2 is AI #
    prev_bet = 0
    last_player = playercount
    round_complete = False
    
    while not round_complete:
        if bet_turn == 1:
            player_turn()
            print("player turn")
        else:
            # AI turn to be added #
            AI_turn()

        if bet_turn != last_player:
            bet_turn = (bet_turn % playercount) + 1
        else:
            round_complete = True

    print("Betting round complete")
    bet_turn = 1

def player_turn():
    global buttons, raise_button, fold_button, call_button, check_button, cancel_button, confirm_button
    # display buttons#
    if in_raise:
        delete_button(screen,confirm_button)
        delete_button(screen,cancel_button)
    raise_button = Button(1075, 700, 100, 50, "Raise", Raise)
    fold_button = Button(1200, 700, 100, 50, "Fold", Fold)
    buttons = [raise_button, fold_button]

    if prev_bet > 0:
        call_button = Button(950, 700, 100, 50, "Call", Call)
        buttons.insert(0, call_button)
    else:
        check_button = Button(950, 700, 100, 50, "Check", Check)
        buttons.insert(0, check_button)
    
    while True:
        for button in buttons:
            button.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.is_hovered(mouse_pos):
                        button.handle_click(mouse_pos)
                        print("Button")
                        break

def AI_turn():
    pass

def Check():
    global bet_turn, pot
    pot += 0
    bet_turn -= 1
    print("Check")
    

def Call():
    global pot, player_money, bet_turn
    pot += prev_bet
    player_money -= prev_bet
    bet_turn -= 1
    print(player_money)
    print(pot)
    print("Call")

in_raise = False

def Raise():
    global prev_bet, last_player, pot, player_money, in_raise, buttons, raise_button,check_button,call_button,fold_button, cancel_button, confirm_button
    #Have slider to define amount#

    slider = Slider(screen, 973, 575, 300, 50, min=prev_bet, max=player_money, step=1, onRelease=bet_checkfunc)
    output = TextBox(screen, 1090, 645, 80, 50, fontSize=30)
    output.disable()

    in_raise = True
    delete_button(screen,raise_button)
    if prev_bet == 0:
        delete_button(screen,check_button)
    else:
        delete_button(screen,call_button)
    delete_button(screen,fold_button)
   
    confirm_button = Button(1015, 700, 100, 50, "Confirm", ConfirmRaise)
    cancel_button = Button(1135, 700, 100, 50, "Cancel", player_turn)
    
    buttons = [confirm_button, cancel_button]
    
    print(pot)
    
    while in_raise:
        slider.draw()
        output.setText(slider.getValue())
        output.draw()
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
    print("brh")
    prev_bet = amount
    player_money -= amount
    pot += amount
    if bet_turn == 1:
        last_player = playercount
    else:
        last_player = bet_turn - 1
    print("Raise")

def ConfirmRaise():
    global bet_check, in_raise
    in_raise = False
    bet_check+=1
    print("hi")

def Fold():
    print("Fold")

def Flop():
    draw_card(deck, community_cards)

def Turn():
    draw_card(deck, community_cards)

def River():
    global bet_turn
    draw_hand(3, deck, community_cards)
    bet_turn = 0

# Main Game Loop #
running = True
hand_drawn = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

    screen.fill((0, 128, 0))
    if not hand_drawn:
        draw_hand(2, deck, player_hand)
        draw_hand(2, deck, opponent_hand)
        hand_drawn = True
    
    display_hand(player_hand)
    display_hand(opponent_hand) 
    display_hand(community_cards)
    bet_phase()
    Flop()
    bet_phase()
    Turn()
    bet_phase()
    River()
    bet_phase()


    

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
