"""Reference adapter for S1 mock, uses v0.4 operation request/response schema."""
import hashlib,json,copy
from mock import MockSUT

def raw_encode(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

class S1Adapter:
    def __init__(self,sut:MockSUT):
        self.sut=sut
        self.observations={}
    def operation(self, req):
        op=req['operation'];arg=req['arguments'];pid=arg['project_id'];cid=req['correlation_id']
        if op!='load_config':raise ValueError('S1 only supports load_config')
        status,body=self.sut.load(pid,arg['config'])
        raw=raw_encode(body);digest=hashlib.sha256(raw).hexdigest()
        ref='evidence://s1/'+cid
        self.observations[ref]=raw
        accepted=status in (200,201,202)
        return {'contract_version':'0.4','operation':op,'correlation_id':cid,'success':True,
                'data':{'sut':{'outcome':'accepted' if accepted else 'rejected','status':status,
                               'body_ref':ref,'body_sha256':digest,'surface':'equivalent'}},
                'evidence_refs':[ref]}
    def read_body(self,response):
        x=response['data']['sut'];raw=self.observations[x['body_ref']]
        if hashlib.sha256(raw).hexdigest()!=x['body_sha256']:raise ValueError('evidence corruption')
        return json.loads(raw)
