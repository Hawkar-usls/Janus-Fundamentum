from __future__ import annotations

"""Frozen generators and canonical serialization for JANUS/TRUMP USF R0.

FREEZE-ONLY SOURCE.  Importing this module never generates a scheduled USF
instance.  A caller must explicitly request a frozen ScheduledInstance.
"""

from dataclasses import dataclass
import hashlib
import itertools
from typing import Iterable, Sequence

SCHEMA = "TRUMP_USF_R0_FROZEN_GENERATORS"
VERSION = "1.0"
PREREG_COMMIT = "542422a741c151cafc03191aaa5808ab46dfa9a0"
PREREG_BLOB = "fda7092ec377b18abc0bc192d36610cca2e9f904"

NO_RANDOM_SEED = "NO_RANDOM_SEED__DETERMINISTIC_CONSTRUCTION"
C2_SEED_DESCRIPTOR = "NO_ADDITIONAL_SEED__JANUS-C2-TRUESET_HASH_DOMAIN"

DISCOVERY_EXECUTION_ORDER = (
    "LANE_A_CALIBRATION_POSITIVE_CONTROLS",
    "LANE_B_ADVERSARIAL_GENERAL_3CNF",
    "LANE_C_STRUCTURED_NP_HARD_STRESS",
)
HOLDOUT_RELEASE_RULE = (
    "do not execute holdout sizes until any candidate family-level theorem or "
    "separator-destruction lemma statement, constants, and proof obligations "
    "have been frozen in a separate append-only candidate-theorem preregistration"
)

A_DISCOVERY = (32, 64, 128, 256, 512)
A_HOLDOUT = (768, 1024)
A4_DISCOVERY_K = (16, 32, 64, 128, 256)
A4_HOLDOUT_K = (384, 512)
B_DISCOVERY_N = (48, 72, 96, 144, 192, 288, 384)
B_HOLDOUT_N = (576, 768, 1152)
C_DISCOVERY_N = (24, 36, 48, 72, 96, 144)
C_HOLDOUT_N = (192, 288, 384)

B_BASE_SEED = "JANUS-USF-R0-LANE-B-D15"
C1_BASE_SEED = "JANUS-USF-R0-LANE-C-CUBIC"

Literal = int
Clause = tuple[Literal, ...]
Formula = tuple[Clause, ...]
Token = tuple[int, int]


class GeneratorIntegrityError(RuntimeError):
    verdict = "GENERATOR_INTEGRITY_FAIL"


@dataclass(frozen=True)
class ScheduledInstance:
    scheduled_instance_id: str
    phase: str
    lane: str
    family_id: str
    cohort: str
    size_parameter_name: str
    size_parameter: int | None
    frozen_seed_string: str
    variant: str | None = None


@dataclass(frozen=True)
class GeneratedFormula:
    schedule: ScheduledInstance
    formula: Formula
    generator_integrity_status: str
    generator_spec_version: str = VERSION


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def lit_key(lit: int) -> tuple[int, int]:
    lit = int(lit)
    if lit == 0:
        raise GeneratorIntegrityError("literal zero is DIMACS terminator, not a literal")
    return (abs(lit), 1 if lit < 0 else 0)


def canonical_clause(clause: Iterable[int]) -> Clause:
    """Structural canonicalization: duplicate literals collapse; tautologies remain."""
    return tuple(sorted(set(int(x) for x in clause), key=lit_key))


def canonical_formula(clauses: Iterable[Iterable[int]]) -> Formula:
    """R33-compatible structural normalization and deterministic clause ordering."""
    unique = {canonical_clause(c) for c in clauses}
    return tuple(sorted(unique))


def formula_counts(formula: Formula) -> tuple[int, int, int]:
    variables = {abs(lit) for clause in formula for lit in clause}
    return len(formula), sum(len(c) for c in formula), len(variables)


