import pygame
import random
import time


# Pygame Set Up #
pygame.init()
screen_width = 1400
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Poker Game')


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
        
    def set_image(self, image):
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


# Creating the deck and images #
deck = create_deck()
load_card_images(deck)
random.shuffle(deck)

# Function to draw a card from the deck # //You need to add somewhere for the popped card to land (player/ai hand)
def draw_card(deck, hand):
    if deck:
        card = deck.pop(0)  # Remove the top card from the deck
        return card
    else:
        return None  # Return None if the deck is empty



# Main Game Loop #
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 128, 0))

    if deck[0].image:
        # Get original dimensions of image #
        original_width, original_height = deck[0].image.get_size()
        
        # Calculate new dimensions #
        new_width = original_width * 0.15
        new_height = original_height * 0.15

        scaled_image = pygame.transform.scale(deck[0].image, (new_width, new_height))
        screen.blit(scaled_image, (screen_width // 2 - new_width // 2, screen_height // 2 - new_height // 2))

    pygame.display.flip()

pygame.quit()


