"""Offline source-relative scoring; imports neither gateway nor client."""
import hashlib,json,pathlib,sys
SOURCE_SHA='0f9e6a966ab8879f35f54e96164f71015e3a0f10cad7368946553c5f4e6a7dd4'

def score_answer(raw,snapshot):
    if hashlib.sha256(snapshot).hexdigest()!=SOURCE_SHA:raise ValueError('wrong frozen primary snapshot')
    source=json.loads(snapshot)['info'];a=json.loads(raw)
    if source['version']!='2.0.0' or source['yanked'] is not True:raise ValueError('wrong issuer claim')
    if a['claim_id']!='x' or a['package_version']!='2.0.0' or a['source_id']!=SOURCE_SHA:raise ValueError('source substitution')
    if type(a['yanked']) is not bool or a['knowledge_version'] not in ('x+','x-'):raise ValueError('bad answer schema')
    text=f'At snapshot {a["epoch"]}, PyPI reported urllib3 2.0.0 yanked={str(a["yanked"]).lower()}.'
    if a['answer']!=text:raise ValueError('structured claim/text disagreement')
    if (a['knowledge_version']=='x+')!=a['yanked']:raise ValueError('declared old/new content mismatch')
    return {'source_agrees':a['yanked']==source['yanked'],
            'old_served':int(a['knowledge_version']=='x-' and a['yanked'] is False),
            'claim_scope':'issuer-declared snapshot fidelity only','P4b':'NOT_ESTABLISHED','delta_zero':'NOT_TESTED'}

def assess(out,source_path):
    snapshot=pathlib.Path(source_path).read_bytes();out=pathlib.Path(out)
    scores={};records={};hash_checks=[]
    for world in ('GOOD','STALE_EGRESS'):
        records[world]=[json.loads(x) for x in (out/f'{world}-gateway.jsonl').read_text().splitlines()]
        if len(records[world])!=2:raise ValueError('missing gateway receipts')
        scores[world]={}
        for q,r in zip(('q1','q2'),records[world]):
            actual=(out/f'{world}-{q}-client.bin').read_bytes();sent=(out/f'{world}-{q}-egress.bin').read_bytes()
            cr=json.loads((out/f'{world}-{q}-client.json').read_text());a=json.loads(actual)
            for key in ('route','query_id','request_id','epoch'):
                if a[key]!=cr[key] or a[key]!=r['egress'][key]:raise ValueError('route/correlation mismatch')
            h=hashlib.sha256(actual).hexdigest()
            consistent=actual==sent and h==cr['sha256']==r['egress']['sha256'] and len(actual)==cr['bytes_received']==r['egress']['bytes_written']
            if not consistent:raise ValueError('client-egress byte mismatch')
            if a['knowledge_version']!=r['egress']['knowledge_version']:raise ValueError('egress version mismatch')
            hash_checks.append({'world':world,'query':q,'sha256':h,'bytes':len(actual),'matches':consistent})
            scores[world][q]=score_answer(actual,snapshot)
    pre_equal=all(records['GOOD'][i][key]==records['STALE_EGRESS'][i][key] for i in range(2)
                  for key in ('source','store','retrieval','generated'))
    same={q:(out/f'GOOD-{q}-client.bin').read_bytes()==(out/f'STALE_EGRESS-{q}-client.bin').read_bytes() for q in ('q1','q2')}
    old_counts={w:sum(s['old_served'] for s in qs.values()) for w,qs in scores.items()}
    decisions={w:{'q1_only_source_consistent':qs['q1']['source_agrees'],'all_D_source_consistent':all(x['source_agrees'] for x in qs.values())} for w,qs in scores.items()}
    passed=pre_equal and same['q1'] and not same['q2'] and old_counts=={'GOOD':0,'STALE_EGRESS':1}
    return {'verdict':'PASS' if passed else 'FAIL','pre_egress_equal':pre_equal,'q1_only_indistinguishable':same['q1'],
            'q1_plus_q2_distinguishes':not same['q2'],'source_scores':scores,'old_answer_counts':old_counts,
            'finite_domain_judgments':decisions,'egress_client_hash_checks':hash_checks,
            'meaning':'Finite-domain source fidelity; not general safety, semantic W1, P4b, novelty or delta=0.'}

if __name__=='__main__':
    output=pathlib.Path(sys.argv[1]);result=assess(output,sys.argv[2])
    with (output/'scores.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
    if result['verdict']!='PASS':sys.exit(1)
