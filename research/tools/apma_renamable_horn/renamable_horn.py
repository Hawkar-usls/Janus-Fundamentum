import hashlib, json
from itertools import combinations

from research.tools.apma_ss_provenance.apma_ss_controller import solve_source


def _clean_source(source):
    out = []
    for clause in source:
        lits = set(int(x) for x in clause)
        if any(-x in lits for x in lits):
            continue
        c = tuple(sorted(lits, key=lambda x: (abs(x), x)))
        if c:
            out.append(c)
    return tuple(sorted(out))


def _flip_literal_constraint(lit):
    v = abs(int(lit))
    return v if lit > 0 else -v


def build_flip_2cnf(source):
    cleaned = _clean_source(source)
    constraints = []
    for clause in cleaned:
        for a, b in combinations(clause, 2):
            constraints.append((_flip_literal_constraint(a), _flip_literal_constraint(b)))
    return cleaned, tuple(constraints)


def apply_renaming(source, flips):
    out = []
    for clause in source:
        renamed = [-lit if flips.get(abs(lit), False) else lit for lit in clause]
        out.append(tuple(sorted(renamed, key=lambda x: (abs(x), x))))
    return tuple(sorted(out))


def is_horn(source):
    return all(sum(1 for lit in clause if lit > 0) <= 1 for clause in source)


def verify_renaming(source, flips):
    cleaned = _clean_source(source)
    renamed = apply_renaming(cleaned, flips)
    if not is_horn(renamed):
        return False
    restored = apply_renaming(renamed, flips)
    return restored == cleaned


def _source_digest(source):
    raw = json.dumps([list(c) for c in _clean_source(source)], separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def compile_renamable_horn(source, n):
    cleaned, flip_2cnf = build_flip_2cnf(source)
    flip_solution = solve_source(flip_2cnf, n, "2CNF")
    if flip_solution["sat"] is not True:
        return {
            "status": "OPEN_NOT_RENAMABLE_HORN",
            "source_digest": _source_digest(cleaned),
            "flip_constraint_count": len(flip_2cnf),
        }
    flips = {i: bool(flip_solution["witness"][i]) for i in range(1, n + 1)}
    if not verify_renaming(cleaned, flips):
        return {"status": "FAIL_RENAMING_CERTIFICATE"}
    renamed = apply_renaming(cleaned, flips)
    horn_solution = solve_source(renamed, n, "HORN")
    certificate = {
        "flipped_variables": tuple(i for i in range(1, n + 1) if flips[i]),
        "flip_constraint_count": len(flip_2cnf),
        "source_digest": _source_digest(cleaned),
        "renamed_horn": True,
    }
    if horn_solution["sat"] is False:
        return {
            "status": "CERTIFIED_UNSAT_RENAMABLE_HORN",
            "certificate": certificate,
        }
    renamed_witness = {i: bool(horn_solution["witness"][i]) for i in range(1, n + 1)}
    witness = {i: (renamed_witness[i] ^ flips[i]) for i in range(1, n + 1)}
    return {
        "status": "CERTIFIED_SAT_RENAMABLE_HORN",
        "witness": witness,
        "certificate": certificate,
    }
