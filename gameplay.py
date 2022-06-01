import time

import pygame
from graphics import Screen, CELL_SIZE
from random import randint

WIDTH_PX = 1000
HEIGHT_PX = 600
FOOD_POS_OFFSET = CELL_SIZE * 0.2
INIT_ENT = 20
INIT_FOOD = 1500

AGE_LIMIT = 120

FOOD_COST = 15
ORGANIC_COST = 43
MOVE_COST = 1

PREY_START_ENERGY = 20
PREY_ENERGY_LIMIT = 50
PREY_CHILD_COST = 20

PREDATOR_START_ENERGY = 20
PREY_CHILD_COST = 20


class Animal():

    def die(self, session):
        self.alive = False
        session.field.canvas[self.y_pos][self.x_pos] = Food(self.x_pos, self.y_pos, True)

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
            if session.field.canvas[self.y_pos][self.x_pos].organic:
                self.energy += ORGANIC_COST
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
            deltas[0] = 0 if self.x_pos == sel_x else int(
                (sel_x - self.x_pos) / abs(sel_x - self.x_pos))
            deltas[1] = 0 if self.y_pos == sel_y else int(
                (sel_y - self.y_pos) / abs(sel_y - self.y_pos))
        else:
            deltas = [randint(-1, 1), randint(-1, 1)]
            deltas = self.check_edges(deltas)
        counter = 0
        while isinstance(field.canvas[self.y_pos + deltas[1]][self.x_pos + deltas[0]], Prey):
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


class Predator(Animal):
    age_limit = AGE_LIMIT

    def __repr__(self):
        return 'X'

    def __init__(self, x_pos, y_pos):
        self.age = 0
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.energy = PREDATOR_START_ENERGY
        self.alive = True

    def pass_epoch(self, session):
        pass

    def calculate_move(self, field):
        pass

    def reproduce(self, field):
        selected = []
        for row in range(self.y_pos - 1, self.y_pos + 1 + 1):
            for cell in range(self.x_pos - 1, self.x_pos + 1 + 1):
                if (HEIGHT_PX // CELL_SIZE) > row >= 0 and (
                        WIDTH_PX // CELL_SIZE) > cell >= 0 and row != self.y_pos and cell != self.x_pos:
                    if field.canvas[row][cell] == '':
                        sel_x = cell
                        sel_y = row
                        selected.append((sel_x, sel_y))
        if selected:
            sel_x, sel_y = selected[randint(0, len(selected) - 1)]
            new = Prey(sel_x, sel_y)


class Food:
    def __init__(self, x_pos, y_pos, organic=False):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.organic = organic
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

    def print(self):
        for row in self.canvas:
            for cell in row:
                print(cell, end=' ')
            print()
        print(self.empty)

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
        self.summon(INIT_ENT, 50, INIT_FOOD)

    def summon(self, entities, predators, foods):
        for _ in range(foods):
            x_pos, y_pos = self.generate_empty_position()
            if x_pos != -1:
                new = Food(x_pos, y_pos)
                self.field.canvas[y_pos][x_pos] = new
                self.field.empty.remove((x_pos, y_pos))

        for _ in range(entities):
            x_pos, y_pos = self.generate_empty_position()
            if x_pos != -1:
                new = Prey(x_pos, y_pos)
                self.field.canvas[y_pos][x_pos] = new
                self.field.empty.remove((x_pos, y_pos))

        for _ in range(predators):
            x_pos, y_pos = self.generate_empty_position()
            if x_pos != -1:
                new = Predator(x_pos, y_pos)
                self.field.canvas[y_pos][x_pos] = new
                self.field.empty.remove((x_pos, y_pos))

    def extinct(self, count):
        pass

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
                if isinstance(cell, Prey) and cell.alive:
                    cell_position_size = (
                        cell.x_pos * self.screen.cell_size, cell.y_pos * self.screen.cell_size,
                        self.screen.cell_size,
                        self.screen.cell_size)
                    entity_type = str(type(cell))[str(type(cell)).find('.') + 1:str(type(cell)).rfind("'")]
                    if entity_type == 'Prey':
                        color = (0, 255, 0)
                    elif entity_type == 'Predator':
                        color = (255, 0, 0)
                    else:
                        color = (100, 100, 0)
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

    def log(self, fps, full=False):
        print(f'Ent:{len(self.entities)}  Foods:{len(self.foods)}  Epoch:{self.epoch}  FPS:{fps}')
        if full:
            self.field.print()
            print('Animals:')
            for animal in self.entities:
                print(f'x:{animal.x_pos} y:{animal.y_pos}')
            print('Foods:')
            for animal in self.foods:
                print(f'x:{animal.x_pos} y:{animal.y_pos}')
            print('________________________')

    def update_arrs(self):
        self.entities = []
        self.foods = []
        for row in self.field.canvas:
            for cell in row:
                if isinstance(cell, Prey) and cell.alive:
                    self.entities.append(cell)
                elif isinstance(cell, Food) and not cell.eaten:
                    self.foods.append(cell)

    def main_loop(self):
        start_time = time.time()
        self.update_arrs()
        for ent in self.entities:
            ent.pass_epoch(self)
        self.screen.canvas.fill((0, 0, 0))
        self.display()
        self.screen.update()
        self.epoch += 1
        fps = 1 // (time.time() - start_time)
        self.log(fps)