def canonical_dimacs_bytes(clauses: Iterable[Iterable[int]]) -> bytes:
    """Canonical USF-R0 scientific serialization.

    Structural normalization is canonical_formula above. DIMACS variables are
    positive 1-based integer ids. Header nvars is max used variable id, or 0
    for empty formula. There are no comments or extra whitespace. Each clause
    is its canonical literal sequence followed by " 0"; an empty clause is
    "0". Encoding is ASCII, line ending is LF (0x0a), and one final LF is
    mandatory.
    """
    formula = canonical_formula(clauses)
    max_var = max((abs(l) for c in formula for l in c), default=0)
    lines = [f"p cnf {max_var} {len(formula)}"]
    for clause in formula:
        if clause:
            lines.append(" ".join(str(x) for x in clause) + " 0")
        else:
            lines.append("0")
    return ("\n".join(lines) + "\n").encode("ascii")


def canonical_dimacs_sha256(clauses: Iterable[Iterable[int]]) -> str:
    return hashlib.sha256(canonical_dimacs_bytes(clauses)).hexdigest()


def _schedule_id(phase: str, lane: str, family: str, cohort: str, size_name: str,
                 size: int | None, variant: str | None = None) -> str:
    fields = ["USF-R0", phase, lane, family, cohort]
    if variant:
        fields.append(variant)
    fields.append(f"{size_name}={size}" if size is not None else f"{size_name}=NONE")
    return "|".join(fields)


def _a_records(phase: str) -> list[ScheduledInstance]:
    sizes = A_DISCOVERY if phase == "DISCOVERY" else A_HOLDOUT
    a4_sizes = A4_DISCOVERY_K if phase == "DISCOVERY" else A4_HOLDOUT_K
    out: list[ScheduledInstance] = []
    for family, variants in (
        ("A1_2SAT_EQUIVALENCE_RING", ("SAT", "UNSAT")),
        ("A2_HORN_FORWARD_CHAIN", ("SAT", "UNSAT")),
        ("A3_RENAMABLE_HORN_FLIPPED_WIDTH3", ("SAT",)),
    ):
        for n in sizes:
            for variant in variants:
                out.append(ScheduledInstance(
                    _schedule_id(phase, "A", family, "CALIBRATION", "n", n, variant),
                    phase, "A", family, "CALIBRATION", "n", n,
                    NO_RANDOM_SEED, variant,
                ))
    for k in a4_sizes:
        for variant in ("SAT", "UNSAT"):
            out.append(ScheduledInstance(
                _schedule_id(phase, "A", "A4_AFFINE_TSEITIN_CIRCULAR_LADDER", "CALIBRATION", "k", k, variant),
                phase, "A", "A4_AFFINE_TSEITIN_CIRCULAR_LADDER",
                "CALIBRATION", "k", k, NO_RANDOM_SEED, variant,
            ))
    if phase == "DISCOVERY":
        out.append(ScheduledInstance(
            _schedule_id(phase, "A", "A5_HISTORICAL_R38", "SEALED_REPLAY", "sealed", None, "REPLAY"),
            phase, "A", "A5_HISTORICAL_R38", "SEALED_REPLAY", "sealed", None,
            "SEALED_HISTORICAL_R38_SEED_36001", "REPLAY",
        ))
    return out


def _b_records(phase: str) -> list[ScheduledInstance]:
    sizes = B_DISCOVERY_N if phase == "DISCOVERY" else B_HOLDOUT_N
    out = []
    for n in sizes:
        for cohort in ("B1_BALANCED_BLIND", "B2_HASH_PLANTED_SAT"):
            out.append(ScheduledInstance(
                _schedule_id(phase, "B", "B_HASHED_REGULAR_3CNF_D15", cohort, "n", n),
                phase, "B", "B_HASHED_REGULAR_3CNF_D15", cohort, "n", n, B_BASE_SEED,
            ))
    return out


def _c_records(phase: str) -> list[ScheduledInstance]:
    sizes = C_DISCOVERY_N if phase == "DISCOVERY" else C_HOLDOUT_N
    out = []
    for n in sizes:
        for cohort, seed in (
            ("C1_CUBIC_HASH_BLIND", C1_BASE_SEED),
            ("C2_CUBIC_PLANTED_EXACT_ONE", C2_SEED_DESCRIPTOR),
        ):
            out.append(ScheduledInstance(
                _schedule_id(phase, "C", "CUBIC_MONOTONE_1_IN_3_SAT", cohort, "n", n),
                phase, "C", "CUBIC_MONOTONE_1_IN_3_SAT", cohort, "n", n, seed,
            ))
    return out


