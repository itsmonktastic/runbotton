import re
from StringIO import StringIO

# eat everything up to first unescaped {
# /.*?[^\\]{/
# eat everything up to first }
# /.*?}/
# repeat until empty

BEFORE_INTERP = re.compile(r'(|(?:.*?)[^\\])\{')
IN_INTERP = re.compile(r'\{(.*?)\}')

def execute(interp_string, parse_context):
    result = StringIO()
    while interp_string:
        match = BEFORE_INTERP.match(interp_string)
        print match and match.groups()
        if match is not None:
            result.write(match.groups()[0])
            interp_string = interp_string[len(match.groups()[0]):]
        else:
            # no interpolation left
            result.write(interp_string)
            interp_string = ''
            next

        inside_match = IN_INTERP.match(interp_string)
        if inside_match is not None:
            result.write(str(getattr(parse_context, inside_match.groups()[0])))
            interp_string = interp_string[len(inside_match.groups()[0]) + 2:]
        else:
            # only broken interpolation left
            result.write(interp_string)
            interp_string = ''
            next

    return result.getvalue()

class ParseContext(object):
    def __init__(self, data):
        self._data = data

    def __getattr__(self, k):
      try:
        return self._data[k]
      except KeyError as e:
        raise Exception('Tried to use variable %s but only had %s' %
            (k, ", ".join("{}={}".format(*it) for it in self._data.iteritems()))
        )
