#!/usr/bin/env python3
"""BABEL-17: exact seed3 anti-sector transfer scheme, contingent on source syzygies."""
import json,hashlib
from pathlib import Path
from janus_babel14_antisector_augmented import prepare,extra_generators
from janus_babel14_exact_transfer import signed_forest
from janus_babel15_sector_quotient import forced_source_zero_coordinates
from janus_babel15_seed1_transfer import choose_eight, exact_determinant
from janus_babel6_transfer import signed_graph

def run():
    source,lift,labels,Q,e,canonical,touched,active,missing=prepare(3)
    signatures,supports,singleton,processed=extra_generators(source,lift,labels,Q,e,canonical,missing)
    forced,_=forced_source_zero_coordinates(source,lift,labels,Q,canonical,missing)
    union=json.loads(Path("babel17_SEED3_COMBINED_COMPATIBILITY.json").read_text())
    assert union["target_in_exact_span"] and union["rank_exact"]==6
    invisible=union["seven_invisible_frequencies"]
    nonzero=[w for w in union["basis"] if w["exact_coefficient"] not in (None,"0")]
    assert len(nonzero)==4
    singles={missing[j] for j in singleton}
    assert not singles & forced and not singles & set(invisible) and not forced & set(invisible)
    rest=[q for q in missing if q not in forced and q not in singles and q not in invisible]
    selected,matrix=choose_eight(signatures,missing,rest)
    det=exact_determinant(matrix)
    print("SEED3_SECTOR",len(missing),"forced",len(forced),"singletons",len(singleton),"invisible",len(invisible),"coupled",len(rest),flush=True)
    print("SEED3_COUPLED_MATRIX_DIM",len(matrix),"determinant",det,"selected",len(selected),flush=True)
    _,_,edges=signed_graph(source,lift,labels,e)
    forest,chords,roots=signed_forest(edges,Q,labels,canonical,touched)
    print("SEED3_FOREST",len(forest),"CHORDS",len(chords),"ROOTS",len(roots),flush=True)
    frozen=Path("babel9_BALANCED_BIT68_DEGREE4_KRYLOV.json")
    record={
      "format":"JANUS_BABEL17_SEED3_FULL_TRANSFER_SCHEME_CANDIDATE",
      "seed":3,"source":"SCL126_flip68","source_krylov_sha256":hashlib.sha256(frozen.read_bytes()).hexdigest(),
      "extra_character":e,"multiplier_degree_bound":2,
      "canonical_active_degree3_frequencies":len(active),
      "touched_signed_graph_frequencies":len(touched),
      "missing_graph_frequencies":len(missing),
      "base_forced_zero_frequencies":sorted(forced),
      "source_syzygy_witnesses":nonzero,
      "paired_invisible_frequencies":invisible,
      "singleton_witnesses":[{"frequency":missing[j],"row":r,"multiplier":u,"signed_coefficient":s}
                             for j,(r,u,s) in sorted(singleton.items())],
      "coupled_residual_frequencies":rest,"coupled_generators":selected,
      "coupled_matrix_rows_by_frequencies_columns_by_generators":matrix,
      "coupled_determinant_integer":det,
      "graph_spanning_forest_edges":forest,"graph_frustrating_chords":chords,"graph_roots":roots,
      "status":"CANDIDATE_REQUIRES_COMPLETE_COEFFICIENT_EXPANSION",
      "scientific_limit":"Fourier degree-2 linear multipliers on one legal frozen seed only."
    }
    Path("babel17_SEED3_TRANSFER_SCHEME.json").write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    return record
if __name__=="__main__":run()
