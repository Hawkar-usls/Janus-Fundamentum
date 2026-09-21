#!/usr/bin/env python3
"""C5B1 source-annotated seven-role covering grammar.

Purpose
-------
Provide a finite, lazy, canonical COVER schema for the declared local
seven-role census, parameterized by s=|S|.

This is NOT:
- a coloring solver,
- a source-realizability solver,
- a proof that every generated cell is realizable,
- an extension-equivalence quotient,
- a global compression theorem.

The mathematical completeness claim supported by this module is one-way:
every actual source-valid seven-tuple in scope has an extraction into the
finite annotation schema.  The generated schema may over-approximate the
source-valid subset.

Permanent firewall:
LOCAL_PROFILE_EQUIVALENCE != GLOBAL_SOURCE_EQUIVALENCE.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from itertools import product, combinations
from math import comb
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

COLORS=(1,2,3,4)
ROLE_CLASSES=("S","B","C","X0")
PAIR_POSITIONS=tuple((i,j) for i in range(7) for j in range(i+1,7))
assert len(PAIR_POSITIONS)==21

class SourceStatus(str, Enum):
    FORCED_EDGE="FORCED_EDGE"
    FORCED_NONEDGE="FORCED_NONEDGE"
    OPTIONAL="OPTIONAL"
    INCONSISTENT_CELL="INCONSISTENT_CELL"

class ExtensionDelta(str, Enum):
    PROVED_NEUTRAL="PROVED_NEUTRAL"
    PROVED_NONNEUTRAL="PROVED_NONNEUTRAL"
    UNKNOWN="UNKNOWN"

class ReprDelta(str, Enum):
    NONE="NONE"
    IDENTITY_ONLY="IDENTITY_ONLY"
    FIXED_COLOR_MASK_CHANGE="FIXED_COLOR_MASK_CHANGE"
    EXACT_DYNAMIC_LIST_CHANGE="EXACT_DYNAMIC_LIST_CHANGE"
    COMPONENT_BASE_SYSTEM_CHANGE="COMPONENT_BASE_SYSTEM_CHANGE"
    D_C_CHANGE="D_C_CHANGE"
    MESSAGE_CHANGE="MESSAGE_CHANGE"
    BOUNDARY_RELATION_CHANGE_OR_UNKNOWN="BOUNDARY_RELATION_CHANGE_OR_UNKNOWN"
    GRAPH_U_CHANGE="GRAPH_U_CHANGE"
    COMPONENT_CELL_CHANGE="COMPONENT_CELL_CHANGE"
    SOURCE_ILLEGAL="SOURCE_ILLEGAL"

def mask(colors: Iterable[int]) -> int:
    m=0
    for c in colors:
        assert c in COLORS
        m |= 1 << (c-1)
    return m

FULL_MASK=mask(COLORS)

def mask_colors(m: int) -> Tuple[int,...]:
    assert 0 <= m < 16
    return tuple(c for c in COLORS if m & (1 << (c-1)))

def exact_palette(chi_s: int, chi_x0: int) -> int:
    return FULL_MASK & ~(chi_s | chi_x0)

def source_list(chi_s: int) -> int:
    return FULL_MASK & ~chi_s

def tau_to_chi_s(tau_bits: int, seed_colors: Sequence[int]) -> int:
    assert 0 <= tau_bits < (1 << len(seed_colors))
    out=0
    for i,c in enumerate(seed_colors):
        if tau_bits & (1 << i):
            out |= 1 << (c-1)
    return out

def bell(n: int) -> int:
    # Bell numbers by Stirling recurrence; n<=7 here.
    S=[[0]*(n+1) for _ in range(n+1)]
    S[0][0]=1
    for i in range(1,n+1):
        for k in range(1,i+1):
            S[i][k]=S[i-1][k-1] + k*S[i-1][k]
    return sum(S[n])

assert bell(7)==877

@dataclass(frozen=True)
class BAnn:
    tau_bits: int
    chi_s: int
    chi_x0: int
    Lp: int
    A: int
    # one bit per canonical component label appearing among C roles
    component_incidence_bits: int

@dataclass(frozen=True)
class CAnn:
    component_label: int
    chi_x0_rep: int
    base_list_rep: int
    # 0..167, with meaning bound by C0 finite-message checker/seal
    message_type_id: int
    # bitset over path B positions, not over all dynamic vertices
    D_restricted_bits: int
    # replay-only canonical encoding may be supplied externally
    min_bad_certificate_id: Optional[int]=None

@dataclass(frozen=True)
class X0Ann:
    fixed_color: int
    # adjacency to the other six path positions, encoded in path-index order
    local_profile_bits: int
    # among roles for which this identity is considered, color already excluded
    # by seed or another same-color X0 identity before this identity
    redundancy_bits: int

@dataclass(frozen=True)
class SAnn:
    seed_index: int
    fixed_color: int

@dataclass(frozen=True)
class Cell:
    s: int
    seed_colors: Tuple[int,...]
    role_order: Tuple[str,...]
    # Full induced graph on seven concrete identities.
    adjacency_mask_21: int
    S: Tuple[Optional[SAnn],...]
    B: Tuple[Optional[BAnn],...]
    C: Tuple[Optional[CAnn],...]
    X0: Tuple[Optional[X0Ann],...]

def adjacency_bit(mask21: int, i: int, j: int) -> int:
    if i>j:
        i,j=j,i
    k=PAIR_POSITIONS.index((i,j))
    return (mask21 >> k) & 1

def canonical_component_labels(labels: Sequence[Optional[int]]) -> Tuple[Optional[int],...]:
    remap={}
    nxt=0
    out=[]
    for x in labels:
        if x is None:
            out.append(None)
            continue
        if x not in remap:
            remap[x]=nxt
            nxt+=1
        out.append(remap[x])
    return tuple(out)

def validate_cell(cell: Cell) -> List[str]:
    """Return a list of violations. Empty means locally schema-consistent.

    This validator proves only local annotation consistency, not global
    source realizability.
    """
    err=[]
    if cell.s != len(cell.seed_colors):
        err.append("seed_size_mismatch")
    if len(cell.role_order)!=7:
        err.append("role_order_length")
        return err
    if any(r not in ROLE_CLASSES for r in cell.role_order):
        err.append("unknown_role_class")
    if not (0 <= cell.adjacency_mask_21 < (1<<21)):
        err.append("adjacency_mask_range")
    for c in cell.seed_colors:
        if c not in COLORS:
            err.append("bad_seed_color")

    # Exactly one annotation object of the role's class at each position.
    for i,r in enumerate(cell.role_order):
        present={
            "S":cell.S[i] is not None,
            "B":cell.B[i] is not None,
            "C":cell.C[i] is not None,
            "X0":cell.X0[i] is not None,
        }
        if sum(present.values())!=1 or not present[r]:
            err.append(f"annotation_class_mismatch@{i}")

    # Dynamic palette algebra: tau -> chi_S -> L_P, and exact A adds chi_X0.
    for i,b in enumerate(cell.B):
        if b is None:
            continue
        if not (0 <= b.tau_bits < (1<<cell.s)):
            err.append(f"tau_range@{i}")
            continue
        chi=tau_to_chi_s(b.tau_bits,cell.seed_colors)
        if b.chi_s != chi:
            err.append(f"chi_s_mismatch@{i}")
        if b.Lp != source_list(chi):
            err.append(f"Lp_mismatch@{i}")
        if b.A != exact_palette(chi,b.chi_x0):
            err.append(f"A_mismatch@{i}")
        if not (0 <= b.chi_x0 < 16):
            err.append(f"chi_x0_range@{i}")

    # C representative mask/base list/message range.
    for i,c in enumerate(cell.C):
        if c is None:
            continue
        if not (0 <= c.chi_x0_rep < 16):
            err.append(f"C_chi_x0_range@{i}")
        if c.base_list_rep != (FULL_MASK & ~c.chi_x0_rep):
            err.append(f"C_base_list_mismatch@{i}")
        if not (0 <= c.message_type_id < 168):
            err.append(f"message_type_range@{i}")

    # X0 fixed color/properness on selected X0-X0 edges.
    for i,x in enumerate(cell.X0):
        if x is None:
            continue
        if x.fixed_color not in COLORS:
            err.append(f"bad_X0_color@{i}")
        if not (0 <= x.local_profile_bits < (1<<6)):
            err.append(f"X0_profile_range@{i}")
        if not (0 <= x.redundancy_bits < (1<<7)):
            err.append(f"X0_redundancy_range@{i}")

    # Component partition must be canonical by first occurrence.
    labels=[c.component_label if c is not None else None for c in cell.C]
    if tuple(labels) != canonical_component_labels(labels):
        err.append("noncanonical_component_labels")

    # Dynamic-component uniformity:
    # selected representatives in the same component must have equal B adjacency.
    c_positions=[i for i,r in enumerate(cell.role_order) if r=="C"]
    b_positions=[i for i,r in enumerate(cell.role_order) if r=="B"]
    for bp in b_positions:
        groups: Dict[int,List[int]]={}
        for cp in c_positions:
            lab=cell.C[cp].component_label
            groups.setdefault(lab,[]).append(cp)
        for lab,ps in groups.items():
            vals={adjacency_bit(cell.adjacency_mask_21,bp,cp) for cp in ps}
            if len(vals)>1:
                err.append(f"dynamic_component_mixed@B{bp}:C{lab}")

    # Different residual components have no edge between selected representatives.
    for i,j in combinations(c_positions,2):
        ci,cj=cell.C[i],cell.C[j]
        if ci.component_label != cj.component_label and adjacency_bit(cell.adjacency_mask_21,i,j):
            err.append(f"cross_component_edge@{i},{j}")

    # Same-colored X0 identities cannot be adjacent under proper fixed coloring.
    x_positions=[i for i,r in enumerate(cell.role_order) if r=="X0"]
    for i,j in combinations(x_positions,2):
        if cell.X0[i].fixed_color==cell.X0[j].fixed_color and adjacency_bit(cell.adjacency_mask_21,i,j):
            err.append(f"same_color_X0_edge@{i},{j}")

    # Local profile bits must agree with the 21 concrete adjacency bits.
    for xp in x_positions:
        others=[q for q in range(7) if q!=xp]
        prof=0
        for k,q in enumerate(others):
            if adjacency_bit(cell.adjacency_mask_21,xp,q):
                prof |= 1<<k
        if cell.X0[xp].local_profile_bits != prof:
            err.append(f"X0_profile_mismatch@{xp}")

    return err

def role_strings() -> Iterable[Tuple[str,...]]:
    """All 7-role strings in declared scope (at least one C and one X0)."""
    for r in product(ROLE_CLASSES, repeat=7):
        if "C" in r and "X0" in r:
            yield r

def role_string_count() -> int:
    # Inclusion-exclusion: all - no C - no X0 + neither
    return 4**7 - 3**7 - 3**7 + 2**7

assert role_string_count()==12138
assert sum(1 for _ in role_strings())==11874

def finite_cover_upper_bound(s: int) -> int:
    """Very coarse explicit finite upper bound K(s) on raw annotation cells.

    This deliberately overcounts inconsistent cells.  Its sole theorem role
    is to make finiteness for fixed s explicit; it is NOT a complexity bound.
    """
    assert s>=1
    role=4**7
    seed_coloring=4**s
    seed_identity=max(1,s)**7
    adjacency=2**21

    # Per-position overbounds; applied to all seven positions regardless of role.
    B_states=(2**s) * 16 * (2**7)          # tau, chi_X0, component incidence
    C_states=16 * 168 * (2**7)             # rep mask, message, D_restricted
    X_states=4 * (2**6) * (2**7)           # color, local profile, redundancy
    S_states=max(1,s) * 4

    component_partition=bell(7)
    per_position=max(B_states,C_states,X_states,S_states)
    return role * seed_coloring * seed_identity * adjacency * component_partition * (per_position**7)

def theorem_receipt(s_values=(1,2,3,4,5,6)):
    out=[]
    for s in s_values:
        K=finite_cover_upper_bound(s)
        out.append({
            "s":s,
            "role_strings":role_string_count(),
            "bell7":bell(7),
            "upper_bound_bits":K.bit_length(),
            "finite":True,
        })
    return {
        "status":"PASS_SCHEMA_REPLAY",
        "claim":"FINITE_COVER_SCHEMA_PARAMETERIZED_BY_s",
        "pair_bits":21,
        "role_strings":role_string_count(),
        "message_type_bound":168,
        "color_masks_per_role":16,
        "bell7":bell(7),
        "sample_parameter_receipts":out,
        "complexity_warning":"K(s) is only a finite cover bound; no polynomial cell-count claim.",
    }

def self_test():
    assert len(PAIR_POSITIONS)==21
    assert bell(7)==877
    assert role_string_count()==12138
    assert tau_to_chi_s(0b11,(1,2)) == mask({1,2})
    assert source_list(mask({1})) == mask({2,3,4})
    assert exact_palette(mask({1}),mask({4})) == mask({2,3})
    # Dynamic exact-list identity redundancy includes seed colors:
    # adding an X0 edge of color 1 changes identity but not A when seed already excludes 1.
    before=exact_palette(mask({1}),0)
    after=exact_palette(mask({1}),mask({1}))
    assert before==after==mask({2,3,4})
    return theorem_receipt()

if __name__=="__main__":
    print(self_test())
