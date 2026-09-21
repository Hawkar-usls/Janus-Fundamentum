#!/usr/bin/env python3
"""C5B2 symbolic chord classifier over one B1 covering-grammar cell.

No global grammar materialization.  Unsupported downstream semantics returns
UNKNOWN.  This module is a local rule engine / proof-certificate generator,
not a solver and not a source-realizability oracle.
"""

from dataclasses import asdict
from typing import Dict, Tuple

from research.tools.r5_b1b1c5b1_source_annotated_role_grammar.covering_grammar import (
    Cell, ReprDelta, ExtensionDelta, COLORS,
    adjacency_bit, validate_cell, message_table, mask_colors,
)

SOURCE_FORCED_EDGE="FORCED_EDGE"
SOURCE_FORCED_NONEDGE="FORCED_NONEDGE"
SOURCE_OPTIONAL_LOCAL="OPTIONAL_LOCAL"
SOURCE_INCONSISTENT="INCONSISTENT_CELL"
SOURCE_UNKNOWN="UNKNOWN_GLOBAL_REALIZABILITY"

def bit_for_color(c: int) -> int:
    assert c in COLORS
    return 1 << (c-1)

def mu(table_bits: int, F: int) -> int:
    assert 0 <= F < 16
    return (table_bits >> F) & 1

def b_x0_palette_redundant(*, chi_s: int, chi_x0_without_identity: int, color: int) -> bool:
    return bool((chi_s | chi_x0_without_identity) & bit_for_color(color))

def c_x0_base_redundant(*, chi_x0_without_identity: int, color: int) -> bool:
    return bool(chi_x0_without_identity & bit_for_color(color))

def bb_disjoint_palette(Au: int, Av: int) -> bool:
    return (Au & Av) == 0

def bc_universal_mask_neutral(message_type_id: int, A_b: int) -> Tuple[bool, Dict]:
    """Sufficient exact neutrality certificate.

    Checks mu(F)=mu(F union {alpha}) for all 16 masks F and all alpha in A(b).
    This is stronger than equality only on reachable boundary states, hence
    sound without a reachability enumerator.
    """
    table=message_table(message_type_id)
    checked=[]
    for F in range(16):
        for alpha in mask_colors(A_b):
            G=F | bit_for_color(alpha)
            left=mu(table,F)
            right=mu(table,G)
            checked.append((F,alpha,left,right))
            if left != right:
                return False,{
                    "rule":"B_C_UNIVERSAL_MASK_EQUALITY",
                    "counterexample_abstract_mask":{"F":F,"alpha":alpha,"mu_F":left,"mu_F_union_alpha":right},
                    "warning":"Abstract inequality is NOT a PROVED_NONNEUTRAL witness without legal/source-valid reachability.",
                }
    return True,{
        "rule":"B_C_UNIVERSAL_MASK_EQUALITY",
        "checks":len(checked),
        "message_type_id":message_type_id,
        "A_b":A_b,
    }

def _x0_color_without_identity(cell: Cell, xpos: int, target_pos: int, current_edge: int) -> Tuple[int,bool]:
    """Return fixed color and whether that color remains represented without
    this selected X0 identity at target_pos.

    For an absent pair, the declared mask already describes the without-edge
    state.  For a present pair, the X0 redundancy bit certifies another source
    of the same fixed color at that target (seed handled separately for B).
    """
    x=cell.X0[xpos]
    c=x.fixed_color
    if current_edge:
        redundant=bool((x.redundancy_bits >> target_pos) & 1)
    else:
        if cell.role_order[target_pos]=="B":
            redundant=bool(cell.B[target_pos].chi_x0 & bit_for_color(c))
        elif cell.role_order[target_pos]=="C":
            redundant=bool(cell.C[target_pos].chi_x0_rep & bit_for_color(c))
        else:
            redundant=False
    return c,redundant

def local_source_status(cell: Cell, i: int, j: int) -> str:
    """Sound local source status from annotations represented in B1.

    OPTIONAL_LOCAL is not a global realizability claim.
    """
    if validate_cell(cell):
        return SOURCE_INCONSISTENT
    if i>j:
        i,j=j,i
    ri,rj=cell.role_order[i],cell.role_order[j]

    # Residual Y0 is anticomplete to seed.
    if {ri,rj}=={"S","C"}:
        return SOURCE_FORCED_NONEDGE

    # Different residual connected components are anticomplete.
    if ri=="C" and rj=="C":
        if cell.C[i].component_label != cell.C[j].component_label:
            return SOURCE_FORCED_NONEDGE
        return SOURCE_OPTIONAL_LOCAL

    # Same-colored already-fixed vertices cannot be adjacent.
    if ri in {"S","X0"} and rj in {"S","X0"}:
        ci=cell.S[i].fixed_color if ri=="S" else cell.X0[i].fixed_color
        cj=cell.S[j].fixed_color if rj=="S" else cell.X0[j].fixed_color
        if ci==cj:
            return SOURCE_FORCED_NONEDGE
        return SOURCE_OPTIONAL_LOCAL

    # These are precisely the pair families whose local source legality is
    # represented sufficiently for B2's built-in rules.
    if {ri,rj} in ({"B","B"},{"B","X0"},{"C","X0"},{"B","C"}):
        return SOURCE_OPTIONAL_LOCAL

    # Pairs involving seed/source-type transitions need more global source
    # information before the opposite bit is called realizable.
    return SOURCE_UNKNOWN

