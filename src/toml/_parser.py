import rply
import rply.errors

from ._nodes import Array, Document, Statement, Table, TableName
from ._nodes import (
    Assignment, BareKey, BasicString, Comment, LineEnd, Node, Whitespace,
    OpenBracket, CloseBracket, OffsetDateTime, Integer, Boolean, Comma, Dot,
    LiteralString,
)


_token_to_node = {
    "ASSIGNMENT": Assignment,
    "BARE_KEY": BareKey,
    "BASIC_STRING": BasicString,
    "LITERAL_STRING": LiteralString,
    "BOOLEAN": Boolean,
    "INTEGER": Integer,
    "OFFSET_DATETIME": OffsetDateTime,
    "COMMENT": Comment,
    "LINE_END": LineEnd,
    "WHITESPACE": Whitespace,
    "OPEN_BRACKET": OpenBracket,
    "CLOSE_BRACKET": CloseBracket,
    "COMMA": Comma,
    "PERIOD": Dot,
}


_pg = rply.ParserGenerator(_token_to_node.keys())


@_pg.production("main : statements")
def main(state, pack):
    root = Document()
    statements, = pack
    for statement in statements:
        statement.parent = root

    return root


@_pg.production("statements : statements statement")
@_pg.production("statements : statements WHITESPACE statement")
def statements_statement(state, pack):
    statements = pack[0]
    whitespace = [_token_to_node[p.name](content=p.value) for p in pack[1:-1]]
    statement = pack[-1]
    return statements + whitespace + statement


@_pg.production("statements : statement")
def statement(state, pack):
    statement_, = pack
    return statement_


@_pg.production("statement : line_end")
def statement_line_end(state, pack):
    line_end, = pack
    return line_end


@_pg.production("statement : value_stmt line_end")
@_pg.production("statement : value_stmt WHITESPACE line_end")
def statement_value_stmt(state, pack):
    value_stmt = pack[0]
    whitespace = [_token_to_node[p.name](content=p.value) for p in pack[1:-1]]
    line_end = pack[-1]

    stmt = Statement()
    for item in value_stmt:
        item.parent = stmt

    output = [stmt] + whitespace + line_end

    if state.current_table is None:
        return output
    else:
        for item in output:
            item.parent = state.current_table
        return []


@_pg.production("line_end : LINE_END")
def line_end(state, pack):
    return [_token_to_node[p.name](content=p.value) for p in pack]


@_pg.production("line_end : COMMENT LINE_END")
def comment(state, pack):
    return [_token_to_node[p.name](content=p.value) for p in pack]

@_pg.production("value_stmt : value_key WHITESPACE ASSIGNMENT WHITESPACE value_type")  # noqa
@_pg.production("value_stmt : value_key WHITESPACE ASSIGNMENT value_type")
@_pg.production("value_stmt : value_key ASSIGNMENT WHITESPACE value_type")
@_pg.production("value_stmt : value_key ASSIGNMENT value_type")
def value_stmt(state, pack):
    output = []
    for item in pack:
        if isinstance(item, Node):
            output.append(item)
        else:
            output.append(_token_to_node[item.name](content=item.value))
    return output


@_pg.production("value_key : BARE_KEY")
@_pg.production("value_key : INTEGER")
@_pg.production("value_key : BASIC_STRING")
@_pg.production("value_key : LITERAL_STRING")
def value_key(state, pack):
    token, = pack

    # THis is a total hack. Unfortunately our lexer isn't smart enough to
    # differentiate a integer bare key from an actual integer in all of the
    # cases, so we give up and allow an integer here even though it's not
    # allowed and we'll treat it as a bare key. This includes needing to do
    # extra validation because INTEGER accepts values that are not valid in a
    # BARE_KEY.
    if token.name == "INTEGER":
        if token.value.startswith("+"):
            raise rply.ParsingError(None, token.getsourcepos())
        return BareKey(content=token.value)

    return _token_to_node[token.name](content=token.value)


