import json,zipfile
z="experiments/babel14/BABEL14_SEED2_COMPACT_PROOF_BUNDLE_20261020.zip"
with zipfile.ZipFile(z) as f:
 obj=json.loads(f.read("babel10_SCL126_flip68_EXACT_DEGREE1_OBSTRUCTION.json"))
 print("SOURCE_LOWER_FIELDS",list(obj),flush=True)
 for key,v in obj.items():
  if isinstance(v,list):print("LOWER_FIELD",key,"LIST",len(v),"sample",repr(v[:4])[:180],flush=True)
  elif isinstance(v,dict):print("LOWER_FIELD",key,"DICT",len(v),"keys",list(v)[:12],flush=True)
  else:print("LOWER_FIELD",key,repr(v)[:250],flush=True)
 for path in ("janus_babel10_exact_lower.py","test_janus_babel15.py"):
  print("BEGIN_SOURCE",path,flush=True)
  try:print(f.read(path).decode(),flush=True)
  except KeyError as e:print("MISSING",str(e),flush=True)
  print("END_SOURCE",path,flush=True)
