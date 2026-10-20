"""Frozen eight atoms, 24 rule/world paths and independent exact identities."""

import ast
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/x0b-exact8-v01/attempt-01'
INVOCATION = os.environ.get('X0B_INVOCATION', 'unrecorded')
VIOLATIONS = []


def audit(event, args):
    if (event.startswith(('subprocess.', 'socket.', 'os.exec', 'os.spawn', 'os.posix_spawn'))
            or event in ('os.fork', 'os.forkpty', 'os.system')):
        VIOLATIONS.append(event)
        raise RuntimeError('Forbidden process/network event: ' + event)


sys.addaudithook(audit)
from src.x0b import analytic, policies, score, worlds  # noqa: E402


def exact(params):
    return {key: F(value) for key, value in params.items()}


def conditional(atoms, event, given):
    denominator = sum((a.mass for a in atoms if given(a)), F(0))
    numerator = sum((a.mass for a in atoms if given(a) and event(a)), F(0))
    return numerator / denominator if denominator else None


def topology():
    pid = os.getpid()
    return dict(pid=pid, ppid=os.getppid(),
                threads=sorted(p.name for p in Path('/proc/self/task').iterdir()),
                children=Path(f'/proc/self/task/{pid}/children').read_text().strip(),
                rlimit_as=list(resource.getrlimit(resource.RLIMIT_AS)))