@_pg.production("value_type : BASIC_STRING")
@_pg.production("value_type : OFFSET_DATETIME")
@_pg.production("value_type : INTEGER")
@_pg.production("value_type : BOOLEAN")
def value_type(state, pack):
    token, = pack
    return _token_to_node[token.name](content=token.value)


@_pg.production("value_type : OPEN_BRACKET CLOSE_BRACKET")
@_pg.production("value_type : OPEN_BRACKET WHITESPACE CLOSE_BRACKET")
@_pg.production("value_type : OPEN_BRACKET array_values CLOSE_BRACKET")
@_pg.production("value_type : OPEN_BRACKET WHITESPACE array_values CLOSE_BRACKET")  # noqa
@_pg.production("value_type : OPEN_BRACKET array_values WHITESPACE CLOSE_BRACKET")  # noqa
@_pg.production("value_type : OPEN_BRACKET WHITESPACE array_values WHITESPACE CLOSE_BRACKET")  # noqa
def value_type_array(state, pack):
    array = Array()
    for item in pack:
        if isinstance(item, Node):
            item.parent = array
        elif isinstance(item, list):
            for sitem in item:
                sitem.parent = array
        else:
            _token_to_node[item.name](content=item.value).parent = array
    return array


@_pg.production("array_values : array_values COMMA value_type")
@_pg.production("array_values : array_values WHITESPACE COMMA value_type")
@_pg.production("array_values : array_values COMMA WHITESPACE value_type")
@_pg.production("array_values : array_values WHITESPACE COMMA WHITESPACE value_type")  # noqa
@_pg.production("array_values : value_type")
def array_values(state, pack):
    output = []
    for item in pack:
        if isinstance(item, Node):
            output.append(item)
        elif isinstance(item, list):
            output += item
        else:
            output.append(_token_to_node[item.name](content=item.value))
    return output


@_pg.production("statement : table_def line_end")
@_pg.production("statement : table_def WHITESPACE line_end")
def statement_table_def(state, pack):
    table_def = pack[0]
    whitespace = [_token_to_node[p.name](content=p.value) for p in pack[1:-1]]
    line_end = pack[-1]

    state.current_table = table = Table()
    table_name = TableName()
    for item in table_def:
        if isinstance(item, list):
            for sitem in item:
                sitem.parent = table_name
        else:
            item.parent = table_name

    for item in ([table_name] + whitespace + line_end):
        item.parent = table

    return [table]


@_pg.production("table_def : OPEN_BRACKET table_names CLOSE_BRACKET")
@_pg.production("table_def : OPEN_BRACKET WHITESPACE table_names CLOSE_BRACKET")  # noqa
@_pg.production("table_def : OPEN_BRACKET table_names WHITESPACE CLOSE_BRACKET")  # noqa
@_pg.production("table_def : OPEN_BRACKET WHITESPACE table_names WHITESPACE CLOSE_BRACKET")  # noqa
def table_def(state, pack):
    output = []
    for item in pack:
        if isinstance(item, list):
            output += item
        else:
            output.append(_token_to_node[item.name](content=item.value))

    return output


@_pg.production("table_names : table_name")
@_pg.production("table_names : table_names PERIOD table_name")
@_pg.production("table_names : table_names WHITESPACE PERIOD table_name")
@_pg.production("table_names : table_names PERIOD WHITESPACE table_name")
@_pg.production("table_names : table_names WHITESPACE PERIOD WHITESPACE table_name")  # noqa
def table_names(state, pack):
    output = []
    for item in pack:
        if isinstance(item, list):
            output += item
        else:
            output.append(_token_to_node[item.name](content=item.value))

    return output


@_pg.production("table_name : BARE_KEY")
def table_def_name(state, pack):
    return [_token_to_node[p.name](content=p.value) for p in pack]


_parser = _pg.build()


class ParserState:

    def __init__(self):
        self.current_table = None


def parse(token_stream):
    return _parser.parse(token_stream, state=ParserState())
