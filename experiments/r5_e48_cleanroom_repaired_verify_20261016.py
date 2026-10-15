#!/usr/bin/env python3
"""E4.8 import-free independent verifier for FROZEN repaired MULTI_Z SCL45.

Standard-library ONLY. Does not import JANUS research code or
reconstruct the source via the bridge generator.
Reads source row triples, voltage mask and witness bits from a
permanently versioned frozen declarative JSON file.

Independent algorithms:
- HIGH-pivot bit-GF2 RREF (producer uses LOW-pivot);
- full exact 2^d solution oracle for source and lifted system;
- Fraction-based exact rational RREF;
- all-63-kernel-directions residual exact-cover counting;
- brute-force up-to-two-edge removal BFS (producer uses Tarjan
  lowlink on single-edge deletions);
- direct integer Exact-One witness checks and sheet-XOR identities.
Any mismatch FAILS CI; finite enumeration is not polynomial in n
when d grows, and source existence alone is not P=NP.
"""
from collections import Counter,deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import argparse,hashlib,json


def check_scl(rows):
    n=len(rows)
    assert n%3==0
    deg=[0]*n
    pairs=set()
    for row in rows:
        assert len(row)==3 and len(set(row))==3
        assert all(0<=v<n for v in row)
        for v in row:deg[v]+=1
        for p in combinations(sorted(row),2):
            assert p not in pairs
            pairs.add(p)
    assert deg==[3]*n
    canon=tuple(sorted(tuple(sorted(row)) for row in rows))
    digest=hashlib.sha256(json.dumps(
        canon,separators=(",",":")).encode()).hexdigest()
    return digest


def kernel_high(bitrows,n):
    pivots={}
    for bitrow in bitrows:
        v=bitrow
        while v:
            j=v.bit_length()-1
            if j in pivots:v^=pivots[j]
            else:
                pivots[j]=v
                break
    free=[j for j in range(n) if j not in pivots]
    basis=[]
    for j in free:
        x=1<<j
        for p in sorted(pivots):
            if (x&pivots[p]).bit_count()&1:x|=1<<p
        assert all((x&row).bit_count()%2==0 for row in bitrows)
        basis.append(x)
    return n-len(basis),tuple(basis)


def exact_oracle(rows,limit=1<<15):
    n=len(rows)
    bits=tuple(sum(1<<v for v in row) for row in rows)
    rank,basis=kernel_high(bits,n)
    if len(basis)>15 or 1<<len(basis)>limit:
        raise RuntimeError("UNKNOWN_RESOURCE_LIMIT: finite oracle cap")
    full=(1<<n)-1
    witness=[]
    for pattern in range(1<<len(basis)):
        z=0
        for i,v in enumerate(basis):
            if (pattern>>i)&1:z^=v
        x=full^z
        assert all((x&row).bit_count()&1 for row in bits)
        if all(sum((x>>v)&1 for v in row)==1 for row in rows):
            witness.append(x)
    return {"rank":rank,"nullity":len(basis),
            "words_checked":1<<len(basis),
            "SAT_count":len(witness),
            "witnesses":witness,
            "kernel_basis":basis}


def rank_over_Q(rows):
    n=len(rows)
    M=[[Fraction(int(v in row)) for v in range(n)] for row in rows]
    rank=0
    for col in range(n):
        i=next((i for i in range(rank,n) if M[i][col]!=0),None)
        if i is None:continue
        M[rank],M[i]=M[i],M[rank]
        c=M[rank][col]
        M[rank]=[v/c for v in M[rank]]
        for i in range(rank+1,n):
            if M[i][col]:
                t=M[i][col]
                M[i]=[u-t*v for u,v in zip(M[i],M[rank])]
        rank+=1
    assert all(not any(v for v in row) for row in M[rank:])
    return rank


def components_without_edges(rows,removed):
    n=len(rows)
    adj=[[] for _ in range(2*n)]
    for i,row in enumerate(rows):
        for j in row:
            if (i,j) in removed:continue
            adj[i].append(n+j)
            adj[n+j].append(i)
    remaining=set(range(2*n))
    sizes=[]
    while remaining:
        start=next(iter(remaining));remaining.remove(start)
        q=[start];size=0
        while q:
            v=q.pop();size+=1
            for j in adj[v]:
                if j in remaining:
                    remaining.remove(j);q.append(j)
        sizes.append(size)
    return sizes


def exhaustive_no_two_edge_cut(rows):
    E=[(i,j) for i,row in enumerate(rows) for j in row]
    assert components_without_edges(rows,set())==[2*len(rows)]
    for i,e in enumerate(E):
        assert len(components_without_edges(rows,{e}))==1,("bridge",e)
        for f in E[i+1:]:
            if len(components_without_edges(rows,{e,f}))!=1:
                raise AssertionError(("two_edge_cut",e,f))
    return len(E)*(len(E)-1)//2


