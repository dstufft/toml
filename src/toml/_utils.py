import collections
import copy


def is_not_noise(node):
    from ._nodes import Whitespace, Comment, LineEnd, Dot
    return not isinstance(node, (Whitespace, Comment, LineEnd, Dot))


def merge(to, from_):
    output = copy.deepcopy(to)
    for key, value in from_.items():
        if (isinstance(output.get(key), collections.MutableMapping)
                and isinstance(value, collections.MutableMapping)):
            value = merge(output[key], value)
        output[key] = value
    return output
