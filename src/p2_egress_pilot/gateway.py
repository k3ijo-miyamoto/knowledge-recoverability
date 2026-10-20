"""Non-generative R gateway. No scorer, expected-world table, or model imports."""
import datetime,hashlib,json,os,pathlib,resource,signal,sys,time

def no_network(event,args):
    if event.startswith('socket.'):
        raise RuntimeError('network forbidden in pilot')
sys.addaudithook(no_network)

def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def run(config_path,world,out_path):
    signal.alarm(60)
    if world not in ('GOOD','STALE_EGRESS'):raise ValueError('unapproved world')
    cfg=json.loads(pathlib.Path(config_path).read_text());out=pathlib.Path(out_path)
    raw=pathlib.Path(cfg['source_path']).read_bytes();source=json.loads(raw)['info']
    if digest(raw)!=cfg['source_sha256'] or source['version']!='2.0.0' or type(source['yanked']) is not bool:
        raise ValueError('source identity mismatch')
    source_receipt={'source_id':cfg['source_sha256'],'git_blob':cfg['source_blob'],'snapshot_epoch':cfg['epoch'],
                    'origin':'https://pypi.org/pypi/urllib3/2.0.0/json','version':source['version'],'yanked':source['yanked'],
                    'scope':'issuer-declared snapshot fidelity only'}
    stored={'claim_id':'x','knowledge_version':'x+','value':source['yanked'],'store_id':cfg['store_id'],'source_id':cfg['source_sha256']}
    seen=[]
    with (out/(world+'-gateway.jsonl')).open('x') as ledger:
        for line in sys.stdin.buffer:
            t=time.perf_counter_ns();request=json.loads(line)
            q=request['query_id']
            if q not in ('q1','q2') or q in seen or request!=cfg['requests'][q]:raise ValueError('request outside fixed protocol')
            seen.append(q)
            common={'route':'R','claim_id':'x','epoch':cfg['epoch'],'source_id':cfg['source_sha256'],
                    'query_id':q,'request_id':request['request_id']}
            retrieved={**stored,**common}
            def answer(version,value):
                return {**common,'package_version':'2.0.0','knowledge_version':version,'yanked':value,
                        'answer':f'At snapshot {cfg["epoch"]}, PyPI reported urllib3 2.0.0 yanked={str(value).lower()}.'}
            generated=answer('x+',stored['value']);generated_bytes=encoded(generated)
            generated_receipt={**common,'knowledge_version':'x+','content':generated,'content_sha256':digest(generated_bytes),
                               'generator_span':{'kind':'stdlib_logical_span_NOT_OTEL','name':'deterministic_generate',
                                                 'span_id':digest((cfg['epoch']+q).encode())[:16],
                                                 'input_sha256':digest(encoded(retrieved)),
                                                 'output_sha256':digest(generated_bytes)}}
            # The only world-dependent operation: post-generation stale cache selection.
            override=(world=='STALE_EGRESS' and q=='q2')
            final=answer('x-',False) if override else generated
            wire=encoded(final)
            sent=0;parts=[]
            while sent<len(wire):
                n=os.write(sys.stdout.fileno(),wire[sent:])
                if n<=0:raise RuntimeError('failed pipe write')
                parts.append(wire[sent:sent+n]);sent+=n
            committed=utc();actual=b''.join(parts)
            (out/f'{world}-{q}-egress.bin').write_bytes(actual)
            receipt={'source':source_receipt,'store':stored,'retrieval':retrieved,'generated':generated_receipt,
                     'egress':{**common,'knowledge_version':final['knowledge_version'],'sha256':digest(actual),
                               'bytes_written':sent,'committed_utc':committed,'cache_override':override},
                     'runtime':{'world':world,'pid':os.getpid(),'elapsed_ns':time.perf_counter_ns()-t,
                                'rlimit_as':resource.getrlimit(resource.RLIMIT_AS)}}
            ledger.write(json.dumps(receipt,sort_keys=True)+'\n');ledger.flush()
    if seen!=['q1','q2']:raise ValueError('incomplete fixed query sequence')

if __name__=='__main__':run(*sys.argv[1:])
