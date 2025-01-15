import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Button")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)

# Fonts
font = pygame.font.Font(None, 36)

# Button variables
button_rect = pygame.Rect(300, 250, 200, 50)  # Initial button position and size
button_exists = False  # Track if the button exists

# Add/Remove button controls
add_button_rect = pygame.Rect(50, 50, 150, 50)
remove_button_rect = pygame.Rect(50, 120, 150, 50)

def draw_text(text, font, color, surface, x, y):
    """Utility function to draw text on the screen."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def main():
    global button_exists
    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)

        # Draw Add/Remove buttons
        pygame.draw.rect(screen, GREEN, add_button_rect)
        pygame.draw.rect(screen, RED, remove_button_rect)
        draw_text("Add Button", font, WHITE, screen, add_button_rect.centerx, add_button_rect.centery)
        draw_text("Remove Button", font, WHITE, screen, remove_button_rect.centerx, remove_button_rect.centery)

        # Draw the dynamic button if it exists
        if button_exists:
            pygame.draw.rect(screen, GRAY, button_rect)
            draw_text("Dynamic Button", font, WHITE, screen, button_rect.centerx, button_rect.centery)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if add_button_rect.collidepoint(event.pos):
                        button_exists = True  # Add the button
                    elif remove_button_rect.collidepoint(event.pos):
                        button_exists = False  # Remove the button
                    elif button_exists and button_rect.collidepoint(event.pos):
                        print("Dynamic Button Clicked!")

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