DISCOVERY_SCHEDULE: tuple[ScheduledInstance, ...] = tuple(
    _a_records("DISCOVERY") + _b_records("DISCOVERY") + _c_records("DISCOVERY")
)
HOLDOUT_SCHEDULE_FROZEN_BUT_UNOPENED: tuple[ScheduledInstance, ...] = tuple(
    _a_records("HOLDOUT") + _b_records("HOLDOUT") + _c_records("HOLDOUT")
)


def scheduled_instance(instance_id: str, *, allow_holdout: bool = False) -> ScheduledInstance:
    for rec in DISCOVERY_SCHEDULE:
        if rec.scheduled_instance_id == instance_id:
            return rec
    for rec in HOLDOUT_SCHEDULE_FROZEN_BUT_UNOPENED:
        if rec.scheduled_instance_id == instance_id:
            if not allow_holdout:
                raise GeneratorIntegrityError("HOLDOUT_UNOPENED_BY_R0_RELEASE_RULE")
            return rec
    raise GeneratorIntegrityError("UNKNOWN_SCHEDULED_INSTANCE_ID")


def _digest_order_key(seed: str, n: int, d: int, token: Token) -> tuple[str, int, int]:
    v, r = token
    digest = sha256_text(f"{seed}|{n}|{d}|{v}|{r}")
    return digest, v, r


def _triple_vars(stream: Sequence[Token], clause_index: int) -> tuple[int, int, int]:
    base = 3 * clause_index
    return tuple(sorted(stream[base + j][0] for j in range(3)))


def hash_config_3(seed_string: str, n_variables: int, variable_degree_d: int) -> tuple[tuple[Token, Token, Token], ...]:
    """Exact HASH_CONFIG_3 implementation binding for USF R0.

    Repeated-variable clauses are repaired first. A pre-existing duplicate
    simple triple is also treated as a collision; its leftmost token is the
    offending token. This enforces the preregistered simple-incidence
    postcondition. No reseeding occurs.
    """
    n, d = int(n_variables), int(variable_degree_d)
    if n <= 0 or d <= 0 or (d * n) % 3:
        raise GeneratorIntegrityError("HASH_CONFIG_3_PRECONDITION_FAIL")
    stream: list[Token] = [(v, r) for v in range(n) for r in range(d)]
    stream.sort(key=lambda t: _digest_order_key(seed_string, n, d, t))
    m = len(stream) // 3
    prior: set[tuple[int, int, int]] = set()

    for ci in range(m):
        base = 3 * ci
        vars_now = [stream[base + j][0] for j in range(3)]
        triple = tuple(sorted(vars_now))
        repeated = len(set(vars_now)) != 3
        duplicate = triple in prior
        if repeated or duplicate:
            if repeated:
                counts = {v: vars_now.count(v) for v in set(vars_now)}
                offending_local = next(j for j, v in enumerate(vars_now) if counts[v] > 1)
            else:
                offending_local = 0
            offending = base + offending_local
            repaired = False
            for later in range(base + 3, len(stream)):
                stream[offending], stream[later] = stream[later], stream[offending]
                candidate = _triple_vars(stream, ci)
                if len(set(candidate)) == 3 and candidate not in prior:
                    repaired = True
                    break
                stream[offending], stream[later] = stream[later], stream[offending]
            if not repaired:
                raise GeneratorIntegrityError(f"HASH_CONFIG_3_COLLISION_REPAIR_FAIL:clause={ci}")
            triple = _triple_vars(stream, ci)
        if len(set(triple)) != 3 or triple in prior:
            raise GeneratorIntegrityError(f"HASH_CONFIG_3_SIMPLE_POSTCONDITION_FAIL:clause={ci}")
        prior.add(triple)

    degree = [0] * n
    clauses = []
    for ci in range(m):
        row = tuple(stream[3 * ci + j] for j in range(3))
        row = tuple(sorted(row, key=lambda t: t[0]))
        for v, _ in row:
            degree[v] += 1
        clauses.append(row)
    if degree != [d] * n:
        raise GeneratorIntegrityError("HASH_CONFIG_3_DEGREE_PRESERVATION_FAIL")
    return tuple(clauses)


