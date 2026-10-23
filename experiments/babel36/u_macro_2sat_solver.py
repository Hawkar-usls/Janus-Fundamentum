#!/usr/bin/env python3
"""BABEL36: exact polynomial 2-SAT compiler for certified U=SCL27 macro joins.

Input to solver = raw original SCL row incidences plus a supplied fixed-U
block partition / row alignment. It RECONSTRUCTS all port occurrences,
macro adjacencies and imported-bit reciprocity from those rows. No pre-known
SAT assignment, macro outcome, source port choices or constructor receipts.
The exhaustive U port relation is verified in the separate census script.
"""
import hashlib
import itertools
import json
import random
from collections import Counter,deque
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from experiments.babel34.local_three_port_forcing import ROWS,SHA,exact_one,gf2_rank
from experiments.babel36.u_three_port_census import get_relation,TRIPLE_RELATION

PORT_SINGLE0=((0,0),(1,6),(2,5))
PORT_SINGLE1=((0,2),(1,0),(2,5))
PORT_DOUBLE=((0,2),(8,10),(16,4))
PORT_TRIPLE=((0,1),(8,10),(16,4))


def prism(t,seed):
    assert t>=8 and t%2==0
    m=t//2
    edges=set()
    for off in (0,m):
        for i in range(m):
            edges.add(tuple(sorted((off+i,off+(i+1)%m))))
    for i in range(m):edges.add((i,m+i))
    adj={i:set() for i in range(t)}
    for a,b in edges:adj[a].add(b);adj[b].add(a)
    assert all(len(adj[i])==3 for i in range(t))
    rng=random.Random(seed)
    at={}
    for b in range(t):
        neighbors=sorted(adj[b])
        rng.shuffle(neighbors)
        at[b]={nb:k for k,nb in enumerate(neighbors)}
    return tuple(sorted(edges)),adj,at


def compile_physical_fixture(ports_by_block,seed=1234):
    """Independent fixture producer; receives arbitrary U port triples."""
    t=len(ports_by_block)
    edges,adj,slot=prism(t,seed)
    rows=[list(27*b+v for v in row)
          for b in range(t) for row in ROWS]
    for b,c in edges:
        ri,va=ports_by_block[b][slot[b][c]]
        rj,vb=ports_by_block[c][slot[c][b]]
        row_b=27*b+ri;row_c=27*c+rj
        var_b=27*b+va;var_c=27*c+vb
        assert var_b in rows[row_b] and var_c in rows[row_c]
        rows[row_b][rows[row_b].index(var_b)]=var_c
        rows[row_c][rows[row_c].index(var_c)]=var_b
    return tuple(tuple(sorted(row)) for row in rows)


