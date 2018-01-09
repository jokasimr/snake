from collections import deque
from itertools import cycle
import random
import numpy

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

Pos = numpy.array

LEFTRIGHT = deque(['up', 'right', 'down', 'left'])

DIRECTIONS = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0)
        }

REV_DIRECTIONS = {v: k for k, v in DIRECTIONS.items()}

for k, v in DIRECTIONS.items():
    DIRECTIONS[k] = Pos(v)

right = numpy.array([[0, -1], [1, 0]])


class Snake(object):

    def __init__(self, head, direction='up', length=5, color=RED):
        self.direction = DIRECTIONS[direction]
        self.color = color

        head = Pos(head)
        self.body = deque((head,))

        self.energy = length

    @property
    def head(self):
        return tuple(self.body[0])

    @property
    def tail(self):
        return tuple(map(tuple, self.body))[1:]

    def change_direction(self, direction):
        self.direction = DIRECTIONS[direction]

    def step(self):
        self.body.appendleft(self.head+self.direction)
        if self.energy:
            self.energy -= 1
            return None
        else:
            return tuple(self.body.pop())

    def eat(self, energy):
        self.energy += energy

    def update_direction(self, grid):
        pass

    def turn(self, left_right):
        if left_right == 'left':
            self.direction = -right.dot(self.direction.T)
        elif left_right == 'right':
            self.direction = right.dot(self.direction.T)


class ConfusedSnake(Snake):
    def __init__(self, *args, confusion=0.1, **kwargs):
        self.confusion = confusion
        super().__init__(*args, **kwargs)

    def update_direction(self, grid):
        if random.random() < self.confusion:
            self.turn(random.choice(['left', 'right']))


class NotStupidSnake(ConfusedSnake):
    '''Still a slightly confused snake,
    but at least it knows how to take care
    of itself in the simplest of ways:
    by looking in front of its face.

    But it's actually slightly smarter than that.
    Because when it turns to avoid obstacles, it alternates
    between turning left and right and thus avoids getting
    looped up in itself by making the same turn to many times.
    '''
    def __init__(self, *args, **kwargs):
        self.turning_direction = cycle(('left', 'right'))
        super().__init__(*args, **kwargs)

    def update_direction(self, grid):
        super().update_direction(grid)
        self.recurse_save(grid, next(self.turning_direction), 0)

    def recurse_save(self, grid, direction, depth):
        if depth > 4 or grid[tuple(self.head+self.direction)] in (0, 4):
            pass
        else:
            self.turn(direction)
            self.recurse_save(grid, direction, depth+1)
