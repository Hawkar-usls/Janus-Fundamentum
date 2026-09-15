from pathlib import Path
import json
import re

START = Path("START_HERE_TRUMP_CONTEXT.md")
MANIFEST = Path("registry/TRUMP_CONTEXT_MANIFEST.json")

text = START.read_text(encoding="utf-8")
assert "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json" not in text
assert "1. Read `registry/TRUMP_CURRENT_STATE_2026-09-15_v3.15.json` **first**." in text

a = text.index("## Startup sequence")
b = text.index("## Anti-loop test")
prefix, seq, suffix = text[:a], text[a:b], text[b:]
seq = re.sub(r"(?m)^(\d+)\. ", lambda m: f"{int(m.group(1)) + 1}. ", seq)
new_first = (
    "1. Read `registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json` **first**. "
    "This is the latest continuity anchor. It records the raw-reachability/semantic forensic PASS: "
    "the universal full-cube K5 disappears under exact universal-relation normalization, while a reproducibly generated raw predecessor-shaped exact-2-of-4 K5 is nonuniversal, survives normalization, and remains "
    "`OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND`. This is diagnostic probe evidence only, not natural-frequency, hardness, or size-4 branching authority. "
    "The next obligation is exact-2-of-4 cardinality/incidence structure forensic before any wider separator mechanism.\n"
)
pos = seq.index("2. Read `registry/TRUMP_CURRENT_STATE_2026-09-15_v3.15.json`")
seq = seq[:pos] + new_first + seq[pos:]
text = prefix + seq + suffix

old_tail = """The v3.15 diagnostic explains the synthetic K5 depth-cap structurally: K5 requires four edge-variable removals to disconnect, while every three-edge removal remains connected. But the control is unit-test-only, has no raw-reachability authority, and each relation is a universal full Boolean cube. Therefore the structural diagnosis is not a license to branch on four variables and is not evidence that an actual raw predecessor-open case has this semantics.

Captain's nearest blocker is now:

`RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_OF_A_K5_STYLE_DEPTH_CAP_SHAPE_ON_THE_ACTUAL_UNIQUE_CORE_PREDECESSOR_SURFACE`.

`OPEN_NONUNIQUE_COMMON_CORE_SUPPORT` remains a separate secondary blocker.

The next preferred action is diagnostic only:

`TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_DEPTH_CAP_RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_FORENSIC`.

Captain Obvious' directive: **do not engineer a size-4 or deeper separator theorem around the synthetic full-cube K5 unit control**. First establish whether a semantically nontrivial K5-style depth-cap shape is reachable from frozen or reproducibly generated raw predecessor-open inputs, whether the fixed-depth OPEN persists after exact semantic normalization, and whether an already sealed cheaper exact carrier applies.

Forbidden shortcuts include size-4 Boolean branching, automatic extra recursion depth, unpreregistered separator-size >=3 branching, arbitrary-depth recursion, 3+ join chains, global residual Cartesian products, budget raises, treating a synthetic unit control as raw-reachability evidence, treating multiple common-core states as solved, or treating OPEN as negative evidence."""
new_tail = """The v3.16 diagnostic resolves the immediate raw-reachability/semantic question narrowly. A full-cube K5 probe is removed completely by exact universal-relation normalization, so that synthetic control is too weak to drive successor design. A second reproducibly generated raw predecessor-shaped K5 probe, with each relation enforcing exactly two `1` values among its four incident edge variables, is nonuniversal, survives the same exact normalization, and remains `OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND`. This establishes a semantically nontrivial probe family only; it does not establish natural frequency, necessity, hardness, or a lower bound.

Captain's nearest blocker is now:

`EXACT_TWO_OF_FOUR_K5_CARDINALITY_AND_INCIDENCE_STRUCTURE_CLASSIFICATION_BEFORE_ANY_WIDER_SEPARATOR_BRANCHING`.

`OPEN_NONUNIQUE_COMMON_CORE_SUPPORT` remains a separate secondary blocker.

The next preferred action is diagnostic only:

`TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC`.

Captain Obvious' directive: **classify the exact-2-of-4 incidence/degree semantics and test for a cheaper exact carrier or normal form before any size-4 separator branching**. The K5 minimum cut of four is still not a branching license, and no extra recursion level is authorized.

Forbidden shortcuts include size-4 Boolean branching, automatic extra recursion depth, unpreregistered separator-size >=3 branching, arbitrary-depth recursion, 3+ join chains, global residual Cartesian products, budget raises, treating the reproducibly generated probe as natural-frequency evidence, treating multiple common-core states as solved, or treating OPEN as negative evidence."""
assert old_tail in text
text = text.replace(old_tail, new_tail, 1)
old_sentence = "The synthetic K5 depth-cap control is now structurally diagnosed by v3.15, but still licenses no size-4 branching or deeper recursion."
assert old_sentence in text
text = text.replace(
    old_sentence,
    "The synthetic full-cube K5 is structurally diagnosed by v3.15 and semantically normalized away by v3.16; the surviving exact-2-of-4 K5 probe is diagnostic only and still licenses no size-4 branching or deeper recursion.",
    1,
)
START.write_text(text, encoding="utf-8")

