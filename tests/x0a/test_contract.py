"""Twelve G22 fixture families; fixed expected values independent of both modules."""

import ast
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/x0a-deterministic-v01/attempt-02'
ATTEMPT = os.environ.get('X0A_INVOCATION', 'unrecorded')
VIOLATIONS = []


def audit(event, args):
    if (event.startswith(('subprocess.', 'socket.', 'os.exec', 'os.spawn', 'os.posix_spawn'))
            or event in ('os.fork', 'os.forkpty', 'os.system', 'os.setuid', 'os.setgid')):
        VIOLATIONS.append(event)
        raise RuntimeError('Prohibited process/network operation: ' + event)


sys.addaudithook(audit)
from src.x0a.transition import replay  # noqa: E402
from src.x0a.score import score  # noqa: E402


def topology():
    pid = os.getpid()
    tasks = sorted(x.name for x in Path('/proc/self/task').iterdir())
    children = Path('/proc/self/task/' + str(pid) + '/children').read_text().strip()
    return dict(pid=pid, ppid=os.getppid(), tasks=tasks, children=children,
                rlimit_as=list(resource.getrlimit(resource.RLIMIT_AS)))


class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT / 'tests/x0a/fixtures_v01.json').read_bytes()
        frozen = json.loads((OUT / 'fixture_freeze.json').read_text())
        if hashlib.sha256(raw).hexdigest() != frozen['sha256']:
            raise AssertionError('Frozen fixture bytes changed')
        cls.fixtures = json.loads(raw)
        if set(cls.fixtures) != {f'A{i:02}' for i in range(1, 13)}:
            raise AssertionError('Exactly twelve logical families required')
        cls.records = {}
        imports = {}
        for relative in ('src/x0a/transition.py', 'src/x0a/score.py', 'tests/x0a/test_contract.py'):
            tree = ast.parse((ROOT / relative).read_text())
            names = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    names.append(node.module)
                if isinstance(node, ast.Attribute) and node.attr in ('fork', 'system', 'spawn', 'start_new_thread', 'Thread', 'Process', 'Popen'):
                    raise AssertionError('Child/thread launch API in implementation')
            imports[relative] = names
        if imports['src/x0a/transition.py'] != ['copy'] or imports['src/x0a/score.py']:
            raise AssertionError('Engine/scorer interface independence violated')
        (OUT / f'interface-audit-{ATTEMPT}.json').write_text(json.dumps(imports, indent=2) + '\n')

    def check_process(self):
        info = topology()
        self.assertEqual(info['rlimit_as'], [1073741824, 1073741824])
        self.assertEqual(info['tasks'], [str(info['pid'])])
        self.assertEqual(info['children'], '')
        self.assertEqual(VIOLATIONS, [])
        return info

    def run_family(self, case_id):
        before = self.check_process()
        family = self.fixtures[case_id]
        variants = family['variants'] if case_id == 'A10' else [family]
        self.assertEqual(len(variants), 2 if case_id == 'A10' else 1)
        record = dict(status='FAIL', before=before, variants=[])
        self.records[case_id] = record
        try:
            traces = []
            scores = []
            for fixture in variants:
                online, script = deepcopy(fixture['online_input']), deepcopy(fixture['script'])
                # Gold is not passed to replay; expected answers are never computed by score.
                trace = replay(online, script)
                result = score(deepcopy(fixture['offline_truth']), trace)
                expected = fixture['expected']
                record['variants'].append(dict(expected=expected, trace=trace, observed=result))
                self.assertEqual(online, fixture['online_input'])
                self.assertEqual(script, fixture['script'])
                self.assertEqual(trace['terminal'], expected['terminal'])
                self.assertEqual(trace['disposition'], expected['disposition'])
                rejected = [e['reason'] for e in trace['events'][1:] if not e['accepted']]
                self.assertEqual(rejected, [] if expected['reject_reason'] is None else [expected['reject_reason']])
                self.assertEqual(trace['counters'], expected['counters'])
                self.assertEqual(result['counters'], expected['counters'])
                self.assertEqual({k: result[k] for k in expected['scores']}, expected['scores'])
                self.assertEqual(trace['symbolic_costs'], expected['symbolic_costs'])
                self.assertEqual(result['symbolic_costs'], expected['symbolic_costs'])
                for event in trace['events']:
                    s = event['state']
                    self.assertFalse(set(s['M']) & set(s['B']))
                    self.assertFalse(set(s['M']) & set(s['Q']))
                    self.assertLessEqual(set(s['P']), set(s['M']))
                    self.assertEqual(len({online['versions'][v]['identity'] for v in s['M']}), len(s['M']))
                traces.append(trace)
                scores.append(result)
            if case_id == 'A01':
                self.assertEqual(traces[0]['events'][0]['withdrawn'], ['b-', 'r-'])
            elif case_id == 'A03':
                self.assertTrue(scores[0]['predicates']['a+']['content'])
                self.assertTrue(scores[0]['predicates']['a+']['support'])
                self.assertFalse(scores[0]['predicates']['a+']['warrant'])
                self.assertEqual(traces[0]['disposition'], 'TERMINATED')
            elif case_id == 'A04':
                self.assertEqual([e['message'] for e in traces[0]['events'] if e['op'] == 'validate'], ['PASS'])
                self.assertFalse(scores[0]['predicates']['a+']['content'])
            elif case_id == 'A06':
                self.assertIn('a-', traces[0]['events'][-2]['state']['M'])
                self.assertEqual(traces[0]['reasons']['a-'], 'atomic_replacement')
                corrupt = deepcopy(traces[0])
                corrupt['terminal']['M'].append('a-')
                with self.assertRaises(ValueError):
                    score(variants[0]['offline_truth'], corrupt)
            elif case_id in ('A05', 'A08'):
                self.assertEqual(traces[0]['events'][-1]['state'], traces[0]['events'][-2]['state'])
            elif case_id == 'A10':
                self.assertEqual(variants[0]['online_input'], variants[1]['online_input'])
                self.assertEqual(variants[0]['script'], variants[1]['script'])
                self.assertEqual(traces[0], traces[1])
                self.assertNotEqual(scores[0]['NewUnsafe'], scores[1]['NewUnsafe'])
                for key in ('offline_truth', 'content', 'historical_edges', 'expected'):
                    leaked = deepcopy(variants[0]['online_input'])
                    leaked[key] = variants[0]['offline_truth']
                    with self.assertRaises(ValueError):
                        replay(leaked, variants[0]['script'])
                leaked = deepcopy(variants[0]['online_input'])
                leaked['sources']['s+']['valid'] = True
                with self.assertRaises(ValueError):
                    replay(leaked, variants[0]['script'])
            elif case_id == 'A11':
                self.assertEqual([e['message'] for e in traces[0]['events'] if e['op'] == 'repair'], ['FAIL', 'FAIL'])
            record['after'] = self.check_process()
            record['status'] = 'PASS'
        except Exception as exc:
            record['error'] = repr(exc)
            raise
        finally:
            (OUT / f'results-{ATTEMPT}.json').write_text(json.dumps(self.records, indent=2, sort_keys=True) + '\n')


def family_test(case_id):
    def test(self):
        self.run_family(case_id)
    return test


for _number in range(1, 13):
    _id = f'A{_number:02}'
    setattr(Contract, 'test_' + _id, family_test(_id))
