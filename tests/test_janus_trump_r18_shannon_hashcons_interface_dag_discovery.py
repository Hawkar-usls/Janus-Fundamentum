import time

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18


def test_r18_tiny_existential_projection():
    assert r18.tiny_controls()


def test_r18_hashcons_and_boolean_reductions():
    b=r18.Budget(deadline=time.monotonic()+10); d=r18.Dag(b)
    x=d.lit(1); nx=d.lit(-1); y=d.lit(2)
    assert d.OR(x,nx)==1
    assert d.AND(x,nx)==0
    a=d.OR(x,y); bnode=d.OR(y,x)
    assert a==bnode


def test_r18_restrict_identity():
    budget=r18.Budget(deadline=time.monotonic()+10); d=r18.Dag(budget)
    root=d.AND(d.OR(d.lit(1),d.lit(2)),d.OR(d.lit(-1),d.lit(3)))
    r0,_=d.restrict(root,1,False); r1,_=d.restrict(root,1,True)
    ex=d.OR(r0,r1); d.gc(ex)
    allowed=[]
    for m in range(4):
        a={2:bool(m&1),3:bool(m&2)}
        if d.evaluate(ex,a): allowed.append(m)
    assert allowed==[1,2,3]


def test_r18_candidate_firewall():
    assert r18.candidate_firewall()['pass'] is True
