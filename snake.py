from collections import deque
from itertools import cycle
from random import random, choice
import numpy as np
import scipy.ndimage as scn
import settings as S
from search import search_candy, secure_path, neighboors
from time import sleep


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

    def __init__(self, head, direction='up', length=5, color=S.RED):
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
        if depth > 3 or grid[tuple(self.head+self.direction)] in (S.AIR, S.CANDY):
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
    def distance(self, dx):
        return np.abs(dx).sum(axis=1)

    def update_direction(self, grid):
        # Step 1: Find the candies
        candies = np.vstack(np.where(grid == S.CANDY)).T
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
                        # the self.next direction and should notify the safe
                        # part of me of that.
                        self.last_turn, self.next_turn = (self.next_turn,
                                                          self.last_turn)
                    break
                self.turn(self.next_turn)
        super().update_direction(grid)


class SecureSnake(Snake):
    def turn_to_fit(self, path, grid):
        pick = Pos(choice(path))
        self.direction = pick-self.head
        assert tuple(self.head + self.direction) in path

    def update_direction(self, grid):
        depth_lim = 25
        path = tuple(secure_path(self.head, grid, 0, depth_lim, set()))
        c = 0
        while len(path) == 0 and depth_lim-c > 0:
            c += 1
            path = tuple(secure_path(self.head, grid, 0, depth_lim-c, set()))
        if path:
            if not tuple(self.head + self.direction) in path:
                self.turn_to_fit(path, grid)
        super().update_direction(grid)


class SuperSnake(SecureSnake):
    def distance(self, dx):
        return np.abs(dx).sum(axis=1)

    def update_direction(self, grid):
        road = search_candy(tuple(self.head), grid)
        if road:
            next(road)
            next_step = next(road)
            self.direction = Pos(next_step)-self.head
        super().update_direction(grid)


class MySnake(ConfusedSnake):
    def __init__(self, *args, confusion=0.1, **kwargs):
        super().__init__(*args, confusion=0.1, **kwargs)
        self.rand = random
    
    def set_direction(self,direction):
        self.direction = DIRECTIONS[direction]

    def find_candy(self,grid):
        loc = np.vstack(np.where(grid == 4)).T
        if len(loc) != 0:
            dist = np.sum((loc-self.head)**2, axis=1) 
            ind = np.argmin(dist)
            return loc[ind]
        else:
            return self.head+self.direction
        
    def update_direction(self,grid):
        candy = self.find_candy(grid)
        old_dir = self.direction
        
        
        
        if self.head[0] == candy[0]:
            if self.head[1] > candy[1]:
                self.set_direction('up')   
            else:
                self.set_direction('down')
        elif self.head[0] > candy[0]:
            self.set_direction('left')
        else:
            self.set_direction('right')
        
            
        grid_copy = np.sign(grid.copy())
        labeled_array, num_features = scn.label(grid_copy-1)
        
            
        if np.linalg.norm(old_dir - self.direction) < 0.02  and grid[tuple(self.head+self.direction)] == 2:
          
           #Get left label
           self.turn('left')
           left_label = labeled_array[tuple(self.head+self.direction)]
           self.turn('right')
           
           #Get Right label
           self.turn('right')
           right_label = labeled_array[tuple(self.head+self.direction)]
           self.turn('left')
           
           size_left = np.count_nonzero(labeled_array == left_label)
           size_right = np.count_nonzero(labeled_array == right_label)
           
           
         
           if size_left > size_right:
               self.turn('left')
           #    print('turn left')
           else:
               self.turn('right')
           #    print('turn right')
           
        
        for i in range(3):
            if grid[tuple(self.head+self.direction)] != 0 and grid[tuple(self.head+self.direction)] != 4:
                self.turn('left')
