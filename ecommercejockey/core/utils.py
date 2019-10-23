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
