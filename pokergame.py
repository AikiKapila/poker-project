import pygame
import random

# Pygame Set Up #
pygame.init()
screen_width = 1400
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Poker Game')

# Chip Creation #
class Chip:
    def __init__(self, value, image=None):
        self.image = image

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

# Function to make deck #
def create_deck():
    suits = ['H', 'D', 'C', 'S']
    deck = [Card(number, suit) for suit in suits for number in range(1, 13)]
    return deck

# Function to make chips #
def create_chips():
    values = [1, 5, 10, 25, 100]
    colors = [(255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 0, 0)]
    chips = []
    for value, color in zip(values, colors):
        chip = Chip(value)

        #chip_image = pygame.surface((50, 50), pygame.SRCALPHA)
        #pygame.draw.circle(chip_image, color, (25, 25), 25)
        #chip.image = chip_image

        chips.append(chip)

    return chips

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

# Betting #

global bet_turn
bet_turn = 0
# 0 is neutral, 1 is player, 2 is AI #
global prev_bet
prev_bet = 0

def Check():
    bet_turn += 1

def Call():
    bet_turn += 1

def Raise(amount):
    prev_bet = amount
    bet_turn += 1

def Fold():

    bet_turn += 1

def Flop():
    draw_card(deck, community_cards)

def Turn():
    draw_card(deck, community_cards)

def River():
    draw_hand(3, deck, community_cards)
    bet_turn = 0



# Creating the deck and images and empty player hand #
deck = create_deck()
load_card_images(deck)
random.shuffle(deck)
player_hand = []
opponent_hand = []
community_cards = []
player_chips = create_chips()
opponent_chips = create_chips()
initial_money = 1000
player_money = initial_money
opponent_money = initial_money

# Main Game Loop #
running = True
hand_drawn = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 128, 0))
    if not hand_drawn:
       draw_hand(2, deck, player_hand)
       draw_hand(2, deck, opponent_hand)
       Flop()
       Turn()
       River()
       hand_drawn = True

    display_hand(player_hand)
    display_hand(opponent_hand) 
    display_hand(community_cards)


    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()