def classify(cell: Cell, i: int, j: int) -> Dict:
    errs=validate_cell(cell)
    if errs:
        return {
            "source_status":SOURCE_INCONSISTENT,
            "representation_delta":ReprDelta.SOURCE_ILLEGAL.value,
            "extension_delta":ExtensionDelta.UNKNOWN.value,
            "certificate":{"rule":"B1_CELL_VALIDATION","errors":errs},
        }
    assert 0 <= i < 7 and 0 <= j < 7 and i!=j
    if i>j:
        i,j=j,i
    ri,rj=cell.role_order[i],cell.role_order[j]
    edge=adjacency_bit(cell.adjacency_mask_21,i,j)
    source=local_source_status(cell,i,j)

    # B-X0 exact palette redundancy.
    if {ri,rj}=={"B","X0"}:
        bpos=i if ri=="B" else j
        xpos=i if ri=="X0" else j
        c,redundant_x0=_x0_color_without_identity(cell,xpos,bpos,edge)
        seed_redundant=bool(cell.B[bpos].chi_s & bit_for_color(c))
        neutral=seed_redundant or redundant_x0
        if neutral:
            return {
                "source_status":source,
                "representation_delta":ReprDelta.IDENTITY_ONLY.value,
                "extension_delta":ExtensionDelta.PROVED_NEUTRAL.value,
                "certificate":{
                    "rule":"B_X0_ALREADY_FORBIDDEN_COLOR",
                    "fixed_color":c,
                    "edge_present":edge,
                    "seed_redundant":seed_redundant,
                    "x0_redundant_without_identity":redundant_x0,
                    "proof":"Color c remains forbidden at B without this identity edge, so A(B) and the list-coloring relation are unchanged.",
                },
            }
        return {
            "source_status":source,
            "representation_delta":ReprDelta.EXACT_DYNAMIC_LIST_CHANGE.value,
            "extension_delta":ExtensionDelta.UNKNOWN.value,
            "certificate":{
                "rule":"B_X0_NEW_FORBIDDEN_COLOR",
                "fixed_color":c,
                "edge_present":edge,
                "warning":"Exact list changes; extension effect is not inferred.",
            },
        }

    # C-X0 representative/base-system redundancy.
    if {ri,rj}=={"C","X0"}:
        cpos=i if ri=="C" else j
        xpos=i if ri=="X0" else j
        c,redundant=_x0_color_without_identity(cell,xpos,cpos,edge)
        if redundant:
            return {
                "source_status":source,
                "representation_delta":ReprDelta.IDENTITY_ONLY.value,
                "extension_delta":ExtensionDelta.PROVED_NEUTRAL.value,
                "certificate":{
                    "rule":"C_X0_SAME_COLOR_BASE_REDUNDANCY",
                    "fixed_color":c,
                    "edge_present":edge,
                    "proof":"The same fixed color remains represented at z without this identity, so B_C(z) is unchanged; no other component coordinate is modified by the single identity distinction.",
                },
            }
        return {
            "source_status":source,
            "representation_delta":ReprDelta.COMPONENT_BASE_SYSTEM_CHANGE.value,
            "extension_delta":ExtensionDelta.UNKNOWN.value,
            "certificate":{
                "rule":"C_X0_NEW_BASE_COLOR_EXCLUSION",
                "fixed_color":c,
                "edge_present":edge,
                "warning":"A base-list coordinate changes; mu_C/MIN_BAD/R_C change is not inferred.",
            },
        }

    # B-B tautological adjacency under disjoint exact palettes.
    if ri=="B" and rj=="B":
        neutral=bb_disjoint_palette(cell.B[i].A,cell.B[j].A)
        return {
            "source_status":source,
            "representation_delta":ReprDelta.GRAPH_U_CHANGE.value,
            "extension_delta":(
                ExtensionDelta.PROVED_NEUTRAL.value if neutral
                else ExtensionDelta.UNKNOWN.value
            ),
            "certificate":{
                "rule":"B_B_DISJOINT_EXACT_PALETTES" if neutral else "B_B_OVERLAPPING_PALETTES",
                "A_i":cell.B[i].A,
                "A_j":cell.B[j].A,
                "proof":(
                    "Every list-respecting coloring already assigns different colors, so adjacency is tautological."
                    if neutral else
                    "Palette overlap alone does not prove that adjacency is extension-relevant."
                ),
            },
        }

    # B-C source-consistent complete/anticomplete distinction.
    if {ri,rj}=={"B","C"}:
        bpos=i if ri=="B" else j
        cpos=i if ri=="C" else j
        m=cell.C[cpos].message_type_id
        neutral,cert=bc_universal_mask_neutral(m,cell.B[bpos].A)
        return {
            "source_status":source,
            "representation_delta":ReprDelta.D_C_CHANGE.value,
            "extension_delta":(
                ExtensionDelta.PROVED_NEUTRAL.value if neutral
                else ExtensionDelta.UNKNOWN.value
            ),
            "certificate":{
                **cert,
                "edge_present":edge,
                "component_label":cell.C[cpos].component_label,
                "proof":(
                    "Universal mask equality implies R_C is invariant under adding/removing B from D_C for every legal boundary coloring."
                    if neutral else
                    "The universal sufficient certificate fails. No nonneutrality is inferred without a legal/source-valid distinguishing coloring."
                ),
            },
        }

    # Inherited trivial fixed-X0 internal neutrality for differently colored
    # fixed vertices; same color is source-forbidden by proper precoloring.
    if ri=="X0" and rj=="X0":
        ci,cj=cell.X0[i].fixed_color,cell.X0[j].fixed_color
        if ci==cj:
            return {
                "source_status":SOURCE_FORCED_NONEDGE,
                "representation_delta":ReprDelta.SOURCE_ILLEGAL.value,
                "extension_delta":ExtensionDelta.UNKNOWN.value,
                "certificate":{"rule":"SAME_COLOR_FIXED_X0_EDGE_FORBIDDEN"},
            }
        return {
            "source_status":source,
            "representation_delta":ReprDelta.IDENTITY_ONLY.value,
            "extension_delta":ExtensionDelta.PROVED_NEUTRAL.value,
            "certificate":{
                "rule":"DIFFERENT_COLOR_FIXED_X0_INTERNAL_EDGE",
                "proof":"Both endpoints are already fixed to different colors; their mutual edge/nonedge does not alter any extension constraint on unfixed vertices.",
            },
        }

    # Everything else is total but conservative.
    return {
        "source_status":source,
        "representation_delta":ReprDelta.NONE.value,
        "extension_delta":ExtensionDelta.UNKNOWN.value,
        "certificate":{
            "rule":"UNSUPPORTED_PAIR_CLASS",
            "roles":[ri,rj],
            "edge_present":edge,
            "warning":"No exact B2 neutrality/nonneutrality theorem for this pair class.",
        },
    }

