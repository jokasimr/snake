from itertools import tee


def GroupDict(mapping):
    '''Takes a mapping, ((key, value), (key, value) ... )
       and returns a dict with the values grouped by key.

    Returns:
        dict( key : set(value1, value2 ... ) )
    '''
    dictionary = dict()
    for k, v in mapping:
        if k in dictionary:
            dictionary[k].add(v)
            continue
        dictionary[k] = {v}
    return dictionary


def teemap(key, iterable):
    it, itp = tee(iterable)
    return map(key, it), itp


def group(iterable, key):
    return GroupDict(zip(*teemap(key, iterable)))
