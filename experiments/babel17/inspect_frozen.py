import zipfile
archives={"15":"experiments/babel15/BABEL15_SEED1_COMPACT_PROOF_BUNDLE_20261020.zip","16":"experiments/babel16/BABEL16_SEED3_CANONICAL_TRANSFER_BARRIER_20261020.zip"}
for key,fn in [("15","janus_babel15_seed1_transfer.py"),("15","janus_babel15_seed1_expand_exact.py"),("16","janus_babel16_seed3_exact_pair_kernel.py"),("16","janus_babel16_seed3_source_residual.py")]:
 with zipfile.ZipFile(archives[key]) as z:
  src=z.read(fn).decode("utf-8")
 print(f"--- BEGIN {fn} ---")
 print(src)
 print(f"--- END {fn} ---")