def finite_rule_replay() -> Dict:
    """Replay finite semantic helpers without enumerating grammar cells."""
    # B-X0: seed redundancy is sufficient even with no X0 redundancy.
    assert b_x0_palette_redundant(chi_s=bit_for_color(2),chi_x0_without_identity=0,color=2)
    assert not b_x0_palette_redundant(chi_s=0,chi_x0_without_identity=0,color=2)

    # C-X0 identity redundancy.
    assert c_x0_base_redundant(chi_x0_without_identity=bit_for_color(4),color=4)
    assert not c_x0_base_redundant(chi_x0_without_identity=0,color=4)

    # B-B disjoint palette criterion.
    assert bb_disjoint_palette(bit_for_color(1),bit_for_color(2))
    assert not bb_disjoint_palette(bit_for_color(1)|bit_for_color(2),bit_for_color(2))

    # Exhaust all 168 message types x 16 exact dynamic palettes.
    neutral_pairs=0
    unknown_pairs=0
    for mid in range(168):
        for A in range(16):
            ok,_=bc_universal_mask_neutral(mid,A)
            if ok:
                neutral_pairs+=1
            else:
                unknown_pairs+=1
    assert neutral_pairs + unknown_pairs == 168*16

    return {
        "status":"PASS_FINITE_RULE_REPLAY",
        "message_types_checked":168,
        "dynamic_palette_masks_checked_per_message":16,
        "B_C_rule_cases":168*16,
        "B_C_universal_neutral_cases":neutral_pairs,
        "B_C_unresolved_cases":unknown_pairs,
        "global_grammar_materialized":False,
    }

if __name__=="__main__":
    print(finite_rule_replay())
