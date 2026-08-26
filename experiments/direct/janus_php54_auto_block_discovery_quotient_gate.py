#!/usr/bin/env python3
"""C025 exact auto block-discovery + histogram quotient gate.

This stage removes the manually supplied PHP_5_4_C1 block identities and center.
The machine receives only the frozen residual CNF.  It then:

  RAW CNF
    -> enumerate every 3-variable local gadget candidate
    -> canonicalize signed local CNF under all variable renamings
    -> find the unique maximum disjoint repeated gadget system
    -> treat uncovered variables as fixed coordinates
    -> certify adjacent block swaps preserve the full residual
    -> synthesize the local state alphabet
    -> compile full residual into bounded-arity orbit templates
    -> enumerate the exact histogram quotient
    -> synthesize a minimum UNSAT template subset
    -> emit an exact replayable certificate/report

There is no SAT oracle, semantic-equivalence oracle, ML, randomness, score-based
promotion, or manually supplied block identity.  Ambiguity fails closed.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from math import factorial
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole

CAPTURED: base.EngineState | None = None
ORIGINAL = v2.discover_macro_restore_v2
BLOCK_WIDTH = 3  # grammar bound for this exact discovery stage; identities are unknown.


def capture(state: base.EngineState):
    global CAPTURED
    out = ORIGINAL(state)
    if out is None and not any(v in set(state.root_vars) for v in base.vars_of(state.residual)):
        CAPTURED = state
    return out


def eval_lit(lit: int, assignment: dict[int, bool]) -> bool:
    value = assignment[abs(lit)]
    return value if lit > 0 else not value


def eval_clause(clause: base.Clause, assignment: dict[int, bool]) -> bool:
    return any(eval_lit(lit, assignment) for lit in clause)


def local_clauses(residual: base.CNF, variables: tuple[int, ...]) -> tuple[base.Clause, ...]:
    vset = set(variables)
    rows = []
    for clause in residual:
        cvars = {abs(lit) for lit in clause}
        if cvars and cvars <= vset:
            rows.append(clause)
    return tuple(sorted(rows, key=lambda c: (len(c), c)))


def oriented_signature(
    clauses: tuple[base.Clause, ...],
    variables: tuple[int, ...],
) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    """Return canonical signed local CNF signature plus role->actual-variable order."""
    candidates = []
    for role_vars in permutations(variables):
        pos = {v: i + 1 for i, v in enumerate(role_vars)}
        sig_rows = []
        for clause in clauses:
            row = tuple(sorted(
                (pos[abs(lit)] if lit > 0 else -pos[abs(lit)])
                for lit in clause
            , key=lambda z: (abs(z), z < 0)))
            sig_rows.append(row)
        signature = tuple(sorted(sig_rows, key=lambda c: (len(c), c)))
        candidates.append((signature, tuple(role_vars)))
    return min(candidates)


def local_state_alphabet(
    block: tuple[int, ...],
    clauses: tuple[base.Clause, ...],
) -> tuple[tuple[int, ...], ...]:
    states = []
    for bits in product((0, 1), repeat=len(block)):
        assignment = {v: bool(bit) for v, bit in zip(block, bits)}
        if all(eval_clause(c, assignment) for c in clauses):
            states.append(bits)
    return tuple(states)


def connected_local_interaction(clauses: tuple[base.Clause, ...], variables: tuple[int, ...]) -> bool:
    """Require local clauses to couple all three variables, avoiding isolated padding vars."""
    adj = {v: set() for v in variables}
    for clause in clauses:
        cvars = sorted({abs(lit) for lit in clause})
        for a, b in combinations(cvars, 2):
            adj[a].add(b)
            adj[b].add(a)
    seen = set()
    stack = [variables[0]]
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        stack.extend(adj[v] - seen)
    return seen == set(variables)


def enumerate_local_gadgets(residual: base.CNF):
    vars_ = base.vars_of(residual)
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    inspected = 0
    admitted = 0
    for triple in combinations(vars_, BLOCK_WIDTH):
        inspected += 1
        clauses = local_clauses(residual, triple)
        if len(clauses) < 2:
            continue
        if not connected_local_interaction(clauses, triple):
            continue
        signature, oriented = oriented_signature(clauses, triple)
        # Recompute internal clauses in the canonical role order; semantics are unchanged.
        oriented_clauses = local_clauses(residual, oriented)
        alphabet = local_state_alphabet(oriented, oriented_clauses)
        if not (1 < len(alphabet) < (1 << BLOCK_WIDTH)):
            continue
        key = (signature, len(alphabet))
        grouped[key].append({
            "vars": tuple(sorted(triple)),
            "block": oriented,
            "clauses": oriented_clauses,
            "signature": signature,
            "alphabet": alphabet,
        })
        admitted += 1
    return grouped, inspected, admitted


def maximal_disjoint_packings(rows: list[dict]) -> list[tuple[int, ...]]:
    """Exact enumeration of all maximum-cardinality disjoint block packings."""
    rows = sorted(rows, key=lambda r: r["vars"])
    best_size = -1
    best: list[tuple[int, ...]] = []

    def rec(i: int, used: frozenset[int], chosen: tuple[int, ...]) -> None:
        nonlocal best_size, best
        # Exact branch bound; it prunes only branches unable to match current optimum.
        if len(chosen) + (len(rows) - i) < best_size:
            return
        if i == len(rows):
            size = len(chosen)
            if size > best_size:
                best_size = size
                best = [chosen]
            elif size == best_size:
                best.append(chosen)
            return
        rec(i + 1, used, chosen)
        rvars = frozenset(rows[i]["vars"])
        if not (used & rvars):
            rec(i + 1, used | rvars, chosen + (i,))

    rec(0, frozenset(), ())
    # Remove duplicate systems, canonicalized by sorted variable sets.
    uniq = {}
    for indices in best:
        key = tuple(sorted(rows[i]["vars"] for i in indices))
        uniq[key] = indices
    return [uniq[k] for k in sorted(uniq)]


def discover_unique_block_system(residual: base.CNF):
    grouped, inspected, admitted = enumerate_local_gadgets(residual)
    candidates = []
    for key, rows0 in grouped.items():
        rows = sorted(rows0, key=lambda r: r["vars"])
        packings = maximal_disjoint_packings(rows)
        if not packings:
            continue
        size = len(packings[0])
        # A repeated gadget must occur at least twice; singleton motifs are not a block system.
        if size < 2:
            continue
        for indices in packings:
            blocks = tuple(sorted((rows[i]["block"] for i in indices), key=lambda b: tuple(sorted(b))))
            covered = frozenset(v for b in blocks for v in b)
            candidates.append({
                "key": key,
                "rows": rows,
                "indices": indices,
                "blocks": blocks,
                "covered": covered,
                "block_count": size,
            })

    if not candidates:
        raise AssertionError("AUTO_BLOCK_DISCOVERY_FAILED_NO_REPEATED_DISJOINT_GADGET_SYSTEM")

    max_blocks = max(c["block_count"] for c in candidates)
    finalists = [c for c in candidates if c["block_count"] == max_blocks]

    # Same geometric partition may arise through duplicate bookkeeping; dedupe exactly.
    uniq = {}
    for c in finalists:
        partition = tuple(sorted(tuple(sorted(b)) for b in c["blocks"]))
        sig = c["key"]
        uniq[(partition, sig)] = c
    finalists = [uniq[k] for k in sorted(uniq, key=lambda x: repr(x))]

    if len(finalists) != 1:
        diagnostic = [
            {
                "blocks": [list(b) for b in c["blocks"]],
                "signature": [list(x) for x in c["key"][0]],
                "local_state_count": c["key"][1],
            }
            for c in finalists[:16]
        ]
        raise AssertionError(
            "AUTO_BLOCK_DISCOVERY_AMBIGUOUS_MAXIMUM_SYSTEMS=" + json.dumps(diagnostic, sort_keys=True)
        )

    winner = finalists[0]
    vars_ = set(base.vars_of(residual))
    outside = tuple(sorted(vars_ - set(winner["covered"])))
    # Rebuild per-block local clauses/alphabet from the selected orientation.
    block_rows = []
    for block in winner["blocks"]:
        clauses = local_clauses(residual, block)
        signature, oriented = oriented_signature(clauses, tuple(sorted(block)))
        assert signature == winner["key"][0]
        clauses = local_clauses(residual, oriented)
        alphabet = local_state_alphabet(oriented, clauses)
        assert len(alphabet) == winner["key"][1]
        block_rows.append((oriented, clauses, alphabet))
    blocks = tuple(row[0] for row in block_rows)
    signatures = [oriented_signature(row[1], row[0])[0] for row in block_rows]
    assert len(set(signatures)) == 1
    alphabets = [row[2] for row in block_rows]
    assert len(set(alphabets)) == 1
    return {
        "blocks": blocks,
        "outside": outside,
        "signature": signatures[0],
        "alphabet": alphabets[0],
        "triples_inspected": inspected,
        "local_gadgets_admitted": admitted,
        "signature_classes": len(grouped),
        "maximum_block_count": max_blocks,
    }


def swap_mapping(blocks: tuple[tuple[int, ...], ...], i: int, j: int) -> dict[int, int]:
    mapping = {}
    for pos in range(BLOCK_WIDTH):
        mapping[blocks[i][pos]] = blocks[j][pos]
        mapping[blocks[j][pos]] = blocks[i][pos]
    return mapping


def rename_clause_with_mapping(clause: base.Clause, mapping: dict[int, int]) -> base.Clause:
    out = base.canon_clause(
        (mapping.get(abs(lit), abs(lit)) if lit > 0 else -mapping.get(abs(lit), abs(lit)))
        for lit in clause
    )
    assert out is not None
    return out


def certify_adjacent_block_swaps(residual: base.CNF, blocks: tuple[tuple[int, ...], ...]):
    residual_set = set(residual)
    rows = []
    for i in range(len(blocks) - 1):
        mapping = swap_mapping(blocks, i, i + 1)
        renamed = {rename_clause_with_mapping(c, mapping) for c in residual}
        ok = renamed == residual_set
        rows.append({"swap": [i, i + 1], "preserves_residual": ok})
        if not ok:
            raise AssertionError(f"ADJACENT_BLOCK_SWAP_{i}_{i+1}_FAILED")
    return rows


def clause_template(
    clause: base.Clause,
    blocks: tuple[tuple[int, ...], ...],
    outside: tuple[int, ...],
):
    var_to_block = {}
    for bi, block in enumerate(blocks):
        for pos, var in enumerate(block):
            var_to_block[var] = (bi, pos)
    outside_pos = {v: i for i, v in enumerate(outside)}
    mentioned = sorted({var_to_block[abs(lit)][0] for lit in clause if abs(lit) in var_to_block})

    candidates = []
    for ordering in permutations(mentioned):
        role = {bi: ri for ri, bi in enumerate(ordering)}
        pattern = []
        for lit in clause:
            var = abs(lit)
            positive = lit > 0
            if var in var_to_block:
                bi, pos = var_to_block[var]
                pattern.append(("b", role[bi], pos, positive))
            else:
                pattern.append(("o", outside_pos[var], -1, positive))
        candidates.append(tuple(sorted(pattern)))
    if not mentioned:
        pattern = []
        for lit in clause:
            var = abs(lit)
            pattern.append(("o", outside_pos[var], -1, lit > 0))
        return tuple(sorted(pattern)), 0
    return min(candidates), len(mentioned)


def materialize_template(
    template: tuple[tuple[str, int, int, bool], ...],
    block_assignment: tuple[int, ...],
    blocks: tuple[tuple[int, ...], ...],
    outside: tuple[int, ...],
) -> base.Clause:
    lits = []
    for kind, role, pos, positive in template:
        if kind == "b":
            var = blocks[block_assignment[role]][pos]
        else:
            var = outside[role]
        lits.append(var if positive else -var)
    out = base.canon_clause(lits)
    assert out is not None
    return out


def compile_templates(residual: base.CNF, blocks, outside):
    buckets = defaultdict(list)
    arities = {}
    for clause in residual:
        template, arity = clause_template(clause, blocks, outside)
        buckets[template].append(clause)
        arities[template] = arity

    # Exact replay: materialize every injective role->block assignment, never k! permutations.
    reconstructed = set()
    replay_rows = []
    for template in sorted(buckets, key=repr):
        arity = arities[template]
        images = set()
        if arity == 0:
            assignments = [()]
        else:
            assignments = permutations(range(len(blocks)), arity)
        for assignment in assignments:
            images.add(materialize_template(template, tuple(assignment), blocks, outside))
        reconstructed |= images
        replay_rows.append({
            "template": [list(x) for x in template],
            "block_arity": arity,
            "materialized_images": len(images),
            "source_clauses": len(buckets[template]),
        })
    if reconstructed != set(residual):
        missing = sorted(set(residual) - reconstructed, key=lambda c: (len(c), c))
        extra = sorted(reconstructed - set(residual), key=lambda c: (len(c), c))
        raise AssertionError(f"TEMPLATE_REPLAY_MISMATCH missing={missing[:4]} extra={extra[:4]}")
    return tuple(sorted(buckets, key=repr)), arities, replay_rows


def compositions(total: int, k: int):
    if k == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, k - 1):
            yield (first,) + tail


def feasible_type_tuple(type_tuple: tuple[int, ...], hist: tuple[int, ...]) -> bool:
    need = Counter(type_tuple)
    return all(need[t] <= hist[t] for t in need)


def template_holds_direct(template, hist, outside_bits, local_states):
    arity = 0
    for kind, role, _, _ in template:
        if kind == "b":
            arity = max(arity, role + 1)
    for type_tuple in product(range(len(local_states)), repeat=arity):
        if not feasible_type_tuple(type_tuple, hist):
            continue
        clause_true = False
        for kind, role, pos, positive in template:
            if kind == "b":
                value = bool(local_states[type_tuple[role]][pos])
            else:
                value = bool(outside_bits[role])
            if value if positive else not value:
                clause_true = True
                break
        if not clause_true:
            return False
    return True


def canonical_assignment(blocks, outside, hist, outside_bits, local_states):
    assignment = {v: bool(bit) for v, bit in zip(outside, outside_bits)}
    cursor = 0
    for state_idx, count in enumerate(hist):
        for _ in range(count):
            block = blocks[cursor]
            state = local_states[state_idx]
            assignment.update({v: bool(bit) for v, bit in zip(block, state)})
            cursor += 1
    assert cursor == len(blocks)
    return assignment


def explicit_template_holds(template, blocks, outside, hist, outside_bits, local_states):
    assignment = canonical_assignment(blocks, outside, hist, outside_bits, local_states)
    arity = max((role + 1 for kind, role, _, _ in template if kind == "b"), default=0)
    assignments = [()] if arity == 0 else permutations(range(len(blocks)), arity)
    return all(
        eval_clause(materialize_template(template, tuple(ba), blocks, outside), assignment)
        for ba in assignments
    )


def minimum_unsat_template_subset(templates, quotient_states, local_states):
    for size in range(1, len(templates) + 1):
        for indices in combinations(range(len(templates)), size):
            if all(
                not all(template_holds_direct(templates[i], hist, outside_bits, local_states) for i in indices)
                for outside_bits, hist in quotient_states
            ):
                return indices
    return None


def main() -> None:
    global CAPTURED
    old = v2.discover_macro_restore_v2
    v2.discover_macro_restore_v2 = capture
    try:
        old_result = v2.solve_fail_closed_v2(pigeonhole(5, 4), cap_exponent=1, extension_exponent=1)
    finally:
        v2.discover_macro_restore_v2 = old

    assert old_result["status"] == "OPEN" and CAPTURED is not None
    state = CAPTURED
    residual = state.residual
    fingerprint = base.fingerprint(residual)
    assert fingerprint == "990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6"

    discovery = discover_unique_block_system(residual)
    blocks = discovery["blocks"]
    outside = discovery["outside"]
    local_states = discovery["alphabet"]

    # Frozen regression expectations are structural only; no variable IDs are supplied.
    assert len(blocks) == 4
    assert all(len(block) == BLOCK_WIDTH for block in blocks)
    assert len(outside) == 1
    assert len(local_states) == 4

    swap_rows = certify_adjacent_block_swaps(residual, blocks)
    assert len(swap_rows) == len(blocks) - 1

    templates, arities, replay_rows = compile_templates(residual, blocks, outside)
    max_block_arity = max(arities.values(), default=0)
    assert max_block_arity <= 2
    assert len(templates) == 8

    hists = tuple(compositions(len(blocks), len(local_states)))
    outside_states = tuple(product((0, 1), repeat=len(outside)))
    quotient_states = tuple((obits, hist) for obits in outside_states for hist in hists)
    assert len(hists) == 35
    assert len(quotient_states) == 70

    orbit_coverage = 0
    for hist in hists:
        denom = 1
        for count in hist:
            denom *= factorial(count)
        orbit_coverage += factorial(len(blocks)) // denom
    orbit_coverage *= len(outside_states)
    assert orbit_coverage == (2 ** len(outside)) * (len(local_states) ** len(blocks)) == 512

    rejection_rows = []
    violating = Counter()
    crosschecks = 0
    for outside_bits, hist in quotient_states:
        failed = []
        for idx, template in enumerate(templates):
            direct = template_holds_direct(template, hist, outside_bits, local_states)
            explicit = explicit_template_holds(template, blocks, outside, hist, outside_bits, local_states)
            assert direct == explicit
            crosschecks += 1
            if not direct:
                failed.append(idx)
        if not failed:
            raise AssertionError(f"SURVIVING_QUOTIENT_STATE outside={outside_bits} hist={hist}")
        violating[min(failed)] += 1
        rejection_rows.append({
            "outside": list(outside_bits),
            "hist": list(hist),
            "violated_template": min(failed),
        })

    minimum = minimum_unsat_template_subset(templates, quotient_states, local_states)
    assert minimum is not None

    certificate = {
        "kind": "AUTO_DISCOVERED_SYMMETRY_QUOTIENT_PROGRAM",
        "source_fingerprint": fingerprint,
        "block_width": BLOCK_WIDTH,
        "blocks": [list(b) for b in blocks],
        "outside_variables": list(outside),
        "local_clause_signature": [list(x) for x in discovery["signature"]],
        "local_states": [list(x) for x in local_states],
        "adjacent_swap_generators": [[i, i + 1] for i in range(len(blocks) - 1)],
        "orbit_templates": [[list(atom) for atom in templates[i]] for i in minimum],
        "histogram_sum": len(blocks),
    }
    cert_bytes = len(json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    report = {
        "schema": "JANUS/C025/PHP54-AUTO-BLOCK-DISCOVERY-QUOTIENT/v1",
        "P_VS_NP": "OPEN",
        "frozen_case": "PHP_5_4_C1",
        "fingerprint": fingerprint,
        "discovery": {
            "input_live_variables": list(base.vars_of(residual)),
            "manually_supplied_block_ids": False,
            "manually_supplied_center_id": False,
            "block_width_bound": BLOCK_WIDTH,
            "triples_inspected": discovery["triples_inspected"],
            "local_gadgets_admitted": discovery["local_gadgets_admitted"],
            "signature_classes": discovery["signature_classes"],
            "selection_rule": "UNIQUE_MAXIMUM_CARDINALITY_DISJOINT_REPEATED_CANONICAL_SIGNED_LOCAL_GADGET_SYSTEM_OR_FAIL_CLOSED",
            "blocks_discovered": [list(b) for b in blocks],
            "outside_variables_discovered": list(outside),
            "block_count": len(blocks),
            "local_clause_signature": [list(x) for x in discovery["signature"]],
            "local_state_alphabet": [list(x) for x in local_states],
            "local_state_count": len(local_states),
        },
        "symmetry_certificate": {
            "generators_checked": swap_rows,
            "adjacent_transpositions_generate": f"S_{len(blocks)}",
            "full_group_closure_enumerated_for_certificate": False,
            "all_generators_preserve_residual": all(row["preserves_residual"] for row in swap_rows),
        },
        "orbit_program": {
            "template_count": len(templates),
            "max_block_arity": max_block_arity,
            "template_replay": replay_rows,
            "exact_full_residual_replay": True,
            "factorial_group_elements_enumerated": 0,
        },
        "quotient": {
            "outside_state_count": len(outside_states),
            "histogram_count": len(hists),
            "quotient_state_count": len(quotient_states),
            "local_valid_assignment_space": orbit_coverage,
            "raw_assignment_space": 2 ** len(base.vars_of(residual)),
            "all_quotient_states_rejected": len(rejection_rows) == len(quotient_states),
            "direct_vs_explicit_template_crosschecks": crosschecks,
            "violating_template_histogram": {str(k): v for k, v in sorted(violating.items())},
        },
        "exact_program_synthesis": {
            "candidate_template_subsets": 2 ** len(templates) - 1,
            "ordering": "subset cardinality then lexicographic indices",
            "heuristic": False,
            "minimum_unsat_template_count": len(minimum),
            "minimum_unsat_template_indices": list(minimum),
            "certificate_json_bytes": cert_bytes,
        },
        "result": {
            "status": "UNSAT",
            "reason": "ALL_70_AUTO_DISCOVERED_EXACT_QUOTIENT_STATES_REJECTED",
            "old_engine_status": old_result["status"],
            "auto_block_discovery_breakthrough": True,
        },
        "paradox_rule": {
            "name": "JANUS_MATHEMATICAL_ALGEBRAIC_PARADOX_RULE",
            "principle": "SEARCH_FOR_EXACT_REPRESENTATION_CHANGES_WHERE_EXPLICIT_DIMENSION_OR_STATE_VOLUME_COLLAPSES_WHILE_INFORMATION_AND_REPLAYABILITY_ARE_PRESERVED_IN_A_LATENT_ALGEBRAIC_FIBER",
            "allowed": [
                "EXACT_SYMMETRY_QUOTIENT",
                "REVERSIBLE_COORDINATE_CHANGE",
                "ORBIT_REPRESENTATIVE_PLUS_GENERATORS",
                "ALGEBRAIC_CANCELLATION",
                "BASIS_CHANGE",
                "HISTOGRAM_LIFTING",
                "PROOF_CARRYING_COMPRESSION"
            ],
            "forbidden": [
                "HEURISTIC_PROMOTION",
                "UNVERIFIED_INFORMATION_LOSS",
                "NUMERICAL_COINCIDENCE_AS_PROOF",
                "PARADOX_NAME_WITHOUT_EXACT_SEMANTICS"
            ],
            "gate": "EVERY_PARADOXICAL_COMPRESSION_MUST_HAVE_EXACT_FORWARD_SEMANTICS_EXACT_REPLAY_OR_VERIFICATION_AND_A_RESOURCE_LEDGER"
        },
        "scientific_boundary": {
            "finite_frozen_witness": True,
            "no_sat_oracle": True,
            "no_semantic_equivalence_oracle": True,
            "no_ml": True,
            "no_randomness": True,
            "no_score_ranking": True,
            "block_identities_discovered_from_raw_residual": True,
            "block_width_three_is_still_a_bounded_search_grammar": True,
            "general_block_width_discovery": "OPEN",
            "PHP_family_scaling": "OPEN",
            "arbitrary_CNF_coverage": "OPEN",
            "universal_polynomial_algorithm": "OPEN",
            "P_VS_NP": "OPEN"
        }
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
