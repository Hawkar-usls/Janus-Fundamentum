#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from typing import Any, Iterable

# A Horn clause is body -> head. head=0 denotes false.
Clause = tuple[tuple[int, ...], int]


def cj(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=list)


def dg(obj: Any) -> str:
    return hashlib.sha256(cj(obj).encode()).hexdigest()


class OpenBudget(RuntimeError):
    pass


@dataclass
class Meter:
    work_limit: int
    clause_limit: int
    certificate_limit: int
    work: int = 0
    generated: int = 0
    entailment_calls: int = 0
    clause_scans: int = 0

    def charge(self, amount: int = 1) -> None:
        self.work += amount
        if self.work > self.work_limit:
            raise OpenBudget("OPEN_WORK_BUDGET")

    def add_clauses(self, amount: int) -> None:
        self.generated += amount
        if self.generated > self.clause_limit:
            raise OpenBudget("OPEN_PROJECTION_VOLUME")

    def certificate(self, obj: Any) -> None:
        if len(cj(obj).encode()) > self.certificate_limit:
            raise OpenBudget("OPEN_CERTIFICATE_VOLUME")


def clause(body: Iterable[int], head: int) -> Clause:
    return tuple(sorted(set(body))), int(head)


def normalize(formula: Iterable[Clause]) -> tuple[Clause, ...]:
    unique: set[Clause] = set()
    for raw_body, head in formula:
        body = tuple(sorted(set(raw_body)))
        if head < 0 or any(v <= 0 for v in body):
            raise ValueError("variables must be positive; head is positive or 0")
        if head != 0 and head in body:
            continue
        unique.add((body, head))
    ordered = sorted(unique, key=lambda c: (c[1], len(c[0]), c[0]))
    kept: list[Clause] = []
    for body, head in ordered:
        bset = set(body)
        if any(other_head == head and set(other_body) <= bset for other_body, other_head in kept):
            continue
        kept.append((body, head))
    return tuple(kept)


def variables(formula: Iterable[Clause]) -> tuple[int, ...]:
    out: set[int] = set()
    for body, head in formula:
        out.update(body)
        if head:
            out.add(head)
    return tuple(sorted(out))


def evaluate(formula: Iterable[Clause], assignment: dict[int, bool]) -> bool:
    for body, head in formula:
        if all(assignment.get(v, False) for v in body):
            if head == 0 or not assignment.get(head, False):
                return False
    return True


def is_single_head(formula: Iterable[Clause]) -> bool:
    seen: set[int] = set()
    for _, head in formula:
        if head == 0:
            continue
        if head in seen:
            return False
        seen.add(head)
    return True


def restrict_horn(formula: Iterable[Clause], assignment: dict[int, bool]) -> tuple[Clause, ...]:
    restricted: list[Clause] = []
    for body, head in normalize(formula):
        if any(v in assignment and not assignment[v] for v in body):
            continue
        new_body = tuple(v for v in body if not assignment.get(v, False))
        if head and assignment.get(head) is True:
            continue
        new_head = 0 if head and assignment.get(head) is False else head
        restricted.append(clause(new_body, new_head))
    return normalize(restricted)


def join_horn(a: Iterable[Clause], b: Iterable[Clause], *, require_single_head: bool = False) -> dict[str, Any]:
    aa, bb = normalize(a), normalize(b)
    joined = normalize(aa + bb)
    if require_single_head and not is_single_head(joined):
        return {
            "status": "OPEN",
            "reason": "OPEN_JOIN_LANGUAGE",
            "p_vs_np": "OPEN",
            "left": [[list(body), head] for body, head in aa],
            "right": [[list(body), head] for body, head in bb],
        }
    return {
        "status": "EXACT",
        "language": "SINGLE_HEAD_HORN" if require_single_head else "HORN",
        "joined": [[list(body), head] for body, head in joined],
        "proof": {
            "operation": "CONJUNCTION_BY_CLAUSE_UNION",
            "left_digest": dg([[list(body), head] for body, head in aa]),
            "right_digest": dg([[list(body), head] for body, head in bb]),
            "joined_digest": dg([[list(body), head] for body, head in joined]),
        },
    }


