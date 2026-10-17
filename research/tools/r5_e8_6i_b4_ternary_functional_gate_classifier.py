#!/usr/bin/env python3
"""Exhaustive classification of all ternary Boolean functional gates under B4.

For every Boolean function h:{0,1}^3->{0,1}, test all mixed B4 tuples
(f1,f2,f3,g) for preservation of graph(h).

The exact finite result:
- 18 essentially-ternary h have any compatible tuple;
- each has exactly one compatible tuple;
- they are precisely signed 3-literal conjunction/minterm functions,
  signed 3-literal disjunction/maxterm functions, XOR3 and XNOR3;
- the other 200 ternary truth tables with no compatible tuple plus lower
  essential-arity cases account for all 256 functions.

This is a fixed finite classification, not a general lower bound on arbitrary
relations or arbitrary lifted domains.
"""
from __future__ import annotations
import itertools, json

D=(0,1)
LABELS=("AND3","OR3","MAJ3","XOR3")
VECTORS=tuple(itertools.product(D,repeat=3))
VIDX={v:i for i,v in enumerate(VECTORS)}


def op(label,a,b,c):
    if label=="AND3": return a & b & c
    if label=="OR3": return a | b | c
    if label=="MAJ3": return int(a+b+c>=2)
    if label=="XOR3": return a ^ b ^ c
    raise KeyError(label)


OPTAB={l:{v:op(l,*v) for v in VECTORS} for l in LABELS}


def depends_on(tt,i):
    for v in VECTORS:
        w=list(v);w[i]^=1;w=tuple(w)
        if tt[VIDX[v]]!=tt[VIDX[w]]:
            return True
    return False


def compatible(tt,labels):
    f1,f2,f3,g=labels
    for a,b,c in itertools.product(VECTORS,repeat=3):
        lhs=OPTAB[g][(tt[VIDX[a]],tt[VIDX[b]],tt[VIDX[c]])]
        merged=(
            OPTAB[f1][(a[0],b[0],c[0])],
            OPTAB[f2][(a[1],b[1],c[1])],
            OPTAB[f3][(a[2],b[2],c[2])],
        )
        rhs=tt[VIDX[merged]]
        if lhs!=rhs:
            return False
    return True


def truth_string(tt):
    return "".join(map(str,tt))


def signed_minterm_or_maxterm(tt):
    ones=sum(tt)
    if ones==1: return "SIGNED_CONJUNCTION_MINTERM"
    if ones==7: return "SIGNED_DISJUNCTION_MAXTERM"
    xor=tuple(v[0]^v[1]^v[2] for v in VECTORS)
    if tt==xor: return "XOR3"
    if tt==tuple(1-x for x in xor): return "XNOR3"
    return None


def build_receipt():
    label_tuples=tuple(itertools.product(LABELS,repeat=4))
    hist={}
    by_ess={}
    essential3=[]
    no_compatible=0

    for tt in itertools.product(D,repeat=8):
        allowed=[x for x in label_tuples if compatible(tt,x)]
        n=len(allowed)
        hist[str(n)]=hist.get(str(n),0)+1
        ess=sum(depends_on(tt,i) for i in range(3))
        by_ess.setdefault(str(ess),{})
        by_ess[str(ess)][str(n)]=by_ess[str(ess)].get(str(n),0)+1
        if n==0:
            no_compatible+=1
        if ess==3 and allowed:
            cls=signed_minterm_or_maxterm(tt)
            assert cls is not None
            assert len(allowed)==1
            essential3.append({
                "truth_table_000_to_111":truth_string(tt),
                "class":cls,
                "compatible_label_tuple":list(allowed[0]),
            })

    assert len(essential3)==18
    assert sum(1 for x in essential3 if x["class"]=="SIGNED_CONJUNCTION_MINTERM")==8
    assert sum(1 for x in essential3 if x["class"]=="SIGNED_DISJUNCTION_MAXTERM")==8
    assert sum(1 for x in essential3 if x["class"]=="XOR3")==1
    assert sum(1 for x in essential3 if x["class"]=="XNOR3")==1
    assert no_compatible==200
    assert hist=={"256":2,"64":6,"4":30,"1":18,"0":200}

    return {
      "schema":"janus.r5_e8_6i.b4_ternary_functional_gate_classification.v1",
      "status":"PASS_EXHAUSTIVE_ALL_256_TERNARY_BOOLEAN_FUNCTIONS",
      "library":list(LABELS),
      "truth_tables_checked":256,
      "mixed_label_tuples_checked_per_function":256,
      "input_triples_checked_per_candidate":512,
      "compatible_tuple_count_histogram":hist,
      "essential_arity_by_compatible_count":by_ess,
      "functions_with_no_B4_compatible_graph":no_compatible,
      "essential_arity_3_compatible_count":len(essential3),
      "essential_arity_3_classes":{
        "SIGNED_CONJUNCTION_MINTERM":8,
        "SIGNED_DISJUNCTION_MAXTERM":8,
        "XOR3":1,
        "XNOR3":1,
      },
      "essential_arity_3_catalog":essential3,
      "theorem_candidate":"EVERY_ESSENTIALLY_TERNARY_BOOLEAN_FUNCTION_WITH_B4_COMPATIBLE_GRAPH_IS_A_SIGNED_MINTERM_MAXTERM_OR_PARITY_FUNCTION; EACH_HAS_ONE_COMPATIBLE_B4_TYPE_PATTERN",
      "consequence":{
        "ARITY_LE_3_BOOLEAN_FUNCTIONAL_AUXILIARIES_CREATE_NEW_B4_ALGEBRA_TYPE_ROUTER":False,
        "MAJ3_APPEARS_AS_ACTIVE_LABEL_IN_ESSENTIALLY_TERNARY_COMPATIBLE_GATE":False,
        "remaining_escape_classes":[
          "NONFUNCTIONAL_AUXILIARY_RELATIONS",
          "LARGER_LIFTED_DOMAINS",
          "GENUINELY_NONLOCAL_EXACT_PREPROCESSING",
          "HIGHER_ARITY_FUNCTIONS_PENDING_GENERAL_CLASSIFICATION"
        ]
      },
      "firewall":{
        "P_VS_NP":"OPEN","D1":"EMPTY","SUCCESSOR_ALGORITHM":"LOCKED",
        "finite_classification_scope":"ALL_BOOLEAN_FUNCTIONS_OF_ARITY_3"
      }
    }


if __name__=="__main__":
    print(json.dumps(build_receipt(),indent=2,sort_keys=True))
