import time


def randint(a, b):
    integer = (int(time.time() * 10000)) % (b - a + 1) + a
    return integer
