from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis

ROOT=Path(__file__).resolve().parents[3]
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SOURCE_BOUND_CORE_PROJECTION_RESULT_2026-09-16.json'
RAW_BASIS=ROOT/'research/tools/apma_unseen_basis/raw_relation_basis.py'
EXPECTED={PARENT:'3a1e13a72183490a33e879d3f0c033f7c805b7e5',RAW_BASIS:'63490c05ef3e91a4f682f75da26ff2af811839a6'}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
CORE={'000','111'}

def blob(path:Path)->str:
 data=path.read_bytes();return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def parse(path:Path):
 clauses=[];buf=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):x=s.split();header=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:
    assert len(buf)==3 and len({abs(x) for x in buf})==3
    clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert header==(20,91) and len(clauses)==91 and not buf
 return clauses

def rid(clause):return ''.join('0' if lit>0 else '1' for lit in sorted(clause,key=lambda x:abs(x)))
def canonical_bytes(obj:Any)->bytes:return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')

def normalize_projection(source:str,clauses):
 selected=[(i,c) for i,c in enumerate(clauses,1) if rid(c) in CORE]
 variables=sorted({abs(lit) for _,c in selected for lit in c});constraints=[];prefix=source.lower()
 for ordinal,clause in selected:
  scope=sorted(abs(lit) for lit in clause);allowed=[]
  for bits in itertools.product((0,1),repeat=3):
   a=dict(zip(scope,bits,strict=True));sat=any((a[abs(lit)]==1) if lit>0 else (a[abs(lit)]==0) for lit in clause)
   if sat:allowed.append(list(bits))
  constraints.append({'id':f'satlib_{prefix}_c{ordinal:03d}','scope':scope,'allowed':allowed})
 raw=raw_basis.canonicalize_raw({'variables':variables,'constraints':constraints})
 return raw,[i for i,_ in selected]

def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};source_bindings={n:blob(p)==s for n,(p,s) in SOURCES.items()}
 if not all(bindings.values()) or not all(source_bindings.values()):return {'verdict':'SOURCE_OR_PARENT_GUARD_FAILURE','bindings':bindings,'source_bindings':source_bindings}
 rows=[]
 for name,(path,_) in SOURCES.items():
  raw,ordinals=normalize_projection(name,parse(path));rows.append({'source':name,'selected_clause_ordinals':ordinals,'variables':raw['variables'],'constraint_count':len(raw['constraints']),'projected_raw_sha256':hashlib.sha256(canonical_bytes(raw)).hexdigest()})
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-RAW-IDENTITY-FREEZE-2026-09-16-v1.0','authority':'PRE_REPLAY_IDENTITY_MATERIALIZATION_ONLY','verdict':'PASS_PROJECTED_RAW_IDENTITIES_MATERIALIZED','bindings':bindings,'source_bindings':source_bindings,'rows':rows,'resource_receipt':{'portfolio_invocations':0,'solver_invocations':0,'new_adapters':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED'}}

if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
