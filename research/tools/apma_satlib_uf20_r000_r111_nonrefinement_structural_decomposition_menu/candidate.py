from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Hashable

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_PREREGISTRATION_2026-09-17.json'
REVIEW = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_PREREGISTRATION_REVIEW_2026-09-17.json'
ROUTE = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_CLOSURE_LEVERAGE_REQUIREMENTS_SYNTHESIS_RESULT_2026-09-17.json'
FRESH = ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
PROJECTION = ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
EXPECTED = {
    PREREG:'cb82240f1b7183f6875cf20a658eca3270baad52',
    REVIEW:'38e8d7fb6a91f3aa66d36a742ef210ed47483b02',
    ROUTE:'c5e2e7b6e7612cea498045611d6173d8aa14ffe4',
    FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092',
    PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
ORDER = ('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES = {
    'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
    'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
    'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
    'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6'),
}
DIDS = ('D1_PRIMAL_ARTICULATION_BLOCK_PROFILE','D2_INCIDENCE_ARTICULATION_BLOCK_PROFILE','D3_PRIMAL_MINIMAL_TWO_VERTEX_SEPARATOR_PROFILE')


def blob(path:Path)->str:
    data=path.read_bytes(); return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def csha(obj:Any)->str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def node_key(n:Hashable):
    if isinstance(n,tuple) and len(n)==2:
        return (0,int(n[1])) if n[0]=='VAR' else (1,str(n[1]))
    return (2,str(n))

def components(graph:dict[Hashable,set[Hashable]], removed:set[Hashable]|None=None)->list[set[Hashable]]:
    removed=removed or set(); unseen=set(graph)-removed; out=[]
    while unseen:
        start=min(unseen,key=node_key); stack=[start]; unseen.remove(start); comp={start}
        while stack:
            u=stack.pop()
            for v in graph[u]:
                if v not in removed and v in unseen:
                    unseen.remove(v); comp.add(v); stack.append(v)
        out.append(comp)
    out.sort(key=lambda c:(len(c),[node_key(x) for x in sorted(c,key=node_key)]))
    return out

def connected(graph:dict[Hashable,set[Hashable]], removed:set[Hashable]|None=None)->bool:
    return len(components(graph,removed))<=1

def tarjan_articulations(graph:dict[Hashable,set[Hashable]])->list[Hashable]:
    disc:dict[Hashable,int]={}; low:dict[Hashable,int]={}; parent:dict[Hashable,Hashable|None]={}; aps:set[Hashable]=set(); clock=0
    def dfs(u:Hashable):
        nonlocal clock
        clock+=1; disc[u]=low[u]=clock; children=0
        for v in sorted(graph[u],key=node_key):
            if v not in disc:
                parent[v]=u; children+=1; dfs(v); low[u]=min(low[u],low[v])
                if parent.get(u) is None and children>1: aps.add(u)
                if parent.get(u) is not None and low[v]>=disc[u]: aps.add(u)
            elif v!=parent.get(u):
                low[u]=min(low[u],disc[v])
    for u in sorted(graph,key=node_key):
        if u not in disc:
            parent[u]=None; dfs(u)
    return sorted(aps,key=node_key)

def primal_graph(raw:dict[str,Any])->dict[int,set[int]]:
    g={int(v):set() for v in raw['variables']}
    for row in raw['constraints']:
        for a,b in itertools.combinations(row['scope'],2):
            a=int(a);b=int(b);g[a].add(b);g[b].add(a)
    return g

def incidence_graph(raw:dict[str,Any])->dict[tuple[str,Any],set[tuple[str,Any]]]:
    g:dict[tuple[str,Any],set[tuple[str,Any]]]={('VAR',int(v)):set() for v in raw['variables']}
    for row in raw['constraints']:
        c=('CONSTRAINT',str(row['id']));g[c]=set()
        for v in row['scope']:
            x=('VAR',int(v));g[x].add(c);g[c].add(x)
    return g

def d1(g:dict[int,set[int]])->dict[str,Any]:
    rows=[]
    for v in tarjan_articulations(g):
        sizes=sorted(len(c) for c in components(g,{v}) if c)
        rows.append({'variable':int(v),'residual_component_sizes':sizes})
    present=any(len(r['residual_component_sizes'])>=2 for r in rows)
    return {'articulation_rows':rows,'articulation_count':len(rows),'decomposition_present':present}

def d2(g:dict[tuple[str,Any],set[tuple[str,Any]]])->dict[str,Any]:
    rows=[]
    for a in tarjan_articulations(g):
        profiles=[]
        for comp in components(g,{a}):
            if not comp: continue
            nv=sum(n[0]=='VAR' for n in comp); nc=sum(n[0]=='CONSTRAINT' for n in comp)
            profiles.append([nv,nc,nv+nc])
        profiles.sort()
        rows.append({'node_type':a[0],'node_name':('v'+str(a[1])) if a[0]=='VAR' else str(a[1]),'residual_component_profiles':profiles})
    rows.sort(key=lambda r:(r['node_type'],r['node_name']))
    present=any(len(r['residual_component_profiles'])>=2 for r in rows)
    return {'articulation_rows':rows,'articulation_count':len(rows),'decomposition_present':present}