class ExactEight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT / 'tests/x0b/fixture_exact8_v01.json').read_bytes()
        if hashlib.sha256(raw).hexdigest() != json.loads((OUT / 'fixture_freeze.json').read_text())['sha256']:
            raise AssertionError('Frozen fixture was changed')
        cls.fixture = json.loads(raw)
        cls.params = exact(cls.fixture['params'])
        cls.atoms = worlds.enumerate_exact(cls.params)
        cls.cache, cls.channels = {}, {}
        cls.evidence = dict(atoms=[dict(a.sealed(), mass=str(a.mass)) for a in cls.atoms],
                            paths=[], tests={}, aggregates={}, boundaries={})
        # Only 24 main-world online replays; boundary assertions reweight this table.
        for i, atom in enumerate(cls.atoms):
            for rule in ('pi_0', 'pi_R', 'pi_Q'):
                channel = worlds.PaidValidation(atom.V)  # H,C are not channel inputs.
                initial = policies.public_initial()
                trace = policies.run(rule, initial, channel)
                result = score.score_truth(atom.sealed(), trace)
                cls.cache[i, rule] = (trace, result)
                cls.channels[i, rule] = channel.audit()
                cls.evidence['paths'].append(dict(atom=i, rule=rule, trace=trace,
                                                 observed=result, observation_audit=channel.audit()))

    def process_check(self):
        t = topology()
        self.assertEqual(t['rlimit_as'], [1073741824, 1073741824])
        self.assertEqual(t['threads'], [str(t['pid'])])
        self.assertEqual(t['children'], '')
        self.assertEqual(VIOLATIONS, [])
        return t

    def setUp(self):
        self.before = self.process_check()

    def tearDown(self):
        after = self.process_check()
        errors = self._outcome.result.errors + self._outcome.result.failures
        failed = any(test is self or getattr(test, 'test_case', None) is self for test, _ in errors)
        self.evidence['tests'][self._testMethodName] = dict(status='FAIL' if failed else 'PASS',
                                                          before=self.before, after=after)
        (OUT / f'results-{INVOCATION}.json').write_text(json.dumps(self.evidence, default=str, indent=2, sort_keys=True) + '\n')

    def aggregate(self, atoms, rule):
        columns = {'global_unsafe': 'GlobalUnsafe', 'expected_W': 'W',
                   'pub_new': 'PubNew', 'retained_valid_old': 'retained_valid_old_count'}
        output = {k: sum((a.mass * self.cache[i, rule][1][col]
                          for i, a in enumerate(atoms)), F(0)) for k, col in columns.items()}
        histories = ['NO_QUERY'] if rule == 'pi_0' else ['PASS', 'FAIL']
        output['history_mass'], output['history_risk'] = {}, {}
        for history in histories:
            mass = sum((a.mass for i, a in enumerate(atoms)
                        if self.cache[i, rule][1]['history'] == history), F(0))
            unsafe = sum((a.mass * self.cache[i, rule][1]['GlobalUnsafe'] for i, a in enumerate(atoms)
                          if self.cache[i, rule][1]['history'] == history), F(0))
            output['history_mass'][history] = mass
            output['history_risk'][history] = unsafe / mass if mass else None
        numerator = sum((a.mass * self.cache[i, rule][1]['NewUnsafe'] for i, a in enumerate(atoms)
                         if self.cache[i, rule][1]['PubNew']), F(0))
        output['publication_risk'] = numerator / output['pub_new'] if output['pub_new'] else None
        return output

    def check_tower(self, result):
        terms = []
        for history, mass in result['history_mass'].items():
            risk = result['history_risk'][history]
            if mass == 0:
                self.assertIsNone(risk)  # Undefined is not a zero-valued risk.
            else:
                self.assertIsInstance(risk, F)
                terms.append(mass * risk)
        self.assertEqual(sum(terms, F(0)), result['global_unsafe'])

    def test_01_atoms_normalization_and_conditional_law(self):
        self.assertEqual(len(self.atoms), 8)
        for atom, fixed in zip(self.atoms, self.fixture['atoms']):
            self.assertEqual(atom.sealed(), {k: fixed[k] for k in ('H', 'C', 'V')})
            self.assertIsInstance(atom.mass, F)
            self.assertEqual(atom.mass, F(fixed['mass']))
            self.assertGreaterEqual(atom.mass, 0)
        self.assertEqual(sum((a.mass for a in self.atoms), F(0)), 1)
        self.assertEqual(sum((a.mass for a in self.atoms if a.H), F(0)), self.params['h'])
        self.assertEqual(sum((a.mass for a in self.atoms if a.C), F(0)), self.params['c'])
        for h in (0, 1):
            for c in (0, 1):
                given = lambda a: a.H == h and a.C == c
                pass_prob = conditional(self.atoms, lambda a: a.V == 'PASS', given)
                fail_prob = conditional(self.atoms, lambda a: a.V == 'FAIL', given)
                self.assertEqual(pass_prob + fail_prob, 1)
                self.assertEqual(pass_prob, self.params['t' if c else 'f'])
                joint = sum((a.mass for a in self.atoms if given(a)), F(0))
                self.assertEqual(joint, (self.params['h'] if h else 1-self.params['h']) *
                                 (self.params['c'] if c else 1-self.params['c']))

    def test_02_all_24_frozen_states_scores_and_costs(self):
        self.assertEqual(len(self.fixture['expected24']), 24)
        self.assertEqual(len(self.cache), 24)
        for fixed in self.fixture['expected24']:
            i, rule = fixed['atom'], fixed['rule']
            with self.subTest(atom=i, rule=rule):
                trace, result = self.cache[i, rule]
                self.assertEqual({k: result[k] for k in fixed['scores']}, fixed['scores'])
                self.assertEqual(trace['terminal'], fixed['terminal'])
                self.assertEqual(result['terminal'], fixed['terminal'])
                self.assertEqual(trace['counters'], fixed['counters'])
                self.assertEqual(result['counters'], fixed['counters'])
                self.assertEqual([e['op'] for e in trace['events']], fixed['ops'])
                self.assertEqual(trace['events'][0]['withdrawn'], ['b-', 'r-'])
                self.assertLessEqual(result['counters']['optional_steps'], 4)
                self.assertLessEqual(result['counters']['repair'], 2)
                self.assertLessEqual(result['counters']['paid_query'], 2)
                self.assertEqual(result['cited_witness'], 's+' if fixed['scores']['PubNew'] else None)
                for event in trace['events']:
                    s = event['state']
                    self.assertFalse(set(s['M']) & set(s['B']))
                    self.assertFalse(set(s['M']) & set(s['Q']))
                    self.assertLessEqual(set(s['P']), set(s['M']))
                    ids = trace['initial']['identities']
                    self.assertEqual(len(s['M']), len({ids[v] for v in s['M']}))
                if fixed['scores']['PubNew']:
                    self.assertIn('a+', trace['events'][-2]['state']['Q'])
                    self.assertNotIn('a+', trace['events'][-2]['state']['M'])
                    if rule == 'pi_R':
                        self.assertIn('a-', trace['events'][-2]['state']['M'])
                        self.assertEqual(trace['events'][-1]['retired'], ['a-'])
                self.evidence['paths'][i*3+('pi_0','pi_R','pi_Q').index(rule)]['expected'] = fixed

    def test_03_exact_aggregates_and_independent_formula(self):
        for rule, fixed in self.fixture['expected_summary'].items():
            result = self.aggregate(self.atoms, rule)
            self.assertEqual({k: result[k] for k in fixed}, exact(fixed))
            self.assertEqual(result, analytic.expected(self.params, rule))
            self.check_tower(result)
            self.evidence['aggregates'][rule] = result
        repair, quarantine = (self.aggregate(self.atoms, r) for r in ('pi_R', 'pi_Q'))
        self.assertEqual(repair['global_unsafe'] - quarantine['global_unsafe'], F(7,80))
        self.assertEqual(repair['expected_W'], quarantine['expected_W'])
        self.assertEqual(repair['retained_valid_old'] - quarantine['retained_valid_old'], F(21,80))

    def test_04_bayes_reachable_histories_and_undefined(self):
        fixed = self.fixture['conditional']
        correct = conditional(self.atoms, lambda a: a.C == 1, lambda a: a.V == 'PASS')
        incorrect = conditional(self.atoms, lambda a: a.C == 0, lambda a: a.V == 'PASS')
        self.assertEqual(correct, F(fixed['correct_given_pass']))
        self.assertEqual(incorrect, F(fixed['incorrect_given_pass']))
        self.assertEqual(correct + incorrect, 1)
        self.assertEqual(correct, analytic.posterior(self.params, 'PASS'))
        for rule in ('pi_R', 'pi_Q'):
            result = self.aggregate(self.atoms, rule)
            self.assertEqual(result['history_mass']['PASS'], F(fixed['pass_mass']))
            self.assertEqual(result['history_mass']['FAIL'], F(fixed['fail_mass']))
            self.assertEqual(result['history_risk']['PASS'], F(fixed[rule+'_pass_risk']))
            self.assertEqual(result['history_risk']['FAIL'], F(fixed[rule+'_fail_risk']))
            self.assertEqual(result['publication_risk'], incorrect)
            self.check_tower(result)
        zero = self.aggregate(self.atoms, 'pi_0')
        self.assertEqual(zero['history_mass'], {'NO_QUERY': F(1)})
        self.assertIsNone(zero['publication_risk'])
        self.evidence['bayes'] = dict(correct_given_pass=correct, incorrect_given_pass=incorrect,
                                      pi_0_publication_risk=zero['publication_risk'])

    def test_05_online_separation_and_paid_admission(self):
        for rule in ('pi_0', 'pi_R', 'pi_Q'):
            for i, atom in enumerate(self.atoms):
                trace, result = self.cache[i, rule]
                calls = self.channels[i, rule]['calls']
                self.assertEqual(calls, 0 if rule == 'pi_0' else 1)
                self.assertEqual(calls, trace['counters']['paid_query'])
                if rule == 'pi_0':
                    self.assertEqual(self.channels[i, rule]['receipts'], [])
                else:
                    self.assertEqual(self.channels[i, rule]['receipts'],
                                     [('repair','validate')] if rule == 'pi_R' else [('quarantine','repair','validate')])
                for j, other in enumerate(self.atoms):
                    if rule == 'pi_0' or atom.V == other.V:
                        self.assertEqual(trace, self.cache[j, rule][0])
        self.assertNotEqual(self.cache[0, 'pi_R'][1]['NewUnsafe'], self.cache[2, 'pi_R'][1]['NewUnsafe'])
        channel = worlds.PaidValidation('PASS')
        for bad in ((), ('validate',), ('repair',), ('repair','validate','validate')):
            with self.assertRaises(ValueError):
                channel.request(bad)
        self.assertEqual(channel.audit()['calls'], 0)
        self.assertEqual(channel.request(('repair', 'validate')), 'PASS')
        with self.assertRaises(ValueError):
            channel.request(('repair', 'validate'))
        # pi_0 must not even attempt to read or call an observation channel.
        class NoObservation:
            def __getattribute__(self, name):
                raise AssertionError('pi_0 accessed observation channel')
        self.assertEqual(policies.run('pi_0', policies.public_initial(), NoObservation()), self.cache[0, 'pi_0'][0])
        for key in ('H', 'C', 'V', 'offline_truth'):
            initial = policies.public_initial()
            initial[key] = 1
            with self.assertRaises(ValueError):
                policies.run('pi_R', initial, worlds.PaidValidation('PASS'))
        # Independent scorer refuses forged publication and free query traces.
        for field in ('terminal', 'paid'):
            bad = deepcopy(self.cache[0, 'pi_R'][0])
            if field == 'terminal':
                bad['terminal']['M'].append('a-')
            else:
                next(e for e in bad['events'] if e['op'] == 'validate')['paid'] = False
            with self.assertRaises(ValueError):
                score.score_truth(self.atoms[0].sealed(), bad)

    def test_06_mathematical_boundary_sanity_only(self):
        for boundary in self.fixture['boundaries']:
            params = dict(self.params, **exact(boundary['overrides']))
            atoms = worlds.enumerate_exact(params)
            self.assertEqual(sum((a.mass for a in atoms), F(0)), 1)
            outputs = {}
            for rule, fixed in boundary['summary'].items():
                result = self.aggregate(atoms, rule)
                self.assertEqual({k: result[k] for k in fixed}, exact(fixed))
                self.assertEqual(result, analytic.expected(params, rule))
                self.check_tower(result)
                outputs[rule] = result
            name = boundary['name']
            if name == 'h_zero':
                self.assertEqual(outputs['pi_R']['global_unsafe'], outputs['pi_Q']['global_unsafe'])
            elif name == 'noninformative':
                for message in ('PASS','FAIL'):
                    self.assertEqual(conditional(atoms, lambda a: a.C == 1, lambda a: a.V == message), params['c'])
                    self.assertEqual(analytic.posterior(params, message), params['c'])
            elif name == 'no_false_pass':
                self.assertEqual(sum((a.mass for a in atoms if a.C == 0 and a.V == 'PASS'), F(0)), 0)
                self.assertEqual(outputs['pi_R']['history_risk']['PASS'], 0)
            elif name in ('all_pass', 'no_pass'):
                unreachable = 'FAIL' if name == 'all_pass' else 'PASS'
                self.assertIsNone(conditional(atoms, lambda a: a.C == 1, lambda a: a.V == unreachable))
                self.assertIsNone(analytic.posterior(params, unreachable))
                for rule in ('pi_R','pi_Q'):
                    self.assertIsNone(outputs[rule]['history_risk'][unreachable])
            self.evidence['boundaries'][name] = outputs

    def test_07_import_exactness_and_process_contract(self):
        allowed = {'worlds': {'dataclasses', 'fractions'}, 'policies': {'copy'},
                   'score': set(), 'analytic': {'fractions'}}
        inventory = {}
        for module, imports in allowed.items():
            tree = ast.parse((ROOT / f'src/x0b/{module}.py').read_text())
            actual = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    actual.update(a.name for a in node.names)
                elif isinstance(node, ast.ImportFrom):
                    actual.add(node.module)
                elif isinstance(node, ast.Constant):
                    self.assertNotIsInstance(node.value, float)
                elif isinstance(node, ast.Attribute):
                    self.assertNotIn(node.attr, ('fork','system','Popen','Thread','Process','start_new_thread'))
            self.assertEqual(actual, imports)
            inventory[module] = sorted(actual)
        self.evidence['imports'] = inventory
        with self.assertRaises(ValueError):
            worlds.enumerate_exact(dict(self.params, h='1/4'))
        with self.assertRaises(ValueError):
            worlds.enumerate_exact(dict(self.params, h=F(2)))
        with self.assertRaises(ValueError):
            analytic.expected(self.params, 'optimized_policy')
        self.process_check()
