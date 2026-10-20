"""Independent post-replay reconstruction and gold-only scoring (no engine import)."""


def _descendants(edges, roots):
    found, pending = set(), list(roots)
    while pending:
        node = pending.pop()
        if node in found:
            continue
        found.add(node)
        pending.extend(dst for src, dst in edges if src == node)
    return found


def _reconstruct(trace):
    """Derive final sets, counters and staging evidence from the event log."""
    initial = trace['initial']
    versions = initial['versions']
    m, b, q, p = (set(initial['state'][k]) for k in ('M', 'B', 'Q', 'P'))
    staged = set(q)
    counters = dict(barrier_count=0, quarantine_count=0, repair_count=0,
                    paid_query_count=0, replacement_count=0, optional_steps=0)
    citations = {}
    for index, event in enumerate(trace['events']):
        op = event['op']
        if index == 0:
            if op != 'B0':
                raise ValueError('Missing barrier')
            logged = _descendants(initial['logged_edges'], [initial['root']])
            removed = {v for v in m if v in logged and versions[v]['kind'] == 'old'}
            if sorted(removed) != event['withdrawn']:
                raise ValueError('Invalid logged barrier evidence')
            m -= removed
            b |= removed
            counters['barrier_count'] += 1
        elif event['accepted']:
            action = event['action']
            if op == 'terminate':
                for publication in action['publications']:
                    v = publication['successor_id']
                    if v not in q:
                        raise ValueError('Unstaged publish in accepted trace')
                    old = {x for x in m if versions[x]['identity'] == versions[v]['identity']}
                    counters['replacement_count'] += len(old)
                    m.difference_update(old)
                    b.update(old)
                    q.discard(v)
                    p.add(v)
                    m.add(v)
                    citations[v] = publication['cited_witness_id']
            else:
                counters['optional_steps'] += 1
                v = action['target']
                if op == 'quarantine':
                    counters['quarantine_count'] += 1
                    if v in m:
                        m.remove(v)
                        p.discard(v)
                        b.add(v)
                elif op == 'repair':
                    counters['repair_count'] += 1
                    if event['message'] == 'SUCCESS':
                        q.add(v)
                        staged.add(v)
                elif op in ('validate', 'audit', 'checkIndependent'):
                    counters['paid_query_count'] += 1
                else:
                    raise ValueError('Unknown accepted action')
        state = dict(M=sorted(m), B=sorted(b), Q=sorted(q), P=sorted(p))
        if state != event['state']:
            raise ValueError('Event state does not match independent reconstruction')
    if state != trace['terminal'] or counters != trace['counters'] or citations != trace['citations']:
        raise ValueError('Terminal accounting mismatch')
    if counters['optional_steps'] > 4 or counters['repair_count'] > 2 or counters['paid_query_count'] > 2:
        raise ValueError('Quota mismatch')
    return m, b, q, p, staged, counters, citations


def score(offline_truth, transition_trace):
    """Access gold only here, after replay. No semantic filtering of publication."""
    truth = offline_truth
    m, b, q, p, staged, counters, citations = _reconstruct(transition_trace)
    versions = truth['versions']
    if versions != transition_trace['initial']['versions']:
        raise ValueError('Version inventory mismatch')
    old = {v for v, item in versions.items() if item['kind'] == 'old'}
    affected = _descendants(truth['historical_edges'], [truth['root']]) & old
    sources = truth['sources']
    bad_origins = _descendants(truth['origin_edges'], truth['contaminated_origins'])
    prereqs = {}
    for parent, child in truth['support_edges']:
        prereqs.setdefault(child, []).append(parent)

    def source_legal_valid(s):
        item = sources[s]
        return (item['type'] == 'evidence' and item['valid'] and item['authorized']
                and item['context_valid'] and item['scope_valid'] and item['role_allowed'])

    def support_closed(v, visiting=()):
        if v in visiting:
            raise ValueError('Active support is not a DAG')
        for parent in prereqs.get(v, []):
            if parent in sources:
                if parent not in truth['external_sources'] or not source_legal_valid(parent):
                    return False
            elif parent in versions:
                if parent not in m or parent in affected or not truth['content'][parent] or not truth['authorized'][parent]:
                    return False
            else:
                raise ValueError('Unknown active support endpoint')
            if not support_closed(parent, visiting + (v,)):
                return False
        return True

    def warranted(v):
        w = citations.get(v)
        if w not in sources:
            return False
        item = sources[w]
        return (source_legal_valid(w) and item['origin'] not in bad_origins
                and v in item['supports'] and w in prereqs.get(v, [])
                and support_closed(v))

    identity_unique = len({versions[v]['identity'] for v in m}) == len(m)
    valid_new = {}
    for v in sorted(p):
        valid_new[v] = dict(content=truth['content'][v], support=support_closed(v),
                            warrant=warranted(v), authorized=truth['authorized'][v],
                            staged=v in staged, unique_identity=identity_unique)
    new_good = all(all(predicates.values()) for predicates in valid_new.values())
    stale = bool(m & affected)
    old_other = any(truth['old_other_unsafe'][v] or not truth['content'][v]
                    or not truth['authorized'][v] or not support_closed(v) for v in m & old)
    new_unsafe = bool(p) and not new_good
    global_unsafe = stale or old_other or new_unsafe
    retained = sum(v not in affected and truth['content'][v] and truth['authorized'][v]
                   and support_closed(v) and not truth['old_other_unsafe'][v] for v in m & old)
    return dict(StaleServed=int(stale), NewUnsafe=int(new_unsafe),
                OldOtherUnsafe=int(old_other), GlobalUnsafe=int(global_unsafe),
                PubNew=int(bool(p)), W=len(p) if p and new_good and not global_unsafe else 0,
                retained_valid_old_count=retained, counters=counters,
                predicates=valid_new,
                symbolic_costs=dict(barrier='barrier_admin_cost',
                                    quarantine='quarantine_admin_cost',
                                    replacement='replacement_admin_cost'))
