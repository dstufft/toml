import datetime

import anytree

from ._utils import is_not_noise, merge


class Node(anytree.NodeMixin):

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


class Document(Node):

    def compile(self):
        output = {}
        for node in filter(is_not_noise, self.children):
            output = merge(output, node.compile())
        return output


class Statement(Node):

    def compile(self):
        key, op, value = filter(is_not_noise, self.children)
        assert isinstance(op, Assignment)
        return {key.compile(): value.compile()}


class TableName(Node):

    def compile(self):
        children = list(filter(is_not_noise, self.children))
        openb, name_parts, closeb = children[0], children[1:-1], children[-1]

        assert isinstance(openb, OpenBracket)
        assert isinstance(closeb, CloseBracket)

        return [n.compile() for n in name_parts]


class Table(Node):

    def compile(self):
        output = {}

        # The very first item in our children should *always* be a TableName
        # node.
        assert isinstance(self.children[0], TableName)
        name = self.children[0].compile()

        # Go through all of the names and generate our dictionary values as
        # well as get the "current" (e.g. the one we're currently acting on")
        # dictionary.
        current, previous = output, None
        for level in name:
            previous = current
            current[level] = current = {}

        # Now that we have our current dictionary, we can go through the rest
        # of the children and compile them.
        for node in filter(is_not_noise, self.children[1:]):
            previous[level] = merge(previous[level], node.compile())

        return output


class Array(Node):
    pass


class ContentNode(Node):

    def __init__(self, content, **kwargs):
        self.content = content
        return super(ContentNode, self).__init__(**kwargs)

    def __repr__(self):
        return "{}(content={!r})".format(self.__class__.__name__, self.content)


class LineEnd(ContentNode):
    pass


class Whitespace(ContentNode):
    pass


class Comment(ContentNode):
    pass


class OpenBracket(ContentNode):
    pass


class CloseBracket(ContentNode):
    pass


class Comma(ContentNode):
    pass


class Dot(ContentNode):
    pass


class BareKey(ContentNode):

    def compile(self):
        return self.content


class Assignment(ContentNode):
    pass


class BasicString(ContentNode):

    def compile(self):
        # TODO: How do I actually complile a string? HALP.
        return self.content[1:-1]


class Integer(ContentNode):
    pass


class Boolean(ContentNode):
    pass


class OffsetDateTime(ContentNode):

    def compile(self):
        if self.content.endswith("Z"):
            return datetime.datetime.strptime(
                self.content, "%Y-%m-%dT%H:%M:%SZ")
        else:
            assert self.content[-3] == ":"
            content = self.content[:-3] + self.content[-2:]
            return datetime.datetime.strptime(content, "%Y-%m-%dT%H:%M:%S%z")
