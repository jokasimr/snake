from collections import deque
from random import random, choice
import numpy as np
import settings
from search import search_candy, secure_path, neighboors


Pos = np.array

DIRECTIONS = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0)
        }

for k, v in DIRECTIONS.items():
    DIRECTIONS[k] = Pos(v)

right = np.array([[0, -1], [1, 0]])


class Snake(object):

    def __init__(self, head, direction='up', length=5, color=settings.RED):
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
        if random() < self.confusion:
            self.turn(choice(['left', 'right']))
        super().update_direction(grid)


class SafeSnake(Snake):
    '''This snake knows how to take care
    of itself in the simplest of ways:
    by looking in front of its face.

    But it's actually slightly smarter than that.
    Because when it turns to avoid obstacles, it alternates
    between turning left and right and thus avoids getting
    looped up in itself by making the same turn to many times.
    '''
    def __init__(self, *args, **kwargs):
        self.last_turn = 'right'
        self.next_turn = 'left'
        super().__init__(*args, **kwargs)

    def update_direction(self, grid):
        super().update_direction(grid)
        self.recurse_save(grid, self.next_turn, 0)

    def recurse_save(self, grid, direction, depth):
        if depth > 3 or grid[tuple(self.head+self.direction)] in \
                (settings.AIR, settings.CANDY):
            if depth == 1:
                self.last_turn, self.next_turn = self.next_turn, self.last_turn
        else:
            self.turn(direction)
            self.recurse_save(grid, direction, depth+1)


class NotStupidSnake(ConfusedSnake, SafeSnake):
    '''Still kind of confused,
    but it's also kind of safe.'''
    pass


class FoodSnake(SafeSnake):
    '''Sees the food over a long distance and turns
    towards the closest of them.'''
    def distance(self, dx):
        return np.abs(dx).sum(axis=1)

    def update_direction(self, grid):
        # Step 1: Find the candies
        candies = np.vstack(np.where(grid == settings.CANDY)).T
        if candies.size > 0:
            # Step 2: Calculate distances between candies and me
            distances = self.distance(candies-self.head)
            # Step 3: Aquire candy-target
            target = candies[np.argmin(distances)]
            # In what direction can I find it?
            direction = np.sign(target-self.head)
            # Try to turn in that direction, 4 tries maximum
            for tries in range(4):
                # Is the direction correct?
                if direction.dot(self.direction) == 1:
                    if tries == 1:
                        # If I tried once and succeded, then I've turned in
                        # the self.next_turn direction and should notify the safe
                        # part of me of that.
                        self.last_turn, self.next_turn = (self.next_turn,
                                                          self.last_turn)
                    break
                self.turn(self.next_turn)
        super().update_direction(grid)


class SecureSnake(Snake):
    '''Uses the secure_path search algorithm to check
    if it's going in a direction that means certain death.
    If so, it changes direction.'''
    def turn_to_fit(self, path, grid):
        pick = Pos(choice(path))
        self.direction = pick-self.head
        assert tuple(self.head + self.direction) in path

    def update_direction(self, grid):
        depth_lim = 25
        path = tuple(secure_path(self.head, grid, 0, depth_lim, set()))
        c = 0
        while not path and depth_lim-c > 0:
            c += 1
            path = tuple(secure_path(self.head, grid, 0, depth_lim-c, set()))
        if path:
            if not tuple(self.head + self.direction) in path:
                self.turn_to_fit(path, grid)
        super().update_direction(grid)


class SuperSnake(SecureSnake):
    '''Searches the grid for paths towards food
    in a more sofisticated manner than FoodSnake.
    And protects itself by also being a SecureSnake'''
    def distance(self, dx):
        return np.abs(dx).sum(axis=1)

    def update_direction(self, grid):
        road = search_candy(tuple(self.head), grid)
        if road:
            next(road)
            next_step = next(road)
            self.direction = Pos(next_step)-self.head
        super().update_direction(grid)