def residual_Y_count(rows,z):
    n=len(rows)
    S={j for j in range(n) if (z>>j)&1}
    R0=[i for i,row in enumerate(rows) if not any(j in S for j in row)]
    R2=[i for i,row in enumerate(rows) if sum(j in S for j in row)==2]
    assert len(R0)+len(R2)==n and 3*len(S)==2*len(R2)
    outside=[]
    for j in range(n):
        if j in S:continue
        incident={i for i,row in enumerate(rows) if j in row}
        if incident.issubset(set(R0)):outside.append((j,incident))
    options={i:[] for i in R0}
    for j,incident in outside:
        for i in incident:options[i].append((j,incident))
    chosen=[]
    found=[]
    def walk(remaining):
        if not remaining:
            p=n//3-len(S)//2
            assert len(chosen)==p
            y=[int(v in S)+2*int(v in chosen) for v in range(n)]
            assert all(sum(y[v] for v in row)==2 for row in rows)
            assert sum(1<<v for v,vv in enumerate(y) if vv%2)==z
            found.append(tuple(sorted(chosen)))
            return
        i=min(remaining)
        for j,incident in options[i]:
            if incident.issubset(remaining):
                chosen.append(j)
                walk(remaining-incident)
                chosen.pop()
    walk(set(R0))
    assert len(found)==len(set(found))
    return found


def reconstruct_cover(rows,sign):
    n=len(rows)
    edge_order=[(i,j) for i,row in enumerate(rows) for j in row]
    assert sign>>len(edge_order)==0
    volt={edge:(sign>>i)&1 for i,edge in enumerate(edge_order)}
    lift=[]
    for sheet in (0,1):
        for i,row in enumerate(rows):
            lift.append(tuple(j+n*(sheet^volt[(i,j)]) for j in row))
    check_scl(lift)
    return lift


def replay(path):
    D=json.loads(Path(path).read_text())
    assert D["version"]=="R5_E48_REPAIRED_SOURCE_V1"
    rows=[tuple(row) for row in D["base_45_rows"]]
    n=len(rows)
    assert n==45 and check_scl(rows)==D["base_canonical_sha256"]
    source=exact_oracle(rows)
    assert (source["rank"],source["nullity"],source["SAT_count"],
            source["words_checked"])==(39,6,0,64)
    qrank=rank_over_Q(rows)
    assert qrank==42 and n-qrank==3
    cut_pairs_checked=exhaustive_no_two_edge_cut(rows)
    assert cut_pairs_checked==9045
    relevant=[]
    bits=[sum(1<<v for v in row) for row in rows]
    for pattern in range(1,1<<source["nullity"]):
        z=0
        for j,v in enumerate(source["kernel_basis"]):
            if (pattern>>j)&1:z^=v
        assert all((z&r).bit_count()%2==0 for r in bits)
        covers=residual_Y_count(rows,z)
        if covers:relevant.append({"z":str(z),"Y_count":len(covers),
                                   "y2_columns":[list(c) for c in covers]})
    assert len(relevant)==D["expected"]["base_Yz_count"]==2
    assert {v["z"] for v in relevant}==set(D["distinct_z_decimal"])
    lift=reconstruct_cover(rows,int(D["sat_lift_voltage_bits_decimal"]))
    exact=exact_oracle(lift)
    assert (exact["rank"],exact["nullity"],exact["SAT_count"],
            exact["words_checked"])==(81,9,4,512)
    given=[int(s) for s in D["SAT_witness_bits_decimal"]]
    assert len(given)==2
    assert all(x in exact["witnesses"] for x in given)
    assert len(set(given))==2
    induced=Counter()
    for x in exact["witnesses"]:
        z=(x&((1<<n)-1))^(x>>n)
        induced[str(z)]+=1
    assert set(induced)==set(D["distinct_z_decimal"])
    assert sorted(induced.values())==[2,2]
    return {"gate":"E4_8_STANDALONE_CLEANROOM_REPAIRED_MULTI_Z",
            "standard_library_only":True,
            "source_hash":D["base_canonical_sha256"],
            "source_GF2_UNSAT_certificate":{
                "rank":source["rank"],"nullity":source["nullity"],
                "all_GF2_words":source["words_checked"],
                "solutions":source["SAT_count"]},
            "source_exact_Q_rank":qrank,
            "no_one_or_two_edge_cut_proof":{
                "all_edge_pairs_exhaustively_checked":cut_pairs_checked,
                "no_1_or_2_edge_cut":True},
            "all_source_nonzero_GF2_directions_checked":(1<<source["nullity"])-1,
            "exact_Z_A":relevant,
            "lift_GF2_complete_oracle":{
                "n":2*n,"rank":exact["rank"],"nullity":exact["nullity"],
                "all_parity_words":exact["words_checked"],
                "exact_SAT_solution_count":exact["SAT_count"]},
            "lift_exact_SAT_sheet_XOR_multiplicities":dict(induced),
            "joint_2lift_witnesses_checked":len(given),
            "balanced_separators":"NOT_ESTABLISHED",
            "expansion":"NOT_ESTABLISHED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    args=p.parse_args()
    print(json.dumps(replay(args.fixture),indent=2,sort_keys=True))
