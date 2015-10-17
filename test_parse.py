import parse

import hamcrest as h

#def test_parse_context():
#    h.assert_that(parse.ParseContext(foo=2).foo, h.equal_to(2))
#
#def test_no_interp():
#    h.assert_that(parse.execute('foo', None), h.equal_to('foo'))
#
#def test_interp_at_start():
#    h.assert_that(parse.execute('{foo}', parse.ParseContext(foo=2)), h.equal_to('2'))
#
#def test_unclosed():
#    h.assert_that(parse.execute('{foo', parse.ParseContext(foo=2)), h.equal_to('{foo'))
#
#def test_unclosed():
#    h.assert_that(parse.execute('{foo}', parse.ParseContext(foo=2)), h.equal_to('{foo'))

def test_multiple():
    h.assert_that(parse.execute('{foo}, {bar}', parse.ParseContext(dict(foo=2, bar=3))), h.equal_to('2, 3'))
