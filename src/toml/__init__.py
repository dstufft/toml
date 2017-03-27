import six

from . import _lexer, _parser


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
