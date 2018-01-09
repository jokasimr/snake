from itertools import chain
from random import choice
# from time import sleep
import pygame
from pygame.locals import KEYDOWN, K_RIGHT, K_LEFT
import numpy as np
from utils import group
from snake import Snake, ConfusedSnake, NotStupidSnake
from barriers import borders, four_rooms, random_barriers

# define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# constants
AIR = 0
WALL = 1
BODY = 2
HEAD = 3
CANY = 4

WALL_COLOR = WHITE
CANDY_COLOR = RED

CANDY_ENERGY = 10
NUMBER_OF_CANDY = 10

pygame.init()

# world pixel-size
size = (600, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Snake")

# how large is the world (in grid squares)
grid = (100, 100)
# barriers contains the walls of the current map
barriers = random_barriers(grid)

# pixel widths of the grid squares
DX = int(size[0] / grid[0])
DY = int(size[1] / grid[1])

player_controlled_snake = Snake((5, 5), direction='down', color=BLUE)
# set containing the living snakes
snakes = {player_controlled_snake}
# set containing the dead snakes
dead = set()
# set containing candy
candies = set()


def pos(p):
    '''
    Takes: The game gridpoint
    Returns: The screen gridpoint
    '''
    x, y = p
    return (x*DX, y*DY)


def rect(p):
    '''Returns a pygame Rect of the gridsquare at (x,y)'''
    return pygame.Rect(pos(p), (DX, DY))


def random_free_spot():
    no_walls = zip(*np.where(barriers == 0))
    bodies = chain(*(s.tail for s in snakes))
    heads = (s.head for s in snakes)
    free = tuple(set(no_walls).difference(set(chain(bodies, heads))))
    return choice(free)


def fill_borders(barrier):
    for p in zip(*np.where(barrier == 1)):
        screen.fill(WALL_COLOR, rect(p))


# this is the input given to each snake at decision time
def generate_world(candies, snakes, barrier):
    world = barrier.copy()
    bodies = tuple(zip(*chain(*(s.tail for s in snakes))))
    if bodies:
        world[bodies] = 2
    heads = tuple(zip(*(s.head for s in snakes)))
    if heads:
        world[heads] = 3
    for c in candies:
        world[c] = 4
    return world


# making a random snake factory
def random_snakes(cls):
    while True:
        pos = random_free_spot()
        direction = choice(('left', 'right', 'up', 'down'))
        snake = cls(pos, direction=direction, color=WHITE)
        yield snake


# add some snakes
snake_factory = random_snakes(NotStupidSnake)
for _ in range(30):
    snakes.add(next(snake_factory))


# fill borders and place snakes on the screen
fill_borders(barriers)
for s in snakes:
    screen.fill(s.color, rect(s.head))

done = False
clock = pygame.time.Clock()

while not done:
    # main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                player_controlled_snake.turn('right')
            elif event.key == K_LEFT:
                player_controlled_snake.turn('left')

    # Allow the snakes to change directions
    # and then make them take a step
    world = generate_world(candies, snakes, barriers)
    for s in snakes:
        s.update_direction(world.copy())
    changes = {s: {s.step()} for s in snakes}

    # Let's see who died this step
    died = set()

    # head on head collisions
    heads = group(snakes, lambda s: s.head)
    for k, v in heads.items():
        if len(v) > 1:
            print(*v)
            died.update(v)

    # other collisions
    bodies = set(chain(*(s.tail for s in snakes)))
    for s in snakes:
        if s in died:
            continue
        if barriers[s.head] == WALL or s.head in bodies:
            died.add(s)
            print(s)

    snakes.difference_update(died)
    dead.update(died)

    # remove the bodies of dead snakes
    for s in died:
        changes[s].update(s.tail)

    for change in changes.values():
        for p in change:
            if p:
                screen.fill(BLACK, rect(p))

    # update candy-position if it has been eaten
    for s in snakes:
        if s.head in candies:
            s.eat(CANDY_ENERGY)
            candies.remove(s.head)

    if len(candies) < NUMBER_OF_CANDY:
        candy = random_free_spot()
        candies.add(candy)
        screen.fill(CANDY_COLOR, rect(candy))

    # move the heads of living snakes
    for s in snakes:
        screen.fill(s.color, rect(s.head))

    pygame.display.flip()

    # limit frames per second
    clock.tick(30)

pygame.quit()
