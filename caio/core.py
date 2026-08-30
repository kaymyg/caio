import base64, hashlib, json, time, uuid
from dataclasses import dataclass, field
from enum import IntEnum
from threading import RLock
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), default=list).encode()

def keypair():
    p = ed25519.Ed25519PrivateKey.generate(); return p, p.public_key()

def pubkey(pub):
    return base64.b64encode(pub.public_bytes_raw()).decode()

def pubkey_load(s): return ed25519.Ed25519PublicKey.from_public_bytes(base64.b64decode(s))
def sign(k, data): return base64.b64encode(k.sign(data)).decode()
def verify(k, sig, data):
    try: k.verify(base64.b64decode(sig), data); return True
    except (InvalidSignature, ValueError): return False

def sha(x): return hashlib.sha256(x).hexdigest()

@dataclass(frozen=True)
class LineageNode:
    node_id: str; node_type: str; public_key: str; previous_hash: str; signature: str = ''
    def digest(self): return sha(canonical({'node_id':self.node_id,'node_type':self.node_type,'public_key':self.public_key,'previous_hash':self.previous_hash}))

class Lineage:
    def __init__(self, root): self.nodes=[root]
    def append(self,node,parent_private):
        if node.previous_hash != self.nodes[-1].digest(): raise ValueError('lineage link mismatch')
        n=LineageNode(node.node_id,node.node_type,node.public_key,node.previous_hash,sign(parent_private,node.digest().encode()))
        self.nodes.append(n); return n
    def verify(self):
        for a,b in zip(self.nodes,self.nodes[1:]):
            if b.previous_hash != a.digest() or not verify(pubkey_load(a.public_key),b.signature,b.digest().encode()): return False
        return True
    @property
    def tip(self): return self.nodes[-1].digest()

@dataclass
class Budget:
    compute:int; network:int; children:int=0
    def covers(self,b): return self.compute>=b.compute and self.network>=b.network and self.children>=b.children

@dataclass(frozen=True)
class LedgerEntry:
    sequence:int; parent:str; child:str; budget:Budget

class Ledger:
    def __init__(self): self.balances={}; self.entries=[]; self.seq=0; self.lock=RLock()
    def init(self,agent,budget):
        with self.lock:
            if agent in self.balances: raise ValueError('duplicate agent')
            self.balances[agent]=Budget(**vars(budget))
    def delegate(self,parent,child,budget):
        with self.lock:
            p=self.balances[parent]
            if not p.covers(budget): raise PermissionError('insufficient balance')
            p.compute-=budget.compute; p.network-=budget.network; p.children-=budget.children
            if child in self.balances: raise ValueError('duplicate child')
            self.balances[child]=Budget(**vars(budget)); self.seq+=1
            self.entries.append(LedgerEntry(self.seq,parent,child,budget))
    def consume(self,agent,compute=0,network=0):
        with self.lock:
            b=self.balances[agent]
            if b.compute<compute or b.network<network: raise PermissionError('fuel exhausted')
            b.compute-=compute; b.network-=network

@dataclass
class Lease:
    token_id:str; lineage_root:str; lineage_hash:str; agent_pubkey:str; capabilities:set; endpoints:set; budget:Budget; issued_at:float; expires_at:float; nonce:str; signature:str=''
    def payload(self): return {'token_id':self.token_id,'lineage_root':self.lineage_root,'lineage_hash':self.lineage_hash,'agent_pubkey':self.agent_pubkey,'capabilities':sorted(self.capabilities),'endpoints':sorted(self.endpoints),'budget':vars(self.budget),'issued_at':self.issued_at,'expires_at':self.expires_at,'nonce':self.nonce}

class Level(IntEnum): NORMAL=0; OBSERVATION=1; CAPABILITY_REDUCTION=2; NETWORK_RESTRICTION=3; QUARANTINE=4; TERMINATED=5
@dataclass(frozen=True)
class Evidence:
    id:str; agent:str; perspective:str; action:str; target:str; ts:float=field(default_factory=time.time)

class EvidenceGraph:
    def __init__(self): self.events={}; self.state={}
    def add(self,e): self.events.setdefault(e.agent,[]).append(e)
    def evaluate(self,agent,lease):
        ev=self.events.get(agent,[]); c=[e for e in ev if e.perspective=='CLAIM']; h=[e for e in ev if e.perspective=='HOST']; n=[e for e in ev if e.perspective=='NETWORK']; level=Level.NORMAL
        if c and h and (c[-1].action!=h[-1].action or c[-1].target!=h[-1].target): level=max(level,Level.CAPABILITY_REDUCTION)
        badhost=any(e.action in ('CRITICAL_TAMPER','UNSANCTIONED_EXEC') for e in h)
        badnet=any(e.target not in lease.endpoints for e in n)
        if badnet: level=max(level,Level.NETWORK_RESTRICTION)
        if badhost: level=max(level,Level.QUARANTINE)
        if badhost and badnet: level=Level.TERMINATED
        self.state[agent]=level; return level

class Audit:
    def __init__(self): self.rows=[]; self.tip='0'*64
    def add(self,event,data):
        r={'i':len(self.rows)+1,'ts':time.time(),'event':event,'data':data,'prev':self.tip}
        r['hash']=sha(canonical(r)); self.tip=r['hash']; self.rows.append(r)
    def verify(self):
        prev='0'*64
        for r in self.rows:
            if r['prev']!=prev: return False
            q=dict(r); h=q.pop('hash')
            if sha(canonical(q))!=h: return False
            prev=h
        return True

class Gateway:
    def __init__(self,issuer_public,graph,ledger): self.issuer=issuer_public; self.graph=graph; self.ledger=ledger; self.audit=Audit(); self.used=set()
    def issue(self,lease,issuer_private): lease.signature=sign(issuer_private,canonical(lease.payload())); self.audit.add('LEASE_ISSUED',{'token':lease.token_id}); return lease
    def valid(self,l): return verify(self.issuer,l.signature,canonical(l.payload())) and time.time()<l.expires_at
    def transact(self,l,agent_private,action,endpoint,host_action,host_target,net_target):
        if not self.valid(l): return {'status':401,'reason':'invalid/expired lease'}
        if l.nonce in self.used: return {'status':409,'reason':'replay detected'}
        if not verify(pubkey_load(l.agent_pubkey),sign(agent_private,(c:=uuid.uuid4().bytes)),c): return {'status':401,'reason':'agent binding failed'}
        self.used.add(l.nonce); a=l.token_id
        self.graph.add(Evidence(str(uuid.uuid4()),a,'CLAIM',action,endpoint)); self.graph.add(Evidence(str(uuid.uuid4()),a,'HOST',host_action,host_target)); self.graph.add(Evidence(str(uuid.uuid4()),a,'NETWORK','CONNECT',net_target))
        level=self.graph.evaluate(a,l); self.audit.add('EVALUATED',{'agent':a,'level':int(level)})
        if level>=Level.TERMINATED:return {'status':500,'reason':'terminated'}
        if level>=Level.QUARANTINE:return {'status':403,'reason':'quarantined'}
        if level>=Level.NETWORK_RESTRICTION:return {'status':403,'reason':'network restricted'}
        if endpoint not in l.endpoints:return {'status':403,'reason':'endpoint outside lease'}
        try:self.ledger.consume(a,network=1)
        except PermissionError:return {'status':429,'reason':'network fuel exhausted'}
        return {'status':200,'level':level.name,'route':'VERIFIED_OVERLAY'}
