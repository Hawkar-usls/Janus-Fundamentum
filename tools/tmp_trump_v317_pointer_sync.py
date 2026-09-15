from pathlib import Path
import json
import re

START = Path("START_HERE_TRUMP_CONTEXT.md")
MANIFEST = Path("registry/TRUMP_CONTEXT_MANIFEST.json")

text = START.read_text(encoding="utf-8")
assert "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json" not in text
assert "1. Read `registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json` **first**." in text

a = text.index("## Startup sequence")
b = text.index("## Anti-loop test")
prefix, seq, suffix = text[:a], text[a:b], text[b:]
seq = re.sub(r"(?m)^(\d+)\. ", lambda m: f"{int(m.group(1)) + 1}. ", seq)
new_first = (
    "1. Read `registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json` **first**. "
    "This is the latest continuity anchor. It records the exact-two-of-four K5 cardinality forensic PASS: relation truth equals selected degree two exactly; candidate and independent checker agree on exactly 12 K5 solutions, each one five-cycle; the exact semantic object is an undirected 2-factor / f(v)=2 incidence system. "
    "This is semantic classification only: no general 2-factor/f-factor carrier is sealed yet and `SIZE4_BRANCHING_LICENSED=false`. The next allowed successor is a separately preregistered proof-carrying two-factor/f-factor carrier attempt with exact semantics and total polynomial resource accounting.\n"
)
pos = seq.index("2. Read `registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json`")
seq = seq[:pos] + new_first + seq[pos:]
text = prefix + seq + suffix

old_tail = """The v3.16 diagnostic resolves the immediate raw-reachability/semantic question narrowly. A full-cube K5 probe is removed completely by exact universal-relation normalization, so that synthetic control is too weak to drive successor design. A second reproducibly generated raw predecessor-shaped K5 probe, with each relation enforcing exactly two `1` values among its four incident edge variables, is nonuniversal, survives the same exact normalization, and remains `OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND`. This establishes a semantically nontrivial probe family only; it does not establish natural frequency, necessity, hardness, or a lower bound.

Captain's nearest blocker is now:

`EXACT_TWO_OF_FOUR_K5_CARDINALITY_AND_INCIDENCE_STRUCTURE_CLASSIFICATION_BEFORE_ANY_WIDER_SEPARATOR_BRANCHING`.

`OPEN_NONUNIQUE_COMMON_CORE_SUPPORT` remains a separate secondary blocker.

The next preferred action is diagnostic only:

`TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC`.

Captain Obvious' directive: **classify the exact-2-of-4 incidence/degree semantics and test for a cheaper exact carrier or normal form before any size-4 separator branching**. The K5 minimum cut of four is still not a branching license, and no extra recursion level is authorized.

Forbidden shortcuts include size-4 Boolean branching, automatic extra recursion depth, unpreregistered separator-size >=3 branching, arbitrary-depth recursion, 3+ join chains, global residual Cartesian products, budget raises, treating the reproducibly generated probe as natural-frequency evidence, treating multiple common-core states as solved, or treating OPEN as negative evidence."""
new_tail = """The v3.17 diagnostic closes the semantic-classification obligation for the surviving exact-two-of-four K5 probe. Across all 1024 finite K5 edge assignments, raw relation truth is exactly equivalent to selected degree two at every vertex. Candidate and an independent 252-subset checker agree on exactly 12 satisfying edge sets; every solution is a spanning 2-regular graph and, on K5, exactly one five-cycle. The representation is identity on edge variables, so the exact semantic object is an undirected 2-factor, equivalently the f-factor specialization `f(v)=2`.

This does **not** yet seal a TRUMP 2-factor/f-factor carrier. Classical polynomial f-factor/matching theory is only an algorithmic door until it is bound to exact admission recognition, semantics-preserving construction, proof-carrying SAT/UNSAT authority, raw witness reconstruction, original-relation verification, and a total polynomial resource/certificate envelope in the original explicit input size.

Captain's nearest blocker is now:

`EXACT_PROOF_CARRYING_TWO_FACTOR_F_FACTOR_CARRIER_WITH_RECOGNITION_CONSTRUCTION_RECONSTRUCTION_VERIFICATION_AND_POLYNOMIAL_TOTAL_RESOURCE_ACCOUNTING`.

`OPEN_NONUNIQUE_COMMON_CORE_SUPPORT` remains a separate secondary blocker.

The next preferred successor is:

`TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_EXACT_TWO_FACTOR_F_FACTOR_CARRIER_FALSIFIER_GATE`.

Captain Obvious' directive: **attempt the cheaper exact two-factor/f-factor carrier before any size-4 separator branching, but do not import f-factor as an unchecked black box**. The carrier must be separately preregistered and independently checked.

Forbidden shortcuts include size-4 Boolean branching, automatic extra recursion depth, importing a black-box f-factor solver without exact semantic/certificate binding, treating finite K5 enumeration as the general algorithm, 3+ join chains, global residual Cartesian products, budget raises, treating multiple common-core states as solved, or promoting this scoped structure to general SAT."""
assert old_tail in text
text = text.replace(old_tail, new_tail, 1)
old_sentence = "The synthetic full-cube K5 is structurally diagnosed by v3.15 and semantically normalized away by v3.16; the surviving exact-2-of-4 K5 probe is diagnostic only and still licenses no size-4 branching or deeper recursion."
assert old_sentence in text
text = text.replace(
    old_sentence,
    "The synthetic full-cube K5 is structurally diagnosed by v3.15 and normalized away by v3.16; v3.17 identifies the surviving exact-2-of-4 K5 exactly as a two-factor/f(v)=2 incidence system, but no general two-factor carrier or size-4 branching is licensed yet.",
    1,
)
START.write_text(text, encoding="utf-8")

