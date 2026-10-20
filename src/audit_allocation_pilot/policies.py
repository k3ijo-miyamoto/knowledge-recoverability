"""Online decisions use only declared priors and purchased observations.

No world, scorer, fixture or analytical reference is imported here. Repeated
queries return the same potential response and still cost one; search includes
these dominated choices rather than silently assuming a new independent draw.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from functools import lru_cache

DELTA = F(1, 5)
LIMIT = 2

@dataclass(frozen=True)
class View:
    priors: tuple
    history: tuple = ()
    spent: int = 0
    quarantined: bool = False

@dataclass(frozen=True)
class Receipt:
    action: str
    response: object
    cost: int


def marginal(view, axis):
    p = view.priors[0 if axis == 'C' else 1]
    observed = dict(view.history)
    if axis not in observed:
        return p
    likelihood_good = F(9, 10) if observed[axis] else F(1, 10)
    likelihood_bad = 1 - likelihood_good
    return p * likelihood_good / (p * likelihood_good + (1-p) * likelihood_bad)


def goodness(view):
    return marginal(view, 'C') * marginal(view, 'E')


def response_distribution(view, axis):
    observed = dict(view.history)
    if axis in observed:
        return ((observed[axis], F(1)),)
    plus = marginal(view, axis) * F(9, 10) + (1-marginal(view, axis)) * F(1, 10)
    return ((False, 1-plus), (True, plus))


def after_audit(view, axis, response):
    if axis not in ('C', 'E') or type(response) is not bool or view.spent >= LIMIT:
        raise ValueError('invalid or unaffordable audit')
    old = dict(view.history)
    if axis in old and old[axis] != response:
        raise ValueError('inconsistent repeated audit')
    return replace(view, history=view.history+((axis, response),), spent=view.spent+1)


@lru_cache(None)
def optimum(view):
    """Bellman search over all actions; maximize W, then minimize expected K.

PUB and STOP are terminal. Q can be followed by an audit/publication, so the
optimizer includes quarantine-first strategies. An infeasible positive-mass
child invalidates the whole action tree. Remaining budget strictly decreases.
"""
    candidates = []
    if 1-goodness(view) <= DELTA:
        candidates.append((goodness(view), F(0), 'PUB'))
    if view.quarantined:
        candidates.append((F(0), F(0), 'STOP'))
    if view.spent < LIMIT:
        q = optimum(replace(view, spent=view.spent+1, quarantined=True))
        if q is not None:
            candidates.append((q[0], 1+q[1], 'Q'))
        for axis in ('C', 'E'):
            branches = [(p, optimum(after_audit(view, axis, answer)))
                        for answer, p in response_distribution(view, axis)]
            if all(child is not None for _, child in branches):
                candidates.append((sum(p*child[0] for p, child in branches),
                                   1+sum(p*child[1] for p, child in branches), axis))
    return max(candidates, key=lambda v: (v[0], -v[1])) if candidates else None


def choose(name, view):
    if name == 'P_OPT':
        best = optimum(view)
        if best is None:
            raise ValueError('no feasible completion')
        return best[2]
    if name not in ('P_C', 'P_E', 'P_Q'):
        raise ValueError('unknown policy')
    if view.quarantined:
        return 'STOP'
    if name == 'P_Q':
        return 'Q'
    if not view.history:
        return name[-1]
    return 'PUB' if 1-goodness(view) <= DELTA else 'Q'
