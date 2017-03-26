import rply


_tokens = {
    "LINE_END": "LineEnd",
    "COMMENT": "Comment",
    "BARE_KEY": "BareKey",
    "WHITESPACE": "Whitespace",
    "ASSIGNMENT": "Assignment",
    "BASIC_STRING": "BasicString",
    "OPEN_BRACKET": "OpenBracket",
    "CLOSE_BRACKET": "CloseBracket",
    "PERIOD": "Period",
    "OFFSET_DATETIME": "OffsetDateTime",
    "INTEGER": "Integer",
    "COMMA": "Comma",
    "BOOLEAN": "Boolean",
}


_pg = rply.ParserGenerator(
    # All of the tokens supported by this parser.
    ["COMMENT", "LINE_END", "WHITESPACE", "BARE_KEY", "ASSIGNMENT",
     "BASIC_STRING", "OPEN_BRACKET", "CLOSE_BRACKET", "PERIOD",
     "OFFSET_DATETIME", "INTEGER", "COMMA", "BOOLEAN"],
)


@_pg.production("main : statements")
def main(pack):
    (statements,) = pack
    return [x for x in statements if x] if statements else []


@_pg.production("statements : statements statement")
def statements_statement(pack):
    statements, statement = pack
    return statements + statement


@_pg.production("statements : statement")
def statement(pack):
    statement_, = pack
    return statement_


@_pg.production("statement : line_end")
def statement_line_end(pack):
    line_end, = pack
    return line_end


@_pg.production("statement : value_stmt line_end")
@_pg.production("statement : WHITESPACE value_stmt line_end")
def statement_value_stmt(pack):
    output = []
    for item in pack:
        if isinstance(item, list):
            output += item
        else:
            output.append({"type": _tokens[item.name], "value": item.value})
    return [output]


@_pg.production("line_end : LINE_END")
@_pg.production("line_end : WHITESPACE LINE_END")
def line_end(pack):
    return [{"type": _tokens[i.name], "value": i.value} for i in pack]


@_pg.production("line_end : COMMENT LINE_END")
@_pg.production("line_end : WHITESPACE COMMENT LINE_END")
def comment(pack):
    return [{"type": _tokens[i.name], "value": i.value} for i in pack]

@_pg.production("value_stmt : BARE_KEY WHITESPACE ASSIGNMENT WHITESPACE value_type")  # noqa
@_pg.production("value_stmt : BARE_KEY WHITESPACE ASSIGNMENT value_type")
@_pg.production("value_stmt : BARE_KEY ASSIGNMENT WHITESPACE value_type")
@_pg.production("value_stmt : BARE_KEY ASSIGNMENT value_type")
def value_stmt(pack):
    output = []
    for item in pack:
        if isinstance(item, (dict, list)):
            output.append(item)
        else:
            output.append({"type": _tokens[item.name], "value": item.value})
    return output


@_pg.production("value_type : BASIC_STRING")
@_pg.production("value_type : OFFSET_DATETIME")
@_pg.production("value_type : INTEGER")
@_pg.production("value_type : BOOLEAN")
def value_type(pack):
    type_, = pack
    return {"type": _tokens[type_.name], "value": type_.value}


@_pg.production("value_type : OPEN_BRACKET CLOSE_BRACKET")
@_pg.production("value_type : OPEN_BRACKET WHITESPACE CLOSE_BRACKET")
@_pg.production("value_type : OPEN_BRACKET array_values CLOSE_BRACKET")
@_pg.production("value_type : OPEN_BRACKET WHITESPACE array_values CLOSE_BRACKET")  # noqa
@_pg.production("value_type : OPEN_BRACKET array_values WHITESPACE CLOSE_BRACKET")  # noqa
@_pg.production("value_type : OPEN_BRACKET WHITESPACE array_values WHITESPACE CLOSE_BRACKET")  # noqa
def value_type_array(pack):
    output = []
    for item in pack:
        if isinstance(item, list):
            output.extend(item)
        else:
            output.append({"type": _tokens[item.name], "value": item.value})
    return [output[0], output[1:]]


@_pg.production("array_values : array_values COMMA value_type")
@_pg.production("array_values : array_values WHITESPACE COMMA value_type")
@_pg.production("array_values : array_values COMMA WHITESPACE value_type")
@_pg.production("array_values : array_values WHITESPACE COMMA WHITESPACE value_type")  # noqa
@_pg.production("array_values : value_type")
def array_values(pack):
    output = []
    for item in pack:
        if isinstance(item, list):
            output += item
        elif isinstance(item, dict):
            output.append(item)
        else:
            output.append({"type": _tokens[item.name], "value": item.value})

    return output


@_pg.production("statement : table_def line_end")
@_pg.production("statement : WHITESPACE table_def line_end")
def statement_table_def(pack):
    output = []
    for item in pack:
        if isinstance(item, list):
            output += item
        else:
            output.append({"type": _tokens[item.name], "value": item.value})
    return [output]


@_pg.production("table_def : OPEN_BRACKET table_names CLOSE_BRACKET")
@_pg.production("table_def : OPEN_BRACKET WHITESPACE table_names CLOSE_BRACKET")  # noqa
@_pg.production("table_def : OPEN_BRACKET table_names WHITESPACE CLOSE_BRACKET")  # noqa
@_pg.production("table_def : OPEN_BRACKET WHITESPACE table_names WHITESPACE CLOSE_BRACKET")  # noqa
def table_def(pack):
    output = []
    for item in pack:
        if isinstance(item, list):
            output += item
        else:
            output.append({"type": _tokens[item.name], "value": item.value})

    return output


@_pg.production("table_names : table_name")
@_pg.production("table_names : table_names PERIOD table_name")
@_pg.production("table_names : table_names WHITESPACE PERIOD table_name")
@_pg.production("table_names : table_names PERIOD WHITESPACE table_name")
@_pg.production("table_names : table_names WHITESPACE PERIOD WHITESPACE table_name")  # noqa
def table_names(pack):
    output = []
    for item in pack:
        if isinstance(item, list):
            output += item
        else:
            output.append({"type": _tokens[item.name], "value": item.value})

    return output


@_pg.production("table_name : BARE_KEY")
def table_def_name(pack):
    return [{"type": _tokens[i.name], "value": i.value} for i in pack]


parser = _pg.build()
