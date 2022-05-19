import pygame
from pygame import mouse
import sys

from engine import Session
from engine import Entity, Carnivore

WHITE = (255, 255, 255)
RED = (255, 0, 0)

session = Session()
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    session.main_loop()
