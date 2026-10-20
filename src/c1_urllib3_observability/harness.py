"""One bounded C1 A/B sequence, offline local wheels and controlled children."""
import datetime, hashlib, json, os, pathlib, selectors, subprocess, sys, time

ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/urllib3-c1-observability-v01/attempt-01'

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def installed(inspect):
    matches=[p for p in inspect['installed'] if p['metadata']['name'].lower()=='urllib3']
    if len(matches)!=1:raise ValueError('exactly one installed urllib3 required')
    return matches[0]

def verdict(a,b,before,after):
    disk_a=installed(before);disk_b=installed(after)
    return {'same_installed_record':disk_a==disk_b,'same_full_inspect':before==after,
            'installed_A':disk_a['metadata']['version'],'installed_B':disk_b['metadata']['version'],
            'same_interpreter':a['interpreter']==b['interpreter'],
            'same_module_path':a['module_file']==b['module_file'],
            'different_process_identity':(a['pid'],a['start_identity'])!=(b['pid'],b['start_identity']),
            'runtime_A':a['version'],'runtime_B':b['version'],
            'PASS':disk_a==disk_b and disk_a['metadata']['version']=='2.0.2' and
                   a['version']=='2.0.0' and b['version']=='2.0.2' and
                   a['interpreter']==b['interpreter'] and a['module_file']==b['module_file'] and
                   a['start_identity']!=b['start_identity']}

