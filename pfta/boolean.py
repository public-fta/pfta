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

    def __eq__(self, other):
        return self.encoding == other.encoding

    def __repr__(self):
        return f'Term({bin(self.encoding)})'

    @staticmethod
    def conjunction(*terms: 'Term') -> 'Term':
        """
        Compute the conjunction (AND) of a sequence of terms.

        Since a factor is present in a conjunction if and only if it is present in at least one of the inputs,
        the conjunction encoding is the bitwise OR of the input term encodings.
        """
        conjunction_encoding = 0  # True

        for term in terms:
            conjunction_encoding |= term.encoding

        return Term(conjunction_encoding)


class Expression:
    """
    A general disjunction (OR) of minimal cut sets, represented as a Boolean sum of products, i.e. an expression.
    """
    __slots__ = ('terms',)

    def __init__(self, *terms: Term):
        self.terms = frozenset({*terms})

    def __repr__(self):
        return f'Expression({set(self.terms)!r})'
