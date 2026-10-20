"""Independent offline replay. Does not import policies or world generation."""
from fractions import Fraction as F


def replay(gold, receipts):
    old_served, published, spent, audits, qs = True, False, 0, 0, 0
    history = []
    ended = False
    for rec in receipts:
        if ended:
            raise ValueError('action after terminal')
        a, answer, cost = rec.action, rec.response, rec.cost
        if a in ('C', 'E'):
            if type(answer) is not bool or answer != getattr(gold, 'V_'+a) or cost != 1:
                raise ValueError('invalid paid response/charge')
            history.append((a, answer)); spent += 1; audits += 1
        elif a == 'Q':
            if answer is not None or cost != 1:
                raise ValueError('invalid quarantine receipt')
            old_served = False; spent += 1; qs += 1
        elif a in ('PUB', 'STOP'):
            if answer is not None or cost != 0:
                raise ValueError('invalid terminal receipt')
            ended = True
            if a == 'PUB':
                published = True; old_served = False
        else:
            raise ValueError('unknown action')
        if spent > 2:
            raise ValueError('worst-path budget violation')
    if not ended:
        raise ValueError('missing terminal action')
    new_unsafe = published and not (gold.C and gold.E)
    unsafe = old_served or new_unsafe
    return {'W': int(published and gold.C and gold.E and not old_served),
            'GlobalUnsafe': int(unsafe), 'StaleServed': int(old_served),
            'NewUnsafe': int(new_unsafe), 'PubNew': int(published),
            'W1Valid': int(gold.E), 'RetainedValidOld': 0,
            'K': spent, 'audits': audits, 'quarantines': qs,
            'replacement_actions': int(published),
            'staging_repair_units': 1, 'publication_admin_units': int(published)}


def summarize(rows):
    """Rows: (exact mass, gold, receipts); group by full observable receipt path.

Gold is used only after the path has been generated. Conditional risk and prior
risk are separately computed; unsafe STOP paths are not silently accepted.
"""
    totals = {}; branches = {}; max_k = 0
    for mass, gold, receipts in rows:
        score = replay(gold, receipts)
        for key, value in score.items():
            totals[key] = totals.get(key, F(0)) + mass*value
        max_k = max(max_k, score['K'])
        key = tuple((r.action, r.response, r.cost) for r in receipts)
        b = branches.setdefault(key, {'mass': F(0), 'unsafe_mass': F(0)})
        b['mass'] += mass; b['unsafe_mass'] += mass*score['GlobalUnsafe']
    if sum(b['mass'] for b in branches.values()) != 1:
        raise ValueError('incomplete world law')
    for b in branches.values():
        b['conditional_unsafe'] = b['unsafe_mass']/b['mass']
        b['admissible'] = b['conditional_unsafe'] <= F(1, 5)
    return {'totals': totals, 'branches': branches, 'max_K': max_k}
