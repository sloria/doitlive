import sys

PY2 = int(sys.version[0]) == 2


def ensure_utf8(string):
    return string.encode("utf-8") if PY2 else string
