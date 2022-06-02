import time

import pygame
from graphics import Screen, CELL_SIZE, WIDTH_PX, HEIGHT_PX, FOOD_POS_OFFSET
from random import randint

# Изначальное количество клеток в симуляции
INIT_PREY = 30  # Травоядные
INIT_SYNTH = 0  # Синтезаторы
INIT_FOOD = 500  # Органика

AGE_LIMIT = 120  # Продолжительность жизни клеток

FOOD_COST = 42  # Количество энергии за одну клетку органики
SYNTHETIC_COST = 30  # Количество энергии за одну клетку синтетики
MOVE_COST = 1  # Стоимость передвижения

# Изначаьное количество энергии у клетки
PREY_START_ENERGY = 20

PREY_ENERGY_LIMIT = 50  # По достижении этйо отметки существо родит отпрыска
PREY_CHILD_COST = 20  # Стоимость рождения потомства

SYNTH_FOOD_PER_MOVE = 5  # Количество еды, генерируемое синтезтором за один подход
SYNTHESIS_PROBABILITY = 25  # Вероятность того, что на этом ходу синтезатор создаст еду (в процентах)
SYNTH_MOVE_PROBABILITY = 100  # Вероятность того, что синтезатор переместится (в процентах)


class Animal:
    def die(self, session):
        self.alive = False
        session.field.canvas[self.y_pos][self.x_pos] = Food(self.x_pos, self.y_pos)

    def check_edges(self, deltas):
        if self.x_pos == 0:
            deltas[0] = 1
        elif self.x_pos == (WIDTH_PX // CELL_SIZE) - 1:
            deltas[0] = -1
        if self.y_pos == 0:
            deltas[1] = 1
        elif self.y_pos == (HEIGHT_PX // CELL_SIZE) - 1:
            deltas[1] = -1
        return deltas

    def move(self, deltas, session):
        session.field.canvas[self.y_pos][self.x_pos] = ''
        session.field.empty.append((self.x_pos, self.y_pos))
        self.x_pos += deltas[0]
        self.y_pos += deltas[1]
        self.energy -= MOVE_COST
        if isinstance(session.field.canvas[self.y_pos][self.x_pos], Food):
            session.field.canvas[self.y_pos][self.x_pos].eat()
            if session.field.canvas[self.y_pos][self.x_pos].synthetic:
                self.energy += SYNTHETIC_COST
            else:
                self.energy += FOOD_COST
        session.field.canvas[self.y_pos][self.x_pos] = self


class Prey(Animal):
    age_limit = AGE_LIMIT

    def __repr__(self):
        return 'P'

    def __init__(self, x_pos, y_pos):
        self.age = 0
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.energy = PREY_START_ENERGY
        self.alive = True

    def pass_epoch(self, session):
        self.age += 1
        deltas = self.calculate_move(session.field)
        self.move(deltas, session)
        if self.energy == 0:
            self.die(session)
        if self.age >= self.age_limit:
            self.die(session)
        if self.energy >= PREY_ENERGY_LIMIT:
            self.reproduce(session)

    def calculate_move(self, field):
        deltas = [0, 0]
        selected = []
        for row in range(self.y_pos - 2, self.y_pos + 2 + 1):
            for cell in range(self.x_pos - 2, self.x_pos + 2 + 1):
                if (HEIGHT_PX // CELL_SIZE) > row >= 0 and (
                        WIDTH_PX // CELL_SIZE) > cell >= 0:
                    if isinstance(field.canvas[row][cell], Food):
                        sel_x = cell
                        sel_y = row
                        selected.append((sel_x, sel_y))
        if selected:
            sel_x, sel_y = selected[randint(0, len(selected) - 1)]
            deltas[0] = 0 if self.x_pos == sel_x else int((sel_x - self.x_pos) / abs(sel_x - self.x_pos))
            deltas[1] = 0 if self.y_pos == sel_y else int((sel_y - self.y_pos) / abs(sel_y - self.y_pos))
        else:
            deltas = [randint(-1, 1), randint(-1, 1)]
            deltas = self.check_edges(deltas)
        counter = 0
        cell = field.canvas[self.y_pos + deltas[1]][self.x_pos + deltas[0]]
        while isinstance(cell, Prey) or isinstance(cell, Synth):
            if counter == 15:
                deltas = [0, 0]
                break
            deltas = [randint(-1, 1), randint(-1, 1)]
            deltas = self.check_edges(deltas)
            counter += 1
        return deltas

    def reproduce(self, session):
        selected = []
        for row in range(self.y_pos - 1, self.y_pos + 1 + 1):
            for cell in range(self.x_pos - 1, self.x_pos + 1 + 1):
                if (HEIGHT_PX // CELL_SIZE) > row >= 0 and (
                        WIDTH_PX // CELL_SIZE) > cell >= 0 and (row != self.y_pos and cell != self.x_pos):
                    if session.field.canvas[row][cell] == '':
                        sel_x = cell
                        sel_y = row
                        selected.append((sel_x, sel_y))
        if selected:
            sel_x, sel_y = selected[randint(0, len(selected) - 1)]
            new = Prey(sel_x, sel_y)
            session.field.canvas[new.y_pos][new.x_pos] = new
            self.energy -= PREY_CHILD_COST
        else:
            self.die(session)


class Synth(Animal):
    age_limit = AGE_LIMIT*5

    def __repr__(self):
        return 'X'

    def __init__(self, x_pos, y_pos):
        self.age = 0
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.energy = 1
        self.alive = True

    def move(self, deltas, session):
        super().move(deltas, session)
        self.energy += MOVE_COST

    def produce_energy(self, field):
        cells = []
        for row in range(self.y_pos - 2, self.y_pos + 2 + 1):
            for cell in range(self.x_pos - 2, self.x_pos + 2 + 1):
                if (HEIGHT_PX // CELL_SIZE) > row >= 0 and (
                        WIDTH_PX // CELL_SIZE) > cell >= 0 and (
                        abs(row - self.y_pos) != 0 or abs(cell - self.x_pos) != 0):
                    if field.canvas[row][cell] == '':
                        cells.append((row, cell))
        if cells:
            for i in range(SYNTH_FOOD_PER_MOVE):
                ind = randint(0, len(cells) - 1)
                cell = cells[ind]
                cells.remove(cell)
                new = Food(cell[1], cell[0], True)
                field.canvas[cell[0]][cell[1]] = new
                field.empty.remove((cell[1], cell[0]))
                if not cells:
                    break

    def pass_epoch(self, session):
        self.age += 1
        if randint(0, 100 // SYNTH_MOVE_PROBABILITY) == 0:
            deltas = self.calculate_move(session.field)
            self.move(deltas, session)
        if randint(0, 100 // SYNTHESIS_PROBABILITY) == 0:
            pass
        self.produce_energy(session.field)
        if self.age >= self.age_limit:
            self.die(session)

    def calculate_move(self, field):
        deltas = [0, 0]
        selected = []
        foods = []
        for row in range(self.y_pos - 1, self.y_pos + 2):
            for cell in range(self.x_pos - 1, self.x_pos + 2):
                if (HEIGHT_PX // CELL_SIZE) > row >= 0 and (
                        WIDTH_PX // CELL_SIZE) > cell >= 0:
                    if field.canvas[row][cell] == '':
                        sel_x = cell
                        sel_y = row
                        selected.append((sel_x, sel_y))
                    elif isinstance(field.canvas[row][cell], Food):
                        sel_x = cell
                        sel_y = row
                        foods.append((sel_x, sel_y))

        if selected:
            sel_x, sel_y = selected[randint(0, len(selected) - 1)]
            deltas[0] = 0 if self.x_pos == sel_x else int((sel_x - self.x_pos) / abs(sel_x - self.x_pos))
            deltas[1] = 0 if self.y_pos == sel_y else int((sel_y - self.y_pos) / abs(sel_y - self.y_pos))
        else:
            if foods:
                sel_x, sel_y = foods[randint(0, len(foods) - 1)]
                deltas[0] = 0 if self.x_pos == sel_x else int((sel_x - self.x_pos) / abs(sel_x - self.x_pos))
                deltas[1] = 0 if self.y_pos == sel_y else int((sel_y - self.y_pos) / abs(sel_y - self.y_pos))
            else:
                deltas = [0, 0]
        counter = 0
        cell = field.canvas[self.y_pos + deltas[1]][self.x_pos + deltas[0]]
        while isinstance(cell, Prey) or isinstance(cell, Synth):
            if counter == 15:
                deltas = [0, 0]
                break
            deltas = [randint(-1, 1), randint(-1, 1)]
            deltas = self.check_edges(deltas)
            counter += 1
        return deltas


class Food:
    def __init__(self, x_pos, y_pos, synthetic=False):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.synthetic = synthetic
        self.eaten = False

    def __repr__(self):
        return 'O'

    def eat(self):
        self.eaten = True


class Field:
    def __init__(self, width, height):
        self.canvas = [[''] * width for _ in range(height)]
        self.empty = []
        self.__update_empty()

    def __update_empty(self):
        self.empty = []
        for row in enumerate(self.canvas):
            for cell in enumerate(row[1]):
                self.empty.append((cell[0], row[0]))


class Session:
    def __init__(self):
        self.width = WIDTH_PX // CELL_SIZE
        self.height = HEIGHT_PX // CELL_SIZE
        self.screen = Screen(WIDTH_PX, HEIGHT_PX)

        self.epoch = 0
        self.entities = []
        self.foods = []
        self.field = Field(self.width, self.height)
        self.summon(INIT_PREY, INIT_SYNTH, INIT_FOOD)

    # Отладочная фукнция
    def draw(self):
        offset = WIDTH_PX
        for y, row in enumerate(self.field.canvas):
            for x, cell in enumerate(row):
                if cell != '' and not isinstance(cell, Food) and cell.alive:
                    cell_position_size = (
                        cell.x_pos * self.screen.cell_size + 1, cell.y_pos * self.screen.cell_size + 1,
                        self.screen.cell_size - 2,
                        self.screen.cell_size - 2)
                    if isinstance(cell, Prey):
                        color = (0, 0, 255)
                    elif isinstance(cell, Synth):
                        color = (0, 255, 0)
                    else:
                        color = (100, 100, 0)
                    pygame.draw.rect(self.screen.canvas, color, cell_position_size)
                elif isinstance(cell, Food):
                    if not cell.eaten:
                        cell_position_size = (
                            cell.x_pos * self.screen.cell_size + FOOD_POS_OFFSET + 1,
                            cell.y_pos * self.screen.cell_size + FOOD_POS_OFFSET + 1,
                            self.screen.cell_size - 2 * (FOOD_POS_OFFSET - 1),
                            self.screen.cell_size - 2 * (FOOD_POS_OFFSET - 1))
                        color = (0, 255, 255)
                        pygame.draw.rect(self.screen.canvas, color, cell_position_size)
                elif (x, y) in self.field.empty:
                    color = (255, 255, 255)
                    cell_position_size = (
                        offset + x * self.screen.cell_size, y * self.screen.cell_size,
                        self.screen.cell_size,
                        self.screen.cell_size)
                    pygame.draw.rect(self.screen.canvas, color, cell_position_size)

    def log(self, fps, full=False):
        synths = len([ent for ent in self.entities if isinstance(ent, Synth)])
        print(
            f'Ent:{len(self.entities) - synths}  Synths:{synths}  Foods:{len(self.foods)}  Epoch:{self.epoch}  FPS:{fps}')
        if full:
            print('Animals:')
            for animal in self.entities:
                print(f'x:{animal.x_pos} y:{animal.y_pos}')
            print('Foods:')
            for animal in self.foods:
                print(f'x:{animal.x_pos} y:{animal.y_pos}')
            print('________________________')

    def summon(self, *args):
        classes = [Prey, Synth, Food]
        for index, entity in enumerate(classes):
            for _ in range(args[index]):
                x_pos, y_pos = self.generate_empty_position()
                if x_pos != -1:
                    new = entity(x_pos, y_pos)
                    self.field.canvas[y_pos][x_pos] = new
                    self.field.empty.remove((x_pos, y_pos))

    def generate_empty_position(self):
        if self.field.empty:
            index = randint(0, len(self.field.empty) - 1)
            x = self.field.empty[index][0]
            y = self.field.empty[index][1]
            return x, y
        else:
            return -1, -1

    def display(self):
        for y, row in enumerate(self.field.canvas):
            for x, cell in enumerate(row):
                if cell != '' and not isinstance(cell, Food) and cell.alive:
                    cell_position_size = (
                        cell.x_pos * self.screen.cell_size, cell.y_pos * self.screen.cell_size,
                        self.screen.cell_size,
                        self.screen.cell_size)
                    if isinstance(cell, Prey):
                        color = (0, 255, 0)
                    elif isinstance(cell, Synth):
                        color = (0, 120, 180)
                    else:
                        color = (0, 0, 0)
                    pygame.draw.rect(self.screen.canvas, color, cell_position_size)
                elif isinstance(cell, Food):
                    if not cell.eaten:
                        cell_position_size = (
                            cell.x_pos * self.screen.cell_size + FOOD_POS_OFFSET,
                            cell.y_pos * self.screen.cell_size + FOOD_POS_OFFSET,
                            self.screen.cell_size - 2 * FOOD_POS_OFFSET,
                            self.screen.cell_size - 2 * FOOD_POS_OFFSET)
                        color = (255, 223, 0)
                        pygame.draw.rect(self.screen.canvas, color, cell_position_size)

    def update_arrs(self):
        self.entities = []
        self.foods = []
        for row in self.field.canvas:
            for cell in row:
                if isinstance(cell, Prey) or isinstance(cell, Synth) and cell.alive:
                    self.entities.append(cell)
                elif isinstance(cell, Food) and not cell.eaten:
                    self.foods.append(cell)

    def main_loop(self):
        start_time = time.time()
        self.update_arrs()
        for ent in self.entities:
            ent.pass_epoch(self)
        self.screen.canvas.fill((15, 15, 15))
        self.display()
        # self.draw()
        self.screen.update()
        self.epoch += 1
        fps = 1 // (time.time() - start_time)
        self.log(fps)
