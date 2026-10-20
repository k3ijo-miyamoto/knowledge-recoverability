"""Preparation only: two exact public releases, no dependency resolution."""
import datetime, hashlib, json, os, pathlib, resource, subprocess, sys, time
import urllib.request
from urllib.parse import urlparse

root = pathlib.Path(__file__).resolve().parents[2]
out = root/'artifacts/urllib3-c1-observability-v01/attempt-01'
scratch = pathlib.Path((out/'scratch-path.txt').read_text().strip())
python = str(scratch/'venv/bin/python')
wheels = scratch/'wheels'; wheels.mkdir()
env = {'PATH':'/usr/bin:/bin','HOME':str(scratch),'TMPDIR':str(scratch),
       'PIP_CONFIG_FILE':'/dev/null','PIP_NO_INPUT':'1','PIP_DISABLE_PIP_VERSION_CHECK':'1',
       'PYTHONDONTWRITEBYTECODE':'1','LC_ALL':'C.UTF-8'}
ledger=[]; total=0
try:
    for version in ('2.0.0','2.0.2'):
        url=f'https://pypi.org/pypi/urllib3/{version}/json'
        started=datetime.datetime.now(datetime.timezone.utc).isoformat(); tick=time.monotonic()
        # No proxy/private config and no unbounded JSON body; default TLS verification.
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url,timeout=20) as response:
            raw=response.read(1048577)
            if len(raw)>1048576: raise RuntimeError('metadata size cap')
            if response.url!=url: raise RuntimeError('unexpected metadata redirect')
        total+=len(raw)
        (out/f'pypi-{version}.json').write_bytes(raw)
        meta=json.loads(raw)
        candidates=[x for x in meta['urls'] if x['filename']==f'urllib3-{version}-py3-none-any.whl' and x['packagetype']=='bdist_wheel']
        if len(candidates)!=1: raise RuntimeError('pinned public wheel not unique')
        wheel=candidates[0]; parsed=urlparse(wheel['url'])
        if parsed.scheme!='https' or parsed.hostname!='files.pythonhosted.org' or parsed.username or parsed.password:
            raise RuntimeError('unapproved wheel origin')
        if wheel['size']>=1048576 or total+wheel['size']>10*1048576: raise RuntimeError('download budget')
        argv=['timeout','--signal=TERM','--kill-after=2s','120s','prlimit','--as=1073741824:1073741824',
              '--fsize=1048576:1048576','--',python,'-B','-m','pip','--no-cache-dir','download',
              '--no-deps','--only-binary=:all:','--retries','0','--timeout','20',
              '--index-url','https://pypi.org/simple','--dest',str(wheels),
              wheel['url']+'#sha256='+wheel['digests']['sha256']]
        p=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=120)
        (out/f'download-{version}.log').write_text(p.stdout+p.stderr)
        entry={'version':version,'metadata_url':url,'metadata_bytes':len(raw),'metadata_sha256':hashlib.sha256(raw).hexdigest(),
               'started_utc':started,'elapsed_seconds':time.monotonic()-tick,'command':argv,'exit_code':p.returncode,
               'wheel_url':wheel['url'],'published_size':wheel['size'],'published_sha256':wheel['digests']['sha256'],
               'yanked':wheel['yanked'],'yanked_reason':wheel['yanked_reason']}
        ledger.append(entry)
        if p.returncode: raise RuntimeError('wheel download command failed')
        b=(wheels/wheel['filename']).read_bytes(); total+=len(b)
        entry.update(actual_bytes=len(b),actual_sha256=hashlib.sha256(b).hexdigest())
        if len(b)!=wheel['size'] or entry['actual_sha256']!=wheel['digests']['sha256']:
            raise RuntimeError('wheel provenance mismatch')
        if total>10*1048576: raise RuntimeError('download cap exceeded')
finally:
    (out/'download-ledger.json').write_text(json.dumps({'commands':ledger,'downloaded_payload_bytes':total,
       'cap_bytes':10485760,'scope':'2 version JSON responses and 2 wheel payloads; HTTP/TLS overhead not measured',
       'bounds':'Each metadata response <=1 MiB; wheel sizes prechecked <1 MiB, pip file limit 1 MiB, no pip retries/dependencies/self-update.'},indent=2)+'\n')
print(json.dumps({'status':'verified','downloaded_payload_bytes':total,'wheel_count':len(list(wheels.glob('*.whl')))}))
