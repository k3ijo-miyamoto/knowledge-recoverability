"""Inspect the single saved sequence; no gateway/client re-execution."""
import ast,copy,hashlib,importlib.util,json,pathlib,shutil,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/p2-egress-pilot-v01/attempt-01'
SOURCE=ROOT/'artifacts/urllib3-c1-observability-v01/attempt-01/pypi-2.0.0.json'
spec=importlib.util.spec_from_file_location('offline_score',ROOT/'src/p2_egress_pilot/scorer.py')
scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)

class Evidence(unittest.TestCase):
    def test_fixed_four_actual_receipts(self):
        ledger=json.loads((OUT/'sequence-ledger.json').read_text());self.assertEqual(ledger['responses_received'],4)
        self.assertEqual(ledger['paired_sequences'],1);self.assertEqual(len(ledger['commands']),2)
        self.assertTrue(all(x['exit_code']==0 for x in ledger['commands']))
        plan=json.loads((OUT/'frozen-plan.json').read_text())
        self.assertEqual(hashlib.sha256((OUT/'frozen-plan.json').read_bytes()).hexdigest(),(OUT/'plan.sha256').read_text().split()[0])
        for world in ('GOOD','STALE_EGRESS'):
            records=[json.loads(x) for x in (OUT/f'{world}-gateway.jsonl').read_text().splitlines()]
            for q,r in zip(('q1','q2'),records):
                received=(OUT/f'{world}-{q}-client.bin').read_bytes();answer=json.loads(received)
                self.assertEqual(answer['knowledge_version'],plan['expected'][world][q])
                self.assertEqual(answer['epoch'],plan['epoch']);self.assertEqual(answer['claim_id'],'x')
                self.assertEqual(answer['query_id'],q);self.assertEqual(answer['route'],'R')
                self.assertEqual(received,(OUT/f'{world}-{q}-egress.bin').read_bytes())
                self.assertEqual(r['runtime']['rlimit_as'],[1073741824,1073741824])
                self.assertEqual(r['source']['source_id'],hashlib.sha256(SOURCE.read_bytes()).hexdigest())
                self.assertEqual(r['source']['yanked'],True);self.assertEqual(r['source']['version'],'2.0.0')
                self.assertEqual(r['store']['store_id'],plan['store_id'])
                self.assertEqual(r['retrieval']['knowledge_version'],'x+')
                g=r['generated'];self.assertTrue(g['content']['yanked']);self.assertEqual(g['content']['knowledge_version'],'x+')
                serialized=(json.dumps(g['content'],sort_keys=True,separators=(',',':'))+'\n').encode()
                self.assertEqual(hashlib.sha256(serialized).hexdigest(),g['content_sha256'])
                self.assertEqual(g['generator_span']['output_sha256'],g['content_sha256'])
            self.assertEqual((OUT/f'{world}-stdout.bin').read_bytes(),b''.join((OUT/f'{world}-{q}-client.bin').read_bytes() for q in ('q1','q2')))

    def test_pre_egress_equality_and_q1_negative_control(self):
        actual=scorer.assess(OUT,SOURCE)
        self.assertEqual(actual['verdict'],'PASS')
        self.assertTrue(actual['pre_egress_equal']);self.assertTrue(actual['q1_only_indistinguishable'])
        self.assertTrue(actual['q1_plus_q2_distinguishes'])
        self.assertEqual(actual['old_answer_counts'],{'GOOD':0,'STALE_EGRESS':1})
        self.assertTrue(actual['finite_domain_judgments']['STALE_EGRESS']['q1_only_source_consistent'])
        self.assertFalse(actual['finite_domain_judgments']['STALE_EGRESS']['all_D_source_consistent'])
        self.assertTrue(actual['finite_domain_judgments']['GOOD']['all_D_source_consistent'])
        self.assertEqual(actual,json.loads((OUT/'scores.json').read_text()))

    def test_source_misuse_and_old_declaration(self):
        raw=(OUT/'GOOD-q2-client.bin').read_bytes();snapshot=SOURCE.read_bytes()
        other=(ROOT/'artifacts/urllib3-c1-observability-v01/attempt-01/pypi-2.0.2.json').read_bytes()
        with self.assertRaises(ValueError):scorer.score_answer(raw,other)
        bad=json.loads(raw);bad['package_version']='2.0.2'
        with self.assertRaises(ValueError):scorer.score_answer(json.dumps(bad).encode(),snapshot)
        bad=json.loads(raw);bad['knowledge_version']='x-'
        with self.assertRaises(ValueError):scorer.score_answer(json.dumps(bad).encode(),snapshot)
        stale=(OUT/'STALE_EGRESS-q2-client.bin').read_bytes()
        self.assertEqual(scorer.score_answer(stale,snapshot)['old_served'],1)
        self.assertEqual(scorer.score_answer(raw,snapshot)['old_served'],0)
        bad=json.loads(raw);bad['answer']='urllib3 is universally safe'
        with self.assertRaises(ValueError):scorer.score_answer(json.dumps(bad).encode(),snapshot)

    def test_tampered_delivery_and_route_rejected(self):
        scratch=json.loads((OUT/'preflight.json').read_text())['scratch']
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            dst=pathlib.Path(tmp)
            for p in OUT.iterdir():
                if p.suffix in ('.json','.jsonl','.bin'):shutil.copyfile(p,dst/p.name)
            target=dst/'STALE_EGRESS-q2-client.bin';original=target.read_bytes();target.write_bytes(original+b' ')
            with self.assertRaises(ValueError):scorer.assess(dst,SOURCE)
            target.write_bytes(original)
            receipt=dst/'GOOD-q1-client.json';bad=json.loads(receipt.read_text());bad['route']='not-R';receipt.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):scorer.assess(dst,SOURCE)

    def test_code_boundaries_and_otel_label(self):
        for name,forbidden in [('scorer',('gateway','client')),('client',('gateway','scorer')),('gateway',('scorer',))]:
            tree=ast.parse((ROOT/f'src/p2_egress_pilot/{name}.py').read_text())
            for n in ast.walk(tree):
                if isinstance(n,ast.Import):self.assertFalse(any(any(x in a.name for x in forbidden) for a in n.names))
                if isinstance(n,ast.ImportFrom):self.assertFalse(any(x in (n.module or '') for x in forbidden))
        pre=json.loads((OUT/'preflight.json').read_text())
        self.assertEqual(pre['otel'],'OTEL_NOT_INSTALLED')
        for world in ('GOOD','STALE_EGRESS'):
            for line in (OUT/f'{world}-gateway.jsonl').read_text().splitlines():
                self.assertEqual(json.loads(line)['generated']['generator_span']['kind'],'stdlib_logical_span_NOT_OTEL')
