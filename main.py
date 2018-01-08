import itertools
from utils import group
from snake import Snake, ConfusedSnake
import pygame
from pygame.locals import *

# define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

pygame.init()

# world pixel-size
size = (400, 400)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Snake")

# how large is the world (in grid squares)
grid = (200, 200)

# pixel widths of the grid squares
DX = int(size[0] / grid[0])
DY = int(size[1] / grid[1])


player_controlled_snake = Snake((50, 50), direction='down')

# set containing the living snakes
snakes = {
        player_controlled_snake,
        ConfusedSnake((100, 150)),
        ConfusedSnake((100, 50), direction='down', color=GREEN),
        ConfusedSnake((150, 140), direction='up', color=WHITE, length=50),
        ConfusedSnake((200, 100), direction='left', color=GREEN),
        ConfusedSnake((100, 100), direction='left', color=RED),
        ConfusedSnake((150, 150), direction='right', color=WHITE)
        }

# set containing the dead snakes
dead = set()


def pos(p):
    '''Returns the pixel numbers of gridpoint (x,y)'''
    x, y = p
    return (x*DX, y*DY)


def rect(p):
    '''Returns a pygame Rect of the gridsquare at (x,y)'''
    return pygame.Rect(pos(p), (DX, DY))


done = False
clock = pygame.time.Clock()

while not done:
    # main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                player_controlled_snake.change_direction('right')
            elif event.key == K_UP:
                player_controlled_snake.change_direction('up')
            elif event.key == K_LEFT:
                player_controlled_snake.change_direction('left')
            elif event.key == K_DOWN:
                player_controlled_snake.change_direction('down')

    for s in snakes:
        s.update_direction(None)

    change = {s: {s.step()} for s in snakes}

    died = set()
    # head on collisions
    heads = group(snakes, lambda s: s.head)
    for k, v in heads.items():
        if len(v) > 1:
            print(*v)
            died.update(v)

    # head body collissions
    bodies = list(itertools.chain(*(s.tail for s in snakes)))
    for s in snakes:
        if s in died:
            continue
        if s.head in bodies:
            died.add(s)
            print(s)

    snakes.difference_update(died)
    dead.update(died)

    # remove the bodies of dead snakes
    for s in died:
        change[s].update([*s.tail])

    for s, c in change.items():
        for p in c:
            if p:
                screen.fill(BLACK, rect(p))

    # move the heads of living snakes
    for s in snakes:
        screen.fill(s.color, rect(s.head))

    pygame.display.flip()

    # limit frames per second
    clock.tick(30)

pygame.quit()