def d3(g:dict[int,set[int]])->dict[str,Any]:
    rows=[]; vertices=sorted(g); base_connected=connected(g)
    if base_connected:
        for u,v in itertools.combinations(vertices,2):
            if not connected(g,{u}) or not connected(g,{v}):
                continue
            comps=[c for c in components(g,{u,v}) if c]
            if len(comps)>=2:
                rows.append({'pair':[u,v],'residual_component_sizes':sorted(len(c) for c in comps)})
    return {'separator_rows':rows,'separator_count':len(rows),'decomposition_present':bool(rows),'base_primal_graph_connected':base_connected}

def graph_receipt(pg:dict[int,set[int]],ig:dict[tuple[str,Any],set[tuple[str,Any]]],raw:dict[str,Any])->dict[str,int]:
    return {'primal_vertex_count':len(pg),'primal_edge_count':sum(len(x) for x in pg.values())//2,'incidence_variable_node_count':len(raw['variables']),'incidence_constraint_node_count':len(raw['constraints']),'incidence_edge_count':sum(len(x) for x in ig.values())//2}

def guard()->dict[str,Any]:
    pre=json.loads(PREREG.read_text()); review=json.loads(REVIEW.read_text()); binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}; sb={n:blob(p)==sha for n,(p,sha,_) in SOURCES.items()}
    checks={'authority_bindings':all(binds.values()),'source_bindings':all(sb.values()),'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_STRUCTURAL_DECOMPOSITION_VALUE_COMPUTATION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','targets_exact':tuple(pre['discovery_scope']['primary_execution_targets'])==ORDER,'diagnostic_ids_exact':tuple(x['diagnostic_id'] for x in pre['diagnostic_menu'])==DIDS,'fresh_holdout_values_forbidden':pre['discovery_scope']['fresh_evaluation_holdout_values_may_be_read_or_computed'] is False}
    return {'ok':all(checks.values()),'checks':checks,'bindings':binds,'source_bindings':sb}
def outcome(count:int)->str:
    if count==4:return 'COMMON_FOUR_SOURCE_STRUCTURAL_DIAGNOSTIC'
    if 1<=count<=3:return 'PARTIAL_STRUCTURAL_DIAGNOSTIC'
    return 'NO_STRUCTURAL_DIAGNOSTIC'
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','STRUCTURAL_SEPARATOR_IMPLIES_TRACTABILITY':False,'STRUCTURAL_SEPARATOR_IMPLIES_HARDNESS':False,'STRUCTURAL_SEPARATOR_IMPLIES_CLOSURE':False}
def main()->dict[str,Any]:
    g=guard()
    if not g['ok']:return {'verdict':'HALT_FROZEN_AUTHORITY_OR_SOURCE_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
    rows=[]
    for name in ORDER:
        path,_,expected_raw=SOURCES[name]; clauses=projection_identity.parse(path); raw,_=projection_identity.normalize_projection(name,clauses); raw_sha=csha(raw)
        if raw_sha!=expected_raw:return {'verdict':'HALT_PROJECTED_RAW_BINDING_FAILURE','source':name,'expected':expected_raw,'observed':raw_sha,'source_guard':g,'scientific_firewall':firewall()}
        pg=primal_graph(raw);ig=incidence_graph(raw)
        rows.append({'source':name,'projected_raw_sha256':raw_sha,'graph_receipt':graph_receipt(pg,ig,raw),'diagnostics':{DIDS[0]:d1(pg),DIDS[1]:d2(ig),DIDS[2]:d3(pg)}})
    summary={}
    for did in DIDS:
        count=sum(bool(r['diagnostics'][did]['decomposition_present']) for r in rows);summary[did]={'presence_count':count,'outcome':outcome(count),'sources_present':[r['source'] for r in rows if r['diagnostics'][did]['decomposition_present']],'sources_absent':[r['source'] for r in rows if not r['diagnostics'][did]['decomposition_present']]}
    if any(v['outcome']=='COMMON_FOUR_SOURCE_STRUCTURAL_DIAGNOSTIC' for v in summary.values()):overall='COMMON_FOUR_SOURCE_STRUCTURAL_LEVERAGE_PRESENT'
    elif any(v['outcome']=='PARTIAL_STRUCTURAL_DIAGNOSTIC' for v in summary.values()):overall='PARTIAL_STRUCTURAL_LEVERAGE_ONLY'
    else:overall='NO_TESTED_STRUCTURAL_DECOMPOSITION_LEVERAGE'
    return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-NONREFINEMENT-STRUCTURAL-DECOMPOSITION-MENU-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_SOURCE_AGNOSTIC_POLYNOMIAL_STRUCTURAL_DECOMPOSITION_FALSIFIER_ONLY__NO_HOLDOUT_VALUES_NO_SOLVER_ACTION_AUTOMORPHISM_GROUP_SEARCH_CARRIER_ADAPTER_OR_QUOTIENT','verdict':overall,'source_guard':g,'rows':rows,'diagnostic_summary':summary,'overall_outcome':overall,'resource_receipt':{'target_sources':4,'diagnostics':3,'fresh_holdout_values_read':0,'solver_invocations':0,'portfolio_replays':0,'boundary_relation_enumerations':0,'component_solution_attempts':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
