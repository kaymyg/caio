import time,uuid
from caio.core import *

def setup():
    rp,rpub=keypair(); ap,apub=keypair(); root=LineageNode('H','HUMAN',pubkey(rpub),'0'*64); chain=Lineage(root); chain.append(LineageNode('A','AGENT',pubkey(apub),chain.tip),rp)
    ledger=Ledger(); ledger.init('A',Budget(100,10,1)); graph=EvidenceGraph(); gw=Gateway(rpub,graph,ledger)
    lease=Lease('A','H',chain.tip,pubkey(apub),{'GET'},{'good'},Budget(50,5),time.time(),time.time()+60,str(uuid.uuid4())); gw.issue(lease,rp)
    return rp,rpub,ap,chain,ledger,graph,gw,lease

def test_lineage(): assert setup()[3].verify()
def test_replay():
    _,_,ap,_,_,_,gw,l=setup(); assert gw.transact(l,ap,'GET','good','GET','good','good')['status']==200; assert gw.transact(l,ap,'GET','good','GET','good','good')['status']==409
def test_conservation():
    x=Ledger(); x.init('p',Budget(10,10,1)); x.delegate('p','c',Budget(5,5,1)); assert vars(x.balances['p'])=={'compute':5,'network':5,'children':0}
    try:x.delegate('p','x',Budget(6,1,0)); assert False
    except PermissionError:pass
def test_termination():
    *_,graph,gw,l=setup(); graph.add(Evidence('1','A','CLAIM','GET','good')); graph.add(Evidence('2','A','HOST','UNSANCTIONED_EXEC','/etc/shadow')); graph.add(Evidence('3','A','NETWORK','CONNECT','evil')); assert graph.evaluate('A',l)==Level.TERMINATED
def test_audit(): assert setup()[6].audit.verify()

def test_expired_lease_rejected():
    rp,rpub,ap,chain,ledger,graph,gw,l=setup()
    l.expires_at=time.time()-1
    res=gw.transact(l,ap,'GET','good','GET','good','good')
    assert res['status']==401 and 'invalid/expired' in res['reason']

def test_tampered_signature_rejected():
    rp,rpub,ap,chain,ledger,graph,gw,l=setup()
    l.capabilities={'GET','ADMIN'}  # mutate payload after signing -- signature no longer matches
    res=gw.transact(l,ap,'GET','good','GET','good','good')
    assert res['status']==401 and 'invalid/expired' in res['reason']

def test_endpoint_outside_lease_rejected():
    # net_target must stay inside the lease so NETWORK_RESTRICTION doesn't
    # fire first and mask this check -- this isolates the dedicated
    # endpoint-outside-lease branch, which only triggers when the *claimed*
    # endpoint diverges from an otherwise-allowed network target.
    rp,rpub,ap,chain,ledger,graph,gw,l=setup()
    res=gw.transact(l,ap,'GET','not-in-lease','GET','good','good')
    assert res['status']==403 and 'endpoint' in res['reason']

def test_network_fuel_exhaustion():
    rp,rpub,ap,chain,ledger,graph,gw,l=setup()
    ledger.balances['A'].network=0  # drain the agent's remaining network budget
    res=gw.transact(l,ap,'GET','good','GET','good','good')
    assert res['status']==429 and 'fuel' in res['reason']

def test_transact_level_status_mapping():
    # Exercises the QUARANTINE and NETWORK_RESTRICTION branches through the
    # real gw.transact() call, not just EvidenceGraph.evaluate() directly --
    # the existing test_termination only covered the graph-level evaluation,
    # not the HTTP-style status code Gateway.transact() maps it to.
    rp,rpub,ap,chain,ledger,graph,gw,l=setup()
    quarantine=gw.transact(l,ap,'GET','good','UNSANCTIONED_EXEC','/etc/shadow','good')
    assert quarantine['status']==403 and quarantine['reason']=='quarantined'

    rp,rpub,ap,chain,ledger,graph,gw,l=setup()
    restricted=gw.transact(l,ap,'GET','good','GET','good','not-allowed')
    assert restricted['status']==403 and restricted['reason']=='network restricted'
