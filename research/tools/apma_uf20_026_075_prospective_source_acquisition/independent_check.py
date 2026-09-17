from __future__ import annotations

import argparse,hashlib,json,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
CANDIDATE=ROOT/'research/tools/apma_uf20_026_075_prospective_source_acquisition/candidate.py'
CANDIDATE_BLOB='f051f1a8b7636018aacc9a4909fa51b28db1568e'
PRIMARY_REPO='Jany26/tree-aut-lib';PRIMARY_COMMIT='6cd58ade6de0a5c05511deb76c261ee75356ff31'
VERIFY_REPO='dncarley/MolecularSimulation';VERIFY_COMMIT='d23a1d1775a939af0a6032ec459e5055919843a7'
ORDER=tuple(f'UF20_{i:03d}' for i in range(26,76))
def blob_bytes(d):return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def sha256(d):return hashlib.sha256(d).hexdigest()
def fetch(repo,commit,path):
    req=urllib.request.Request(f'https://raw.githubusercontent.com/{repo}/{commit}/{path}',headers={'User-Agent':'Janus-Fundamentum-independent-source-freeze/1.0'})
    with urllib.request.urlopen(req,timeout=30) as r:return r.read()
def parse(data):
    nv=nc=None;clauses=[]
    for raw in data.decode().splitlines():
        s=raw.strip()
        if not s or s.startswith('c') or s in {'%','0'}:continue
        if s.startswith('p '):
            p=s.split();nv,nc=int(p[2]),int(p[3]);continue
        vals=[int(x) for x in s.split()];assert vals[-1]==0
        c=vals[:-1];assert len(c)==3 and len({abs(x) for x in c})==3;clauses.append(c)
    assert nv==20 and nc==91 and len(clauses)==91
    canonical=''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')
    return clauses,sha256(canonical)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);args=ap.parse_args()
    c=json.loads(Path(args.candidate).read_text())
    if blob_bytes(CANDIDATE.read_bytes())!=CANDIDATE_BLOB:return {'verdict':'HALT_INDEPENDENT_CANDIDATE_BLOB_MISMATCH'}
    if c.get('verdict')!='PASS_UF20_026_075_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE':return {'verdict':'HALT_INDEPENDENT_CANDIDATE_NOT_PASS','candidate_verdict':c.get('verdict')}
    by={r['source']:r for r in c['source_receipts']};rows=[]
    try:
        for source in ORDER:
            n=int(source.split('_')[1]);nnn=f'{n:03d}';pp=f'benchmark/dimacs/uf20/uf20-{nnn}.cnf';vp=f'data/uf20-91/uf20-{nnn}.cnf'
            p=fetch(PRIMARY_REPO,PRIMARY_COMMIT,pp);v=fetch(VERIFY_REPO,VERIFY_COMMIT,vp);pc,ph=parse(p);vc,vh=parse(v)
            local=(ROOT/f'research/source_data/SATLIB_UF20_{nnn}_2026-09-17.cnf').read_bytes();row=by[source]
            ok=(pc==vc and ph==vh and local==p and blob_bytes(local)==row['computed_committed_git_blob'] and ph==row['canonical_formula_sha256'] and blob_bytes(p)==row['primary_git_blob'] and blob_bytes(v)==row['verification_git_blob'])
            rows.append({'source':source,'independent_verified':ok,'committed_git_blob':blob_bytes(local),'canonical_formula_sha256':ph,'ordered_clause_sequence_equal':pc==vc})
    except Exception as exc:return {'verdict':'HALT_INDEPENDENT_FETCH_OR_PARSE_FAILURE','error':f'{type(exc).__name__}:{exc}','verified_rows':rows}
    passed=len(rows)==50 and all(r['independent_verified'] for r in rows)
    return {'verdict':'PASS_INDEPENDENT_UF20_026_075_SOURCE_FREEZE_VERIFICATION' if passed else 'FAIL_INDEPENDENT_UF20_026_075_SOURCE_FREEZE_MISMATCH','candidate_imported':False,'verified_rows':rows,'sources_verified':sum(r['independent_verified'] for r in rows),'resource_receipt':{'remote_source_fetches':100,'projected_raw_computations':0,'pendant_target_computations':0,'wl_computations':0,'direct_transposition_checks':0,'portfolio_replays':0,'e3_witness_computations':0,'solver_invocations':0}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
