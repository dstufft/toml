import datetime

import anytree

from ._utils import is_not_noise, merge


class Node(anytree.NodeMixin):

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def compile(self):
        raise NotImplementedError(
            "{} does not implement compile.".format(self.__class__.__name__))

    def render(self):
        raise NotImplementedError(
            "{} does not implement render.".format(self.__class__.__name__))


class ContainerNode(Node):
    # While all nodes can *technically* contain other nodes, a ContainerNode
    # contains additional functionality that makes it much easier to work with
    # a node whose only purpose is to act as a container.

    def render(self):
        output = []
        for node in self.children:
            output.append(node.render())
        return "".join(output)


class ContentNode(Node):
    # ContentNodes do not contain other nodes (even though they technically
    # have the ability to do so), instead they hold onto a chunk of content
    # that originally came from our parsed TOML document.

    def __init__(self, content, **kwargs):
        self.content = content
        return super(ContentNode, self).__init__(**kwargs)

    def __repr__(self):
        return "{}(content={!r})".format(self.__class__.__name__, self.content)

    def render(self):
        return self.content


class Document(ContainerNode):

    def compile(self):
        output = {}
        for node in filter(is_not_noise, self.children):
            output = merge(output, node.compile())
        return output


class ValueStatement(ContainerNode):

    def compile(self):
        key, op, value = filter(is_not_noise, self.children)
        assert isinstance(op, Assignment)
        return {key.compile(): value.compile()}


class TableName(ContainerNode):

    def compile(self):
        children = list(filter(is_not_noise, self.children))
        openb, name_parts, closeb = children[0], children[1:-1], children[-1]

        assert isinstance(openb, OpenBracket)
        assert isinstance(closeb, CloseBracket)

        return [n.compile() for n in name_parts]


class Table(ContainerNode):

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


class Array(ContainerNode):

    def compile(self):
        assert isinstance(self.children[0], OpenBracket)
        assert isinstance(self.children[-1], CloseBracket)
        return [n.compile() for n in filter(is_not_noise, self.children[1:-1])]


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


class LiteralString(ContentNode):

    def compile(self):
        # TODO: Learn 2 compile
        return self.content[1:-1]


class Integer(ContentNode):

    def compile(self):
        return int(self.content)


class Boolean(ContentNode):

    def compile(self):
        return {"true": True, "false": False}[self.content]


class OffsetDateTime(ContentNode):

    def compile(self):
        if self.content.endswith("Z"):
            return datetime.datetime.strptime(
                self.content, "%Y-%m-%dT%H:%M:%SZ")
        else:
            assert self.content[-3] == ":"
            content = self.content[:-3] + self.content[-2:]
            return datetime.datetime.strptime(content, "%Y-%m-%dT%H:%M:%S%z")