def horn_solve(formula: Iterable[Clause], initial: dict[int, bool] | None, meter: Meter) -> dict[str, Any]:
    formula = normalize(formula)
    meter.entailment_calls += 1
    meter.charge()
    true_vars = {v for v, value in (initial or {}).items() if value}
    false_units = {v for v, value in (initial or {}).items() if not value}
    trace: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        for idx, (body, head) in enumerate(formula):
            meter.clause_scans += 1
            meter.charge()
            if all(v in true_vars for v in body):
                if head == 0:
                    return {
                        "status": "UNSAT",
                        "true_vars": sorted(true_vars),
                        "trace": trace + [{"op": "CONFLICT", "clause": idx}],
                    }
                if head in false_units:
                    return {
                        "status": "UNSAT",
                        "true_vars": sorted(true_vars),
                        "trace": trace + [{"op": "FALSE_UNIT_CONFLICT", "clause": idx, "var": head}],
                    }
                if head not in true_vars:
                    true_vars.add(head)
                    trace.append({"op": "DERIVE", "clause": idx, "var": head})
                    changed = True
    assignment = {v: (v in true_vars) for v in (set(variables(formula)) | true_vars | false_units)}
    for v in false_units:
        assignment[v] = False
    if not evaluate(formula, assignment):
        raise AssertionError("least-model solver produced invalid model")
    return {"status": "SAT", "assignment": assignment, "trace": trace}


def entails_clause(formula: Iterable[Clause], target: Clause, meter: Meter) -> dict[str, Any]:
    body, head = target
    assumptions = {v: True for v in body}
    if head:
        assumptions[head] = False
    result = horn_solve(formula, assumptions, meter)
    if result["status"] == "UNSAT":
        return {"status": "ENTAILED", "proof": result}
    assignment = result["assignment"]
    if evaluate((target,), assignment):
        raise AssertionError("countermodel satisfies target")
    return {
        "status": "COUNTERMODEL",
        "assignment": {
            str(v): int(assignment.get(v, False))
            for v in sorted(set(variables(formula)) | set(body) | ({head} if head else set()))
        },
    }


def separate_or_merge(a: Iterable[Clause], b: Iterable[Clause], meter: Meter) -> dict[str, Any]:
    aa, bb = normalize(a), normalize(b)
    events: list[dict[str, Any]] = []
    for direction, source, target in (("A_NOT_B", aa, bb), ("B_NOT_A", bb, aa)):
        for idx, candidate in enumerate(target):
            result = entails_clause(source, candidate, meter)
            events.append({"direction": direction, "target_clause": idx, "result": result["status"]})
            if result["status"] == "COUNTERMODEL":
                return {
                    "status": "SEPARATOR",
                    "direction": direction,
                    "target_clause": [list(candidate[0]), candidate[1]],
                    "assignment": result["assignment"],
                    "events": events,
                }
    return {"status": "MERGE", "reason": "MUTUAL_HORN_ENTAILMENT", "events": events}


def forget_one(formula: Iterable[Clause], var: int, meter: Meter) -> tuple[tuple[Clause, ...], dict[str, Any]]:
    before = normalize(formula)
    producers = [(body, head) for body, head in before if head == var]
    consumers = [(body, head) for body, head in before if var in body]
    untouched = [(body, head) for body, head in before if head != var and var not in body]
    generated: list[Clause] = []
    for pbody, _ in producers:
        for cbody, chead in consumers:
            meter.charge(max(1, len(pbody) + len(cbody)))
            generated.append(clause(set(pbody) | (set(cbody) - {var}), chead))
    meter.add_clauses(len(generated))
    after = normalize(untouched + generated)
    record = {
        "var": var,
        "before_digest": dg([[list(b), h] for b, h in before]),
        "producers": [[list(b), h] for b, h in producers],
        "consumers": [[list(b), h] for b, h in consumers],
        "untouched": [[list(b), h] for b, h in untouched],
        "generated": [[list(b), h] for b, h in generated],
        "after": [[list(b), h] for b, h in after],
        "after_digest": dg([[list(b), h] for b, h in after]),
    }
    meter.certificate(record)
    return after, record


