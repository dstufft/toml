import ast
import os
import os.path
import shlex

import pytest

from rply.token import Token

from toml import _lexer as lexer


def _load_lexer_fixtures():
    fixture_dir = os.path.join(os.path.dirname(__file__), "data", "lexer")
    fixtures = os.listdir(fixture_dir)

    for fixture in fixtures:
        path = os.path.join(fixture_dir, fixture)
        with open(path, "r", encoding="utf8") as fp:
            data = fp.read()

        inp, expected_raw = data.split("\n---\n")

        expected = []
        for line in expected_raw.splitlines():
            token_name, token_data = shlex.split(line)
            token_data = ast.literal_eval("'" + token_data + "'")
            expected.append(Token(token_name, token_data))

        yield fixture, inp, expected


@pytest.mark.parametrize(("name", "inp", "expected"), _load_lexer_fixtures())
def test_lexer_lexes(name, inp, expected):
    results = list(lexer.lex(inp))
    assert results == expected
