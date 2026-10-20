"""Sealed finite worlds and a paid-observation runner, not a security sandbox."""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from .policies import View, Receipt, after_audit
from dataclasses import replace

PRIORS = {'L': (F(17, 20), F(3, 4)), 'R': (F(3, 4), F(17, 20))}

@dataclass(frozen=True)
class Gold:
    C: bool
    E: bool
    V_C: bool
    V_E: bool

class Atom:
    __slots__ = ('weight', '__gold', 'priors')

    def __init__(self, weight, gold, priors):
        self.weight, self.__gold, self.priors = weight, gold, priors

    def offline_gold(self):
        """Offline scorer/test harness only; never supplied to policy."""
        return self.__gold

    def run(self, decision):
        view = View(self.priors)
        receipts = []
        for _ in range(4):  # at most two paid actions and one terminal action
            action = decision(view)
            if action in ('C', 'E'):
                if view.spent >= 2:
                    raise ValueError('audit budget exhausted')
                answer = getattr(self.__gold, 'V_'+action)
                receipts.append(Receipt(action, answer, 1))
                view = after_audit(view, action, answer)
            elif action == 'Q':
                if view.spent >= 2:
                    raise ValueError('quarantine budget exhausted')
                receipts.append(Receipt('Q', None, 1))
                view = replace(view, spent=view.spent+1, quarantined=True)
            elif action in ('PUB', 'STOP'):
                receipts.append(Receipt(action, None, 0))
                return tuple(receipts)
            else:
                raise ValueError('unknown action')
        raise ValueError('nonterminating policy')


def atoms(condition):
    c, e = PRIORS[condition]
    result = []
    for C, E, VC, VE in product((False, True), repeat=4):
        mass = (c if C else 1-c) * (e if E else 1-e)
        mass *= F(9, 10) if VC == C else F(1, 10)
        mass *= F(9, 10) if VE == E else F(1, 10)
        result.append(Atom(mass, Gold(C, E, VC, VE), (c, e)))
    return tuple(result)
