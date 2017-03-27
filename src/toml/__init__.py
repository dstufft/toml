import collections
import datetime
import re

import six

from . import _lexer, _parser, _nodes


def loads(data):
    if not isinstance(data, six.string_types):
        # TOML documents are *always* UTF8 encoded, so if somebody hands us
        # some bytes, then we can decode them as UTF8 before going any further.
        data = data.decode("utf8")

    # Generate a FST for our given TOML document, at this point the document
    # will be entirely parsed and can be compiled to return our values.
    toml = _parser.parse(_lexer.lex(data))

    # TODO: There should be an intermediate state between what toml.compile()
    #       returns and the "plain" Python data types that we want to return.
    #       This intermediate state will hold references to what FST nodes
    #       caused which piece of data to be added. While this wouldn't
    #       actually be used in loads(), it would change this line to need to
    #       call some additional funtion to throw that all away.
    output = toml.compile()

    # Now that we've lexed, parsed, and compiled our TOML document, we're done
    # and we can return it to our caller.
    return output


def dumps(data):
    # TODO: This should accept an existing=None keyword argument that allows
    #       passing in an existing string of TOML data. This TOML data will
    #       be used when dumping to attempt to minimize any changes done to the
    #       document, including things like comments and newlines and such.

    # First we need to go through our data and generate a mapping of tables to
    # values, we want our tables to be in order from most specific to least
    # specific by default, so we'll go ahead and do that.
    output = collections.OrderedDict()
    stack = collections.deque([(tuple(), data)])
    while stack:
        name, current = stack.popleft()
        output[name] = collections.OrderedDict()

        # We need to seperate anything that isn't a dictionary from anything
        # that is, that is because dictionaries will be handled differently
        # than anything else will be here.
        for key, value in current.items():
            if isinstance(value, collections.Mapping):
                stack.append((name + (key,), value))
            else:
                output[name][key] = value

    # Now we go through this table by table and build up a FST containing all
    # of our items here. We're going to use a nice set of whitespace here to
    # make the document more readable.
    # TODO: Should we allow customizing what the whitespace ends up being?
    root = current = _nodes.Document()
    while output:
        table_name, values = output.popitem(last=False)
        if table_name:
            # Create our table.
            table = current = _nodes.Table()
            table.parent = root

            # Create our table definition.
            table_def = _nodes.TableName()
            table_def.parent = table
            _nodes.OpenBracket(content="[").parent = table_def
            for i, part in enumerate(table_name):
                if i:
                    _nodes.Dot(content=".").parent = table_def
                # Determine what type of key we're able to use, preferring bare
                # keys but falling back to basic strings or string literals
                # where needed.
                # TODO: Don't copy/paste this!
                if re.fullmatch(_lexer._BARE_KEY, part):
                    _nodes.BareKey(content=part).parent = table_def
                else:
                    raise NotImplementedError("Only bare keys implemented.")
            _nodes.CloseBracket(content="]").parent = table_def

            # End the table with a new line.
            _nodes.LineEnd(content="\n").parent = table

        for key, value in values.items():
            # TODO: These should not be a big hardcoded if/elif/else chain.
            if not isinstance(key, six.string_types):
                raise ValueError("Cannot dump nonstring key: {!r}".format(key))

            value_stmt = _nodes.ValueStatement()
            value_stmt.parent = current

            # Determine what type of key we're able to use, preferring bare
            # keys but falling back to basic strings or string literals where
            # needed.
            if re.fullmatch(_lexer._BARE_KEY, key):
                _nodes.BareKey(content=key).parent = value_stmt
            else:
                raise NotImplementedError("Only bare keys implemented.")

            _nodes.Whitespace(content=" ").parent = value_stmt
            _nodes.Assignment(content="=").parent = value_stmt
            _nodes.Whitespace(content=" ").parent = value_stmt

            if isinstance(value, six.string_types):
                # TODO: We need to figure out how to _actually_ serialize this
                #       because this isn't really the right way.
                _nodes.BasicString(content='"{}"'.format(value)).parent = \
                    value_stmt
            elif isinstance(value, six.integer_types):
                _nodes.Integer(content=str(value)).parent = value_stmt
            elif (isinstance(value, datetime.datetime)
                    and value.tzinfo is not None):
                if value.utcoffset():
                    v = value.strftime("%Y-%m-%dT%H:%M:%S%z")
                    value = v[:-2] + ":" + v[-2:]
                else:
                    value = value.strftime("%Y-%m-%dT%H:%M:%SZ")
                _nodes.OffsetDateTime(content=value).parent = value_stmt
            else:
                raise NotImplementedError("{!r} not implemented.".format(value))  # noqa

            _nodes.LineEnd(content="\n").parent = current

        # If we have more to do, add another newline.
        if output:
            _nodes.LineEnd(content="\n").parent = current

    return root.render()
