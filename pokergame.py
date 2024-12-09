import pygame
import time

######## CARD CREATION ########

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