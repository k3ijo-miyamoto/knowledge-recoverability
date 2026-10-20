"""Sole approved scientific suite; exact fixture frozen before implementation."""
import ast
from dataclasses import fields
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from audit_allocation_pilot import worlds, policies, score, analytic

OUT = ROOT/'artifacts/audit-allocation-pilot-v01/attempt-02'
FIXTURE = Path(__file__).with_name('fixture_exact_v01.json')
FROZEN = '2c64e17a498ceeb3b57fb74c0bf0d5da405b514738859e0a62e732fc9f79c155'
CONTRACT = json.loads(FIXTURE.read_text())
POLICIES = ('P_E', 'P_C', 'P_Q', 'P_OPT')


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def evaluate(cell, name):
    rows = []
    traces = []
    for i, atom in enumerate(worlds.atoms(cell)):
        online = []
        def decide(view):
            action = policies.choose(name, view)
            online.append({'priors': view.priors, 'history': view.history,
                           'spent': view.spent, 'quarantined': view.quarantined,
                           'action': action})
            return action
        receipts = atom.run(decide)
        gold = atom.offline_gold()
        rows.append((atom.weight, gold, receipts))
        traces.append({'cell': cell, 'policy': name, 'atom_index': i,
                       'weight': atom.weight, 'policy_visible': online,
                       'offline_only': {f.name: getattr(gold, f.name) for f in fields(gold)},
                       'receipts': [{'action': r.action, 'response': r.response, 'cost': r.cost}
                                    for r in receipts], 'score': score.replay(gold, receipts)})
    return score.summarize(rows), traces