def _signed_lit(v0: int, positive: bool) -> int:
    x = v0 + 1
    return x if positive else -x


def _b_balanced_positive(n: int, v: int, r: int) -> bool:
    positive = r <= 6
    flip = int(sha256_text(f"JANUS-B1-VFLIP|{n}|{v}")[-1], 16) & 1
    return not positive if flip else positive


def generate_b(record: ScheduledInstance) -> Formula:
    if record.family_id != "B_HASHED_REGULAR_3CNF_D15" or record.size_parameter is None:
        raise GeneratorIntegrityError("B_RECORD_INVALID")
    n = record.size_parameter
    triples = hash_config_3(B_BASE_SEED, n, 15)
    clauses: list[list[int]] = []
    if record.cohort == "B1_BALANCED_BLIND":
        for row in triples:
            clauses.append([_signed_lit(v, _b_balanced_positive(n, v, r)) for v, r in row])
    elif record.cohort == "B2_HASH_PLANTED_SAT":
        plant = {v: bool(int(sha256_text(f"JANUS-B2-PLANT|{n}|{v}")[-1], 16) & 1) for v in range(n)}
        for ci, row in enumerate(triples):
            lits = [_signed_lit(v, _b_balanced_positive(n, v, r)) for v, r in row]
            def lit_true(lit: int) -> bool:
                value = plant[abs(lit) - 1]
                return value if lit > 0 else not value
            if not any(lit_true(l) for l in lits):
                p = int(sha256_text(f"JANUS-B2-FIX|{n}|{ci}")[:2], 16) % 3
                lits[p] = -lits[p]
            if not any(lit_true(l) for l in lits):
                raise GeneratorIntegrityError(f"B2_PLANT_REPAIR_FAIL:clause={ci}")
            clauses.append(lits)
    else:
        raise GeneratorIntegrityError("B_COHORT_INVALID")
    f = canonical_formula(clauses)
    c, l, v = formula_counts(f)
    if (c, l, v) != (5 * n, 15 * n, n):
        raise GeneratorIntegrityError(f"B_COUNTS_FAIL:{(c,l,v)}")
    return f


def _exact_one_cnf(triples: Iterable[tuple[int, int, int]]) -> Formula:
    clauses = []
    for a0, b0, c0 in triples:
        a, b, c = a0 + 1, b0 + 1, c0 + 1
        clauses.extend(((a, b, c), (-a, -b), (-a, -c), (-b, -c)))
    return canonical_formula(clauses)


def generate_c1(record: ScheduledInstance) -> Formula:
    if record.cohort != "C1_CUBIC_HASH_BLIND" or record.size_parameter is None:
        raise GeneratorIntegrityError("C1_RECORD_INVALID")
    n = record.size_parameter
    token_triples = hash_config_3(C1_BASE_SEED, n, 3)
    triples = [tuple(v for v, _ in row) for row in token_triples]
    f = _exact_one_cnf(triples)
    _, _, v = formula_counts(f)
    if v != n:
        raise GeneratorIntegrityError("C1_VARIABLE_COUNT_FAIL")
    occ = {x: 0 for x in range(1, n + 1)}
    for clause in f:
        for lit in clause:
            occ[abs(lit)] += 1
    if any(occ[x] != 9 for x in occ):
        raise GeneratorIntegrityError("C1_CNF_OCCURRENCE_FAIL")
    return f


def _c2_rank(n: int, v: int) -> tuple[str, int]:
    return sha256_text(f"JANUS-C2-TRUESET|{n}|{v}"), v


