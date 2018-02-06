import numpy as np
from itertools import chain
import settings as S
from time import sleep


def neighboors(point, grid):
    xsup, ysup = grid.shape
    IS_FREE = (S.CANDY, S.AIR)
    x, y = point
    if x+1 < xsup and grid[(x+1, y)] in IS_FREE:
        yield (x+1, y)
    if y+1 < ysup and grid[(x, y+1)] in IS_FREE:
        yield (x, y+1)
    if x-1 > 0 and grid[(x-1, y)] in IS_FREE:
        yield (x-1, y)
    if y-1 > 0 and grid[(x, y-1)] in IS_FREE:
        yield (x, y-1)


class Point(object):
    '''A position on a grid, it's part of a chain - a road.
    It has neighboors, four of them at most, but it might have fewer
    if it's in a corner.'''
    def __init__(self, point, road, grid):
        self.head = point
        self.road = chain(road, (point,))
        self.grid = grid
        self.neighboors = neighboors(point, grid)

    def children(self):
        for neighboor in self.neighboors:
            yield Point(neighboor, self.road, self.grid)

    '''Neccesary for putting the Points in a Set'''
    def __hash__(self):
        return hash(self.head)

    '''Neccesary for putting the Points in a Set'''
    def __eq__(self, o):
        return self.head == o.head

    def __repr__(self):
        return str(self.head)


def search_candy(start, grid):
    '''Searches the grid in all directions,
    stopping when a candy is found.
    1. Find the neighbors of the starting-point
    2. Those are now our frontiers
    3a. Do any of them contain candy? If so, return the path to it!
    3b. Find all of the unvisited neighboors of the frontier points.
    4. Go to 2.
    Returns
        The path (a sequence of positions) to the first candy found.'''
    start = Point(start, [], grid)
    visited = {start}
    children = set()
    frontiers = {start}
    while len(frontiers) > 0:
        for frontier in frontiers:
            if grid[frontier.head] == S.CANDY:
                return frontier.road
            children.update(frontier.children())
        visited.update(frontiers)
        frontiers = children.difference(visited)
        # paint(visited, frontiers, grid)
        children = set()
    return None


def secure_path(start, grid, depth, depth_lim, visited={}):
    '''Recursively checks if there is any chance of survival
    in the next $depth steps if the snake goes to the $start position.'''
    if depth == 0:
        safe_routes = []
    if depth > depth_lim:
        return True
    for neighboor in neighboors(start, grid):
        if neighboor in visited:
            continue
        visited.add(neighboor)
        path = secure_path(neighboor, grid, depth+1, depth_lim, visited)
        visited.remove(neighboor)
        if path:
            if depth == 0:
                safe_routes.append(neighboor)
            else:
                return True
    if depth == 0:
        return safe_routes
    return False