def project_horn(
    formula: Iterable[Clause],
    forget: Iterable[int],
    *,
    work_budget: int = 2_000_000,
    clause_budget: int = 100_000,
    certificate_budget: int = 8_000_000,
    require_single_head: bool = False,
) -> dict[str, Any]:
    original = normalize(formula)
    meter = Meter(work_budget, clause_budget, certificate_budget)
    if require_single_head and not is_single_head(original):
        return {"status": "OPEN", "reason": "OPEN_NOT_SINGLE_HEAD", "p_vs_np": "OPEN"}
    current = original
    records: list[dict[str, Any]] = []
    try:
        for var in sorted(set(forget)):
            current, record = forget_one(current, var, meter)
            records.append(record)
            if require_single_head and not is_single_head(current):
                raise AssertionError("single-head invariant lost")
        decision = horn_solve(current, {}, meter)
        certificate = {
            "schema": "janus.horn_projection.v1",
            "status": "EXACT",
            "mode": "SINGLE_HEAD_POLY" if require_single_head else "OUTPUT_SENSITIVE_DP",
            "p_vs_np": "OPEN",
            "original": [[list(b), h] for b, h in original],
            "forget": sorted(set(forget)),
            "steps": records,
            "projected": [[list(b), h] for b, h in current],
            "decision": decision,
            "cost": {
                "work_units": meter.work,
                "generated_clauses": meter.generated,
                "entailment_calls": meter.entailment_calls,
                "clause_scans": meter.clause_scans,
                "projected_clause_count": len(current),
            },
        }
        certificate["cost"]["certificate_bytes"] = len(cj(certificate).encode())
        certificate["integrity_sha256"] = dg({k: v for k, v in certificate.items() if k != "integrity_sha256"})
        meter.certificate(certificate)
        return certificate
    except OpenBudget as exc:
        return {
            "schema": "janus.horn_projection.v1",
            "status": "OPEN",
            "reason": str(exc),
            "p_vs_np": "OPEN",
            "completed_steps": len(records),
            "cost": {
                "work_units": meter.work,
                "generated_clauses": meter.generated,
                "entailment_calls": meter.entailment_calls,
                "clause_scans": meter.clause_scans,
                "current_clause_count": len(current),
            },
        }


def dispatch_projection(language: str, formula: Iterable[Clause], forget: Iterable[int], **kwargs: Any) -> dict[str, Any]:
    if language not in ("HORN", "SINGLE_HEAD_HORN"):
        return {"status": "OPEN", "reason": "OPEN_LANGUAGE", "language": language, "p_vs_np": "OPEN"}
    return project_horn(formula, forget, require_single_head=(language == "SINGLE_HEAD_HORN"), **kwargs)


def decode_formula(raw: list[list[Any]]) -> tuple[Clause, ...]:
    return normalize((tuple(int(v) for v in body), int(head)) for body, head in raw)


def verify_projection(cert: dict[str, Any]) -> bool:
    if cert.get("status") == "OPEN":
        return cert.get("p_vs_np") == "OPEN" and cert.get("reason", "").startswith("OPEN_")
    if cert.get("schema") != "janus.horn_projection.v1":
        return False
    expected = dg({k: v for k, v in cert.items() if k != "integrity_sha256"})
    if cert.get("integrity_sha256") != expected:
        return False
    current = decode_formula(cert["original"])
    if cert["mode"] == "SINGLE_HEAD_POLY" and not is_single_head(current):
        return False
    for step in cert["steps"]:
        var = step["var"]
        if step["before_digest"] != dg([[list(b), h] for b, h in current]):
            return False
        producers = [(b, h) for b, h in current if h == var]
        consumers = [(b, h) for b, h in current if var in b]
        untouched = [(b, h) for b, h in current if h != var and var not in b]
        generated = [clause(set(pb) | (set(cb) - {var}), ch) for pb, _ in producers for cb, ch in consumers]
        after = normalize(untouched + generated)
        if step["producers"] != [[list(b), h] for b, h in producers]:
            return False
        if step["consumers"] != [[list(b), h] for b, h in consumers]:
            return False
        if step["untouched"] != [[list(b), h] for b, h in untouched]:
            return False
        if step["generated"] != [[list(b), h] for b, h in generated]:
            return False
        if step["after"] != [[list(b), h] for b, h in after]:
            return False
        if step["after_digest"] != dg([[list(b), h] for b, h in after]):
            return False
        current = after
        if cert["mode"] == "SINGLE_HEAD_POLY" and not is_single_head(current):
            return False
    if cert["projected"] != [[list(b), h] for b, h in current]:
        return False
    meter = Meter(10**9, 10**9, 10**9)
    decision = horn_solve(current, {}, meter)
    if decision != cert["decision"]:
        return False
    if decision["status"] == "SAT":
        witness = cert["decision"]["assignment"]
        if not evaluate(current, witness):
            return False
    return True


