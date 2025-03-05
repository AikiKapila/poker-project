import pygame
import random
import math
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from poker_utils import create_deck, draw_card, draw_hand, get_hand_rank, get_card_values
from AikiAIOpponent import BayesianOpponentModel, make_decision


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

def display_card(card, index, total_cards, hand):
    global revealing_cards
    card_image = card.image
    if hand == player_hand:
        hand_pos = 9
    elif hand == aiki_AI_hand:
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
    while current_row > 0 or (pile > 0 and chips_placed == 0):
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
    global prev_bet, last_player, bet_turn, round_complete, in_raise, player_bets
    # 0 is neutral, 1 is player, 2 is AI #
    prev_bet = 0
    in_raise = False
    bet_turn = 1
    player_acted = False
    ai_acted = False
    #if current_dealer == 0 else 2
    last_player = playercount
    round_complete = False

    if phase == "pre-flop":
        apply_blinds()

    player_bets = {1: 0, 2: 0}  # Track individual player bets
    #active_players = {1, 2} # Players still active in the round

    while not round_complete and not player_lost and not AI_lost:
        render_chips()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running
                running = False
                pygame.quit()
                return
        if bet_turn == 1:
        #and 1 in active_players:
            player_turn()
            print("player turn")
            player_acted = True
            #if player_lost:
            #    active_players.remove(1)
            #else:
            #    player_bets[1] = prev_bet
            bet_turn = 2
        elif bet_turn == 2:
        #and 2 in active_players:
            # AI turn to be added #
            AI_turn()
            ai_acted = True
            #if AI_lost:
            #    active_players.remove(2)
            #else:
            #    player_bets[2] = prev_bet
            bet_turn = 1
        
        print("past both turns")
        if player_acted and ai_acted:
            if player_bets[1] == player_bets[2]:
                round_complete = True
                print("Round complete - both players have equal bets")
            else:
                # Reset the flags if bets aren't equal
                player_acted = False
                ai_acted = False
                print(f"Continuing round - player bet: {player_bets[1]}, AI bet: {player_bets[2]}")
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
    turn_action_taken = False
    while playerturn_running and not turn_action_taken:
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
                        turn_action_taken = True
                        playerturn_running=False
            elif event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
        

clear_text = pygame.Rect(1000, 180, 250, 60)

def AI_turn():
    global bet_turn, last_player, aiki_AI_money, prev_bet, pot, AI_lost, phase, player_bets
    print("AI turn")

    pygame.draw.rect(screen, (0, 128, 0), clear_text)

    game_state = {"pot":pot, "prev_bet": prev_bet, "player_money": player_money, "ai_money": aiki_AI_money}
    action, bet_amount = make_decision(aiki_AI_hand, community_cards, opponent_list[0], game_state)

    if action == "raise":
        raise_amount = min(bet_amount, aiki_AI_money)  # Ensure AI doesn't bet more than it has
        prev_bet = raise_amount
        pot += raise_amount
        aiki_AI_money -= raise_amount
        player_bets[2] = raise_amount
        display_text(screen, "AI raises", raise_amount, (1000, 200), 50)
        pygame.display.flip()
    
    elif action == "check":
        player_bets[2] = prev_bet
        display_text(screen, "AI checks", False, (1000, 200), 50)
        pygame.display.flip()

    elif action == "call":
        call_amount = min(prev_bet, aiki_AI_money)  # Call the previous bet
        pot += call_amount
        aiki_AI_money -= call_amount
        player_bets[2] = call_amount
        display_text(screen, "AI calls", call_amount, (1000, 200), 50)
        pygame.display.flip()

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

    pygame.display.flip()
    pygame.time.wait(2000)


def render_chips():
    clear_chips = pygame.Rect(0, 0, 350, 1500)
    pygame.draw.rect(screen, (0,128,0), clear_chips)
    display_text(screen, "Player Chips", player_money, (100,800))
    display_text(screen, "Opponents Chips", aiki_AI_money, (100,250))
    display_text(screen, "Pot", pot, (100, 550))
    display_chips(player_money, 180, 700)
    display_chips(aiki_AI_money, 180, 150)
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
    global bet_turn, playerturn_running
    opponent_list[0].track_action("check", phase)
    print("Check")
    playerturn_running = False
    player_bets[1] = prev_bet
    bet_turn = 2
    #if bet_turn == last_player:
        #move_to_next_phase()

def Call():
    global pot, player_money, bet_turn, playerturn_running
    pot += prev_bet
    player_money -= prev_bet
    opponent_list[0].track_action("call", phase)
    print("Call")
    player_bets[1] = prev_bet
    playerturn_running = False
    #if bet_turn != last_player:
        #bet_turn = (bet_turn % playercount) + 1

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
    opponent_list[0].track_action("raise", phase)
    delete_slider(973, 575, 300, 50)
    delete_slider(1090, 645, 80, 50)
    delete_button(screen,confirm_button)
    delete_button(screen,cancel_button)

