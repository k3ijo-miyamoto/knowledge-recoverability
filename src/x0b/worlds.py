"""Exact potential worlds and the sole paid observation channel. No sampling."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Atom:
    H: int
    C: int
    V: str
    mass: Fraction

    def sealed(self):
        return {'H': self.H, 'C': self.C, 'V': self.V}


def enumerate_exact(params):
    if set(params) != {'h', 'c', 't', 'f'}:
        raise ValueError('Exactly h,c,t,f are required')
    if any(type(x) is not Fraction or not 0 <= x <= 1 for x in params.values()):
        raise ValueError('Parameters must be exact Fraction probabilities')
    h, c, t, f = (params[k] for k in ('h', 'c', 't', 'f'))
    atoms = []
    for hidden in (0, 1):
        for correct in (0, 1):
            edge_mass = h if hidden else 1 - h
            content_mass = c if correct else 1 - c
            pass_mass = t if correct else f
            for message in ('PASS', 'FAIL'):
                likelihood = pass_mass if message == 'PASS' else 1 - pass_mass
                atoms.append(Atom(hidden, correct, message, edge_mass * content_mass * likelihood))
    return tuple(atoms)


class PaidValidation:
    """Carries only potential V, never H/C. Request requires a paid action receipt.

    This is a declared interface boundary, not protection against introspection.
    """

    __slots__ = ('__message', '__used', '__receipts')

    def __init__(self, potential_message):
        if potential_message not in ('PASS', 'FAIL'):
            raise ValueError('Invalid validation message')
        self.__message = potential_message
        self.__used = False
        self.__receipts = []

    def request(self, receipt):
        if self.__used:
            raise ValueError('Only one paid observation in this model')
        if receipt not in (('repair', 'validate'), ('quarantine', 'repair', 'validate')):
            raise ValueError('Validation requires prior stage and paid-action receipt')
        self.__used = True
        self.__receipts.append(receipt)
        return self.__message

    def audit(self):
        return {'calls': len(self.__receipts), 'receipts': list(self.__receipts)}
