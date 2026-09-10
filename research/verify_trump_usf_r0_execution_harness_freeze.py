from __future__ import annotations

"""Independent verifier for the final TRUMP USF R0 execution-harness freeze.

This verifier does not import the generator, core harness, or frozen entrypoint.
It verifies their exact Git blobs and AST-level frozen constants, independently
reconstructs the schedule and one canonical-DIMACS fixture, and invokes ONLY
--synthetic-self-test and --print-schedule as subprocesses.  It never invokes
--run-scheduled and therefore cannot generate a scheduled Lane A/B/C instance.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SCHEMA = "TRUMP_USF_R0_EXECUTION_HARNESS_FREEZE_INDEPENDENT_VERIFIER"
VERSION = "1.0"

GENERATOR_PATH = "research/trump_usf_r0_frozen_generators.py"
GENERATOR_BLOB = "fe33883dc08e7e1eacadf287093aa0bb1f16c19a"
CORE_HARNESS_PATH = "research/trump_usf_r0_execution_harness.py"
CORE_HARNESS_BLOB = "ed4203bac76349ab377bb97f67bf1054d837bc96"
FROZEN_ENTRYPOINT_PATH = "research/trump_usf_r0_execution_harness_frozen_entrypoint.py"
FROZEN_ENTRYPOINT_BLOB = "50e8eedd461b87de37385cc9f3d30ea6224909fb"

EXPECTED_BLOBS = {
    GENERATOR_PATH: GENERATOR_BLOB,
    CORE_HARNESS_PATH: CORE_HARNESS_BLOB,
    FROZEN_ENTRYPOINT_PATH: FROZEN_ENTRYPOINT_BLOB,
    "experiments/janus_trump_r37b_fixed_certified_portfolio_restart_cycle.py": "f37da1c2e1696e35695096a2c748a222af7920cc",
    "experiments/janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics.py": "c9234a1ef639a009cc6cb4c8a6098fd09bf9affe",
    "experiments/janus_trump_r34_affine_xor_terminal_against_tseitin_core.py": "7f9bec920fa47af066570d874fe9127dc4b9b968",
    "experiments/janus_trump_r35_nonaffine_core_freeze_structure_intake.py": "ad237e341d9659d33da0568f134815776c1f95d8",
    "experiments/janus_trump_r35b_single_literal_rup_vivification.py": "259d2e38947d09b0c058963ad825a57f2e734203",
    "experiments/janus_trump_r38_portfolio_fixpoint_freeze_structure_intake.py": "816b53c390d78af415e580eaf358acf191796205",
    "experiments/trump_r38_fixpoint_to_ba25_factor_graph_diagnostic.py": "ea36a6b69f8c6034aa00ae4c4217bbd4d7735750",
    "research/janus_trump_r50g25ba25.py": "cad9c5f837d9d3c4e1c4bd4abef40976f2bb36ff",
    "research/TRUMP_UNIVERSAL_STRUCTURAL_FUNNEL_ADVERSARIAL_FAMILY_PREREGISTRATION_2026-09-10.json": "fda7092ec377b18abc0bc192d36610cca2e9f904",
    "research/TRUMP_USF_R0_MANDATORY_INFRASTRUCTURE_SELF_TEST_COMPLETION_2026-09-10.json": "69e5f73b8dae8be98bab549c88762c5794e80ba0",
}

EXPECTED_CAUSAL_ORDER = (
    "SCHEDULED_INSTANCE_ID", "GENERATE", "CANONICALIZE",
    "FREEZE_ORIGINAL_CNF_SHA256", "RUN_FROZEN_REDUCER",
    "CANONICALIZE_RESIDUAL", "FREEZE_RESIDUAL_SHA256",
    "MEASURE_WIDTH_EVIDENCE", "TERMINAL_RECOGNITION",
    "OPTIONAL_BA25_PEAK_STATE_DIAGNOSTIC", "TRUTH_ORACLE",
)
EXPECTED_TERMINALS = (
    "EMPTY_CNF_SAT", "EMPTY_CLAUSE_UNSAT", "2CNF", "HORN",
    "AFFINE_XOR_COMPLETE_CNF_BUNDLE", "RENAMABLE_HORN", "DUAL_HORN",
    "BETA_ACYCLIC",
)
EXPECTED_TRUTH_STATES = (
    "SAT_WITNESS_VERIFIED", "UNSAT_PROOF_VERIFIED", "UNKNOWN_RESOURCE_LIMIT",
    "PROOF_PRODUCER_FAILURE", "PROOF_CHECKER_FAILURE", "WITNESS_VALIDATION_FAILURE",
    "GENERATOR_INTEGRITY_FAIL", "OPEN_UNVERIFIED",
)
EXPECTED_ANCESTRY = {
    "INFRASTRUCTURE_PARENT_HEAD": "33446263c7780d151dc9131bf4f8ae5d7ee10f60",
    "USF_R0_PREREG_COMMIT": "542422a741c151cafc03191aaa5808ab46dfa9a0",
    "TRUTH_PINNING_COMMIT": "08d34d7dde07188eb82ad8dc7c87281a38559c46",
    "BINARY_COMPLETION_COMMIT": "194143902497e65c225b76ba1f2b267d8b3114e7",
    "MANDATORY_SELF_TEST_COMPLETION_COMMIT": "33446263c7780d151dc9131bf4f8ae5d7ee10f60",
}
EXPECTED_CADICAL = "d258dc72e4ec52d434a29f3b2c44dcfd800c10f898cce783f2bf6755b711fb39"
EXPECTED_LRAT = "35caa09cb09bc24178ccbddafaedac1f5774190e3ac3d8c9f03cf11e133dee8c"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assignments(path: Path) -> dict:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        out[target.id] = ast.literal_eval(node.value)
                    except Exception:
                        pass
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            try:
                out[node.target.id] = ast.literal_eval(node.value)
            except Exception:
                pass
    return out


def eq(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected={expected!r} observed={actual!r}")


def independent_canonical_dimacs(clauses) -> bytes:
    def lit_key(l):
        return (abs(l), 1 if l < 0 else 0)
    normalized = {tuple(sorted(set(map(int, c)), key=lit_key)) for c in clauses}
    formula = tuple(sorted(normalized))
    max_var = max((abs(l) for c in formula for l in c), default=0)
    lines = [f"p cnf {max_var} {len(formula)}"]
    for clause in formula:
        lines.append((" ".join(str(x) for x in clause) + " 0") if clause else "0")
    return ("\n".join(lines) + "\n").encode("ascii")


def expected_discovery_schedule() -> list[str]:
    ids = []
    for family, variants in (
        ("A1_2SAT_EQUIVALENCE_RING", ("SAT", "UNSAT")),
        ("A2_HORN_FORWARD_CHAIN", ("SAT", "UNSAT")),
        ("A3_RENAMABLE_HORN_FLIPPED_WIDTH3", ("SAT",)),
    ):
        for n in (32, 64, 128, 256, 512):
            for variant in variants:
                ids.append(f"USF-R0|DISCOVERY|A|{family}|CALIBRATION|{variant}|n={n}")
    for k in (16, 32, 64, 128, 256):
        for variant in ("SAT", "UNSAT"):
            ids.append(f"USF-R0|DISCOVERY|A|A4_AFFINE_TSEITIN_CIRCULAR_LADDER|CALIBRATION|{variant}|k={k}")
    ids.append("USF-R0|DISCOVERY|A|A5_HISTORICAL_R38|SEALED_REPLAY|REPLAY|sealed=NONE")
    for n in (48, 72, 96, 144, 192, 288, 384):
        for cohort in ("B1_BALANCED_BLIND", "B2_HASH_PLANTED_SAT"):
            ids.append(f"USF-R0|DISCOVERY|B|B_HASHED_REGULAR_3CNF_D15|{cohort}|n={n}")
    for n in (24, 36, 48, 72, 96, 144):
        for cohort in ("C1_CUBIC_HASH_BLIND", "C2_CUBIC_PLANTED_EXACT_ONE"):
            ids.append(f"USF-R0|DISCOVERY|C|CUBIC_MONOTONE_1_IN_3_SAT|{cohort}|n={n}")
    return ids


def expected_holdout_schedule() -> list[str]:
    ids = []
    for family, variants in (
        ("A1_2SAT_EQUIVALENCE_RING", ("SAT", "UNSAT")),
        ("A2_HORN_FORWARD_CHAIN", ("SAT", "UNSAT")),
        ("A3_RENAMABLE_HORN_FLIPPED_WIDTH3", ("SAT",)),
    ):
        for n in (768, 1024):
            for variant in variants:
                ids.append(f"USF-R0|HOLDOUT|A|{family}|CALIBRATION|{variant}|n={n}")
    for k in (384, 512):
        for variant in ("SAT", "UNSAT"):
            ids.append(f"USF-R0|HOLDOUT|A|A4_AFFINE_TSEITIN_CIRCULAR_LADDER|CALIBRATION|{variant}|k={k}")
    for n in (576, 768, 1152):
        for cohort in ("B1_BALANCED_BLIND", "B2_HASH_PLANTED_SAT"):
            ids.append(f"USF-R0|HOLDOUT|B|B_HASHED_REGULAR_3CNF_D15|{cohort}|n={n}")
    for n in (192, 288, 384):
        for cohort in ("C1_CUBIC_HASH_BLIND", "C2_CUBIC_PLANTED_EXACT_ONE"):
            ids.append(f"USF-R0|HOLDOUT|C|CUBIC_MONOTONE_1_IN_3_SAT|{cohort}|n={n}")
    return ids


def run_json(argv, cwd):
    cp = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, check=False)
    if cp.returncode != 0:
        raise AssertionError(f"subprocess rc={cp.returncode}: {cp.stderr}")
    return json.loads(cp.stdout)


def verify(root: Path) -> dict:
    source_receipts = {}
    for rel, expected in EXPECTED_BLOBS.items():
        p = root / rel
        if not p.is_file():
            raise AssertionError(f"missing pinned source {rel}")
        observed = git_blob_sha1(p)
        eq(observed, expected, f"git blob {rel}")
        source_receipts[rel] = {"git_blob": observed, "sha256_source_bytes": sha256(p)}

    core = assignments(root / CORE_HARNESS_PATH)
    gen = assignments(root / GENERATOR_PATH)
    entry = assignments(root / FROZEN_ENTRYPOINT_PATH)
    eq(tuple(core["CAUSAL_ORDER"]), EXPECTED_CAUSAL_ORDER, "causal order")
    eq(tuple(core["TERMINAL_CATALOGUE"]), EXPECTED_TERMINALS, "terminal catalogue")
    eq(tuple(core["TRUTH_STATES"]), EXPECTED_TRUTH_STATES, "truth states")
    eq(core["CADICAL_SHA256"], EXPECTED_CADICAL, "CaDiCaL executable")
    eq(core["LRAT_CHECK_SHA256"], EXPECTED_LRAT, "lrat-check executable")
    for key, value in EXPECTED_ANCESTRY.items():
        eq(core[key], value, key)
    eq(gen["PREREG_COMMIT"], EXPECTED_ANCESTRY["USF_R0_PREREG_COMMIT"], "generator prereg")
    eq(gen["B_BASE_SEED"], "JANUS-USF-R0-LANE-B-D15", "B seed")
    eq(gen["C1_BASE_SEED"], "JANUS-USF-R0-LANE-C-CUBIC", "C1 seed")
    eq(tuple(gen["B_DISCOVERY_N"]), (48,72,96,144,192,288,384), "B discovery")
    eq(tuple(gen["B_HOLDOUT_N"]), (576,768,1152), "B holdout")
    eq(tuple(gen["C_DISCOVERY_N"]), (24,36,48,72,96,144), "C discovery")
    eq(tuple(gen["C_HOLDOUT_N"]), (192,288,384), "C holdout")
    eq(entry["CORE_HARNESS_BLOB"], CORE_HARNESS_BLOB, "entrypoint core pin")
    eq(entry["GENERATOR_BLOB"], GENERATOR_BLOB, "entrypoint generator pin")
    eq(entry["A5_SOURCE_COMMIT"], "0b941a484143aa130bad9f7bdf9ca94fbbff79cb", "A5 source")
    eq(entry["A5_EXPECTED_INITIAL_CLV"], [118,354,28], "A5 initial CLV")
    eq(entry["A5_EXPECTED_INTERNAL_RESIDUAL_SHA256"],
       "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95",
       "A5 residual")

    fixture = ((3, -1, 3, 2), (2, -1), (2, -1))
    fixture_sha = hashlib.sha256(independent_canonical_dimacs(fixture)).hexdigest()
    generator_test = run_json([sys.executable, str(root / GENERATOR_PATH)], root)
    harness_test = run_json([
        sys.executable, str(root / FROZEN_ENTRYPOINT_PATH), "--root", str(root),
        "--synthetic-self-test"
    ], root)
    schedule = run_json([
        sys.executable, str(root / FROZEN_ENTRYPOINT_PATH), "--root", str(root),
        "--print-schedule"
    ], root)

    eq(generator_test["canonical_dimacs_fixture_sha256"], fixture_sha,
       "independent canonical DIMACS fixture")
    eq(generator_test["generated_real_USF_instances"], 0, "generator real count")
    eq(harness_test["generated_real_USF_instances"], 0, "harness real count")
    eq(harness_test["generated_lane_A_instances"], 0, "Lane A count")
    eq(harness_test["generated_lane_B_instances"], 0, "Lane B count")
    eq(harness_test["generated_lane_C_instances"], 0, "Lane C count")
    eq(harness_test["discovery_execution_started"], False, "discovery started")
    eq(harness_test["holdout_execution_started"], False, "holdout started")
    eq(harness_test["truth_oracle_invoked"], False, "truth invoked")
    eq(harness_test["synthetic_width_interval"], [-1, -1], "empty width binding")
    eq(schedule["discovery_order"], expected_discovery_schedule(), "discovery order")
    eq(schedule["holdout_order_frozen_but_unopened"], expected_holdout_schedule(), "holdout order")
    eq(schedule["generated_real_USF_instances"], 0, "schedule real count")
    eq(schedule["discovery_execution_started"], False, "schedule discovery flag")
    eq(schedule["holdout_execution_started"], False, "schedule holdout flag")

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "EXECUTION_HARNESS_FREEZE_SYNTHETIC_VERIFICATION_PASS",
        "canonical_entrypoint": FROZEN_ENTRYPOINT_PATH,
        "source_receipts": source_receipts,
        "canonical_serialization_independent_fixture_sha256": fixture_sha,
        "discovery_schedule_count": len(schedule["discovery_order"]),
        "holdout_schedule_count_frozen_but_unopened": len(schedule["holdout_order_frozen_but_unopened"]),
        "implementation_binding_empty_graph_width_minus_one_verified": True,
        "A5_historical_replay_binding_ast_verified": True,
        "generated_real_USF_instances": 0,
        "generated_lane_A_instances": 0,
        "generated_lane_B_instances": 0,
        "generated_lane_C_instances": 0,
        "discovery_execution_started": False,
        "holdout_execution_started": False,
        "truth_oracle_invoked_by_freeze_verifier": False,
        "finite_experiment_is_asymptotic_authority": False,
        "H1": "OPEN", "H2": "OPEN", "H3": "OPEN",
        "SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "BA26_STARTED": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument("--output")
    args = p.parse_args()
    out = verify(Path(args.root).resolve())
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
