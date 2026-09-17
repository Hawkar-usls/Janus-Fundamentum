from __future__ import annotations

import hashlib,json,urllib.request
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW=ROOT/'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_REVIEW_2026-09-17_v1.0.json'
RESERVATION=ROOT/'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_PANEL_RESERVATION_PREREGISTRATION_2026-09-17_v1.0.json'
ERRATUM=ROOT/'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_SOURCE_ACQUISITION_FILENAME_ERRATUM_2026-09-17_v1.0.json'
ERRATUM_REVIEW=ROOT/'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_SOURCE_ACQUISITION_FILENAME_ERRATUM_REVIEW_2026-09-17_v1.0.json'
EXPECTED={PREREG:'67f4ddc9704d38816ab126000b503f3302fafa10',REVIEW:'e94025710ccd23691ecddbfe03ef70ccf4a0fbf6',RESERVATION:'a242cb6b60b0f9531a0b942706145417f349aca8',ERRATUM:'d40007eda2cc480c6ba8ba3fb4d95de2d5df7f0f',ERRATUM_REVIEW:'8528779730c38171e36400bc7e5427a7b3538886'}
PRIMARY_REPO='Jany26/tree-aut-lib';PRIMARY_COMMIT='6cd58ade6de0a5c05511deb76c261ee75356ff31'
VERIFY_REPO='dncarley/MolecularSimulation';VERIFY_COMMIT='d23a1d1775a939af0a6032ec459e5055919843a7'
ORDER=tuple(f'UF20_{i:03d}' for i in range(76,176))

def token(n:int)->str:return '0'+str(n)
def blob_bytes(d:bytes)->str:return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def blob(p:Path)->str:return blob_bytes(p.read_bytes())
def sha256(d:bytes)->str:return hashlib.sha256(d).hexdigest()
def fetch(repo:str,commit:str,path:str)->bytes:
    req=urllib.request.Request(f'https://raw.githubusercontent.com/{repo}/{commit}/{path}',headers={'User-Agent':'Janus-Fundamentum-UF20-076-175-source-freeze-v2/1.0'})
    with urllib.request.urlopen(req,timeout=30) as r:return r.read()
def parse(data:bytes)->tuple[list[list[int]],str]:
    nv=nc=None;clauses=[]
    for raw in data.decode('utf-8').splitlines():
        s=raw.strip()
        if not s or s.startswith('c') or s in {'%','0'}:continue
        if s.startswith('p '):
            p=s.split();assert p[:2]==['p','cnf'] and len(p)==4;nv,nc=int(p[2]),int(p[3]);continue
        vals=[int(x) for x in s.split()];assert vals and vals[-1]==0;c=vals[:-1];assert len(c)==3 and len({abs(x) for x in c})==3;clauses.append(c)
    assert nv==20 and nc==91 and len(clauses)==91
    canonical=''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')
    return clauses,sha256(canonical)
def receipt(fetches:int)->dict[str,int]:return {'remote_source_fetches':fetches,'sources_reserved':100,'projected_raw_computations':0,'pendant_target_computations':0,'wl_computations':0,'direct_transposition_checks':0,'portfolio_replays':0,'e3_witness_computations':0,'solver_invocations':0}
def guard()->dict[str,Any]:
    bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
    reservation=json.loads(RESERVATION.read_text());review=json.loads(REVIEW.read_text());er=json.loads(ERRATUM_REVIEW.read_text())
    checks={'authority_bindings':all(bindings.values()),'selection_exact':tuple(reservation['reserved_sources'])==ORDER,'panel_size_exact':reservation['panel_size']==100,'original_review_authorized':review['review_verdict']=='PASS_CLEAN_SOURCE_ACQUISITION_SPEC__AUTHORIZED_TO_FETCH_FREEZE_AND_VERIFY_ALL_ONE_HUNDRED_ONLY','erratum_review_authorized':er['review_verdict']=='PASS_FILENAME_ENCODING_ERRATUM__AUTHORIZED_TO_RERUN_FULL_ONE_HUNDRED_SOURCE_ACQUISITION_ONLY','filename_examples_exact':token(76)=='076' and token(99)=='099' and token(100)=='0100' and token(175)=='0175'}
    return {'ok':all(checks.values()),'checks':checks,'bindings':bindings}
def main()->dict[str,Any]:
    g=guard()
    if not g['ok']:return {'verdict':'HALT_AUTHORITY_OR_ERRATUM_BINDING_FAILURE','guard':g,'resource_receipt':receipt(0)}
    rows=[]
    try:
        for source in ORDER:
            n=int(source.split('_')[1]);remote=token(n);local_id=f'{n:03d}'
            pp=f'benchmark/dimacs/uf20/uf20-{remote}.cnf';vp=f'data/uf20-91/uf20-{remote}.cnf'
            p=fetch(PRIMARY_REPO,PRIMARY_COMMIT,pp);v=fetch(VERIFY_REPO,VERIFY_COMMIT,vp);pc,ph=parse(p);vc,vh=parse(v)
            if pc!=vc or ph!=vh:return {'verdict':'HALT_ORDERED_CLAUSE_OR_CANONICAL_FORMULA_MISMATCH','source':source,'rows':rows,'resource_receipt':receipt(len(rows)*2+2)}
            out=ROOT/f'research/source_data/SATLIB_UF20_{local_id}_2026-09-17.cnf'
            if out.exists():return {'verdict':'HALT_COMMITTED_COPY_BINDING_FAILURE','source':source,'reason':'TARGET_PATH_PREEXISTS','rows':rows,'resource_receipt':receipt(len(rows)*2+2)}
            out.write_bytes(p)
            rows.append({'source':source,'numeric_index':n,'remote_filename':f'uf20-{remote}.cnf','committed_copy_path':str(out.relative_to(ROOT)),'variables':20,'clauses':91,'arity':3,'primary_repo':PRIMARY_REPO,'primary_commit':PRIMARY_COMMIT,'primary_path':pp,'primary_git_blob':blob_bytes(p),'primary_raw_sha256':sha256(p),'verification_repo':VERIFY_REPO,'verification_commit':VERIFY_COMMIT,'verification_path':vp,'verification_git_blob':blob_bytes(v),'verification_raw_sha256':sha256(v),'canonical_formula_sha256':ph,'ordered_clause_sequence_equal':True,'raw_bytes_primary_equal_verification':p==v,'computed_committed_git_blob':blob_bytes(p),'independent_verified':False,'status':'SOURCE_STAGED_FOR_INDEPENDENT_VERIFICATION'})
    except Exception as exc:return {'verdict':'HALT_SOURCE_MISSING_OR_FETCH_FAILURE','error':f'{type(exc).__name__}:{exc}','rows':rows,'resource_receipt':receipt(len(rows)*2)}
    return {'artifact_id':'JANUS-TRUMP-UF20-076-175-SECOND-PROSPECTIVE-SOURCE-ACQUISITION-CANDIDATE-V2-2026-09-17-v1.0','verdict':'PASS_UF20_076_175_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE','guard':g,'source_receipts':rows,'implementation_correction':'REMOTE_FILENAME_ENCODING_ONLY','failed_attempt_run_id':35268385810,'resource_receipt':receipt(200),'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY':'NOT_PROVED'}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
