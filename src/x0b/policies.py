"""Three fixed online rules. No world, gold, scorer or analytic imports."""

from copy import deepcopy


def public_initial():
    return {
        'state': {'M': ['r-', 'a-', 'b-'], 'B': [], 'Q': [], 'P': []},
        'root': 'r-', 'logged_edges': [['r-', 'b-']],
        'identities': {'r-': 'root', 'a-': 'a', 'b-': 'b', 'a+': 'a'},
        'source': {'id': 's+', 'type': 'evidence', 'citeable': True},
        'access': {'quarantine': True, 'repair': True, 'validate': True, 'publish': True},
    }


def run(rule, initial, observation_channel):
    """Admit only this approved public inventory and legal action encoding."""
    if rule not in ('pi_0', 'pi_R', 'pi_Q'):
        raise ValueError('Unapproved reference rule')
    if initial != public_initial():
        raise ValueError('Public input differs from the fixed allowlisted contract')
    state = {k: set(ids) for k, ids in initial['state'].items()}
    counters = dict(barrier=0, quarantine=0, repair=0, paid_query=0,
                    replacement=0, optional_steps=0)
    events, paid_actions = [], []

    def snapshot():
        return {k: sorted(ids) for k, ids in state.items()}

    def event(op, **fields):
        if state['M'] & state['B'] or state['M'] & state['Q'] or not state['P'] <= state['M']:
            raise ValueError('State partition violated')
        if len({initial['identities'][v] for v in state['M']}) != len(state['M']):
            raise ValueError('Duplicate serving identity')
        events.append(dict(op=op, state=snapshot(), **fields))

    reached = {initial['root']}
    while True:
        more = {dst for src, dst in initial['logged_edges'] if src in reached} - reached
        if not more:
            break
        reached.update(more)
    withdrawn = state['M'] & reached
    state['M'] -= withdrawn
    state['B'] |= withdrawn
    counters['barrier'] += 1
    event('B0', withdrawn=sorted(withdrawn))

    def optional(op):
        counters['optional_steps'] += 1
        counters['paid_query' if op == 'validate' else op] += 1
        if counters['optional_steps'] > 4 or counters['repair'] > 2 or counters['paid_query'] > 2:
            raise ValueError('Action quota exceeded')
        paid_actions.append(op)

    message = None
    if rule == 'pi_Q':
        optional('quarantine')
        state['M'].remove('a-')
        state['B'].add('a-')
        event('quarantine', target='a-', reason='optional_quarantine')
    if rule != 'pi_0':
        optional('repair')
        state['Q'].add('a+')
        event('repair', target='a+', message='SUCCESS')
        optional('validate')
        # Charge and record the request before accessing potential V.
        event('validate', target='a+', paid=True, message=None)
        message = observation_channel.request(tuple(paid_actions))
        if message not in ('PASS', 'FAIL'):
            raise ValueError('Invalid paid observation')
        events[-1]['message'] = message

    publications, retired = [], []
    if message == 'PASS':
        if 'a+' not in state['Q'] or not initial['source']['citeable']:
            raise ValueError('Procedurally ineligible publication')
        retired = [old for old in state['M'] if initial['identities'][old] == initial['identities']['a+']]
        state['M'].difference_update(retired)
        state['B'].update(retired)
        counters['replacement'] += len(retired)
        state['Q'].remove('a+')
        state['P'].add('a+')
        state['M'].add('a+')
        publications = [{'successor_id': 'a+', 'cited_witness_id': 's+'}]
    event('terminate', publications=publications, retired=sorted(retired),
          reason='atomic_replacement' if retired else None)
    return dict(rule=rule, initial=deepcopy(initial), events=events, terminal=snapshot(),
                counters=counters, symbolic_costs={
                    'barrier': 'barrier_admin_cost', 'quarantine': 'quarantine_admin_cost',
                    'replacement': 'replacement_admin_cost'})
