import time,uuid
from .core import *

def main():
    rp,rpub=keypair(); ap,apub=keypair()
    root=LineageNode('HUMAN-1','HUMAN',pubkey(rpub),'0'*64); chain=Lineage(root)
    chain.append(LineageNode('AGENT-1','AGENT',pubkey(apub),chain.tip),rp)
    ledger=Ledger(); ledger.init('AGENT-1',Budget(5000,1000,1)); graph=EvidenceGraph(); gw=Gateway(rpub,graph,ledger)
    lease=Lease('AGENT-1','HUMAN-1',chain.tip,pubkey(apub),{'HTTP_GET'},{'api.trusted.local'},Budget(4000,500),time.time(),time.time()+60,str(uuid.uuid4()))
    gw.issue(lease,rp)
    print('Lineage verified:',chain.verify())
    print('Valid transaction:',gw.transact(lease,ap,'HTTP_GET','api.trusted.local','HTTP_GET','api.trusted.local','api.trusted.local'))
    attack=Lease(**{**vars(lease),'nonce':str(uuid.uuid4()),'signature':''}); gw.issue(attack,rp)
    print('Divergence attack:',gw.transact(attack,ap,'HTTP_GET','api.trusted.local','UNSANCTIONED_EXEC','/etc/shadow','evil.example'))
    print('Audit verified:',gw.audit.verify())
if __name__=='__main__': main()
