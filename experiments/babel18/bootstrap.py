#!/usr/bin/env python3
"""BABEL-18 bootstrap: inspect frozen legal-cover generators for rank-2 controls."""
import ast,zipfile,json
archives=["experiments/babel14/BABEL14_SEED2_COMPACT_PROOF_BUNDLE_20261020.zip",
          "experiments/babel15/BABEL15_SEED1_COMPACT_PROOF_BUNDLE_20261020.zip"]
names=["janus_babel6_transfer.py","janus_babel14_antisector_augmented.py",
       "janus_babel15_sector_quotient.py","janus_babel10_degree_scan.py",
       "janus_babel5_lift_dual.py","janus_babel13_sector_graph.py"]
seen=set();inventory={}
for archive in archives:
 with zipfile.ZipFile(archive) as z:
  for fn in names:
   if fn in seen or fn not in z.namelist():continue
   seen.add(fn);source=z.read(fn).decode()
   nodes=ast.parse(source).body
   functions=[{"name":x.name,"args":[v.arg for v in x.args.args],"start":x.lineno}
              for x in nodes if isinstance(x,ast.FunctionDef)]
   inventory[fn]=functions
   print("BABEL18_MODULE",fn,"FUNCTIONS",json.dumps(functions),flush=True)
   if fn in ("janus_babel14_antisector_augmented.py","janus_babel5_lift_dual.py","janus_babel13_sector_graph.py"):
    print("BEGIN_BABEL6_TRANSFER_SOURCE",flush=True)
    print(source,flush=True)
    print("END_BABEL6_TRANSFER_SOURCE",flush=True)
result={"gate":"BABEL18_BOOTSTRAP","status":"INTERFACE_INVENTORY_ONLY",
        "seed_candidates":[0,4],"kernel_rank2_hypothesis":"NOT_REPLAYED",
        "methods":inventory,"scientific_limit":"No seed0/4 degree4 claims yet."}
open("babel18_bootstrap.json","w").write(json.dumps(result,indent=2,sort_keys=True)+"\n")
