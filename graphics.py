import pygame

CELL_SIZE = 10
FPS = 60

class Screen():
    def __init__(self, width, height, cell_size=CELL_SIZE, fps=FPS):
        width = (width // cell_size) * cell_size
        height = (height // cell_size) * cell_size
        self.fps = fps
        self.fps_ticker = pygame.time.Clock()
        self.cell_size = cell_size
        self.food_size = cell_size * 0.6
        self.canvas = pygame.display.set_mode((width, height))
        self.field = [[' '] * width for _ in range(height)]

    def update(self):
        pygame.display.update()
        self.fps_ticker.tick(self.fps)
