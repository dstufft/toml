import rply


_BARE_KEY = r"[A-Za-z0-9_-]+"
_BASIC_STRING = r'"(\\(b|t|n|f|r|"|\\|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})|[^"\\\u0000-\u001F])*(?<!\\)"'  # noqa
_LITERAL_STRING = r"'(?![^']*\r?\n)[^']*'"


_lexer_gen = rply.LexerGenerator()
_lexer_gen.add("LINE_END", r"\r?\n")
_lexer_gen.add("WHITESPACE", r"( |\t)+")
_lexer_gen.add("COMMENT", r"#.*(?=\r?\n)")
_lexer_gen.add("ASSIGNMENT", r"=")
_lexer_gen.add("BOOLEAN", r"(true|false)")
_lexer_gen.add("MULTILINE_BASIC_STRING", r'"""(\\?\r?\n|\\(b|t|n|f|r|"|\\|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})|[^\\\u0000-\u001F])*?(?<!\\)"""')  # noqa
_lexer_gen.add("BASIC_STRING", _BASIC_STRING)
_lexer_gen.add("MULTILINE_LITERAL_STRING", r"'''(.|\r?\n)*?'''")
_lexer_gen.add("LITERAL_STRING", _LITERAL_STRING)
_lexer_gen.add("INTEGER", r"[+-]?([1-9][0-9_]*[0-9]|[0-9])(?=(\r?\n|#| |\t|,|]))")  # noqa
_lexer_gen.add("FLOAT", r"[+-]?([1-9][0-9_]*[0-9]|[0-9])(\.[0-9]([0-9_]*[0-9]|[0-9])?)?([eE][+-]?([1-9]([0-9_]*[0-9]|[0-9])?))?(?=(\r?\n|#| |\t|,|]))")  # noqa
_lexer_gen.add("OFFSET_DATETIME", r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})")  # noqa
_lexer_gen.add("LOCAL_DATETIME", r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?")  # noqa
_lexer_gen.add("LOCAL_DATE", r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_lexer_gen.add("LOCAL_TIME", r"[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?")
_lexer_gen.add("BARE_KEY", r"[A-Za-z0-9_-]+")
_lexer_gen.add("OPEN_BRACKET", r"\[")
_lexer_gen.add("CLOSE_BRACKET", r"]")
_lexer_gen.add("OPEN_BRACE", r"{")
_lexer_gen.add("CLOSE_BRACE", r"}")
_lexer_gen.add("COMMA", r",")
_lexer_gen.add("PERIOD", r"\.")


_lexer = _lexer_gen.build()


def lex(s):
    for token in _lexer.lex(s):
        yield token