m = json.loads(MANIFEST.read_text(encoding="utf-8"))
assert m["latest_successor_state"] == "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.15.json"
s = m["current_scoped_open_surface"]
assert s["latest_state"] == "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.15.json"
assert s["next_gate_candidate"] == "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_DEPTH_CAP_RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_FORENSIC"

m["latest_successor_state"] = "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json"
s["nearest_blocker"] = "EXACT_TWO_OF_FOUR_K5_CARDINALITY_AND_INCIDENCE_STRUCTURE_CLASSIFICATION_BEFORE_ANY_WIDER_SEPARATOR_BRANCHING"
s["next_gate_candidate"] = "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC"
s["next_gate_class"] = "DIAGNOSTIC_ONLY_BEFORE_ANY_SIZE4_OR_DEEPER_SEPARATOR_SUCCESSOR"
s["latest_state"] = "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json"

key = "BICAMERAL_K5_RAW_REACHABILITY_SEMANTIC_FORENSIC"
assert key not in m["mechanisms"]
m["mechanisms"][key] = {
    "aliases": [
        "K5 raw reachability semantic forensic",
        "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_DEPTH_CAP_RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_FORENSIC",
    ],
    "role": "Diagnostic-only test of raw predecessor-shaped K5 reachability, semantic nontriviality, exact universal normalization, and persistence of the fixed-depth OPEN.",
    "classification": "DIAGNOSTIC_ONLY",
    "fundamentum_binding": {
        "latest_state": "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json",
        "preregistration_commit": "e08019890fc9fa88533aa7ef36acfda388bf521d",
        "profiler_commit": "1e74b539aa952a54cca0a2238c59cf8ecd7e4763",
        "independent_checker_commit": "cabd00e6d25c8fcdb4ea5523d99b59c75e91002f",
        "workflow_head": "8328ac373a6f85ec997e9cd867a55e3c06ad92e1",
        "actions_run": 35016202446,
        "actions_job": 104540136784,
        "result_commit": "f1e73a6a63650cb1e258cf57355246e11800003c",
        "journal_commit": "c2f5ac3c49d21ad7eeebfd0eeb88f2c48c828cb6",
        "pull_request": 471,
        "merge_commit": "f6c86b4df75b8eb7b92a0044e26992cf23eddf57",
        "verdict": "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_FORENSIC",
    },
    "machine_conclusion": {
        "full_cube_k5_removed_by_exact_universal_normalization": True,
        "exact_two_of_four_k5_nonuniversal": True,
        "exact_two_of_four_k5_survives_universal_normalization": True,
        "fixed_depth_open_persists_after_normalization": True,
        "size4_branching_licensed": False,
        "natural_benchmark_frequency_evidence": False,
    },
    "current_blocker": "Classify exact-2-of-4 K5 cardinality/incidence semantics and test a cheaper exact carrier or normal form before any wider separator branching.",
    "firewall": "Reproducibly generated raw predecessor-shaped probe evidence is not natural-frequency, hardness, lower-bound, or size-4 branching authority.",
}
MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V3_16_POINTER_SYNC_READY")
