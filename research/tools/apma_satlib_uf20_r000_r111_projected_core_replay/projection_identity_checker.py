from __future__ import annotations
import argparse,hashlib,itertools,json
from pathlib import Path
from research.tools.apma_unseen_basis import raw_relation_basis as rb
ROOT=Path(__file__).resolve().parents[3]
SOURCES={
'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def parse(p):
 cs=[];buf=[];h=None
 for raw in p.read_text().splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):x=s.split();h=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3 and len({abs(x) for x in buf})==3;cs.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert h==(20,91) and len(cs)==91 and not buf;return cs
def kind(c):return ''.join('0' if x>0 else '1' for x in sorted(c,key=lambda z:abs(z)))
def row(source,p):
 selected=[(i,c) for i,c in enumerate(parse(p),1) if kind(c) in {'000','111'}];vs=sorted({abs(x) for _,c in selected for x in c});cons=[]
 for i,c in selected:
  sc=sorted(abs(x) for x in c);allowed=[]
  for bits in itertools.product((0,1),repeat=3):
   a=dict(zip(sc,bits,strict=True))
   if any((a[abs(x)]==1) if x>0 else (a[abs(x)]==0) for x in c):allowed.append(list(bits))
  cons.append({'id':f'satlib_{source.lower()}_c{i:03d}','scope':sc,'allowed':allowed})
 raw=rb.canonicalize_raw({'variables':vs,'constraints':cons});b=json.dumps(raw,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
 return {'source':source,'selected_clause_ordinals':[i for i,_ in selected],'variables':raw['variables'],'constraint_count':len(raw['constraints']),'projected_raw_sha256':hashlib.sha256(b).hexdigest()}
def main(c):
 source_ok={n:blob(p)==s for n,(p,s) in SOURCES.items()};rows=[row(n,p) for n,(p,_) in SOURCES.items()];checks={'candidate_not_imported':True,'candidate_verdict':c.get('verdict')=='PASS_PROJECTED_RAW_IDENTITIES_MATERIALIZED','source_blobs':all(source_ok.values()),'rows':c.get('rows')==rows,'no_portfolio':c.get('resource_receipt',{}).get('portfolio_invocations')==0,'firewall':c.get('scientific_firewall',{}).get('P_VS_NP')=='OPEN'};return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-RAW-IDENTITY-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_rows':rows}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