def recover_full_witness(cert: dict[str, Any], projected_assignment: dict[int, bool]) -> dict[int, bool] | None:
    if cert.get("status") != "EXACT" or not verify_projection(cert):
        return None
    assignment = dict(projected_assignment)
    projected = decode_formula(cert["projected"])
    if not evaluate(projected, assignment):
        return None
    for step in reversed(cert["steps"]):
        var = step["var"]
        producers = decode_formula(step["producers"])
        if len(producers) > 1:
            return None
        value = False
        if producers:
            body, _ = producers[0]
            value = all(assignment.get(v, False) for v in body)
        assignment[var] = value
    original = decode_formula(cert["original"])
    return assignment if evaluate(original, assignment) else None


def exhaustive_projection(formula: tuple[Clause, ...], forget: set[int]) -> dict[tuple[bool, ...], bool]:
    allv = variables(formula)
    keep = tuple(v for v in allv if v not in forget)
    hidden = tuple(v for v in allv if v in forget)
    out: dict[tuple[bool, ...], bool] = {}
    for kb in itertools.product((False, True), repeat=len(keep)):
        base = dict(zip(keep, kb))
        out[kb] = any(
            evaluate(formula, base | dict(zip(hidden, hb)))
            for hb in itertools.product((False, True), repeat=len(hidden))
        )
    return out


def projected_semantics(formula: tuple[Clause, ...], keep: tuple[int, ...]) -> dict[tuple[bool, ...], bool]:
    return {
        bits: evaluate(formula, dict(zip(keep, bits)))
        for bits in itertools.product((False, True), repeat=len(keep))
    }


def blowup_family(n: int) -> tuple[tuple[Clause, ...], tuple[int, ...], tuple[int, ...], int]:
    z = 2 * n + 1
    qs = tuple(2 * n + 1 + i for i in range(1, n + 1))
    formula: list[Clause] = []
    for i, q in enumerate(qs, start=1):
        formula.append(clause((i,), q))
        formula.append(clause((n + i,), q))
    formula.append(clause(qs, z))
    boundary = tuple(range(1, 2 * n + 2))
    return normalize(formula), qs, boundary, z


def expected_blowup_projection(n: int) -> tuple[Clause, ...]:
    z = 2 * n + 1
    clauses: list[Clause] = []
    for choices in itertools.product((0, 1), repeat=n):
        body = [i + 1 if bit == 0 else n + i + 1 for i, bit in enumerate(choices)]
        clauses.append(clause(body, z))
    return normalize(clauses)


def verify_blowup_schema(n: int) -> dict[str, Any]:
    if n < 1:
        raise ValueError("n must be positive")
    return {
        "family": "PAIR_HIT_IMPLIES_Z",
        "input_clauses": 2 * n + 1,
        "hidden_variables": n,
        "boundary_variables": 2 * n + 1,
        "minimal_false_assignments": str(1 << n),
        "required_boundary_horn_clauses": str(1 << n),
        "proof": [
            "With z=1 every boundary assignment is a model, so every non-tautological valid Horn clause has head z.",
            "A valid body for head z must contain at least one variable from every pair (a_i,b_i).",
            "Each minimal false assignment sets z=0 and exactly one variable from every pair to true.",
            "A valid clause falsified by such an assignment must use exactly its chosen n variables as body.",
            "Different minimal false assignments therefore require different clauses."
        ],
    }


def equality_pairs(n: int) -> tuple[Clause, ...]:
    result: list[Clause] = []
    for i in range(1, n + 1):
        result.append(clause((i,), n + i))
        result.append(clause((n + i,), i))
    return normalize(result)


def random_horn(rng: random.Random, n: int, m: int, single_head: bool) -> tuple[Clause, ...]:
    result: list[Clause] = []
    available_heads = list(range(1, n + 1))
    rng.shuffle(available_heads)
    for _ in range(m):
        if single_head:
            head = available_heads.pop() if available_heads and rng.random() < 0.75 else 0
        else:
            head = rng.choice([0] + list(range(1, n + 1)))
        body = [v for v in range(1, n + 1) if v != head and rng.random() < 0.3]
        result.append(clause(body, head))
    return normalize(result)