m = json.loads(MANIFEST.read_text(encoding="utf-8"))
assert m["latest_successor_state"] == "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json"
s = m["current_scoped_open_surface"]
assert s["latest_state"] == "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json"
assert s["next_gate_candidate"] == "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC"

m["latest_successor_state"] = "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json"
s["nearest_blocker"] = "EXACT_PROOF_CARRYING_TWO_FACTOR_F_FACTOR_CARRIER_WITH_RECOGNITION_CONSTRUCTION_RECONSTRUCTION_VERIFICATION_AND_POLYNOMIAL_TOTAL_RESOURCE_ACCOUNTING"
s["next_gate_candidate"] = "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_EXACT_TWO_FACTOR_F_FACTOR_CARRIER_FALSIFIER_GATE"
s["next_gate_class"] = "SUCCESSOR_REPAIR_CANDIDATE__PREREGISTER_BEFORE_IMPLEMENTATION__NO_SIZE4_BRANCHING"
s["latest_state"] = "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json"

key = "BICAMERAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_FORENSIC"
assert key not in m["mechanisms"]
m["mechanisms"][key] = {
    "aliases": [
        "Exact-two-of-four K5 cardinality forensic",
        "K5 two-factor semantic forensic",
        "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC"
    ],
    "role": "Diagnostic-only exact classification of the surviving raw predecessor-shaped exact-two-of-four K5 probe as selected-degree-two / undirected two-factor semantics.",
    "classification": "DIAGNOSTIC_ONLY",
    "fundamentum_binding": {
        "latest_state": "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json",
        "preregistration_commit": "729a72dd12e9ef5ac5cfaa2f4033f089cfa878a7",
        "immutable_first_fail_run": 35019074281,
        "immutable_first_fail_job": 104549852738,
        "candidate_repair_commit": "0bf1005c5ff73cc4c19cfa92a4d530a0fd21519c",
        "candidate_blob": "2980ff274e6217dcc0faa6374bc33ab7ab5ed283",
        "independent_checker_commit": "2cadc96ec3020e90a8fcaf24ae1e34e288765d5f",
        "independent_checker_blob": "629ee96818589ef9bc930c9a95e2ff1fc6e6b771",
        "success_actions_run": 35019473824,
        "success_actions_job": 104551283525,
        "result_commit": "38c586decc95e02aa62db3b859b82b67e41a5b92",
        "journal_commit": "2161dd8ecf265a05fb3f35c9b827c88e5ba8b967",
        "pull_request": 473,
        "merge_commit": "295b536e4a832c1adba8ce53362865df57e94aa0",
        "verdict": "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC"
    },
    "machine_conclusion": {
        "candidate_assignments_checked": 1024,
        "independent_five_edge_subsets_checked": 252,
        "semantic_mismatch_count": 0,
        "k5_solution_count": 12,
        "every_solution_single_five_cycle": True,
        "global_object": "UNDIRECTED_TWO_FACTOR",
        "f_factor_specialization": "F_FACTOR_WITH_F_V_EQUALS_TWO_FOR_EVERY_CONSTRAINED_VERTEX",
        "general_trump_two_factor_carrier_sealed": False,
        "size4_branching_licensed": False
    },
    "current_blocker": "Bind a proof-carrying polynomial two-factor/f-factor carrier to exact TRUMP recognition, semantics, reconstruction, verification and resource accounting before any size-4 separator branching.",
    "firewall": "Semantic identification of an f-factor object is not itself an admitted carrier and is not a general SAT result."
}
MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("V3_17_POINTER_SYNC_READY")
