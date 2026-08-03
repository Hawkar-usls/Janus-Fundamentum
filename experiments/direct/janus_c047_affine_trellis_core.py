#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import hashlib, json
from typing import Any, Iterable

Equation = tuple[int,int]
LinearSpace = tuple[int,...]
AffineSystem = tuple[Equation,...]

SCHEMA = "janus.c047.offset_aware_affine_functional_trellis.v1"
OPEN_CUT_WIDTH = "OPEN_CUT_WIDTH"
OPEN_WORK_BUDGET = "OPEN_WORK_BUDGET"
OPEN_CERTIFICATE_VOLUME = "OPEN_CERTIFICATE_VOLUME"
MAX_WIDTH_CAP = 8
WORK_MULTIPLIER = 256
WORK_EXPONENT = 7
CERT_MULTIPLIER = 128
CERT_EXPONENT = 6

def canonical_json(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",",":"), ensure_ascii=False)

def digest(x: Any) -> str:
    return hashlib.sha256(canonical_json(x).encode()).hexdigest()

def pivot(row:int)->int:
    return (row & -row).bit_length()-1

def linear_rref(vectors: Iterable[int], dimension:int) -> LinearSpace:
    rows=[int(v) for v in vectors if int(v)]
    rank=0
    for bit in range(dimension):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>bit)&1),None)
        if p is None: continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>bit)&1):
                rows[i]^=rows[rank]
        rank+=1
    rows=[r for r in rows if r]
    rows.sort(key=lambda r:(pivot(r),r))
    return tuple(rows)

def affine_rref(equations: Iterable[Equation], dimension:int) -> AffineSystem|None:
    rows=[[int(m),int(b)&1] for m,b in equations]
    rank=0
    for bit in range(dimension):
        p=next((i for i in range(rank,len(rows)) if (rows[i][0]>>bit)&1),None)
        if p is None: continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i][0]>>bit)&1):
                rows[i][0]^=rows[rank][0]
                rows[i][1]^=rows[rank][1]
        rank+=1
    for m,b in rows:
        if m==0 and b: return None
    nz=[(m,b) for m,b in rows if m]
    nz.sort(key=lambda x:(pivot(x[0]),x[0],x[1]))
    return tuple(nz)

def orthogonal_complement(space:LinearSpace, dimension:int)->LinearSpace:
    rows=linear_rref(space,dimension)
    pivots=[pivot(r) for r in rows]
    free=[i for i in range(dimension) if i not in pivots]
    basis=[]
    for f in free:
        x=1<<f
        for r,p in reversed(list(zip(rows,pivots))):
            if (r & x).bit_count()&1:
                x |= 1<<p
        basis.append(x)
    return linear_rref(basis,dimension)

def span(*spaces:LinearSpace, dimension:int)->LinearSpace:
    return linear_rref([v for s in spaces for v in s],dimension)

def intersection(left:LinearSpace,right:LinearSpace,dimension:int)->LinearSpace:
    return orthogonal_complement(
        span(orthogonal_complement(left,dimension),
             orthogonal_complement(right,dimension),dimension=dimension),
        dimension)

def coordinates(vector:int,basis:LinearSpace)->int:
    bits=0
    for i,row in enumerate(basis):
        if vector & (1<<pivot(row)):
            bits |= 1<<i
    rec=0
    for i,row in enumerate(basis):
        if (bits>>i)&1: rec ^= row
    if rec!=vector:
        raise ValueError("vector outside span")
    return bits

def functional_value(vector:int,basis:LinearSpace,values:int)->int:
    return (coordinates(vector,basis)&values).bit_count()&1

def restrict_functional(source_basis:LinearSpace,source_values:int,target_basis:LinearSpace)->int:
    out=0
    for i,v in enumerate(target_basis):
        if functional_value(v,source_basis,source_values):
            out|=1<<i
    return out

def solve_binary_system(equations:list[tuple[int,int]], variables:int)->tuple[int,list[int]]|None:
    rows=[[m,b&1] for m,b in equations]
    rank=0
    pivots=[]
    for bit in range(variables):
        p=next((i for i in range(rank,len(rows)) if (rows[i][0]>>bit)&1),None)
        if p is None: continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i][0]>>bit)&1):
                rows[i][0]^=rows[rank][0]; rows[i][1]^=rows[rank][1]
        pivots.append(bit); rank+=1
    for m,b in rows:
        if m==0 and b: return None
    value=0
    for i,p in enumerate(pivots):
        if rows[i][1]: value|=1<<p
    free=[b for b in range(variables) if b not in pivots]
    null=[]
    for f in free:
        z=1<<f
        for i,p in reversed(list(enumerate(pivots))):
            if (rows[i][0]&z).bit_count()&1:
                z|=1<<p
        null.append(z)
    return value,null

def solve_functional_constraints(
    ambient_basis:LinearSpace,
    constraints:list[tuple[int,int]],
)->int|None:
    eq=[]
    for vector,rhs in constraints:
        eq.append((coordinates(vector,ambient_basis),rhs))
    solved=solve_binary_system(eq,len(ambient_basis))
    return None if solved is None else solved[0]

def extend_avoiding(
    prev_boundary:LinearSpace, prev_state:int,
    current_boundary:LinearSpace, current_state:int,
    factor_space:AffineSystem,
    dimension:int,
)->dict[str,Any]|None:
    normal_basis=tuple(mask for mask,_ in factor_space)
    beta=[rhs for _,rhs in factor_space]
    local=span(prev_boundary,current_boundary,normal_basis,dimension=dimension)
    base=[]
    for i,v in enumerate(prev_boundary):
        base.append((v,(prev_state>>i)&1))
    for i,v in enumerate(current_boundary):
        base.append((v,(current_state>>i)&1))
    if not normal_basis:
        return None
    for j,v in enumerate(normal_basis):
        candidate=solve_functional_constraints(local,base+[(v,beta[j]^1)])
        if candidate is not None:
            tau=restrict_functional(local,candidate,normal_basis)
            return {
                "local_basis":list(local),
                "local_values":candidate,
                "factor_values":tau,
                "separating_row":j,
            }
    return None

