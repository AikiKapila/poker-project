
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
    if most_common[0][1] == 3 and most_common[1][1] == 2:
        return 7, values

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
    if most_common[0][1] == 2 and most_common[1][1] == 2:
        return 3, values

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

def determine_winner():
    global oppenent_win,player_win,pot,player_money,opponent_money
    player_best_hand = player_hand + community_cards
    opponent_best_hand = opponent_hand + community_cards
    winner = compare_hands(player_best_hand, opponent_best_hand)
    print(winner)
    if player_win==1:
        player_money+=pot
        player_win=0
        print(player_money)
    else:
        opponent_money+=pot
        oppenent_win=0
        

    
        
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

def delete_slider(x,y,width,height): #delete slider with given coords of slider(can be used for textbox)
    # Assuming the slider's position and size are known:
    slider_rect = pygame.Rect(x-50, y-50, width+100, height+100)  # Replace with your slider's actual position and size
    expanded_slider_rect = slider_rect.inflate(100, 100)  # Increase the width and height to cover the circles

    pygame.draw.rect(screen, (0, 128, 0), slider_rect)  # Fill the slider area with the background color
    pygame.display.update()  # Update the display
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
            print("Bet turn number is" , bet_turn)
            print("after playerturn bet turn is", bet_turn)
        else:
            # AI turn to be added #
            AI_turn()
            print("ai turn")
            
            print("past both turns")
            print(bet_turn)
            print(last_player)
            if bet_turn != last_player:
                bet_turn = (bet_turn % playercount) + 1
            else:
                round_complete = True

    print("Betting round complete")
    bet_turn = 1
Raise_checker=False

def player_turn():
    global buttons, raise_button, fold_button, call_button, check_button, cancel_button, confirm_button,Raise_checker,bet_turn
    # display buttons#

    if in_raise:
        
        delete_button(screen,confirm_button)
        delete_button(screen,cancel_button)
        delete_slider(973, 575, 300, 50)
        delete_slider(1090, 645, 80, 50)
    raise_button = Button(1075, 700, 100, 50, "Raise", Raise)
    fold_button = Button(1200, 700, 100, 50, "Fold", Fold)
    buttons = [raise_button, fold_button]

    if prev_bet > 0:
        call_button = Button(950, 700, 100, 50, "Call", Call)
        buttons.insert(0, call_button)
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
                        if Raise_checker==True:
                            ConfirmRaise()
                            Raise_checker=False
                            
                            playerturn_running=True
                        else: 
                            print("past raise checker")
                            playerturn_running=False
          
                    
                
def AI_turn():
    global bet_turn, last_player, opponent_money, prev_bet, pot

    print("AI turn")
    
    # Evaluate AI's hand
    opponent_best_hand = opponent_hand + community_cards
    hand_rank, values = get_hand_rank(opponent_best_hand)
    
    # If there's no previous bet, AI will check (or raise if it has a very strong hand)
    if prev_bet == 0:
        if hand_rank >= 7:  # Strong hands like Full House, Straight, Flush
            # Raise with strong hands if no one has bet yet
            raise_amount = min(opponent_money // 2, opponent_money)  # Raise with 50% of available AI's chips
            prev_bet = raise_amount
            pot += raise_amount
            opponent_money -= raise_amount
            print(f"AI raises {raise_amount}")
        else:
            # Otherwise, AI checks with weak hands
            print("AI checks")
    
    # If there's a previous bet, AI can call, raise, or fold based on its hand
    elif prev_bet > 0:
        if hand_rank >= 7:  # Strong hands (Full House, Straight, Flush, etc.)
            # Raise if the hand is strong
            raise_amount = min(opponent_money // 2, opponent_money)  # Raise with 50% of available AI's chips
            prev_bet = raise_amount
            pot += raise_amount
            opponent_money -= raise_amount
            print(f"AI raises {raise_amount}")
        elif hand_rank >= 4:  # Decent hands like Three of a Kind, Two Pair
            # Call with decent hands
            call_amount = prev_bet
            prev_bet = call_amount
            pot += call_amount
            opponent_money -= call_amount
            print(f"AI calls {call_amount}")
        else:  # Weak hand, AI will fold
            print("AI folds")
            return  # End the turn, AI folds

    # Update bet turn to player (or to the next player in the game)
    bet_turn = last_player
 

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
    global prev_bet, last_player, pot, player_money, in_raise, buttons, raise_button,check_button,call_button,fold_button, cancel_button, confirm_button,Raise_checker
    #Have slider to define amount#
    Raise_checker=True
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
    print("brh")
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
    
    global bet_check, in_raise
    in_raise = False
    bet_check+=1
    delete_slider(973, 575, 300, 50)
    delete_slider(1090, 645, 80, 50)
    delete_button(screen,confirm_button)
    delete_button(screen,cancel_button)
    print(pot)

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
    print("bet phase 1 done")
    Flop()
    bet_phase()
    Turn()
    bet_phase()
    River()
    bet_phase()
    determine_winner()  # Determine the winner after the final community card
    running=False


    

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
