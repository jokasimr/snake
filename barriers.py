import numpy as np


def borders(grid):
    X, Y = grid
    barrier = np.zeros((X, Y))
    barrier[0, :] = 1
    barrier[X-1, :] = 1
    barrier[:, 0] = 1
    barrier[:, Y-1] = 1
    return barrier