class Contract(unittest.TestCase):
    def test_00_fixture_and_environment(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), FROZEN)
        self.assertEqual(resource.getrlimit(resource.RLIMIT_AS), (1073741824, 1073741824))
        self.assertEqual(len(list(Path('/proc/self/task').iterdir())), 1)
        self.assertEqual(Path(f'/proc/self/task/{os.getpid()}/children').read_text().strip(), '')
        self.assertTrue(sys.dont_write_bytecode)
        (OUT/'test-environment.json').write_text(json.dumps({
            'python': sys.version, 'rlimit_as': resource.getrlimit(resource.RLIMIT_AS),
            'threads': 1, 'children': 0, 'fixture_sha256': FROZEN}, indent=2)+'\n')

    def test_01_world_law_and_symmetry(self):
        for cell in ('L', 'R'):
            atoms = worlds.atoms(cell)
            self.assertEqual(len(atoms), 16)
            self.assertEqual(sum(a.weight for a in atoms), 1)
            self.assertTrue(all(isinstance(a.weight, F) and a.weight > 0 for a in atoms))
            c, e = map(F, CONTRACT['conditions'][cell])
            self.assertEqual(sum(a.weight for a in atoms if a.offline_gold().C), c)
            self.assertEqual(sum(a.weight for a in atoms if a.offline_gold().E), e)
            self.assertEqual(sum(a.weight for a in atoms if a.offline_gold().C and a.offline_gold().E), F(51,80))
            for axis in ('C','E'):
                for truth in (False, True):
                    group = [a for a in atoms if getattr(a.offline_gold(), axis)==truth]
                    plus = sum(a.weight for a in group if getattr(a.offline_gold(), 'V_'+axis))
                    self.assertEqual(plus/sum(a.weight for a in group), F(9,10) if truth else F(1,10))
            for C in (False,True):
                for E in (False,True):
                    group=[a for a in atoms if (a.offline_gold().C,a.offline_gold().E)==(C,E)]
                    total=sum(a.weight for a in group)
                    for a in group:
                        g=a.offline_gold()
                        self.assertEqual(a.weight/total,(F(9,10) if g.V_C==C else F(1,10))*(F(9,10) if g.V_E==E else F(1,10)))
        swapped = {(a.offline_gold().E, a.offline_gold().C, a.offline_gold().V_E, a.offline_gold().V_C):a.weight for a in worlds.atoms('L')}
        self.assertEqual(swapped,{tuple(getattr(a.offline_gold(),f.name) for f in fields(worlds.Gold)):a.weight for a in worlds.atoms('R')})

    def test_02_all_worlds_branches_and_exact_reference(self):
        all_traces=[]; summaries={}; references={}
        for cell in ('L','R'):
            summaries[cell]={}
            c,e=map(F,CONTRACT['conditions'][cell])
            references[cell]=analytic.exact_tree_reference(c,e)
            self.assertEqual(references[cell]['W'], F(459,800))
            self.assertEqual(references[cell]['expected_K'], F(13,10))
            best=policies.optimum(policies.View((c,e)))
            self.assertEqual(best[:2],(references[cell]['W'],references[cell]['expected_K']))
            for name in POLICIES:
                summary,traces=evaluate(cell,name); all_traces.extend(traces)
                summaries[cell][name]=summary
                expected=CONTRACT[CONTRACT['expected'][cell][name]]
                self.assertEqual(summary['totals']['W'],F(expected['W']))
                self.assertEqual(summary['totals']['GlobalUnsafe'],F(expected['unsafe']))
                self.assertEqual(summary['totals']['K'],F(expected['expected_K']))
                self.assertEqual(summary['max_K'],expected['max_K'])
                self.assertEqual(summary['totals']['StaleServed'],0)
                self.assertEqual(summary['totals']['NewUnsafe'],summary['totals']['GlobalUnsafe'])
                self.assertEqual(summary['totals']['staging_repair_units'],1)
                self.assertEqual(summary['totals']['publication_admin_units'],summary['totals']['PubNew'])
                for path,b in summary['branches'].items():
                    self.assertTrue(b['admissible'],(cell,name,path,b))
                    self.assertGreater(b['mass'],0)
                    if path[-1][0]=='PUB':
                        self.assertEqual(b['conditional_unsafe'],F(101,560))
                    else:
                        self.assertEqual(b['conditional_unsafe'],0)
                if name in ('P_C','P_E'):
                    ref=analytic.audit_reference(c,e,name[-1])
                    for k in ('pass_probability','posterior_good','conditional_unsafe','W','unsafe','expected_K'):
                        self.assertEqual(ref[k],F(expected[k]))
                # Independent per-world Boolean outcomes and costs, not only aggregate matches.
                for t in traces:
                    g=t['offline_only']; rs=t['receipts']; s=t['score']
                    published=rs[-1]['action']=='PUB'
                    self.assertEqual(s['W'],int(published and g['C'] and g['E']))
                    self.assertEqual(s['GlobalUnsafe'],int(published and not(g['C'] and g['E'])))
                    self.assertEqual(s['K'],sum(r['action'] in ('C','E','Q') for r in rs))
                    self.assertLessEqual(s['K'],2)
                    if not published:
                        self.assertTrue(any(r['action']=='Q' and r['cost']==1 for r in rs))
        self.assertEqual(len(all_traces),128)
        # Save complete observed results only after computations; never change frozen expectations.
        (OUT/'traces.json').write_text(json.dumps(encode(all_traces),indent=2)+'\n')
        (OUT/'results.json').write_text(json.dumps(encode(summaries),indent=2)+'\n')
        (OUT/'analytic-reference.json').write_text(json.dumps(encode(references),indent=2)+'\n')
        lines=['cell,policy,expected_W,observed_W,expected_unsafe,observed_unsafe,expected_K,observed_K,max_K']
        for cell in ('L','R'):
            for name in POLICIES:
                expected=CONTRACT[CONTRACT['expected'][cell][name]];s=summaries[cell][name]
                lines.append(','.join(map(str,[cell,name,expected['W'],s['totals']['W'],expected['unsafe'],s['totals']['GlobalUnsafe'],expected['expected_K'],s['totals']['K'],s['max_K']])))
        (OUT/'expected-observed.csv').write_text('\n'.join(lines)+'\n')

    def test_03_information_isolation(self):
        self.assertEqual([f.name for f in fields(policies.View)],['priors','history','spent','quarantined'])
        for cell in ('L','R'):
            for name in POLICIES:
                decisions={}; world_pairs={}
                for atom in worlds.atoms(cell):
                    def callback(view):
                        # Same paid observation state must produce same action for all gold worlds.
                        key=(view.priors,view.history,view.spent,view.quarantined)
                        action=policies.choose(name,view)
                        if key in decisions:
                            self.assertEqual(action,decisions[key])
                        decisions[key]=action
                        world_pairs.setdefault(key,set()).add(atom.offline_gold())
                        self.assertEqual(view.spent,len(view.history)+int(view.quarantined))
                        return action
                    atom.run(callback)
                root=(worlds.PRIORS[cell],(),0,False)
                self.assertEqual(len(world_pairs[root]),16)
                # Full-support hidden truths remain indistinguishable even after a paid message.
                for key, golds in world_pairs.items():
                    if len(key[1])==1:
                        self.assertEqual({(g.C,g.E) for g in golds},set(__import__('itertools').product((False,True),repeat=2)))
        # Static dependency boundary: online decisions have no gold/scorer/world/fixture access.
        tree=ast.parse(Path(policies.__file__).read_text())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertEqual(set(imports),{'dataclasses','fractions','functools'})
        self.assertFalse(any(isinstance(n,ast.Name) and n.id in ('open','eval','exec','__import__') for n in ast.walk(tree)))
        for module,forbidden in ((score,('policies','worlds')),(analytic,('policies','worlds','score'))):
            tree=ast.parse(Path(module.__file__).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    self.assertFalse(any(s in (node.module or '') for s in forbidden))

    def test_04_adversarial_receipts_and_budget(self):
        gold=worlds.Gold(False,False,False,False);R=policies.Receipt
        for receipts in [
            (R('Q',None,0),R('STOP',None,0)),
            (R('C',False,1),R('E',False,1),R('Q',None,1),R('STOP',None,0)),
            (R('C',True,1),R('Q',None,1),R('STOP',None,0)),
            (R('Q',None,1),),
            (R('Q',None,1),R('STOP',None,0),R('PUB',None,0))]:
            with self.assertRaises(ValueError):score.replay(gold,receipts)
        # A cost-free STOP without Q is unsafe, not an implicit free quarantine.
        self.assertEqual(score.replay(gold,(R('STOP',None,0),))['GlobalUnsafe'],1)
        rows=[]
        for atom in worlds.atoms('L'):
            g=atom.offline_gold()
            rows.append((atom.weight,g,(R('C',g.V_C,1),R('E',g.V_E,1),R('PUB',None,0))))
        illegal=score.summarize(rows)
        self.assertTrue(any(not b['admissible'] for b in illegal['branches'].values()))
        # Two paid failed audits leave no safe terminal action under the K=2 limit.
        for cell in ('L','R'):
            v=policies.View(worlds.PRIORS[cell])
            v=policies.after_audit(policies.after_audit(v,'C',False),'E',False)
            self.assertIsNone(policies.optimum(v))
        atom=worlds.atoms('L')[0]
        calls=iter(('C','E','Q'))
        with self.assertRaises(ValueError):atom.run(lambda _:next(calls))

    def test_05_quarantine_first_and_repeat_query(self):
        for cell in ('L','R'):
            v=policies.View(worlds.PRIORS[cell]);axis='E' if cell=='L' else 'C'
            one=policies.after_audit(v,axis,True)
            two=policies.after_audit(one,axis,True)
            self.assertEqual(policies.goodness(one),policies.goodness(two))
            self.assertEqual(two.spent,2)
            with self.assertRaises(ValueError):policies.after_audit(one,axis,False)
            # Q-first is feasible, tied on W, but more costly than audit then contingent Q.
            rows=[]
            for atom in worlds.atoms(cell):
                def q_first(view):
                    if not view.quarantined:return 'Q'
                    if not view.history:return axis
                    return 'PUB' if policies.goodness(view)>=F(4,5) else 'STOP'
                rows.append((atom.weight,atom.offline_gold(),atom.run(q_first)))
            s=score.summarize(rows)
            self.assertEqual(s['totals']['W'],F(459,800))
            self.assertEqual(s['totals']['K'],2)
            self.assertTrue(all(b['admissible'] for b in s['branches'].values()))

    def test_06_swap_results(self):
        for left,right in (('P_E','P_C'),('P_C','P_E'),('P_Q','P_Q'),('P_OPT','P_OPT')):
            a,_=evaluate('L',left);b,_=evaluate('R',right)
            for key in ('W','GlobalUnsafe','K','PubNew','quarantines'):
                self.assertEqual(a['totals'][key],b['totals'][key])

if __name__=='__main__':
    unittest.main()
