"""Independent pipe client; does not import gateway or offline scorer."""
import datetime,hashlib,json,os,pathlib,subprocess,sys,time

def block_network(event,args):
    if event.startswith('socket.'):raise RuntimeError('network forbidden')
sys.addaudithook(block_network)
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/p2-egress-pilot-v01/attempt-01'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def run():
    # Exclusive guard forbids a second paired sequence or overwriting old evidence.
    with (OUT/'sequence-start.json').open('x') as f:json.dump({'started_utc':utc(),'max_responses':4},f)
    plan=json.loads((OUT/'frozen-plan.json').read_text());pre=json.loads((OUT/'preflight.json').read_text())
    scratch=pathlib.Path(pre['scratch'])
    requests={q:{'route':'R','query_id':q,'request_id':'R-'+q+'-at-fixed-epoch','question':text} for q,text in plan['queries'].items()}
    # No frozen expected result or offline truth label crosses into gateway config.
    cfg={k:plan[k] for k in ('source_path','source_sha256','source_blob','store_id','epoch')};cfg['requests']=requests
    cfg_path=scratch/'gateway-config.json';cfg_path.write_text(json.dumps(cfg))
    env={'PATH':'/usr/bin:/bin','HOME':str(scratch),'PYTHONDONTWRITEBYTECODE':'1','LC_ALL':'C.UTF-8'}
    events=[];responses=0;start=time.monotonic()
    try:
        for world in ('GOOD','STALE_EGRESS'):
            argv=['timeout','--signal=TERM','--kill-after=2s','60s','prlimit','--as=1073741824:1073741824','--',
                  sys.executable,'-B','src/p2_egress_pilot/gateway.py',str(cfg_path),world,str(OUT.relative_to(ROOT))]
            payload=b''.join((json.dumps(requests[q])+'\n').encode() for q in ('q1','q2'))
            (OUT/f'{world}-requests.bin').write_bytes(payload)
            stamp=utc();tick=time.monotonic()
            p=subprocess.Popen(argv,cwd=ROOT,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:stdout,stderr=p.communicate(payload,timeout=60)
            except subprocess.TimeoutExpired:
                p.terminate()
                try:stdout,stderr=p.communicate(timeout=2)
                except subprocess.TimeoutExpired:p.kill();stdout,stderr=p.communicate(timeout=2)
                raise
            (OUT/f'{world}-stdout.bin').write_bytes(stdout);(OUT/f'{world}-stderr.bin').write_bytes(stderr)
            events.append({'world':world,'command':argv,'started_utc':stamp,'ended_utc':utc(),'elapsed_seconds':time.monotonic()-tick,
                           'exit_code':p.returncode,'controller_child_pid':p.pid,'transport':'private subprocess stdin/stdout pipes',
                           'stdout_sha256':hashlib.sha256(stdout).hexdigest(),'received_bytes':len(stdout)})
            if p.returncode!=0:raise RuntimeError('gateway failed')
            lines=stdout.splitlines(keepends=True)
            if len(lines)!=2:raise RuntimeError('exactly two actual replies required')
            for q,raw in zip(('q1','q2'),lines):
                answer=json.loads(raw)
                if answer['route']!='R' or answer['query_id']!=q or answer['request_id']!=requests[q]['request_id']:
                    raise RuntimeError('client correlation mismatch')
                # Bytes are from the pipe, never read from gateway egress files.
                (OUT/f'{world}-{q}-client.bin').write_bytes(raw)
                receipt={'route':'R','world':world,'query_id':q,'request_id':answer['request_id'],'epoch':answer['epoch'],
                         'received_utc':utc(),'bytes_received':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                         'controller_child_pid':p.pid,'transport':'subprocess stdout pipe','decoded':answer}
                (OUT/f'{world}-{q}-client.json').write_text(json.dumps(receipt,indent=2)+'\n');responses+=1
    finally:
        (OUT/'sequence-ledger.json').write_text(json.dumps({'commands':events,'responses_received':responses,
           'paired_sequences':1,'elapsed_seconds':time.monotonic()-start,'network_requests':0,'dependency_installs':0,
           'route_authentication_scope':'Controller-owned subprocess pipe and query binding only; no independent attestation or cryptographic service identity.'},indent=2)+'\n')
    print(json.dumps({'responses_received':responses,'paired_sequences':1}))

if __name__=='__main__':run()
