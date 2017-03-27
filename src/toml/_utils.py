import collections
import copy
import itertools

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


def is_not_noise(node):
    from ._nodes import Whitespace, Comment, LineEnd, Dot, Comma
    return not isinstance(node, (Whitespace, Comment, LineEnd, Dot, Comma))


def merge(to, from_):
    output = copy.deepcopy(to)
    for key, value in from_.items():
        if (isinstance(output.get(key), collections.MutableMapping)
                and isinstance(value, collections.MutableMapping)):
            value = merge(output[key], value)
        output[key] = value
    return output


def with_whitespace(pg, format_):
    left, right = format_.split(" : ", 1)
    tokens = right.split()

    # We need to take our right side tokens, and expand them into a list of
    # tokens that exhaustively list all possible combinations with and without
    # whitespace. If we have less than two tokens on the right hand side, then
    # this expansion is just the same as the format that was passed in since
    # without at least two tokens there is no place to insert whitespace.
    if len(tokens) < 2:
        expanded = [format_]
    else:
        expanded = []
        for pat in itertools.product([True, False], repeat=len(tokens) - 1):
            row = []
            for token, use_ws in zip_longest(tokens, pat, fillvalue=None):
                row.append(token)
                if use_ws:
                    row.append("WHITESPACE")
            expanded.append("{} : {}".format(left, " ".join(row)))

    # Now, make a decorator that, when called, will call our pg_production
    # function for each value in our expanded list to generate every possible
    # set of rules for whitespace with the given format string.
    def deco(fn):
        for format_ in expanded:
            fn = pg.production(format_)(fn)
        return fn

    return deco
