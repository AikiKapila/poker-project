import pygame
import random
import time


# Pygame Set Up #
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Poker Game')


# CARD CREATION #
class Card:
    def __init__(self, number, suit):
        self.n = number
        match suit:
            case 0:
                self.s = "clubs"
            case 1:
                self.s = "diamonds"
            case 2:
                self.s = "hearts"
            case 3:
                self.s = "spades"
    

    