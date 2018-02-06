from itertools import chain
from random import choice
# from time import sleep
import pygame
from pygame.locals import KEYDOWN, K_RIGHT, K_LEFT
import numpy as np
from utils import group
from snake import Snake, ConfusedSnake, NotStupidSnake, SafeSnake, \
        FoodSnake, SuperSnake, SecureSnake
from barriers import borders, four_rooms, random_barriers, test_barrier
import settings

# # # # #  GAME SETUP # # # # # # # # # # # # # #
FPS = 30
# screen pixel-size
size = (600, 600)
# world size in grid squares
grid = (100, 100)
# barriers contains the walls of the current map
barriers = four_rooms(grid, door=(0.6, 0.8))
# Player snake setup
player_controlled_snake = SuperSnake((10, 10), direction='down',
                                     color=settings.BLUE)
##################################################

# pixel widths of the grid squares
DX = size[0] // grid[0]
DY = size[1] // grid[1]

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Snake")

# Set containing the living snakes
snakes = {player_controlled_snake}
# Set containing the dead snakes
dead = set()
# Set containing candy
candies = set()


def pos(p):
    '''Args
        p: A game gridpoint.
    Returns
        The screen gridpoint.'''
    x, y = p
    return (x*DX, y*DY)


def rect(p):
    '''Args
        p: A game gridpoint.
    Returns
        A pygame Rect, the grid-square starting at p.'''
    return pygame.Rect(pos(p), (DX, DY))


def where(grid, value):
    '''Returns all positions on the grid where it has the value.
    Args
        grid: 2d numpy-array containing values.
        value: what to search for on the grid.
    Returns
        An iterable over the positions.
    '''
    return zip(*np.where(grid == value))


def random_free_spot():
    '''Returns a random non-occupied positions on the grid.'''
    no_walls = set(where(barriers, settings.AIR))
    heads = (snake.head for snake in snakes)
    bodies = chain(*(snake.tail for snake in snakes))
    free_positions = no_walls - set(chain(bodies, heads))
    return choice(tuple(free_positions))


def generate_world(candies, snakes, barrier):
    '''Creates a snapshot of the world, where all barriers, snakes and candies
    can be located. This is given to the snakes as input to let them make
    informed decisions about where to move.

    Returns
        2d numpy array that represents the content at every grid-square.
    '''
    world = barrier.copy()
    bodies = tuple(zip(*chain(*(s.tail for s in snakes))))
    if bodies:
        world[bodies] = settings.BODY
    heads = tuple(zip(*(s.head for s in snakes)))
    if heads:
        world[heads] = settings.HEAD
    for c in candies:
        world[c] = settings.CANDY
    return world


def fill_barriers(barrier):
    ''' Fill the grid with color'''
    for p in where(barriers, settings.WALL):
        screen.fill(settings.WALL_COLOR, rect(p))


def random_snakes(cls, n):
    '''Utility function to create some random snakes of a specific class.'''
    for _ in range(5):
        pos = random_free_spot()
        direction = choice(('left', 'right', 'up', 'down'))
        snake = cls(pos, direction=direction, color=settings.WHITE)
        yield snake


# add some snakes
snake_factory = random_snakes(FoodSnake, 5)
snakes.update(tuple(snake_factory))

# fill borders and place snakes on the screen
fill_barriers(barriers)
for snake in snakes:
    screen.fill(snake.color, rect(snake.head))

done = False

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
    changes = {change for change in map(lambda s: s.step(), snakes)
               if change is not None}

    # Let's see who died this step
    died = set()

    '''Check head on head collisions
        1. Group snakes by head-position
        2. Remove any snakes belonging to a group with more than one member'''
    position_grouping = group(snakes, lambda snake: snake.head)
    for snakes_at_position in position_grouping.values():
        if len(snakes_at_position) > 1:
            print(*snakes_at_position)
            died.update(snakes_at_position)

    '''Check other collisions
        1. Either you're already dead - then continue
        2. or you've collided with a wall or another snake - then you're dead
        3. or you live!'''
    bodies = set(chain(*(snake.tail for snake in snakes)))
    for snake in snakes:
        if snake in died:
            continue
        if barriers[snake.head] == settings.WALL or snake.head in bodies:
            died.add(snake)
            print(s)

    snakes.difference_update(died)
    dead.update(died)

    # Remove the bodies of dead snakes.
    # Only the tails needs to be removed - the heads haven't been painted yet.
    for snake in died:
        changes.update(snake.tail)

    # Repaint background where worms have moved away or died.
    for change in changes:
        screen.fill(settings.BLACK, rect(change))

    # Feed snakes and update candies if any have been eaten.
    for snake in snakes:
        if snake.head in candies:
            snake.eat(settings.CANDY_ENERGY)
            candies.remove(snake.head)

    if len(candies) < settings.NUMBER_OF_CANDY:
        candy = random_free_spot()
        candies.add(candy)
        screen.fill(settings.CANDY_COLOR, rect(candy))

    # move the heads of living snakes
    for snake in snakes:
        screen.fill(snake.color, rect(snake.head))

    pygame.display.flip()

    # limit frames per second
    clock.tick(FPS)

pygame.quit()