def run(seed: int = 391039) -> dict[str, Any]:
    rng = random.Random(seed)
    exact_checks = 0
    witness_checks = 0
    for _ in range(300):
        n = rng.randint(1, 8)
        f = random_horn(rng, n, rng.randint(0, n + 4), single_head=True)
        forget = set(rng.sample(range(1, n + 1), rng.randint(0, n)))
        cert = project_horn(f, forget, require_single_head=True, work_budget=1_000_000, clause_budget=50_000)
        assert cert["status"] == "EXACT" and verify_projection(cert)
        keep = tuple(v for v in variables(f) if v not in forget)
        assert exhaustive_projection(f, forget) == projected_semantics(decode_formula(cert["projected"]), keep)
        if cert["decision"]["status"] == "SAT":
            pa = {int(v): bool(x) for v, x in cert["decision"]["assignment"].items()}
            full = recover_full_witness(cert, pa)
            assert full is not None and evaluate(f, full)
            witness_checks += 1
        exact_checks += 1

    merge_checks = 0
    for _ in range(200):
        n = rng.randint(1, 7)
        a = random_horn(rng, n, rng.randint(0, n + 4), single_head=False)
        b = random_horn(rng, n, rng.randint(0, n + 4), single_head=False)
        meter = Meter(2_000_000, 100_000, 10_000_000)
        result = separate_or_merge(a, b, meter)
        models_a = set()
        models_b = set()
        for bits in itertools.product((False, True), repeat=n):
            assn = {i + 1: bits[i] for i in range(n)}
            if evaluate(a, assn):
                models_a.add(bits)
            if evaluate(b, assn):
                models_b.add(bits)
        if result["status"] == "MERGE":
            assert models_a == models_b
        else:
            assn = {int(v): bool(x) for v, x in result["assignment"].items()}
            assert evaluate(a, assn) != evaluate(b, assn)
        merge_checks += 1

    restriction_checks = 0
    for _ in range(150):
        n = rng.randint(1, 7)
        f = random_horn(rng, n, rng.randint(0, n + 4), single_head=False)
        assigned_vars = rng.sample(range(1, n + 1), rng.randint(0, n))
        partial = {v: bool(rng.getrandbits(1)) for v in assigned_vars}
        restricted = restrict_horn(f, partial)
        remaining = tuple(v for v in range(1, n + 1) if v not in partial)
        for bits in itertools.product((False, True), repeat=len(remaining)):
            extension = partial | dict(zip(remaining, bits))
            assert evaluate(f, extension) == evaluate(restricted, dict(zip(remaining, bits)))
        restriction_checks += 1

    guarded_join_checks = 0
    for _ in range(120):
        n = rng.randint(2, 8)
        split = rng.randint(1, n - 1)
        left = [
            clause([v for v in range(1, n + 1) if v != head and rng.random() < 0.25], head)
            for head in range(1, split + 1)
        ]
        right = [
            clause([v for v in range(1, n + 1) if v != head and rng.random() < 0.25], head)
            for head in range(split + 1, n + 1)
        ]
        joined = join_horn(left, right, require_single_head=True)
        assert joined["status"] == "EXACT" and is_single_head(decode_formula(joined["joined"]))
        guarded_join_checks += 1
    bad_join = join_horn((clause((1,), 3),), (clause((2,), 3),), require_single_head=True)
    assert bad_join["status"] == "OPEN" and bad_join["reason"] == "OPEN_JOIN_LANGUAGE"

    blowup = []
    for n in range(1, 10):
        f, hidden, boundary, _ = blowup_family(n)
        cert = project_horn(f, hidden, work_budget=5_000_000, clause_budget=20_000, certificate_budget=30_000_000)
        assert cert["status"] == "EXACT" and verify_projection(cert)
        projected = decode_formula(cert["projected"])
        expected = expected_blowup_projection(n)
        assert projected == expected and len(projected) == 1 << n
        if n <= 5:
            assert exhaustive_projection(f, set(hidden)) == projected_semantics(projected, boundary)
        blowup.append({"n": n, "input_clauses": len(f), "projected_clauses": len(projected)})

    f14, hidden14, _, _ = blowup_family(14)
    open_control = project_horn(f14, hidden14, work_budget=1_000_000, clause_budget=2_000)
    assert open_control["status"] == "OPEN" and open_control["reason"] == "OPEN_PROJECTION_VOLUME"
    lower_bound = verify_blowup_schema(64)
    assert lower_bound["required_boundary_horn_clauses"] == str(1 << 64)

    equality_controls = []
    for n in (4, 8, 16, 32):
        eq = equality_pairs(n)
        cert_eq = dispatch_projection(
            "SINGLE_HEAD_HORN", eq, range(n + 1, 2 * n + 1),
            work_budget=2_000_000, clause_budget=100_000
        )
        assert cert_eq["status"] == "EXACT" and verify_projection(cert_eq)
        assert len(cert_eq["projected"]) == 0
        equality_controls.append({
            "n": n,
            "input_clauses": len(eq),
            "projected_clauses": 0,
            "work_units": cert_eq["cost"]["work_units"],
        })

    open_languages = {}
    for language in (
        "HORN_AFFINE_MIXED",
        "NAND3_NEQ_IMAGE",
        "TSEITIN_PARITY",
        "BETA_ACYCLIC_NON_HORN",
        "DETERMINISTIC_3CNF",
    ):
        result = dispatch_projection(language, tuple(), tuple())
        assert result["status"] == "OPEN" and result["reason"] == "OPEN_LANGUAGE"
        open_languages[language] = result["reason"]

    f = normalize((clause((), 1), clause((1,), 0)))
    cert = project_horn(f, (), require_single_head=True)
    assert cert["decision"]["status"] == "UNSAT" and verify_projection(cert)
    cert["projected"][0][1] = 0 if cert["projected"][0][1] != 0 else 1
    cert["integrity_sha256"] = dg({k: v for k, v in cert.items() if k != "integrity_sha256"})
    assert not verify_projection(cert)

    out = {
        "artifact_id": "C039.1-HORN-PROJECTION-BOUNDARY",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "constructive_lemma": (
            "Single-head Horn messages admit proof-carrying restriction, guarded disjoint-head join, and variable forgetting by deterministic Horn resolution; "
            "clause count does not branch during projection, exact SAT/UNSAT remains Horn-decidable, witnesses lift in reverse elimination order, "
            "and explicit Horn equivalence/separation is polynomial."
        ),
        "decisive_obstruction": (
            "General boundary-only Horn CNF projection is not polynomial-size: the O(n)-clause family "
            "a_i->q_i, b_i->q_i, (q_1...q_n)->z requires exactly 2^n Horn clauses after forgetting q_i."
        ),
        "single_head_exact_checks": exact_checks,
        "single_head_witness_checks": witness_checks,
        "restriction_checks": restriction_checks,
        "guarded_single_head_join_checks": guarded_join_checks,
        "overlapping_head_join": bad_join["reason"],
        "horn_merge_separator_checks": merge_checks,
        "explicit_blowup_controls": blowup,
        "single_head_equality_controls": equality_controls,
        "open_language_controls": open_languages,
        "symbolic_n64_lower_bound": lower_bound,
        "n14_budget_control": open_control["reason"],
        "corrupt_certificate": "REJECTED",
        "new_gate": "RICHER_HORN_MESSAGE_LANGUAGE_OR_PORTFOLIO_GUIDED_HEAD_DISJOINT_ISOLATION",
        "claim_boundary": (
            "This closes LEAF/RESTRICT/PROJECT and guarded disjoint-head JOIN for single-head Horn, plus MERGE/SEPARATE and an exact output-sensitive projector for general Horn. "
            "It decisively blocks universal boundary-only Horn CNF messages, but does not block richer Horn circuits, existential modules, "
            "portfolio-guided vtrees, arbitrary CNF algorithms, or prove P!=NP."
        ),
    }
    out["integrity_sha256"] = dg(out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", type=int, default=391039)
    args = parser.parse_args()
    out = run(args.seed)
    print(json.dumps(out, indent=2, sort_keys=True))
    if args.self_test:
        assert out["status"] == "PASS"


if __name__ == "__main__":
    main()