def Fold():
    global player_lost, phase
    print("Fold")
    player_lost = True
    opponent_list[0].track_action("fold", phase)
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
    display_hand(aiki_AI_hand)
    ResolveGame()
    for opponent in opponent_list:
        if opponent.current_hand_actions["fold"] == 0:
            opponent.analyze_showdown()

    #checkwin()

def ResolveGame():
    global aiki_AI_money, player_money, pot, revealing_cards, playerturn_running, player_lost, AI_lost
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
    if not AI_lost and compare_hands(player_hand+ community_cards, aiki_AI_hand + community_cards) == "Aiki's AI wins!":
        player_lost = True
    if player_lost:
        aiki_AI_money += pot
    else:
        player_money += pot
    pot = 0
    while revealing_cards:
        if player_lost:
            display_text(screen, "Opponent wins!", False, (1000, 200), 50)
        elif AI_lost:
            display_text(screen, "Player wins!", False, (1000, 200), 50)
        else:
            display_text(screen, compare_hands(player_hand + community_cards, aiki_AI_hand + community_cards), False, (1000, 200), 50)
        if player_money > 0 and aiki_AI_money > 0:
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

def initialize_opponent_model():
    global opponent_list
    opponent_names = player_names.copy()
    opponent_names.remove("AikiAI")
    opponent_list = [BayesianOpponentModel(opponent) for opponent in opponent_names]

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
            player_win += 1
            return "Player wins!"
        elif values2 > values1:
            oppenent_win += 1
            return "Opponent wins!"
        else:
            player_win += 1
            return "It's a tie!"
        
def start_next_round():
    global playerturn_running, revealing_cards, bet_turn
    playerturn_running = False
    revealing_cards = False
    bet_turn = 1
    rotate_dealer()
    screen.fill((0, 128, 0))
    print("Starting next round...")
    play_round()

def apply_blinds():
    global player_money, aiki_AI_money, pot, current_dealer, prev_bet
    if current_dealer == 0:
        aiki_AI_money -= small_blind
        display_text(screen, f"Small Blind: {small_blind}", False, (1000, 200), 50)
        pygame.display.update()
        pygame.time.wait(1500)
        player_money -= big_blind
        pygame.draw.rect(screen, (0, 128, 0), clear_text)
        display_text(screen, f"Big Blind: {big_blind}", False, (1000, 200), 50)
    else:
        player_money -= small_blind
        display_text(screen, f"Small Blind: {small_blind}", False, (1000, 200), 50)
        pot += small_blind
        pygame.display.update()
        pygame.time.wait(1500)
        aiki_AI_money -= big_blind
        pygame.draw.rect(screen, (0, 128, 0), clear_text)
        display_text(screen, f"Big Blind: {big_blind}", False, (1000, 200), 50)
        pygame.display.update()
        pygame.time.wait(1500)
    pot += big_blind
    #prev_bet = big_blind
    
    

def rotate_dealer():
    global current_dealer
    current_dealer = (current_dealer + 1) % playercount

# Main Game Loop #
running = True
small_blind = 10
big_blind = 20
current_dealer = 0
# Creating the pot#
initial_money = 1000
pot = 0
player_money = initial_money
aiki_AI_money = initial_money
player_names = ["player", "AikiAI"]
initialize_opponent_model()
#, "KeokiAI", "EllisAI"]

def play_round():
    global player_hand, aiki_AI_hand, community_cards, deck, phase, revealing_cards, all_in, running, player_lost, AI_lost
    #keoki_AI_hand, ellis_AI_hand
    deck = create_deck()
    load_card_images(deck)
    random.shuffle(deck)
    player_hand = []
    aiki_AI_hand = []
    #keoki_AI_hand = []
    #ellis_AI_hand = []
    community_cards = []
    print("round starting...")
    screen.fill((0, 128, 0))
    phase = "pre-flop"
    revealing_cards = False
    all_in = False
    player_lost = False
    AI_lost = False

    draw_hand(2, deck, player_hand)
    draw_hand(2, deck, aiki_AI_hand)
    #draw_hand(2, deck, keoki_AI_hand)
    #draw_hand(2, deck, ellis_AI_hand)
    while running:
        screen.fill((0, 128, 0))
        display_hand(player_hand)
        display_hand(aiki_AI_hand)
        #display_hand(keoki_AI_hand)
        #display_hand(ellis_AI_hand)
        display_hand(community_cards)
        render_chips()
        pygame.display.flip()

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return
        
        bet_phase()
        move_to_next_phase()
    if phase == "showdown":
        Showdown()
        
    pygame.display.flip()
    pygame.time.Clock().tick(60)

play_round()

pygame.quit()