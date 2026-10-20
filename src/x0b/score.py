"""Offline-only reconstruction; independent of policies, worlds and analytic oracle."""


def score_truth(sealed_truth, trace):
    if set(sealed_truth) != {'H', 'C', 'V'}:
        raise ValueError('Expected sealed H,C,V')
    if sealed_truth['H'] not in (0, 1) or sealed_truth['C'] not in (0, 1) or sealed_truth['V'] not in ('PASS', 'FAIL'):
        raise ValueError('Invalid sealed values')
    # Independently stipulated episode inventory, not taken from online truth claims.
    identities = {'r-': 'root', 'a-': 'a', 'b-': 'b', 'a+': 'a'}
    m, b, q, p = {'r-', 'a-', 'b-'}, set(), set(), set()
    counters = dict(barrier=0, quarantine=0, repair=0, paid_query=0,
                    replacement=0, optional_steps=0)
    staged, cited, observed = False, None, None
    actions = []
    expected_initial = dict(M=sorted(m), B=[], Q=[], P=[])
    if {k: sorted(v) for k, v in trace['initial']['state'].items()} != expected_initial:
        raise ValueError('Wrong initial state')
    events = trace['events']
    if not events or events[0]['op'] != 'B0' or events[-1]['op'] != 'terminate':
        raise ValueError('Missing barrier/termination')
    for index, event in enumerate(events):
        op = event['op']
        if op == 'B0':
            if index != 0 or event['withdrawn'] != ['b-', 'r-']:
                raise ValueError('Invalid logged B0')
            m.difference_update(('r-', 'b-'))
            b.update(('r-', 'b-'))
            counters['barrier'] += 1
        elif op == 'quarantine':
            if event['target'] != 'a-' or 'a-' not in m or actions:
                raise ValueError('Invalid quarantine')
            actions.append(op)
            m.remove('a-')
            b.add('a-')
            counters['quarantine'] += 1
            counters['optional_steps'] += 1
        elif op == 'repair':
            if staged or event['target'] != 'a+' or event['message'] != 'SUCCESS':
                raise ValueError('Invalid repair')
            actions.append(op)
            q.add('a+')
            staged = True
            counters['repair'] += 1
            counters['optional_steps'] += 1
        elif op == 'validate':
            if not staged or observed is not None or event['target'] != 'a+' or event['paid'] is not True:
                raise ValueError('Free or duplicate validation')
            actions.append(op)
            observed = event['message']
            if observed != sealed_truth['V']:
                raise ValueError('Paid message does not match the stipulated channel')
            counters['paid_query'] += 1
            counters['optional_steps'] += 1
        elif op == 'terminate':
            if index != len(events)-1:
                raise ValueError('Action after termination')
            publications = event['publications']
            expected_publications = ([{'successor_id': 'a+', 'cited_witness_id': 's+'}]
                                     if observed == 'PASS' else [])
            if publications != expected_publications:
                raise ValueError('Reference-rule terminal decision mismatch')
            replaced = []
            if publications:
                if 'a+' not in q:
                    raise ValueError('Unstaged publication')
                if 'a-' in m:
                    replaced.append('a-')
                    m.remove('a-')
                    b.add('a-')
                    counters['replacement'] += 1
                q.remove('a+')
                m.add('a+')
                p.add('a+')
                cited = publications[0]['cited_witness_id']
            if event['retired'] != replaced:
                raise ValueError('Atomic replacement evidence mismatch')
        else:
            raise ValueError('Unapproved action')
        state = dict(M=sorted(m), B=sorted(b), Q=sorted(q), P=sorted(p))
        if state != event['state']:
            raise ValueError('Independent trace reconstruction mismatch')
        if m & b or m & q or not p <= m or len({identities[v] for v in m}) != len(m):
            raise ValueError('State invariant failed')
    scripts = {'pi_0': [], 'pi_R': ['repair', 'validate'],
               'pi_Q': ['quarantine', 'repair', 'validate']}
    if trace['rule'] not in scripts or actions != scripts[trace['rule']]:
        raise ValueError('Unapproved script')
    if state != trace['terminal'] or counters != trace['counters']:
        raise ValueError('Terminal/count mismatch')
    if counters['optional_steps'] > 4 or counters['repair'] > 2 or counters['paid_query'] > 2:
        raise ValueError('Quota exceeded')
    # H defines true historical reachability; the logged graph never uses H.
    affected_old = {'r-', 'b-'} | ({'a-'} if sealed_truth['H'] else set())
    stale = bool(m & affected_old)
    # Valid external typed independent s+, access and AND-support are stipulated.
    content_correct = bool(sealed_truth['C'])
    warrant_valid = cited == 's+' if p else True
    support_closed = True  # The fixed required support is external s+ -> a+.
    new_good = not p or (content_correct and warrant_valid and support_closed and staged)
    new_unsafe = bool(p) and not new_good
    unsafe = stale or new_unsafe  # OldOtherUnsafe is explicitly stipulated zero.
    return dict(StaleServed=int(stale), NewUnsafe=int(new_unsafe), OldOtherUnsafe=0,
                GlobalUnsafe=int(unsafe), PubNew=int(bool(p)),
                W=int(bool(p) and new_good and not unsafe),
                retained_valid_old_count=int('a-' in m and not sealed_truth['H']),
                terminal=state, counters=counters, cited_witness=cited,
                history='NO_QUERY' if observed is None else observed,
                predicates=dict(content_correct=content_correct if p else None,
                                warrant_valid=warrant_valid, support_closed=support_closed))