def verify_extract_template(raw):
    """Check every original SCL incidence and discover all macro port pairs."""
    n=len(raw);assert n%27==0
    t=n//27
    assert all(len(row)==3 and len(set(row))==3 for row in raw)
    assert Counter(v for row in raw for v in row)==Counter({i:3 for i in range(n)})
    pairs=[tuple(sorted(p)) for row in raw for p in itertools.combinations(row,2)]
    assert len(set(pairs))==3*n
    ports={}
    for b in range(t):
        events=[]
        for ri,original in enumerate(ROWS):
            actual=set(raw[27*b+ri])
            expected={27*b+v for v in original}
            inside={v for v in actual if v//27==b}
            lost=expected-inside
            foreign=actual-inside
            if not lost and not foreign:
                assert actual==expected
                continue
            assert len(lost)==len(foreign)==1
            assert expected&inside==inside
            missing=next(iter(lost))%27
            arriving=next(iter(foreign))
            assert arriving//27!=b
            events.append((ri,missing,arriving//27,arriving))
        assert len(events)==3
        assert len({e[0] for e in events})==3
        assert len({e[1] for e in events})==3
        assert len({e[2] for e in events})==3 # simple cubic macro
        ports[b]=tuple(sorted(events))
    links=[]
    neighbors={b:set() for b in range(t)}
    for b in range(t):
        for k,(row,missing,c,foreign) in enumerate(ports[b]):
            reciprocal=[(l,e) for l,e in enumerate(ports[c])
                        if e[1]==foreign%27 and e[2]==b
                        and e[3]==27*b+missing]
            assert len(reciprocal)==1
            l,_=reciprocal[0]
            if b<c:links.append((b,k,c,l))
            neighbors[b].add(c)
    assert len(links)==3*t//2
    assert all(len(v)==3 for v in neighbors.values())
    assert all(b in neighbors[c] for b in neighbors for c in neighbors[b])
    seen={0};queue=[0]
    while queue:
        for j in neighbors[queue.pop()]-seen:
            seen.add(j);queue.append(j)
    assert len(seen)==t
    return ports,tuple(sorted(links))


def const(val):
    return ("c",int(val),0)


def literal(v,positive=True):
    return ("l",int(v),int(bool(positive)))


def neg(lit):
    assert lit[0]=="l"
    return ("l",lit[1],1-lit[2])


def signature_expr(a0,a1,selector):
    if a0==a1:return const(a0)
    return literal(selector,positive=(a0==0 and a1==1))


class Exact2SAT:
    def __init__(self):
        self.n=0;self.imp=[];self.rev=[]
        self.clauses=[]
        self.const_contradictions=0

    def fresh(self):
        v=self.n;self.n+=1
        self.imp.extend(([],[]))
        self.rev.extend(([],[]))
        return v

    def index(self,lit):
        assert lit[0]=="l"
        return 2*lit[1]+(0 if lit[2] else 1)

    def clause(self,a,b):
        assert a[0]==b[0]=="l"
        ia=self.index(a);ib=self.index(b)
        for u,v in ((ia^1,ib),(ib^1,ia)):
            self.imp[u].append(v)
            self.rev[v].append(u)
        self.clauses.append((a,b))

    def force(self,a,value):
        self.clause(a if value else neg(a),a if value else neg(a))

    def equal(self,a,b):
        if a[0]=="c" and b[0]=="c":
            if a[1]!=b[1]:self.const_contradictions+=1
        elif a[0]=="c":
            self.force(b,a[1])
        elif b[0]=="c":
            self.force(a,b[1])
        else:
            self.clause(neg(a),b)
            self.clause(a,neg(b))

    def solve(self):
        if self.const_contradictions:
            return None,{"type":"INCOMPATIBLE_EXACT_PORT_CONSTANTS",
                         "contradiction_count":self.const_contradictions}
        visited=set();finish=[]
        def visit(start):
            stack=[(start,False)]
            while stack:
                v,post=stack.pop()
                if post:
                    finish.append(v);continue
                if v in visited:continue
                visited.add(v)
                stack.append((v,True))
                for w in self.imp[v]:
                    if w not in visited:stack.append((w,False))
        for v in range(2*self.n):
            if v not in visited:visit(v)
        component=[-1]*(2*self.n);cid=0
        for v in reversed(finish):
            if component[v]>=0:continue
            stack=[v];component[v]=cid
            while stack:
                for w in self.rev[stack.pop()]:
                    if component[w]<0:
                        component[w]=cid;stack.append(w)
            cid+=1
        for i in range(self.n):
            if component[2*i]==component[2*i+1]:
                return None,{"type":"SCC_VARIABLE_AND_NEGATION",
                             "var":i,"component":component[2*i]}
        truth=[int(component[2*i]>component[2*i+1]) for i in range(self.n)]
        assert all(self.eval(a,truth) or self.eval(b,truth)
                   for a,b in self.clauses)
        return truth,{"type":"SAT_2CNF_ASSIGNMENT",
                      "selectors":self.n,"clauses":len(self.clauses)}

    @staticmethod
    def eval(expr,assignment):
        if expr[0]=="c":return expr[1]
        return assignment[expr[1]] if expr[2] else 1-assignment[expr[1]]


def solve_admitted(raw):
    """One exact SAT / UNSAT answer for independently verified fixed-U macro."""
    ports,links=verify_extract_template(raw)
    t=len(ports)
    system=Exact2SAT()
    block_data={}
    for b in range(t):
        port_choices=tuple((ri,var) for ri,var,other,incoming in ports[b])
        relation=get_relation(port_choices)
        assert 1<=len(relation)<=3
        if len(relation)==1:
            a,d,x=relation[0]
            outgoing=tuple(const(v) for v in a)
            incoming=tuple(const(v) for v in d)
            state=("single",x)
        elif len(relation)==2:
            sel=system.fresh()
            (a0,d0,x0),(a1,d1,x1)=relation
            outgoing=tuple(signature_expr(a0[k],a1[k],sel) for k in range(3))
            incoming=tuple(signature_expr(d0[k],d1[k],sel) for k in range(3))
            state=("double",sel,(x0,x1))
        else:
            assert tuple(sorted((a,d) for a,d,x in relation))==TRIPLE_RELATION
            a=system.fresh();d=system.fresh()
            system.clause(neg(literal(a)),neg(literal(d)))
            outgoing=tuple(literal(a) for k in range(3))
            incoming=tuple(literal(d) for k in range(3))
            table={(export[0],demand[0]):x for export,demand,x in relation}
            assert set(table)=={(0,0),(0,1),(1,0)}
            state=("triple",a,d,table)
        block_data[b]=(outgoing,incoming,state)
    for b,k,c,l in links:
        out_b,in_b,_=block_data[b]
        out_c,in_c,_=block_data[c]
        system.equal(out_b[k],in_c[l])
        system.equal(out_c[l],in_b[k])
    solution,proof=system.solve()
    if solution is None:
        return {"status":"UNSAT","exact_count":None,
                "n_original_variables":len(raw),
                "template_blocks":t,
                "selectors":system.n,
                "CNF_clauses":len(system.clauses),
                "proof_receipt":proof}
    mask=0
    for b in range(t):
        outgoing,incoming,state=block_data[b]
        if state[0]=="single":
            local=state[1]
        elif state[0]=="double":
            local=state[2][solution[state[1]]]
        else:
            local=state[3][(solution[state[1]],solution[state[2]])]
        for k,(ri,var,neighbor,foreign) in enumerate(ports[b]):
            assert (local>>var&1)==system.eval(outgoing[k],solution)
            assert all(1-sum(local>>j&1 for j in ROWS[ri] if j!=var)==
                       system.eval(incoming[k],solution) for _ in (0,))
        mask|=local<<(27*b)
    assert exact_one(raw,mask)
    return {"status":"SAT","exact_count":None,"n_original_variables":len(raw),
            "template_blocks":t,"selectors":system.n,
            "CNF_clauses":len(system.clauses),
            "physical_SAT_model":mask,
            "SAT_ones":mask.bit_count(),
            "proof_receipt":proof}


def independently_brute_macro(raw):
    """Complete local physical state-product enumeration on small t only."""
    ports,links=verify_extract_template(raw)
    t=len(ports);assert t<=10
    all_tables=[]
    for b in range(t):
        ps=tuple((r,v) for r,v,c,f in ports[b])
        all_tables.append(get_relation(ps))
    count=0
    models=set()
    for combination in itertools.product(*all_tables):
        if all(combination[b][0][k]==combination[c][1][l] and
               combination[c][0][l]==combination[b][1][k]
               for b,k,c,l in links):
            x=sum(combination[b][2]<<(27*b) for b in range(t))
            assert exact_one(raw,x)
            count+=1
            models.add(x)
    assert count==len(models)
    return count


def testcase(name, choices,seed,expected=None,brute=True):
    raw=compile_physical_fixture(choices,seed)
    result=solve_admitted(raw)
    count=independently_brute_macro(raw) if brute else None
    if expected is not None:
        assert (result["status"]=="SAT")==bool(expected),(name,result,expected)
        if brute:assert count==expected,(name,count,expected)
    if brute:
        assert (count>0)==(result["status"]=="SAT"),(name,count,result)
        if count==0:assert result["status"]=="UNSAT"
    if result["status"]=="SAT":
        assert exact_one(raw,result["physical_SAT_model"])
    else:
        assert result["proof_receipt"]["type"] in (
            "INCOMPATIBLE_EXACT_PORT_CONSTANTS",
            "SCC_VARIABLE_AND_NEGATION")
    return {"fixture":name,"n":len(raw),
            "result":result["status"],
            "template_blocks":len(choices),
            "local_state_sizes":[len(get_relation(p)) for p in choices],
            "selectors":result["selectors"],
            "CNF_clauses":result["CNF_clauses"],
            "independent_macro_count_if_small":count,
            "physically_verified_SAT":result["status"]=="SAT",
            "UNSAT_proof_type":result["proof_receipt"]["type"]
                if result["status"]=="UNSAT" else None}


def main():
    assert hashlib.sha256(json.dumps(ROWS,separators=(",",":")).encode()).hexdigest()==SHA
    assert len(get_relation(PORT_SINGLE0))==1
    assert len(get_relation(PORT_SINGLE1))==1
    assert len(get_relation(PORT_DOUBLE))==2
    assert len(get_relation(PORT_TRIPLE))==3
    tests=[
      testcase("SINGLE_000_EVERYWHERE_SAT", [PORT_SINGLE0]*8,361,1),
      testcase("INCOMPATIBLE_SINGLE_NONZERO_UNSAT",
               [PORT_SINGLE1]+[PORT_SINGLE0]*7,362,0),
      testcase("ALL_TRIPLE_BIPARTITE_PRISM_SAT3",[PORT_TRIPLE]*8,363,3),
      testcase("ALL_TRIPLE_NONBIP_PRISM_SAT1",[PORT_TRIPLE]*10,364,1),
      testcase("MIXED_SINGLE_DOUBLE_TRIPLE_T8",
               [PORT_TRIPLE,PORT_DOUBLE,PORT_SINGLE0,PORT_TRIPLE,
                PORT_SINGLE1,PORT_DOUBLE,PORT_SINGLE0,PORT_TRIPLE],365),
      testcase("ALL_DOUBLE_T8",[PORT_DOUBLE]*8,366),
      testcase("MIXED_HIGH_WIDTH_T40",
               [PORT_TRIPLE if i%3==0 else PORT_SINGLE0 if i%3==1
                else PORT_DOUBLE for i in range(40)],367,brute=False),
      testcase("LARGE_TRIPLE_T40",[PORT_TRIPLE]*40,368,brute=False)
    ]
    assert any(t["result"]=="SAT" for t in tests)
    assert any(t["result"]=="UNSAT" for t in tests)
    assert any(2 in t["local_state_sizes"] and 3 in t["local_state_sizes"]
               for t in tests)
    print(json.dumps({
       "gate":"BABEL36_CERTIFIED_U_MACRO_POLYNOMIAL_2SAT_COMPILER",
       "all_n_semantic_2CNF_equivalence":"PROVED",
       "complete_SAT_UNSAT_decision_on_admitted_template":"EXACT_PASS",
       "2SAT_selector_variables_at_most":"2T",
       "witness_replayed_on_original_SCL_rows":"PASS",
       "brute_small_macro_independent_Cartesian_states":"PASS",
       "universal_unlabeled_SCL_template_discovery":"OPEN",
       "general_polynomial_SCL_solver":"NOT_PROVED",
       "P_vs_NP":"OPEN",
       "cases":tests
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
