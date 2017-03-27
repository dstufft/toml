import anytree


class Node(anytree.NodeMixin):

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


class Document(Node):
    pass


class Statement(Node):
    pass


class Table(Node):
    pass


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
    pass


class Assignment(ContentNode):
    pass


class BasicString(ContentNode):
    pass


class Integer(ContentNode):
    pass


class Boolean(ContentNode):
    pass


class OffsetDateTime(ContentNode):
    pass
