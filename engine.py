import pygame
from abc import ABC, abstractmethod
from random import randint

WIDTH = HEIGHT = 500
ROTTEN_LIMIT = 5
CELL_SIZE = 5
FOOD_POS_OFFSET = CELL_SIZE * 0.2
FPS = 60


class Screen():
    def __init__(self, width, height, cell_size=CELL_SIZE, fps=FPS):
        # делаем экран пригодным для ячеек 5х5
        width = (width // cell_size) * cell_size
        height = (height // cell_size) * cell_size
        self.fps = fps
        self.fps_ticker = pygame.time.Clock()
        self.cell_size = cell_size
        self.food_size = cell_size * 0.6
        self.canvas = pygame.display.set_mode((width, height))
        self.field = [[0] * width for _ in range(height)]  # само поле

    def draw_manually(self, field):
        self.canvas.fill((0, 0, 0))
        for index, row in enumerate(field):
            for index2, cell in enumerate(row):
                match cell:
                    case 0:
                        color = (0, 0, 0)
                    case 1:
                        color = (255, 255, 255)
                cell_position_size = (index * self.cell_size, index2 * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.canvas, color, cell_position_size)
        self.update()

    def update(self):
        pygame.display.update()
        self.fps_ticker.tick(self.fps)


class Entity(ABC):
    def __init__(self, size, x_pos, y_pos):
        self.size = size
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.alive = True
        self.hungry = False

    def die(self):
        self.alive = False

    @abstractmethod
    def reproduce(self):
        new_species = []
        return new_species

    @abstractmethod
    def calculate_move(self):
        x, y = 0, 0
        deltas = [x, y]
        return deltas


class Carnivore(Entity):
    def __init__(self, size, x_pos, y_pos):
        super().__init__(size, x_pos, y_pos)
        self.daily_food_quota = 2

    def reproduce(self):
        new_species = [self.__class__()]
        return new_species

    def calculate_move(self):
        return


class Herbivore(Entity):
    def __init__(self, size, x_pos, y_pos):
        super().__init__(size, x_pos, y_pos)
        self.daily_food_quota = 1

    def reproduce(self):
        new_species = [self.__class__()] * 2
        return new_species

    def calculate_move(self, foods):
        dist = 10000
        deltas = [0, 0]
        for food in foods:
            if not food.eaten:
                if dist > ((self.x_pos - food.x_pos) ** 2 + (self.y_pos - food.y_pos) ** 2) ** 0.5:
                    dist = ((self.x_pos - food.x_pos) ** 2 + (self.y_pos - food.y_pos) ** 2) ** 0.5
                    selected = food
        deltas[0] = 0 if self.x_pos == selected.x_pos else int(
            (selected.x_pos - self.x_pos) / abs(selected.x_pos - self.x_pos))
        deltas[1] = 0 if self.y_pos == selected.y_pos else int(
            (selected.y_pos - self.y_pos) / abs(selected.y_pos - self.y_pos))
        if deltas == [0, 0]:
            selected.eaten = True
            del selected
        return deltas

    def move(self, deltas):
        self.x_pos += deltas[0]
        self.y_pos += deltas[1]


class Food:
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rotten_rate = 0
        self.rotten = False
        self.eaten = False

    def to_rotten(self):
        self.rotten_rate += 1
        if self.rotten >= ROTTEN_LIMIT:
            self.rotten = True

    def eat(self):
        self.eaten = True


class Session:
    def __init__(self):
        self.ended = False
        self.entities = []
        self.foods = []
        self.epoch = 0
        self.screen = Screen(WIDTH, HEIGHT)

        for _ in range(5000):
            self.foods.append(Food(randint(0, WIDTH / CELL_SIZE), randint(0, WIDTH / CELL_SIZE)))

        for _ in range(30):
            self.entities.append(Herbivore(1, randint(0, WIDTH / CELL_SIZE), randint(0, WIDTH / CELL_SIZE)))

    def display_entities(self):
        for entity in self.entities:
            cell_position_size = (
                entity.x_pos * self.screen.cell_size, entity.y_pos * self.screen.cell_size, self.screen.cell_size,
                self.screen.cell_size)
            entity_type = str(type(entity))[str(type(entity)).find('.') + 1:str(type(entity)).rfind("'")]
            match entity_type:
                case 'Herbivore':
                    color = (0, 255, 0)
                case 'Carnivore':
                    color = (255, 0, 0)
                case _:
                    color = (100, 100, 0)
            pygame.draw.rect(self.screen.canvas, color, cell_position_size)

    def display_food(self):
        for food in self.foods:
            if not food.eaten:
                cell_position_size = (
                    food.x_pos * self.screen.cell_size + FOOD_POS_OFFSET,
                    food.y_pos * self.screen.cell_size + FOOD_POS_OFFSET, self.screen.cell_size - 2 * FOOD_POS_OFFSET,
                    self.screen.cell_size - 2 * FOOD_POS_OFFSET)
                color = (
                    int(255 - 235 * food.rotten_rate / ROTTEN_LIMIT), int(223 - 203 * food.rotten_rate / ROTTEN_LIMIT), 0)
                pygame.draw.rect(self.screen.canvas, color, cell_position_size)
                food.rotten_rate = 0

    def main_loop(self):
        # self.entities.append(Herbivore(1, randint(0, WIDTH / CELL_SIZE), randint(0, WIDTH / CELL_SIZE)))
        # for _ in range(100):
        #     self.foods.append(Food(randint(0, WIDTH / CELL_SIZE), randint(0, WIDTH / CELL_SIZE)))
        for entity in self.entities:
            deltas = entity.calculate_move(self.foods)
            entity.x_pos += deltas[0]
            entity.y_pos += deltas[1]
        self.screen.canvas.fill((0, 0, 0))
        self.display_entities()
        self.display_food()
        self.screen.update()

# ent = Herbivore(1, 10, 10)
# food1 = Food(15, 80)
# food2 = Food(5, 5)
# food3 = Food(32, 9)
# lst = [food3, food1]
# lol = [1, 1]
# while lol != [0, 0]:
#     lol = ent.calculate_move(lst)
#     print(lol, ent.x_pos, ent.y_pos)
#     ent.x_pos += lol[0]
#     ent.y_pos += lol[1]
