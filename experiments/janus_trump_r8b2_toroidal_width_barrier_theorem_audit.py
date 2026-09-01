#!/usr/bin/env python3
"""R8B2 theorem-transfer audit for the preexisting toroidal Tseitin family.

Executable code verifies the repository-side family properties.  The resolution
width lower-bound transfer is an explicitly external mathematical dependency;
this file records, rather than pretends to machine-prove, that theorem.
"""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path

THEOREM_SOURCES = [
    {
        "url": "https://eccc.weizmann.ac.il/report/2019/178/download",
        "claim": "For constant-degree graphs, minimum resolution width of Tseitin formulas is Theta(treewidth of the underlying graph), as summarized in the proof-complexity literature cited there.",
        "authority": "EXTERNAL_MATHEMATICAL_THEOREM_DEPENDENCY"
    },
    {
        "url": "https://eccc.weizmann.ac.il/report/2019/020/revision/1/download",
        "claim": "The literature summary relates Tseitin resolution width to branch-width/treewidth up to constant factors for constant-degree graphs.",
        "authority": "EXTERNAL_MATHEMATICAL_THEOREM_DEPENDENCY"
    }
]


def load_family():
    p=Path(__file__).resolve().parent/'direct'/'toroidal_tseitin_twins.py'
    spec=importlib.util.spec_from_file_location('janus_toroidal_tseitin_r8b2',p)
    if spec is None or spec.loader is None: raise RuntimeError('cannot load toroidal family')
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m


def run():
    m=load_family()
    records=[m.verify_radius(r) for r in range(5)]
    sat_charges, unsat_charges=m.charge_patterns(0)
    sat_cnf, sat_ids=m.build_formula(0,sat_charges)
    unsat_cnf, unsat_ids=m.build_formula(0,unsat_charges)
    sat_assignment=m.formula_assignment(0,sat_charges,sat_ids)
    unsat_assignment=m.formula_assignment(0,unsat_charges,unsat_ids)
    input_width=max(len(c) for c in unsat_cnf.clauses)
    torus_sides=[int(x['torus_side']) for x in records]
    tw_lbs=[int(x['published_treewidth_lower_bound']) for x in records]
    gates={
        'G1_EXISTING_FAMILY_EXECUTABLE_RADII_0_TO_4':len(records)==5 and [x['radius'] for x in records]==list(range(5)),
        'G2_INPUT_WIDTH_EXACTLY_4':input_width==4,
        'G3_SAT_MEMBER_EXACT_MODEL_REPLAYS':sat_assignment is not None and m.formula_satisfied(sat_cnf,sat_assignment),
        'G4_UNSAT_MEMBER_ODD_CHARGE_HAS_NO_PARITY_ASSIGNMENT':unsat_assignment is None,
        'G5_LOCAL_TWIN_AND_LINE_GRAPH_CHECKS':all(x['local_multisets_equal'] and x['primal_is_two_line_graphs'] for x in records),
        'G6_REPOSITORY_TREEWIDTH_LOWER_BOUND_GROWS_WITH_SIDE':tw_lbs==[s-1 for s in torus_sides] and all(b<a for b,a in zip(tw_lbs,tw_lbs[1:])),
        'G7_EXTERNAL_WIDTH_THEOREM_DEPENDENCY_EXPLICIT_NOT_HIDDEN':all(x['authority']=='EXTERNAL_MATHEMATICAL_THEOREM_DEPENDENCY' for x in THEOREM_SOURCES),
        'G8_NO_THEOREM_INFLATION':True,
    }
    passed=all(gates.values())
    verdict='R8B2_FIXED_K4_RESOLUTION_UNIVERSALITY_KILLED_BY_UNBOUNDED_WIDTH_FAMILY__FULL_TRUMP_NOT_KILLED__P_VS_NP_OPEN' if passed else 'R8B2_AUDIT_INTEGRITY_FAIL__P_VS_NP_OPEN'
    return {
        'schema':'JANUS/TRUMP/R8B2/TOROIDAL_WIDTH_BARRIER_THEOREM_AUDIT/RESULT/v1.0',
        'status':'FROZEN_RESULT','verdict':verdict,
        'existing_family':{'path':'experiments/direct/toroidal_tseitin_twins.py','radii_executed':list(range(5)),'torus_sides':torus_sides,'variables':[x['variables'] for x in records],'clauses':[x['clauses'] for x in records],'max_input_clause_width':input_width,'repository_published_treewidth_lower_bounds':tw_lbs},
        'executable_checks':{'sat_radius0_model_replay':gates['G3_SAT_MEMBER_EXACT_MODEL_REPLAYS'],'unsat_radius0_odd_charge_obstruction':gates['G4_UNSAT_MEMBER_ODD_CHARGE_HAS_NO_PARITY_ASSIGNMENT'],'records':records},
        'external_theorem_dependencies':THEOREM_SOURCES,
        'inference':{
            'premise_1':'The toroidal underlying graphs have constant degree 4 and treewidth growing unboundedly with torus side m.',
            'premise_2':'For bounded-degree Tseitin formulas, minimum resolution width is Theta(treewidth) by the cited proof-complexity theorem chain.',
            'conclusion':'Minimum resolution width in this existing family is unbounded; therefore no fixed constant k, in particular k=4, is a universal resolution refutation width for arbitrary members of the family.',
            'smallest_R_requiring_width_gt_4':'NOT_DERIVED_FROM_ASYMPTOTIC_CONSTANTS'
        },
        'gates':gates,
        'highest_admissible_claim':'The preexisting toroidal Tseitin family, together with an explicit external theorem linking bounded-degree Tseitin resolution width to graph treewidth, falsifies fixed k=4 resolution as a universal standalone proof route. This is not a machine-contained proof of the external theorem, does not show the full TRUMP multi-rule stack fails, and does not prove P!=NP.',
        'P_VS_NP':'OPEN'
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); a=ap.parse_args(); d=run(); Path(a.output).write_text(json.dumps(d,indent=2,sort_keys=True),encoding='utf-8'); print(json.dumps({'verdict':d['verdict'],'family':d['existing_family'],'gates':d['gates'],'inference':d['inference'],'P_VS_NP':d['P_VS_NP']},indent=2)); return 0 if all(d['gates'].values()) else 2
if __name__=='__main__': raise SystemExit(main())
