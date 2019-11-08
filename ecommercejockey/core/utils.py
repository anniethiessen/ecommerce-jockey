import base64
import hmac
import hashlib
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


def get_hmac(body, secret):
    _hash = hmac.new(secret.encode('utf-8'), body, hashlib.sha256)
    return base64.b64encode(_hash.digest()).decode()


def hmac_is_valid(body, secret, hmac_to_verify):
    return get_hmac(body, secret) == hmac_to_verify
