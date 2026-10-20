"""Single C1 stdin/stdout route; never makes a network request."""
import datetime, json, os, pathlib, resource, signal, sys, uuid
import urllib3
signal.alarm(120)
identity={'pid':os.getpid(),'start_identity':uuid.uuid4().hex,
          'start_ticks':pathlib.Path('/proc/self/stat').read_text().split()[21],
          'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'interpreter':sys.executable,'venv':sys.prefix,
          'rlimit_as':resource.getrlimit(resource.RLIMIT_AS)}
for line in sys.stdin:
    request=line.strip()
    if request=='stop':
        print(json.dumps({**identity,'receipt':'graceful_stop','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}),flush=True)
        break
    if request!='probe':raise ValueError('only probe or stop permitted')
    print(json.dumps({**identity,'receipt':'probe','version':urllib3.__version__,'module_file':urllib3.__file__,
                      'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}),flush=True)
