from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_REVIEW_2026-09-17_v1.0.json'
RESERVATION=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_PANEL_RESERVATION_PREREGISTRATION_2026-09-17_v1.0.json'
EXPECTED={PREREG:'dac5bdbe4c7c5948c91ff7c182ff40c70478cdc2',REVIEW:'a4282c039811a54110950fa30ed004cb930dcdbd',RESERVATION:'853d69fba0ba90a892f0bea2d09c04253d3fa028'}
PRIMARY_REPO='Jany26/tree-aut-lib';PRIMARY_COMMIT='6cd58ade6de0a5c05511deb76c261ee75356ff31'
VERIFY_REPO='dncarley/MolecularSimulation';VERIFY_COMMIT='d23a1d1775a939af0a6032ec459e5055919843a7'
ORDER=tuple(f'UF20_{i:03d}' for i in range(26,76))


def blob_bytes(data:bytes)->str:return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
def blob(path:Path)->str:return blob_bytes(path.read_bytes())
def sha256(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def fetch_raw(repo:str,commit:str,path:str)->bytes:
    url=f'https://raw.githubusercontent.com/{repo}/{commit}/{path}'
    req=urllib.request.Request(url,headers={'User-Agent':'Janus-Fundamentum-UF20-026-075-source-freeze/1.0'})
    with urllib.request.urlopen(req,timeout=30) as r:
        if r.status!=200:raise RuntimeError(f'FETCH_STATUS:{repo}:{path}:{r.status}')
        return r.read()

def parse(data:bytes)->dict[str,Any]:
    nvars=nclauses=None;clauses=[]
    for raw in data.decode('utf-8').splitlines():
        s=raw.strip()
        if not s or s.startswith('c') or s in {'%','0'}:continue
        if s.startswith('p '):
            p=s.split();
            if p[:2]!=['p','cnf'] or len(p)!=4:raise ValueError('BAD_HEADER')
            nvars,nclauses=int(p[2]),int(p[3]);continue
        vals=[int(x) for x in s.split()]
        if not vals or vals[-1]!=0:raise ValueError('BAD_CLAUSE_TERMINATOR')
        clause=vals[:-1]
        if len(clause)!=3 or len({abs(x) for x in clause})!=3:raise ValueError('BAD_3CNF_CLAUSE')
        clauses.append(clause)
    if nvars!=20 or nclauses!=91 or len(clauses)!=91:raise ValueError(f'BAD_SHAPE:{nvars}:{nclauses}:{len(clauses)}')
    canonical=''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')
    return {'variables':nvars,'clauses':clauses,'canonical_formula_sha256':sha256(canonical)}
def guard()->dict[str,Any]:
    bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
    pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());reservation=json.loads(RESERVATION.read_text())
    checks={
        'authority_bindings':all(bindings.values()),
        'prereg_status':pre.get('status')=='FROZEN_BEFORE_FIRST_RESERVED_SOURCE_CONTENT_FETCH',
        'review_authorized':review.get('review_verdict')=='PASS_CLEAN_SOURCE_ACQUISITION_SPEC__AUTHORIZED_TO_FETCH_FREEZE_AND_VERIFY_ALL_FIFTY_ONLY',
        'reservation_status':reservation.get('status')=='FROZEN_BEFORE_ANY_UF20_026_TO_UF20_075_SOURCE_CONTENT_INSPECTION_IN_THIS_LINEAGE',
        'selection_exact':tuple(reservation.get('reserved_sources',[]))==ORDER,
        'panel_size_exact':reservation.get('panel_size')==50,
    }
    return {'ok':all(checks.values()),'checks':checks,'bindings':bindings}
def main()->dict[str,Any]:
    g=guard()
    if not g['ok']:return {'verdict':'HALT_AUTHORITY_OR_RESERVATION_BINDING_FAILURE','guard':g,'resource_receipt':receipt(0)}
    rows=[]
    try:
        for source in ORDER:
            n=int(source.split('_')[1]);nnn=f'{n:03d}'
            ppath=f'benchmark/dimacs/uf20/uf20-{nnn}.cnf';vpath=f'data/uf20-91/uf20-{nnn}.cnf'
            primary=fetch_raw(PRIMARY_REPO,PRIMARY_COMMIT,ppath);verify=fetch_raw(VERIFY_REPO,VERIFY_COMMIT,vpath)
            pp=parse(primary);vp=parse(verify)
            ordered=pp['clauses']==vp['clauses'];canonical=pp['canonical_formula_sha256']==vp['canonical_formula_sha256']
            if not ordered or not canonical:
                return {'verdict':'HALT_ORDERED_CLAUSE_OR_CANONICAL_FORMULA_MISMATCH','source':source,'rows':rows,'resource_receipt':receipt(len(rows)*2+2)}
            out=ROOT/f'research/source_data/SATLIB_UF20_{nnn}_2026-09-17.cnf'
            if out.exists():
                return {'verdict':'HALT_COMMITTED_COPY_BINDING_FAILURE','source':source,'reason':'TARGET_PATH_PREEXISTS','rows':rows,'resource_receipt':receipt(len(rows)*2+2)}
            out.write_bytes(primary)
            rows.append({'source':source,'filename':f'uf20-{nnn}.cnf','committed_copy_path':str(out.relative_to(ROOT)),'variables':20,'clauses':91,'arity':3,'primary_repo':PRIMARY_REPO,'primary_commit':PRIMARY_COMMIT,'primary_path':ppath,'primary_git_blob':blob_bytes(primary),'primary_raw_sha256':sha256(primary),'verification_repo':VERIFY_REPO,'verification_commit':VERIFY_COMMIT,'verification_path':vpath,'verification_git_blob':blob_bytes(verify),'verification_raw_sha256':sha256(verify),'canonical_formula_sha256':pp['canonical_formula_sha256'],'ordered_clause_sequence_equal':ordered,'raw_bytes_primary_equal_verification':primary==verify,'computed_committed_git_blob':blob_bytes(primary),'independent_verified':False,'status':'SOURCE_STAGED_FOR_INDEPENDENT_VERIFICATION'})
    except Exception as exc:
        return {'verdict':'HALT_SOURCE_MISSING_OR_FETCH_FAILURE','error':f'{type(exc).__name__}:{exc}','rows':rows,'resource_receipt':receipt(len(rows)*2)}
    return {'artifact_id':'JANUS-TRUMP-UF20-026-075-PROSPECTIVE-SOURCE-ACQUISITION-CANDIDATE-2026-09-17-v1.0','verdict':'PASS_UF20_026_075_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE','guard':g,'source_receipts':rows,'resource_receipt':receipt(100),'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY':'NOT_PROVED'}}
def receipt(fetches:int)->dict[str,int]:
    return {'remote_source_fetches':fetches,'sources_reserved':50,'projected_raw_computations':0,'pendant_target_computations':0,'wl_computations':0,'direct_transposition_checks':0,'portfolio_replays':0,'e3_witness_computations':0,'solver_invocations':0}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