def combine_functionals(
    left_basis:LinearSpace,left_values:int,
    right_basis:LinearSpace,right_values:int,
    dimension:int,
)->tuple[LinearSpace,int]:
    total=span(left_basis,right_basis,dimension=dimension)
    constraints=[]
    for i,v in enumerate(left_basis):
        constraints.append((v,(left_values>>i)&1))
    for i,v in enumerate(right_basis):
        constraints.append((v,(right_values>>i)&1))
    values=solve_functional_constraints(total,constraints)
    if values is None:
        raise AssertionError("compatible functionals failed to combine")
    return total,values

def solve_point(normal_basis:LinearSpace,values:int,dimension:int)->int|None:
    eq=[(v,(values>>i)&1) for i,v in enumerate(normal_basis)]
    solved=solve_binary_system(eq,dimension)
    return None if solved is None else solved[0]

def point_in_factor(point:int,factor:AffineSystem)->bool:
    return all(((point&m).bit_count()&1)==b for m,b in factor)

def normalize_factors(factors:list[dict[str,Any]],dimension:int)->list[dict[str,Any]]:
    out=[]
    for pos,f in enumerate(factors):
        fid=int(f.get("factor_id",pos))
        r=affine_rref([(int(m),int(b)) for m,b in f["equations"]],dimension)
        if r is None:
            continue
        out.append({"factor_id":fid,"equations":r,"input_position":pos})
    out.sort(key=lambda f:(f["input_position"],f["factor_id"]))
    return out

def deterministic_order(factors:list[dict[str,Any]])->list[int]:
    classes=[]
    index={}
    for i,f in enumerate(factors):
        normal=tuple(m for m,_ in f["equations"])
        if normal not in index:
            index[normal]=len(classes); classes.append([])
        classes[index[normal]].append(i)
    return [i for cls in classes for i in cls]

def input_length(factors:list[dict[str,Any]],dimension:int)->int:
    return max(2,dimension+len(factors)+sum(len(f["equations"]) for f in factors)
               +sum(m.bit_count() for f in factors for m,_ in f["equations"]))

@dataclass
class Capability:
    input_length:int
    requested_width_cap:int=3
    work_cap:int|None=None
    certificate_cap:int|None=None
    def __post_init__(self):
        base=self.input_length+1
        self.width_limit=min(MAX_WIDTH_CAP,max(0,int(self.requested_width_cap)))
        self.work_polynomial=WORK_MULTIPLIER*base**WORK_EXPONENT
        self.certificate_polynomial=CERT_MULTIPLIER*base**CERT_EXPONENT
        self.work_limit=min(self.work_polynomial,self.work_cap if self.work_cap is not None else self.work_polynomial)
        self.certificate_limit=min(self.certificate_polynomial,self.certificate_cap if self.certificate_cap is not None else self.certificate_polynomial)
    def manifest(self):
        return {
            "input_length":self.input_length,
            "max_width_cap":MAX_WIDTH_CAP,
            "requested_width_cap":self.requested_width_cap,
            "width_limit":self.width_limit,
            "work_polynomial":str(self.work_polynomial),
            "work_cap":None if self.work_cap is None else str(self.work_cap),
            "work_limit":str(self.work_limit),
            "certificate_polynomial":str(self.certificate_polynomial),
            "certificate_cap":None if self.certificate_cap is None else str(self.certificate_cap),
            "certificate_limit":str(self.certificate_limit),
        }

class OpenResult(Exception):
    def __init__(self,status,stage,evidence):
        super().__init__(status); self.status=status; self.stage=stage; self.evidence=evidence

@dataclass
class Meter:
    capability:Capability
    work:int=0
    transition_tests:int=0
    states_materialized:int=0
    max_width:int=0
    certificate_bytes_charged:int=0
    def charge(self,stage:str,amount:int=1):
        attempted=self.work+max(1,int(amount))
        if attempted>self.capability.work_limit:
            raise OpenResult(OPEN_WORK_BUDGET,stage,{"attempted_work":attempted,"work_limit":self.capability.work_limit})
        self.work=attempted
    def snapshot(self):
        return {
            "total_work_units":self.work,
            "transition_tests":self.transition_tests,
            "states_materialized":self.states_materialized,
            "max_width":self.max_width,
            "certificate_bytes_charged":self.certificate_bytes_charged,
        }

def fixed_point_certificate(body:dict[str,Any],cap:Capability,meter:Meter)->dict[str,Any]:
    charged=0; stated=0
    for _ in range(20):
        body["producer_ledger"]=meter.snapshot()
        body["certificate_bytes"]=stated
        probe=dict(body); probe["integrity_sha256"]="0"*64
        size=len(canonical_json(probe).encode())
        if size>cap.certificate_limit:
            raise OpenResult(OPEN_CERTIFICATE_VOLUME,"certificate_bytes",
                             {"attempted_certificate_bytes":size,"certificate_limit":cap.certificate_limit,
                              "semantic_payload_sha256":digest(body)})
        if size>charged:
            meter.charge("certificate_bytes",size-charged)
            meter.certificate_bytes_charged += size-charged
            charged=size
        if size==stated: break
        stated=size
    body["producer_ledger"]=meter.snapshot()
    body["certificate_bytes"]=stated
    body["integrity_sha256"]=digest(body)
    return body
