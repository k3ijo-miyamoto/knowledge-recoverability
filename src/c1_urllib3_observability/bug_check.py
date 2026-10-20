"""Locally authored bounded #3009-style completeness check, not upstream proof.

The source closes when the compressed byte stream is exhausted, as a finite
HTTP body can. Expected uncompressed bytes/digest use stdlib only. No sockets.
"""
import gzip, hashlib, io, json, resource
import urllib3
from urllib3.response import HTTPResponse
reference=(b'C1 independent streaming reference: 0123456789abcdef\n'*6000)[:262144]
compressed=gzip.compress(reference,mtime=0)
assert len(reference)<=300*1024 and len(compressed)<=1048576
class ClosingSource(io.BytesIO):
    def read(self,n=-1):
        data=super().read(n)
        if self.tell()==len(compressed):self.close()
        return data
response=HTTPResponse(body=ClosingSource(compressed),headers={'content-encoding':'gzip','content-length':str(len(compressed))},preload_content=False)
chunks=list(response.stream(amt=1024,decode_content=True))
actual=b''.join(chunks)
print(json.dumps({'version':urllib3.__version__,'path':'HTTPResponse.stream(amt=1024, decode_content=True); finite closing in-memory gzip source',
                  'expected_bytes':len(reference),'produced_bytes':len(actual),'compressed_bytes':len(compressed),'chunks':len(chunks),
                  'expected_sha256':hashlib.sha256(reference).hexdigest(),'produced_sha256':hashlib.sha256(actual).hexdigest(),
                  'complete':actual==reference,'rlimit_as':resource.getrlimit(resource.RLIMIT_AS),
                  'scope':'one locally authored input, not copied upstream regression, no network or correctness proof'}))