class Harness:
    def __init__(self):
        self.scratch=pathlib.Path((OUT/'scratch-path.txt').read_text().strip())
        self.python=str(self.scratch/'venv/bin/python')
        self.env={'PATH':'/usr/bin:/bin','HOME':str(self.scratch),'TMPDIR':str(self.scratch),
                  'PIP_CONFIG_FILE':'/dev/null','PIP_NO_INPUT':'1','PIP_DISABLE_PIP_VERSION_CHECK':'1',
                  'PYTHONDONTWRITEBYTECODE':'1','LC_ALL':'C.UTF-8'}
        self.events=[];self.worker=None;self.start=time.monotonic()
    def save(self):
        (OUT/'command-lifecycle-ledger.json').write_text(json.dumps(self.events,indent=2)+'\n')
    def size(self,path):
        return sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not p.is_symlink())
    def bounds(self):
        if self.size(self.scratch)>80*1048576:raise RuntimeError('scratch limit')
        if self.size(OUT)>5*1048576:raise RuntimeError('evidence limit')
        if time.monotonic()-self.start>110:raise RuntimeError('measurement harness timeout reserve')
    def command(self,label,args,filename=None):
        self.bounds()
        argv=['timeout','--signal=TERM','--kill-after=2s','120s','prlimit','--as=1073741824:1073741824','--',self.python,'-B']+args
        start=utc();t=time.monotonic()
        p=subprocess.run(argv,env=self.env,cwd=ROOT,capture_output=True,text=True,timeout=120)
        (OUT/(filename or label+'.stdout')).write_text(p.stdout)
        (OUT/(label+'.stderr')).write_text(p.stderr)
        self.events.append({'operation':label,'command':argv,'started_utc':start,'ended_utc':utc(),
                            'elapsed_seconds':time.monotonic()-t,'exit_code':p.returncode})
        self.save();self.bounds()
        if p.returncode:raise RuntimeError(label+' failed')
        return p.stdout
    def install(self,version):
        return self.command('install-'+version,['-m','pip','--no-cache-dir','install','--no-index',
            '--find-links',str(self.scratch/'wheels'),'--no-deps','--report',str(OUT/f'install-{version}.json'),
            'urllib3=='+version])
    def start_worker(self,label):
        if self.worker is not None:raise RuntimeError('concurrent worker forbidden')
        argv=['prlimit','--as=1073741824:1073741824','--',self.python,'-B',str(ROOT/'src/c1_urllib3_observability/worker.py')]
        self.worker=subprocess.Popen(argv,env=self.env,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.events.append({'operation':'start-'+label,'command':argv,'pid':self.worker.pid,'timestamp':utc(),'worker_alarm_seconds':120})
        self.save()
    def request(self,text):
        t=time.monotonic();self.worker.stdin.write(text+'\n');self.worker.stdin.flush()
        with selectors.DefaultSelector() as selector:
            selector.register(self.worker.stdout,selectors.EVENT_READ)
            if not selector.select(timeout=10):raise RuntimeError('worker response timeout')
            raw=self.worker.stdout.readline()
        result=json.loads(raw)
        if result['pid']!=self.worker.pid:raise RuntimeError('worker identity mismatch')
        self.events.append({'operation':text,'timestamp':utc(),'elapsed_seconds':time.monotonic()-t,'response':result})
        self.save();return result
    def stop(self):
        if self.worker is None:return
        p=self.worker
        try:
            receipt=self.request('stop')
            code=p.wait(timeout=10)
            self.events.append({'operation':'reap','timestamp':utc(),'pid':p.pid,'exit_code':code,'stop_receipt':receipt,'stderr':p.stderr.read()})
            if code!=0:raise RuntimeError('worker nonzero exit')
        finally:
            if p.poll() is None:
                p.terminate()
                try:p.wait(timeout=2)
                except subprocess.TimeoutExpired:p.kill();p.wait(timeout=2)
                self.events.append({'operation':'forced-cleanup','pid':p.pid,'exit_code':p.returncode,'timestamp':utc()})
            self.worker=None;self.save()
    def run(self):
        result={'status':'INCOMPLETE','paired_sequences':1}
        try:
            self.command('pip-version',['-m','pip','--version'])
            self.install('2.0.0')
            initial=json.loads(self.command('inspect-initial',['-m','pip','inspect'],'inspect-initial.json'))
            if installed(initial)['metadata']['version']!='2.0.0':raise RuntimeError('initial install mismatch')
            self.start_worker('old')
            baseline=self.request('probe')
            if baseline['version']!='2.0.0':raise RuntimeError('initial worker did not load old version')
            old_bug=json.loads(self.command('bug-2.0.0',['src/c1_urllib3_observability/bug_check.py'],'bug-2.0.0.json'))
            self.install('2.0.2')
            a_disk=json.loads(self.command('inspect-A',['-m','pip','inspect'],'inspect-A.json'))
            fresh=json.loads(self.command('fresh-import',['-c','import urllib3,sys,json; print(json.dumps({"version":urllib3.__version__,"file":urllib3.__file__,"interpreter":sys.executable}))'],'fresh-import.json'))
            if fresh['version']!='2.0.2':raise RuntimeError('fresh import mismatch')
            a=self.request('probe');(OUT/'state-A.json').write_text(json.dumps(a,indent=2)+'\n')
            if (a['pid'],a['start_identity'])!=(baseline['pid'],baseline['start_identity']):raise RuntimeError('old worker replaced')
            self.stop()
            self.start_worker('new')
            b=self.request('probe');(OUT/'state-B.json').write_text(json.dumps(b,indent=2)+'\n')
            b_disk=json.loads(self.command('inspect-B',['-m','pip','inspect'],'inspect-B.json'))
            new_bug=json.loads(self.command('bug-2.0.2',['src/c1_urllib3_observability/bug_check.py'],'bug-2.0.2.json'))
            result.update(verdict(a,b,a_disk,b_disk))
            result['status']='PASS' if result['PASS'] else 'FAIL'
            result['optional_bug_axis']={'old_complete':old_bug['complete'],'new_complete':new_bug['complete'],
                'same_reference':old_bug['expected_sha256']==new_bug['expected_sha256'],
                'status':'PASS issue-specific contrast' if not old_bug['complete'] and new_bug['complete'] and old_bug['expected_sha256']==new_bug['expected_sha256'] else 'INCONCLUSIVE'}
            result['initial_worker']=baseline
        except Exception as e:
            result.update(status='FAIL',error=type(e).__name__+': '+str(e));raise
        finally:
            self.stop();self.bounds()
            result.update(measurement_elapsed_seconds=time.monotonic()-self.start,scratch_bytes=self.size(self.scratch),
                          evidence_bytes_before_result=self.size(OUT),measurement_network='none; in-memory bug check',
                          active_workers_after_completion=0,worker_starts=sum(x['operation'].startswith('start-') for x in self.events),
                          source_metadata='Same premeasurement PyPI snapshot used for A/B; not re-requested between them')
            (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        if result['status']!='PASS':raise RuntimeError('observability contrast failed')
        print(json.dumps(result,indent=2))

if __name__=='__main__':Harness().run()
