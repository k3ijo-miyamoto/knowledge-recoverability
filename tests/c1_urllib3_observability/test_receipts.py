import importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('c1_harness',ROOT/'src/c1_urllib3_observability/harness.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
OUT=ROOT/'artifacts/urllib3-c1-observability-v01/attempt-01'
class Receipts(unittest.TestCase):
    def test_installed_parser_rejects_absent_and_duplicate(self):
        with self.assertRaises(ValueError):h.installed({'installed':[]})
        package={'metadata':{'name':'urllib3','version':'2.0.2'}}
        with self.assertRaises(ValueError):h.installed({'installed':[package,package]})
    def test_actual_receipts_and_controlled_lifecycle(self):
        read=lambda name:json.loads((OUT/name).read_text())
        a,b=read('state-A.json'),read('state-B.json')
        observed=h.verdict(a,b,read('inspect-A.json'),read('inspect-B.json'))
        self.assertTrue(observed['PASS']);self.assertTrue(observed['same_full_inspect'])
        self.assertFalse(h.verdict(a,a,read('inspect-A.json'),read('inspect-B.json'))['PASS'])
        events=read('command-lifecycle-ledger.json')
        self.assertEqual(len([e for e in events if e['operation'].startswith('start-')]),2)
        stops=[e for e in events if e['operation']=='reap']
        self.assertEqual(len(stops),2);self.assertTrue(all(e['exit_code']==0 for e in stops))
        self.assertFalse(any(e['operation']=='forced-cleanup' for e in events))
        for state in (a,b):self.assertEqual(state['rlimit_as'],[1073741824,1073741824])
        for version in ('2.0.0','2.0.2'):
            report=read('install-'+version+'.json')
            self.assertEqual(report['install'][0]['metadata']['version'],version)
            expected=next(x['actual_sha256'] for x in read('download-ledger.json')['commands'] if x['version']==version)
            self.assertEqual(report['install'][0]['download_info']['archive_info']['hashes']['sha256'],expected)
    def test_independent_local_input_identity(self):
        a=json.loads((OUT/'bug-2.0.0.json').read_text());b=json.loads((OUT/'bug-2.0.2.json').read_text())
        self.assertEqual(a['expected_sha256'],b['expected_sha256'])
        self.assertLessEqual(a['expected_bytes'],300*1024)
        self.assertLessEqual(a['compressed_bytes'],1048576)
        self.assertEqual(a['version'],'2.0.0');self.assertEqual(b['version'],'2.0.2')
        # Do not force the optional scientific contrast; report actual completeness separately.
        self.assertEqual(b['complete'],b['expected_sha256']==b['produced_sha256'])
