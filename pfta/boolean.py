"""
# Public Fault Tree Analyser: boolean.py

Classes pertaining to Boolean algebra.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""


class Term:
    """
    A minimal cut set (or mode failure), represented as a Boolean product of events, i.e. a term.

    A Boolean term (i.e. conjunction (AND) of events) is encoded in binary,
    with the nth bit set if and only if the nth event is present as a factor.

    For example, if the events are A, B, C, D, E, then the encoding of the term ABE is
        EDCBA
        10011 (in binary),
    which is 19.

    Note that 0 encodes an empty conjunction, which is True.
    """
    __slots__ = ('encoding',)

    def __init__(self, encoding: int):
        self.encoding = encoding

    def __repr__(self):
        return f'Term({bin(self.encoding)})'


class Expression:
    """
    A general disjunction (OR) of minimal cut sets, represented as a Boolean sum of products, i.e. an expression.
    """
    __slots__ = ('terms',)

    def __init__(self, *terms: Term):
        self.terms = frozenset({*terms})

    def __repr__(self):
        return f'Expression({set(self.terms)!r})'
