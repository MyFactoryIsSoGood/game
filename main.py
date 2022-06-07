import pygame
import sys
import cProfile
import pstats

from gameplay import Session

session = Session()
# with cProfile.Profile() as pr:
#     for _ in range(10):
#         session.main_loop()
# stats = pstats.Stats(pr)
# stats.sort_stats(pstats.SortKey.TIME)
# stats.print_stats()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    if len(session.entities) != 0 or session.epoch == 0:
        session.main_loop()
