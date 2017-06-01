#!/usr/bin/env python

import re
import sys


flag_re = re.compile(r'^[A-Za-z0-9][A-Za-z0-9+_@-]*$')


class Flag(object):
    def __init__(self, name, negated=False):
        if not flag_re.match(name):
            raise ValueError('Invalid flag name: %s' % name)
        self.name = name
        self.negated = negated

    def __repr__(self):
        return '%s%s' % ('!' if self.negated else '', self.name)

    def make_negated(self):
        return Flag(self.name, not self.negated)


class Implication(object):
    def __init__(self, condition, constraint):
        assert isinstance(condition, Flag)
        self.condition = condition
        self.constraint = constraint

    def __repr__(self):
        return '%s? => %s' % (self.condition, self.constraint)


class NaryOperator(object):
    def __init__(self, op, constraint):
        assert op in ('||', '??', '^^')
        self.op = op
        self.constraint = constraint

    def __repr__(self):
        return '%s %s' % (self.op, self.constraint)


class AnyOfOperator(NaryOperator):
    def __init__(self, constraint):
        super(AnyOfOperator, self).__init__('||', constraint)


class ExactlyOneOfOperator(NaryOperator):
    def __init__(self, constraint):
        super(ExactlyOneOfOperator, self).__init__('^^', constraint)


class AtMostOneOfOperator(NaryOperator):
    def __init__(self, constraint):
        super(AtMostOneOfOperator, self).__init__('??', constraint)


def parse_tokens(l, nested=False):
    while l:
        # implication or n-ary operator
        if l[0] in ('||', '??', '^^') or l[0].endswith('?'):
            if l[1] != '(':
                raise ValueError('"%s" must be followed by "("' % l[0])
            k = l.pop(0)
            l.pop(0)

            if k == '||':
                yield AnyOfOperator(list(parse_tokens(l, True)))
            elif k == '??':
                yield AtMostOneOfOperator(list(parse_tokens(l, True)))
            elif k == '^^':
                yield ExactlyOneOfOperator(list(parse_tokens(l, True)))
            else:
                # strip ?
                assert k.endswith('?')
                k = k[:-1]
                if k.startswith('!'):
                    kf = Flag(k[1:], True)
                else:
                    kf = Flag(k)
                yield Implication(kf, list(parse_tokens(l, True)))
                
        # end of group
        elif l[0] == ')':
            if not nested:
                raise ValueError('Stray ")" at top level')
            l.pop(0)
            return
        # plain flag
        else:
            if l[0].startswith('!'):
                yield Flag(l[0][1:], True)
            else:
                yield Flag(l[0])
            l.pop(0)

    if nested:
        raise ValueError('Missing terminating ")"')


def parse_string(s):
    # tokenize & parse
    return parse_tokens(s.split())


if __name__ == '__main__':
    print(repr(list(parse_string(sys.argv[1]))))