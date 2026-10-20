"""Policy-visible replay only. No fixture loading or offline scorer imports."""

from copy import deepcopy


def _keys(value, names):
    if not isinstance(value, dict) or set(value) != set(names):
        raise ValueError("Unexpected or missing interface keys")


def _strings(value):
    if not isinstance(value, list) or any(type(v) is not str for v in value):
        raise ValueError("Expected string list")
    if len(set(value)) != len(value):
        raise ValueError("Duplicate entries")


def validate_online(data):
    """Closed allowlist, including nested records; sealed labels are inadmissible."""
    _keys(data, ('versions', 'state', 'root', 'logged_edges', 'sources',
                 'repair_status', 'check_messages', 'access'))
    for v, item in data['versions'].items():
        _keys(item, ('identity', 'kind'))
        if type(v) is not str or type(item['identity']) is not str:
            raise ValueError('Invalid version identity')
        if item['kind'] not in ('old', 'new'):
            raise ValueError('Invalid version kind')
    _keys(data['state'], ('M', 'B', 'Q', 'P'))
    for ids in data['state'].values():
        _strings(ids)
        if not set(ids) <= data['versions'].keys():
            raise ValueError('Unknown state version')
    if data['root'] not in data['versions']:
        raise ValueError('Unknown reported root')
    if not isinstance(data['logged_edges'], list):
        raise ValueError('Expected edges')
    for edge in data['logged_edges']:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError('Invalid edge')
        if any(v not in data['versions'] for v in edge):
            raise ValueError('Unknown edge endpoint')
    for item in data['sources'].values():
        _keys(item, ('type', 'citeable'))
        if type(item['type']) is not str or type(item['citeable']) is not bool:
            raise ValueError('Invalid public source')
    for v, msg in data['repair_status'].items():
        if v not in data['versions'] or msg not in ('SUCCESS', 'FAIL'):
            raise ValueError('Invalid visible repair message')
    for key, msg in data['check_messages'].items():
        if type(key) is not str or type(msg) is not str:
            raise ValueError('Invalid visible check message')
    for v, allowed in data['access'].items():
        if v not in data['versions'] or type(allowed) is not bool:
            raise ValueError('Invalid public access permission')
    if set(data['access']) != set(data['versions']):
        raise ValueError('Missing public access permission')


def _invariants(state, versions):
    m, b, q, p = (state[k] for k in ('M', 'B', 'Q', 'P'))
    if m & b or m & q or not p <= m:
        raise ValueError('Invalid state partition')
    if any(versions[v]['kind'] != 'new' for v in q | p):
        raise ValueError('Old version in successor sets')
    if len({versions[v]['identity'] for v in m}) != len(m):
        raise ValueError('Multiple servable versions for one identity')


def replay(online_input, script):
    """Replay a predeclared script. Rejection preserves state and stops the trace."""
    validate_online(online_input)
    public = deepcopy(online_input)
    versions = public['versions']
    state = {k: set(v) for k, v in public['state'].items()}
    _invariants(state, versions)
    if not isinstance(script, list):
        raise ValueError('Script must be predeclared list')
    counts = dict(barrier_count=1, quarantine_count=0, repair_count=0,
                  paid_query_count=0, replacement_count=0, optional_steps=0)
    reasons, citations, events = {}, {}, []

    def snapshot():
        return {k: sorted(v) for k, v in state.items()}

    reachable = {public['root']}
    while True:
        expanded = reachable | {b for a, b in public['logged_edges'] if a in reachable}
        if expanded == reachable:
            break
        reachable = expanded
    withdrawn = {v for v in state['M'] & reachable if versions[v]['kind'] == 'old'}
    state['M'] -= withdrawn
    state['B'] |= withdrawn
    for v in withdrawn:
        reasons[v] = 'logged_barrier'
    events.append(dict(op='B0', withdrawn=sorted(withdrawn), state=snapshot()))
    disposition = 'OPEN'
    for action in script:
        if disposition != 'OPEN':
            raise ValueError('Script continues after terminal action')
        op = action.get('op')
        rejection = None
        msg = None
        if op == 'terminate':
            _keys(action, ('op', 'publications'))
            pubs = action['publications']
            if not isinstance(pubs, list):
                raise ValueError('Publications must be a list')
            selected = []
            for item in pubs:
                _keys(item, ('successor_id', 'cited_witness_id'))
                v, w = item['successor_id'], item['cited_witness_id']
                if v not in state['Q']:
                    rejection = 'not_staged'
                elif w not in public['sources'] or not public['sources'][w]['citeable']:
                    rejection = 'witness_permission'
                elif not public['access'][v]:
                    rejection = 'access_denied'
                selected.append(v)
            if len(selected) != len(set(selected)) or len({versions[v]['identity'] for v in selected if v in versions}) != len(selected):
                rejection = rejection or 'duplicate_identity'
            if any(versions[old]['kind'] == 'new' and versions[old]['identity'] == versions[v]['identity'] for old in state['M'] for v in selected if v in versions):
                rejection = rejection or 'duplicate_identity'
            if rejection is None:
                # All checks precede mutations: replacement and multi-publish are atomic.
                for item in pubs:
                    v = item['successor_id']
                    replaced = {old for old in state['M'] if versions[old]['identity'] == versions[v]['identity']}
                    for old in replaced:
                        reasons[old] = 'atomic_replacement'
                    state['M'] -= replaced
                    state['B'] |= replaced
                    counts['replacement_count'] += len(replaced)
                    state['Q'].remove(v)
                    state['M'].add(v)
                    state['P'].add(v)
                    citations[v] = item['cited_witness_id']
                disposition = 'TERMINATED'
        else:
            _keys(action, ('op', 'target'))
            target = action['target']
            if op not in ('quarantine', 'repair', 'validate', 'audit', 'checkIndependent'):
                raise ValueError('Unknown action')
            paid = op in ('validate', 'audit', 'checkIndependent')
            if counts['optional_steps'] >= 4:
                rejection = 'horizon'
            elif op == 'repair' and counts['repair_count'] >= 2:
                rejection = 'repair_quota'
            elif paid and counts['paid_query_count'] >= 2:
                rejection = 'observation_quota'
            elif target not in versions or not public['access'][target]:
                rejection = 'access_denied'
            elif op == 'repair' and (versions[target]['kind'] != 'new' or target in state['M'] or target in state['Q']):
                rejection = 'invalid_repair_target'
            if rejection is None:
                counts['optional_steps'] += 1
                if op == 'quarantine':
                    counts['quarantine_count'] += 1
                    if target in state['M']:
                        state['M'].remove(target)
                        state['P'].discard(target)
                        state['B'].add(target)
                        reasons[target] = 'optional_quarantine'
                elif op == 'repair':
                    counts['repair_count'] += 1
                    msg = public['repair_status'][target]
                    if msg == 'SUCCESS':
                        state['Q'].add(target)
                else:
                    counts['paid_query_count'] += 1
                    msg = public['check_messages'][op + ':' + target]
        if rejection:
            disposition = 'REJECT'
        _invariants(state, versions)
        events.append(dict(op=op, action=deepcopy(action), accepted=rejection is None,
                           reason=rejection, message=msg, state=snapshot()))
        if rejection:
            break
    return dict(initial=public, events=events, terminal=snapshot(),
                disposition=disposition, citations=citations, reasons=reasons,
                counters=counts, symbolic_costs=dict(barrier='barrier_admin_cost',
                quarantine='quarantine_admin_cost', replacement='replacement_admin_cost'))
