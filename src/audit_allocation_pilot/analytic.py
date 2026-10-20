"""Independent algebra/reference tree enumeration. No world/scorer/policy imports."""
from fractions import Fraction as F
from itertools import product


def audit_reference(c, e, axis):
    p, other = (c, e) if axis == 'C' else (e, c)
    plus = p*F(9, 10)+(1-p)*F(1, 10)
    good_plus = other*p*F(9, 10)/plus
    good_minus = other*p*F(1, 10)/(1-plus)
    legal_plus, legal_minus = 1-good_plus <= F(1, 5), 1-good_minus <= F(1, 5)
    pub = plus*legal_plus+(1-plus)*legal_minus
    w = plus*good_plus*legal_plus+(1-plus)*good_minus*legal_minus
    return {'pass_probability': plus, 'posterior_good': good_plus,
            'conditional_unsafe': 1-good_plus, 'W': w, 'unsafe': pub-w,
            'expected_K': 2-pub}


def exact_tree_reference(c, e):
    """Enumerate all feasible deterministic trees, independently of Bellman code.

Posterior weights use four truth assignments and likelihood products; this is
not the 16-world generator. Query repeats are deterministic, charged again.
Q-first and repeated Q are retained. Cost-free terminal STOP is legal only after
Q. Every positive-probability outcome needs a feasible subtree. Randomized
choices cannot improve a linear objective over these admissible actions.
"""
    prior = tuple((C, E, (c if C else 1-c)*(e if E else 1-e))
                  for C, E in product((False, True), repeat=2))

    def posterior(obs):
        weighted = []
        for C, E, p in prior:
            for axis, response in obs:
                truth = C if axis == 'C' else E
                p *= F(9, 10) if response == truth else F(1, 10)
            weighted.append((C, E, p))
        mass = sum(p for _, _, p in weighted)
        return [(C, E, p/mass) for C, E, p in weighted]

    def trees(obs, remaining, quarantined):
        weights = posterior(obs)
        good = sum(p for C, E, p in weights if C and E)
        found = []
        if 1-good <= F(1, 5):
            found.append((good, F(0), ('PUB',)))
        if quarantined:
            found.append((F(0), F(0), ('STOP',)))
        if remaining:
            for w, k, tree in trees(obs, remaining-1, True):
                found.append((w, 1+k, ('Q', tree)))
            seen = dict(obs)
            for axis in ('C', 'E'):
                if axis in seen:
                    for w, k, tree in trees(obs, remaining-1, quarantined):
                        found.append((w, 1+k, (axis, seen[axis], tree)))
                    continue
                prob = sum(p*(F(9, 10) if (C if axis == 'C' else E) else F(1, 10))
                           for C, E, p in weights)
                no = trees(obs+((axis, False),), remaining-1, quarantined)
                yes = trees(obs+((axis, True),), remaining-1, quarantined)
                for a, b in product(no, yes):
                    found.append(((1-prob)*a[0]+prob*b[0],
                                  1+(1-prob)*a[1]+prob*b[1], (axis, a[2], b[2])))
        return found
    candidates = trees((), 2, False)
    best = max(candidates, key=lambda v: (v[0], -v[1]))
    return {'W': best[0], 'expected_K': best[1], 'tree': best[2],
            'feasible_tree_count': len(candidates),
            'all_values': tuple(sorted(set((w, k) for w, k, _ in candidates)))}
