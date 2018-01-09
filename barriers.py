import numpy as np


def borders(grid):
    X, Y = grid
    barrier = np.zeros((X, Y))
    barrier[0, :] = 1
    barrier[X-1, :] = 1
    barrier[:, 0] = 1
    barrier[:, Y-1] = 1
    return barrier


def four_rooms(grid, door=(0.8, 1)):
    X, Y = grid
    d0, d1 = door
    xm, ym = X//2, Y//2

    barrier = borders(grid)
    barrier[xm, :] = 1
    barrier[:, ym] = 1

    dx0, dx1, dy0, dy1 = tuple(map(int, (d0*X/2, d1*X/2, d0*Y/2, d1*Y/2)))
    barrier[xm, dy0:dy1] = 0
    barrier[xm, Y-dy1:Y-dy0] = 0
    barrier[dx0:dx1, ym] = 0
    barrier[X-dx1:X-dx0, ym] = 0
    return barrier


def random_barriers(grid, d=0.05):
    barrier = borders(grid)
    random = np.floor(np.random.random(grid) + d)
    random[barrier == 1] = 1
    return random
