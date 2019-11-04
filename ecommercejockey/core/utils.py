from functools import reduce
from math import floor


def chunkify_list(lst, chunk_size=100):
    chunk_count = floor(len(lst) / chunk_size)
    chunkified = []
    for x in range(chunk_count):
        chunk = lst[x * chunk_size:x * chunk_size + chunk_size]
        chunkified.append(chunk)
    chunk = lst[chunk_count * chunk_size:]
    if chunk:
        chunkified.append(chunk)
    return chunkified


def rgetattr(obj, attr, *args):
    # noinspection PyShadowingNames
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return reduce(_getattr, [obj] + attr.split('.'))