def _repair_c2_false_stream(true_tokens: Sequence[Token], false_stream: list[Token]) -> tuple[tuple[Token, Token, Token], ...]:
    nclauses = len(true_tokens)
    prior: set[tuple[int, int, int]] = set()
    for ci in range(nclauses):
        t = true_tokens[ci]
        b = 2 * ci
        f1, f2 = false_stream[b], false_stream[b + 1]
        triple = tuple(sorted((t[0], f1[0], f2[0])))
        invalid = len(set(triple)) != 3 or triple in prior
        if invalid:
            offending = b
            repaired = False
            for later in range(b + 2, len(false_stream)):
                false_stream[offending], false_stream[later] = false_stream[later], false_stream[offending]
                f1, f2 = false_stream[b], false_stream[b + 1]
                cand = tuple(sorted((t[0], f1[0], f2[0])))
                if len(set(cand)) == 3 and cand not in prior:
                    repaired = True
                    triple = cand
                    break
                false_stream[offending], false_stream[later] = false_stream[later], false_stream[offending]
            if not repaired:
                raise GeneratorIntegrityError(f"C2_COLLISION_REPAIR_FAIL:clause={ci}")
        prior.add(triple)
    return tuple((true_tokens[i], false_stream[2*i], false_stream[2*i+1]) for i in range(nclauses))


