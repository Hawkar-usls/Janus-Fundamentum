import ast, zipfile, pathlib
root=pathlib.Path("experiments")
for z in [root/"babel14/BABEL14_SEED2_COMPACT_PROOF_BUNDLE_20261020.zip",root/"babel15/BABEL15_SEED1_COMPACT_PROOF_BUNDLE_20261020.zip",root/"babel16/BABEL16_SEED3_CANONICAL_TRANSFER_BARRIER_20261020.zip"]:
    with zipfile.ZipFile(z) as f:
        print("ARCHIVE", z, flush=True)
        for m in f.infolist():
            if m.filename.endswith('.py'): print("FILE",m.filename,m.file_size)
            if m.filename.endswith('.json') and m.file_size<10000: print("JSON",m.filename,m.file_size)
for z,fn in [(root/"babel15/BABEL15_SEED1_COMPACT_PROOF_BUNDLE_20261020.zip","janus_babel15_seed1_transfer.py"),(root/"babel15/BABEL15_SEED1_COMPACT_PROOF_BUNDLE_20261020.zip","janus_babel15_seed1_expand_exact.py"),(root/"babel16/BABEL16_SEED3_CANONICAL_TRANSFER_BARRIER_20261020.zip","janus_babel16_seed3_exact_pair_kernel.py"),(root/"babel16/BABEL16_SEED3_CANONICAL_TRANSFER_BARRIER_20261020.zip","janus_babel16_seed3_source_residual.py")]:
    with zipfile.ZipFile(z) as f: src=f.read(fn).decode()
    tree=ast.parse(src)
    print("\nSOURCE",fn,"LINES",len(src.splitlines()),flush=True)
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)):
            print(node.lineno,ast.unparse(node.args) if isinstance(node,ast.FunctionDef) else "CLASS",node.name,"END",node.end_lineno,flush=True)
        elif isinstance(node,(ast.Assign,ast.AnnAssign)):
            line=ast.get_source_segment(src,node).splitlines()[0]
            print("CONST",node.lineno,line[:120],flush=True)
