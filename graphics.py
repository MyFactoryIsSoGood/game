import pygame

WIDTH_PX = 1600  # Размеры экрана
HEIGHT_PX = 600

CELL_SIZE = 6  # Размеры клеток и еды
FOOD_POS_OFFSET = CELL_SIZE * 0.2

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
