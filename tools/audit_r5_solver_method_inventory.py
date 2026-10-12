#!/usr/bin/env python3
"""Reproducible exhaustive repository FILE/FOLDER and method-provenance audit.

Source scanner: every tracked source entry obtainable by git ls-files,
plus all git-tracked parent folder prefixes. Generated artifacts under
'audits/r5_repository_inventory/' are excluded to avoid self-reference
and nondeterministic counts. No external internet/dependencies.

Machine-readable output is an INVENTORY and static import/workflow graph,
NOT a claim that 100% of research claims were manually code-reviewed.
Name/AST/document searches are discovery only, not semantic verification.
No source files are deleted or renamed.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/'audits'/'r5_repository_inventory'
EXCLUDED_PREFIX='audits/r5_repository_inventory/'
ROLE_DECISIONS={
 'experiments/r5_universal_certified_expert_portfolio.py':('INTEGRATED','CERTIFIED','main cooperative router'),
 'experiments/r5_universal_certified_shared_proof_state.py':('INTEGRATED','CERTIFIED','shared no-good+GF2+ANDOR provenance ledger'),
 'experiments/r5_universal_exact_support_hybrid_algebraic_dag.py':('INTEGRATED','EXACT_GUARDED','root algebra + exact bounded DAG'),
 'experiments/r5_universal_exact_support_residual_dag_attack.py':('INTEGRATED','EXACT_GUARDED','source validation, pins, residual DAG'),
 'experiments/r5_universal_exact_support_unsat_andor_certificate.py':('INTEGRATED','EXACT_PROOF','complete fallback/independent replay'),
 'experiments/r5_universal_boolean_pc_degree3_global_attack.py':('INTEGRATED','POLY_SOUND_UNSAT','degree3 GF2 PC refuter, not complete'),
 'experiments/r5_universal_exact_support_mod9_dual_certificate.py':('INTEGRATED_TRANSITIVE','POLY_SOUND_UNSAT','called by ExactSupportHybrid; its negative certificate now lifted to main router and replayed'),
 'experiments/r5_universal_exact_support_pinned_oracle_attack.py':('INTEGRATED_TRANSITIVE','EXACT_EXPONENTIAL','ExactSupportHybrid root calls this old pinned solver; do not duplicate'),
 'experiments/r5_universal_quadratic_gauss_mod4_attack.py':('INTEGRATED_TRANSITIVE','POLY_SOUND_UNSAT','ExactSupport root imports modular Gauss filter; independently check boundary'),
 'experiments/r5_universal_cubic_three_edge_cut_factorization.py':('ADAPTER_PRECONDITION','CUBIC_GRAPH_ONLY','3-edge cut factor + witness gluing'),
 'experiments/r5_universal_cubic_nondegenerate_threecut_recognizer.py':('ADAPTER_PRECONDITION','CUBIC_GRAPH_ONLY','polynomial 3-cut finder'),
 'experiments/r5_universal_cubic_four_cut_21_state_interface.py':('ADAPTER_PRECONDITION','CUBIC_GRAPH_ONLY','four-edge cut signature 21 states'),
 'experiments/r5_universal_cubic_edgecolor_direct_scl_bridge.py':('ADAPTER_PRECONDITION','GADGET_MAP','graph-SCL witness preserving map'),
 'experiments/r5_e108_normal_span_quotient_solver.py':('REVIEW_CONDITIONAL','FPT_BY_RANK','2^rank quotient; not all-input poly'),
 'experiments/r5_e109_normal_matroid_component_decomposition.py':('REVIEW_CONDITIONAL','FPT_BY_COMPONENT','sum 2^component rank; not universal'),
 'experiments/r5_e78_linear_delta_equality_gluing_meta_solver.py':('REVIEW_CONDITIONAL','REPRESENTABILITY_PRECONDITION','delta gluing; need poly construction and exact boundary signatures'),
 'experiments/r5_e119_perfect_conflict_graph_global_terminal.py':('REVIEW_CONDITIONAL','PERFECT_GRAPH_PRECONDITION','MIS terminal only on certified perfect graph'),
 'experiments/r5_parity_fixed_m_hall_tight_dm_trade.py':('REVIEW_CONDITIONAL','FIXED_MATCHING_PRECONDITION','Hall/Dulmage Mendelsohn trade feature'),
 'experiments/r5_parity_fixed_m_trade_span_normal_form.py':('REVIEW_CONDITIONAL','FIXED_MATCHING_PRECONDITION','trade circuit evidence; non-TU firewall'),
 'experiments/direct/janus_tear_policy0a_fc_proof_system.py':('REVIEW_CONDITIONAL','CNF_OTHER_INPUT','FC residual judgements, requires verified SCL/CNF adapter'),
 'experiments/v2.0-selective-distributed/src/solvers.py':('OPTIONAL_SAT_SEARCH','HEURISTIC_SAT_ONLY','WalkSAT/Junction hints never UNSAT proof'),
 'tools/OdontoForge_PNP_EXP.py':('OPTIONAL_SAT_SEARCH','EXACT_CNF_EXTERNAL_ADAPTER','exact CNF branch search, guard UNKNOWN; no general poly'),
 'experiments/r5_universal_pfaffian_cube_k33_cancellation.py':('NEGATIVE_CONTROL','REFUTED_NAIVE_PFAFFIAN','SAT false zero due sign cancellation'),
 'experiments/r5_universal_modular_flow_count_all_q_no_go.py':('NEGATIVE_CONTROL','REFUTED_FIXED_MODULAR_NONZERO','SAT false zero mod arbitrary fixed q'),
 'experiments/r5_universal_kettani_2025_toroidal_treewidth_counterexample.py':('NEGATIVE_CONTROL','REFUTED_TW_SHORTCUT','unbounded treewidth blocks naive bounded-width generality'),
 'experiments/r5_universal_exact_support_exponential_reachable_residual_firewall.py':('NEGATIVE_CONTROL','EXACT_SUPPORT_EXPONENTIAL_STATE_FAMILY','forbid claim state count always polynomial'),
}
TOP_ROLES={
 '.github':'CI_GOVERNANCE','research':'SCIENTIFIC_ARGUMENT_EVIDENCE',
 'experiments':'RUNNABLE_EXPERIMENTS_AND_FIXTURES',
 'registry':'FROZEN_PROVENANCE_JSON','docs':'PUBLIC_SCIENTIFIC_DOCUMENTATION',
 'proof_attempts':'LEGACY_PROOF_ATTEMPTS','tools':'GENERAL_TOOLING',
 'archive':'ARCHIVED_CONTROLS','proposals':'PROPOSALS_UNADMITTED',
 'reviews':'REVIEW_RECORDS','.janus':'AGENT_POLICY'
}
RISK_HINTS={
 'EXPONENTIAL':['exponential','2^n','3^n','unbounded branching','full enumeration'],
 'CONDITIONAL':['under assumptions','if representable','bounded rank','bounded width','subclass'],
 'NONPROOF':['heuristic','empirical','random','finite experiment'],
}
def tracked_paths():
    proc=subprocess.run(['git','-C',str(ROOT),'ls-files','-z'],
        check=True,stdout=subprocess.PIPE)
    return sorted(p.decode('utf8') for p in proc.stdout.split(b'\0')
                  if p and not p.decode('utf8').startswith(EXCLUDED_PREFIX))

def sha256(data):return hashlib.sha256(data).hexdigest()

def code_profile(path,data):
    raw=data.decode('utf-8-sig','replace')
    profile={'syntax':'NOT_PYTHON','functions':[],'classes':[],
             'local_imports':[],'other_imports':[],'static_file_mentions':[],
             'docstring':'','parse_error':None}
    if not path.endswith('.py'):return profile
    try:
        astree=ast.parse(raw,filename=path)
    except SyntaxError as e:
        profile['syntax']='SYNTAX_ERROR'
        profile['parse_error']=f'{e.lineno}:{e.offset} {e.msg}'
        return profile
    profile['syntax']='PARSED'
    profile['functions']=[node.name for node in astree.body
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))]
    profile['classes']=[node.name for node in astree.body
        if isinstance(node,ast.ClassDef)]
    doc=ast.get_docstring(astree) or ''
    profile['docstring']=doc[:440]
    imports=[]
    for node in ast.walk(astree):
        if isinstance(node,ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node,ast.ImportFrom):
            imports.append('.'*node.level+(node.module or ''))
    profile['local_imports']=sorted(set(m for m in imports
        if m.startswith(('r5_','janus_','apma_','sat_core','tools.'))))
    profile['other_imports']=sorted(set(imports)-set(profile['local_imports']))
    return profile

def classify(path):
    if path in ROLE_DECISIONS:
        role,authority,why=ROLE_DECISIONS[path]
        return {'integration_role':role,'claim_ceiling':authority,
                'classification_basis':'MANUALLY_REVIEWED_ENTRYPOINT',
                'rationale':why}
    top=path.split('/')[0]
    if path.endswith('.py'):
        if path.startswith('research/tools/apma_'):
            role='SEPARATE_APMA_TRACK_ADAPTER_NEEDED'
        elif path.startswith('experiments/direct/'):
            role='CNF_FORMULA_CACHING_OR_PROOF_CONTROL'
        elif '/src/' in path or path.startswith('experiments/v'):
            role='LEGACY_OR_HEURISTIC_CONTROL'
        elif path.startswith('experiments/r5_'):
            role='R5_METHOD_REVIEW_QUEUE'
        elif path.startswith('tools/'):
            role='TOOL_REVIEW_QUEUE'
        else:
            role='CODE_REVIEW_QUEUE'
        return {'integration_role':role,'claim_ceiling':'UNVERIFIED_FOR_GLOBAL_SOLVER',
                'classification_basis':'PATH_HEURISTIC_ONLY',
                'rationale':'must review preconditions, semantic adapter, certificate and runtime'}
    if path.endswith('.yml') or path.endswith('.yaml'):
        role='CI_WORKFLOW'
    elif path.endswith('.json'):
        role='PROVENANCE_OR_DATA'
    elif path.endswith('.md'):
        role='SCIENTIFIC_NOTE_OR_DOC'
    elif path.endswith('.csv'):
        role='BENCHMARK_DATA'
    else:role='OTHER_SOURCE'
    return {'integration_role':role,'claim_ceiling':'NOT_SOLVER_IMPLEMENTATION',
            'classification_basis':'EXTENSION_PATH_ONLY','rationale':TOP_ROLES.get(top,'auxiliary')}

def build():
    paths=tracked_paths()
    files=[]; folders=defaultdict(lambda:{'files':0,'bytes':0,'python':0,
                     'json':0,'markdown':0,'workflows':0,'top_role':None})
    python_profiles={}
    source_text={}
    for path in paths:
        full=ROOT/path
        if not full.is_file():
            continue
        data=full.read_bytes()
        role=classify(path)
        pr=code_profile(path,data)
        if path.endswith('.py'):python_profiles[path]=pr
        text=data.decode('utf-8-sig','replace')
        source_text[path]=text if (
            path.endswith(('.py','.yml','.yaml','.md','.json'))
            and len(data)<=350000
        ) else ''
        files.append({'path':path,'bytes':len(data),'sha256':sha256(data),
             'extension':Path(path).suffix,'python':pr,
             **role})
        parts=path.split('/')
        for i in range(1,len(parts)):
            folder='/'.join(parts[:i])
            f=folders[folder];f['files']+=1;f['bytes']+=len(data)
            f['python']+=path.endswith('.py')
            f['json']+=path.endswith('.json')
            f['markdown']+=path.endswith('.md')
            f['workflows']+=(folder=='.github/workflows')
            f['top_role']=TOP_ROLES.get(parts[0],'OTHER')
    file_paths={x['path'] for x in files}
    python_paths={p for p in python_profiles}
    names=defaultdict(list)
    for p in python_paths:
        names[Path(p).stem].append(p)
    static_import_edges=[]
    missing_local=[]
    for f in files:
        p=f['path']
        if not p.endswith('.py'):continue
        for imp in f['python']['local_imports']:
            root=imp.lstrip('.').split('.')[0]
            matches=names.get(root,[])
            for dest in matches:
                static_import_edges.append([p,dest])
            if not matches:
                missing_local.append({'source':p,'import':imp})
    refs=defaultdict(list)
    workflows=[p for p in file_paths if p.startswith('.github/workflows/') and p.endswith(('.yml','.yaml'))]
    for w in workflows:
        text=source_text[w]
        for p in python_paths:
            if p in text or (len(names[Path(p).stem])==1 and
                 re.search(r'(?<![A-Za-z0-9_])'+re.escape(Path(p).name)+r'(?![A-Za-z0-9_])',text)):
                refs[p].append(w)
    imports_to=defaultdict(set)
    for src,dst in static_import_edges:
        imports_to[dst].add(src)
    for f in files:
        if f['path'].endswith('.py'):
            f['python']['static_importers']=len(imports_to[f['path']])
            f['python']['workflow_mentions']=sorted(set(refs[f['path']]))
    role_counts=Counter(f['integration_role'] for f in files)
    syntax_failures=[f['path'] for f in files if f['python']['syntax']=='SYNTAX_ERROR']
    unmatched_workflows=[w for w in workflows if not any(w in v for v in refs.values())]
    summary={
      'schema':'JANUS-R5-ALL-REPO-SOURCE-INVENTORY-v1',
      'source_commit':subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],
          check=True,capture_output=True,text=True).stdout.strip(),
      'files_scanned':len(files),
      'folders_scanned':len(folders),
      'bytes_scanned':sum(f['bytes'] for f in files),
      'by_extension':dict(sorted(Counter(f['extension'] for f in files).items())),
      'by_top':dict(sorted(Counter(p['path'].split('/')[0] for p in files).items())),
      'role_counts':dict(sorted(role_counts.items())),
      'reviewed_entrypoint_count':sum(f['classification_basis']=='MANUALLY_REVIEWED_ENTRYPOINT' for f in files),
      'python_import_edges':len(static_import_edges),
      'python_parsed':sum(f['python']['syntax']=='PARSED' for f in files),
      'python_syntax_failures':syntax_failures,
      'workflow_count':len(workflows),
      'unmatched_workflow_count':len(unmatched_workflows),
      'unresolved_local_imports':missing_local,
      'status':'INVENTORY_COMPLETE__SEMANTIC_REVIEW_PARTIAL__UNIVERSAL_COVERAGE_OPEN',
      'scientific_ceiling':'P_VS_NP_OPEN__SolveLinearCubicXSAT_NOT_CONSTRUCTED'
    }
    return summary,files,folders,static_import_edges

def write_summary(summary,files,folders,edges):
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'source_manifest.json').write_text(json.dumps({
       'summary':summary,'files':files,
       'folders':dict(sorted(folders.items())),
       'static_local_import_edges':sorted(edges)
    },sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    with (DEST/'review_queue.tsv').open('w',newline='',encoding='utf8') as h:
        w=csv.writer(h,delimiter='\t')
        w.writerow(['path','integration_role','claim_ceiling','basis',
                    'syntax','static_importers','workflow_mentions','bytes'])
        for f in files:
            p=f['python']
            w.writerow([f['path'],f['integration_role'],f['claim_ceiling'],
                        f['classification_basis'],p['syntax'],
                        p.get('static_importers',0),
                        ';'.join(p.get('workflow_mentions',[])),f['bytes']])
    lines=[
      '# JANUS R5 — complete tree inventory and provisional solver-method routing',
      '',
      '> Fully enumerated git-tracked source tree. Path/AST-level complete;',
      '> mathematical semantic verification limited to explicitly reviewed entrypoints.',
      '> Code is NOT assumed unused merely because it has no static importer.',
      '',
      f'Frozen source commit: `{summary["source_commit"]}`.',
      f'Tracked files scanned: **{summary["files_scanned"]}**.',
      f'Tracked folders represented: **{summary["folders_scanned"]}**.',
      f'Bytes scanned: **{summary["bytes_scanned"]}**.',
      f'Python modules parsed: **{summary["python_parsed"]}**.',
      f'Python parse errors: **{len(summary["python_syntax_failures"])}**.',
      f'Static local import edges: **{summary["python_import_edges"]}**.',
      f'Workflows: **{summary["workflow_count"]}**.',
      '',
      '## Every top-level subtree',
      '',
      '| Subtree | Tracked files | Role |',
      '|---|---:|---|',
    ]
    for top,n in sorted(summary['by_top'].items()):
        lines.append(f'| `{top}` | {n} | {TOP_ROLES.get(top,"source/root metadata")} |')
    lines += ['', '## Full role classification (discovery, NOT mathematical authority)',
              '', '| Category | Files |', '|---|---:|']
    for role,n in sorted(summary['role_counts'].items()):
        lines.append(f'| `{role}` | {n} |')
    lines += [
      '', '## High-value method audit (manually scoped first-pass)',
      '', '| Method file | Proposed integration role | Current claim ceiling |',
      '|---|---|---|',
    ]
    for p,(role,ceiling,note) in sorted(ROLE_DECISIONS.items()):
        if p in {f['path'] for f in files}:
            lines.append(f'| `{p}` | {role} | {ceiling} — {note} |')
        else:
            lines.append(f'| `{p}` | MISSING PATH AT SOURCE HEAD | FAIL-CLOSED, no import |')
    lines += [
      '', '## Review and integration rules',
      '',
      '1. **Keep:** original source validators, exact support, proof replay, PC3, mod9, and their independently checked SAT/UNSAT gates. Do not duplicate calls already integrated transitively; surface their proof objects in the common router.',
      '2. **Adapter required:** representation-specific 3/4-cut, rank-FPT, perfect graph, matroid/delta, and formula-cache methods, only after exact bidirectional semantics and input preconditions are proved.',
      '3. **Shadow only:** heuristic search, learned routing, old benchmark witnesses. They can suggest or find SAT assignments, but cannot certify UNSAT from timeout or silence.',
      '4. **Negative firewall:** preserve counterexamples to Pfaffian cancellation, fixed modulus, bounded width and exponential-state shortcuts; NEVER import as positive solver passes.',
      '5. **Do not delete:** automatically unreferenced does NOT mean scientifically unused; archived experiments/registry proofs remain provenance.',
      '6. **Global requirement:** show ALL legal SCL inputs receive certified SAT witness or UNSAT within ONE n^O(1) bit bound; finite method coverage, imports, successful CI and polynomial knowledge vocabulary do not prove this.',
      '',
      '## Next source-aligned global coverage gate',
      '',
      '`UNION_POLY_EXPERTS_COVERS_ALL_LEGAL_SCL` = **NOT PROVED**.',
      '`COMPLETE_DAG_FALLBACK_STATES_POLY_BOUNDED_AFTER_SHARED_CLOSURE` = **NOT PROVED**.',
      '`UNIVERSAL_POLY_SolveLinearCubicXSAT` = **NOT CONSTRUCTED**.',
      '`P_VS_NP` = **OPEN**.',
      '',
      'Machine-readable exhaustive file+folder map:',
      '`audits/r5_repository_inventory/source_manifest.json`.',
      'Tabular row-by-row review queue:',
      '`audits/r5_repository_inventory/review_queue.tsv`.',
      '',
      'Generated files are omitted from the self-referential enumeration by design;',
      'the scanner scans every other git-tracked file at the frozen source commit.',
    ]
    (DEST/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')

def main():
    summary,files,folders,edges=build()
    write_summary(summary,files,folders,edges)
    assert summary['files_scanned']>=1200,summary
    assert summary['python_parsed']>=350,summary
    assert len(summary['python_syntax_failures'])==0,summary['python_syntax_failures'][:15]
    assert summary['reviewed_entrypoint_count']>=20
    print('JANUS_REPO_ALL_FOLDER_INVENTORY = COMPLETE')
    print('JANUS_REPO_STATIC_IMPORT_GRAPH = COMPLETE_WITH_KNOWN_LIMITATIONS')
    print('JANUS_REPO_AUDIT_SOURCE='+summary['source_commit'])
    print('JANUS_REPO_SUMMARY='+json.dumps({
        k:summary[k] for k in ('files_scanned','folders_scanned',
        'bytes_scanned','python_parsed','python_import_edges',
        'workflow_count','reviewed_entrypoint_count','by_top')
    },sort_keys=True))
    print('UNIVERSAL_SOLVER_POLY_COVERAGE = NOT_PROVED')
    print('P_VS_NP = OPEN')

if __name__=='__main__':
    main()