def generate_c2(record: ScheduledInstance) -> Formula:
    if record.cohort != "C2_CUBIC_PLANTED_EXACT_ONE" or record.size_parameter is None:
        raise GeneratorIntegrityError("C2_RECORD_INVALID")
    n = record.size_parameter
    if n % 3:
        raise GeneratorIntegrityError("C2_N_NOT_DIVISIBLE_BY_3")
    ranked = sorted(range(n), key=lambda v: _c2_rank(n, v))
    true_vars = set(ranked[: n // 3])
    true_tokens = [(v, r) for v in true_vars for r in range(3)]
    false_tokens = [(v, r) for v in range(n) if v not in true_vars for r in range(3)]
    true_tokens.sort(key=lambda t: (_c2_rank(n, t[0])[0], t[0], t[1]))
    false_tokens.sort(key=lambda t: (_c2_rank(n, t[0])[0], t[0], t[1]))
    token_triples = _repair_c2_false_stream(true_tokens, false_tokens)
    triples = [tuple(v for v, _ in row) for row in token_triples]
    f = _exact_one_cnf(triples)

    assignment = {v + 1: (v in true_vars) for v in range(n)}
    for triple in triples:
        if sum(1 for v in triple if v in true_vars) != 1:
            raise GeneratorIntegrityError("C2_SOURCE_EXACT_ONE_PLANT_FAIL")
    for clause in f:
        if not any(assignment[abs(l)] == (l > 0) for l in clause):
            raise GeneratorIntegrityError("C2_ENCODED_CNF_PLANT_FAIL")
    occ = {x: 0 for x in range(1, n + 1)}
    for clause in f:
        for lit in clause:
            occ[abs(lit)] += 1
    if any(occ[x] != 9 for x in occ):
        raise GeneratorIntegrityError("C2_CNF_OCCURRENCE_FAIL")
    return f


def generate_a(record: ScheduledInstance) -> Formula:
    if record.size_parameter is None:
        if record.family_id == "A5_HISTORICAL_R38":
            raise GeneratorIntegrityError("A5_IS_SEALED_REPLAY_NOT_GENERATION")
        raise GeneratorIntegrityError("A_SIZE_MISSING")
    n = record.size_parameter
    family, variant = record.family_id, record.variant
    clauses: list[tuple[int, ...]] = []

    if family == "A1_2SAT_EQUIVALENCE_RING":
        for i in range(n - 1):
            a, b = i + 1, i + 2
            clauses += [(-a, b), (a, -b)]
        a, b = n, 1
        if variant == "SAT":
            clauses += [(-a, b), (a, -b)]
        elif variant == "UNSAT":
            clauses += [(-a, -b), (a, b)]
        else:
            raise GeneratorIntegrityError("A1_VARIANT")
    elif family == "A2_HORN_FORWARD_CHAIN":
        clauses += [(-(i + 1), -(i + 2), i + 3) for i in range(n - 2)]
        clauses += [(1,), (2,)]
        if variant == "UNSAT":
            clauses.append((-n,))
        elif variant != "SAT":
            raise GeneratorIntegrityError("A2_VARIANT")
    elif family == "A3_RENAMABLE_HORN_FLIPPED_WIDTH3":
        if variant != "SAT":
            raise GeneratorIntegrityError("A3_VARIANT")
        for i in range(n - 2):
            row = [-(i + 1), -(i + 2), i + 3]
            out = []
            for lit in row:
                zero_based = abs(lit) - 1
                out.append(-lit if zero_based % 3 == 0 else lit)
            clauses.append(tuple(out))
    elif family == "A4_AFFINE_TSEITIN_CIRCULAR_LADDER":
        k = n
        vertices = [(layer, i) for layer in (0, 1) for i in range(k)]
        edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
        def add_edge(u, v):
            edges.add(tuple(sorted((u, v))))
        for i in range(k):
            add_edge((0, i), (0, (i + 1) % k))
            add_edge((1, i), (1, (i + 1) % k))
            add_edge((0, i), (1, i))
        edge_list = sorted(edges)
        if len(edge_list) != 3 * k:
            raise GeneratorIntegrityError("A4_EDGE_COUNT_FAIL")
        edge_var = {e: j + 1 for j, e in enumerate(edge_list)}
        incident = {v: [] for v in vertices}
        for e, x in edge_var.items():
            u, v = e
            incident[u].append(x)
            incident[v].append(x)
        charges = {v: 0 for v in vertices}
        if variant == "UNSAT":
            charges[(0, 0)] = 1
        elif variant != "SAT":
            raise GeneratorIntegrityError("A4_VARIANT")
        for vertex in sorted(vertices):
            xs = sorted(incident[vertex])
            if len(xs) != 3:
                raise GeneratorIntegrityError("A4_NOT_3_REGULAR")
            target = charges[vertex]
            for bits in itertools.product((0, 1), repeat=3):
                if sum(bits) % 2 == target:
                    continue
                clauses.append(tuple(x if bit == 0 else -x for x, bit in zip(xs, bits)))
    else:
        raise GeneratorIntegrityError("UNKNOWN_LANE_A_FAMILY")
    return canonical_formula(clauses)


def generate(record: ScheduledInstance) -> GeneratedFormula:
    if record.phase != "DISCOVERY":
        raise GeneratorIntegrityError("HOLDOUT_EXECUTION_FORBIDDEN_UNTIL_RELEASE_GATE")
    if record.lane == "A":
        formula = generate_a(record)
    elif record.lane == "B":
        formula = generate_b(record)
    elif record.lane == "C" and record.cohort == "C1_CUBIC_HASH_BLIND":
        formula = generate_c1(record)
    elif record.lane == "C" and record.cohort == "C2_CUBIC_PLANTED_EXACT_ONE":
        formula = generate_c2(record)
    else:
        raise GeneratorIntegrityError("UNKNOWN_GENERATOR_ROUTE")
    return GeneratedFormula(record, formula, "PASS")


def synthetic_self_test() -> dict:
    """Infrastructure-only micro-fixtures; never calls generate() or frozen USF seeds."""
    synthetic_seed = "SYNTHETIC-INFRASTRUCTURE-ONLY-NOT-USF"
    triples = hash_config_3(synthetic_seed, 12, 3)
    flat = [t for row in triples for t in row]
    degree = {v: 0 for v in range(12)}
    for v, _ in flat:
        degree[v] += 1
    fixture = ((3, -1, 3, 2), (2, -1), (2, -1))
    b1 = canonical_dimacs_bytes(fixture)
    b2 = canonical_dimacs_bytes(reversed(fixture))
    assert b1 == b2
    assert b1.endswith(b"\n") and b"\r" not in b1
    assert all(x == 3 for x in degree.values())
    assert len({tuple(sorted(v for v, _ in row)) for row in triples}) == len(triples)
    assert not any(s in synthetic_seed for s in (B_BASE_SEED, C1_BASE_SEED, "JANUS-C2-TRUESET"))
    return {
        "schema": "TRUMP_USF_R0_FROZEN_GENERATOR_SYNTHETIC_SELF_TEST",
        "pass": True,
        "generated_real_USF_instances": 0,
        "scheduled_instance_generate_function_called": False,
        "discovery_execution_started": False,
        "synthetic_seed": synthetic_seed,
        "synthetic_hash_config_n": 12,
        "synthetic_hash_config_d": 3,
        "canonical_dimacs_fixture_sha256": hashlib.sha256(b1).hexdigest(),
        "finite_experiment_is_asymptotic_authority": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(synthetic_self_test(), indent=2, sort_keys=True))
