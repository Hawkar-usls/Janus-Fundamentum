import copy

from research.tools.apma_ss_provenance.apma_ss_controller import (
    classify_source,
    checkpoint_hash,
    direct_cardinality,
    encode_c023,
    reverse_c023,
    solve_source,
)

MORPH_CATALOG = (
    "PROVENANCE_REVERSE_THEN_NATIVE_TRACTABLE",
    "DIRECT_COMPLETE_NEGATIVE_TRIPLES_TO_AT_MOST_2",
    "STRUCTURAL_NEQ_REVERSE_THEN_NATIVE_TRACTABLE",
)


def _norm_clause(c):
    return tuple(sorted((int(x) for x in c), key=lambda x: (abs(x), x)))


def _rollback_record(name, status, reason, start_hash, image):
    end_hash = checkpoint_hash(image)
    return {
        "morph": name,
        "status": status,
        "reason": reason,
        "checkpoint_hash": start_hash,
        "rollback_hash": end_hash,
        "rollback_exact": end_hash == start_hash,
    }

def structural_reverse_c023(image):
    n = int(image.get("n", 0))
    if n <= 0:
        return {"status": "MORPH_FAIL", "reason": "N"}
    want_affine = {
        ((1 << (i - 1)) | (1 << (n + i - 1)), 1)
        for i in range(1, n + 1)
    }
    got_affine = {(int(m), int(b)) for m, b in image.get("affine", ())}
    if got_affine != want_affine or len(image.get("affine", ())) != n:
        return {"status": "MORPH_FAIL", "reason": "NEQ_PAIR_CERTIFICATE"}
    source = []
    for clause in image.get("horn", ()):
        if not (1 <= len(clause) <= 3) or any(int(l) >= 0 for l in clause):
            return {"status": "MORPH_FAIL", "reason": "HORN_IMAGE_GRAMMAR"}
        decoded = []
        for lit in clause:
            v = abs(int(lit))
            if not (1 <= v <= 2 * n):
                return {"status": "MORPH_FAIL", "reason": "VARIABLE_RANGE"}
            decoded.append(-v if v <= n else v - n)
        source.append(_norm_clause(decoded))
    source = tuple(sorted(source))
    rebuilt = encode_c023(source, n)
    want_horn = tuple(sorted(_norm_clause(c) for c in image.get("horn", ())))
    want_affine_sorted = tuple(sorted((int(m), int(b)) for m, b in image.get("affine", ())))
    if tuple(rebuilt["horn"]) != want_horn or tuple(rebuilt["affine"]) != want_affine_sorted:
        return {"status": "MORPH_FAIL", "reason": "REENCODING_MISMATCH"}
    return {
        "status": "MORPH_PASS",
        "source": source,
        "certificate": {
            "n": n,
            "reencoding_exact": True,
            "provenance_used": False,
        },
    }


def _try_source_terminal(source, n):
    kind = classify_source(source)
    if kind == "GENERAL_3CNF":
        return {"terminal": False, "source_class": kind}
    solved = solve_source(source, n, kind)
    return {
        "terminal": True,
        "source_class": kind,
        "status": "CERTIFIED_SAT" if solved["sat"] else "CERTIFIED_UNSAT",
        "witness": solved["witness"],
    }

def run_portfolio(image):
    checkpoint = copy.deepcopy(image)
    start_hash = checkpoint_hash(checkpoint)
    ledger = []

    # Attempt 1: provenance-bound reverse morph.
    attempt = copy.deepcopy(checkpoint)
    rev = reverse_c023(attempt)
    if rev["status"] == "MORPH_PASS":
        terminal = _try_source_terminal(rev["source"], int(attempt["n"]))
        if terminal["terminal"]:
            ledger.append({"morph": MORPH_CATALOG[0], "status": "MORPH_PASS_TERMINAL", "source_class": terminal["source_class"]})
            return {**terminal, "ledger": ledger, "checkpoint_hash": start_hash, "attempt_count": 1}
        ledger.append(_rollback_record(MORPH_CATALOG[0], "MORPH_PASS_NONTERMINAL_ROLLED_BACK", terminal["source_class"], start_hash, checkpoint))
    else:
        ledger.append(_rollback_record(MORPH_CATALOG[0], "MORPH_FAIL_ROLLED_BACK", rev["reason"], start_hash, checkpoint))

    # Attempt 2: direct symmetric cardinality morph from the untouched image.
    attempt = copy.deepcopy(checkpoint)
    carrier = direct_cardinality(attempt)
    if carrier is not None:
        ledger.append({"morph": MORPH_CATALOG[1], "status": "MORPH_PASS_TERMINAL"})
        return {"terminal": True, "status": "CARDINALITY_CARRIER", "carrier": carrier, "ledger": ledger, "checkpoint_hash": start_hash, "attempt_count": 2}
    ledger.append(_rollback_record(MORPH_CATALOG[1], "MORPH_FAIL_ROLLED_BACK", "NOT_COMPLETE_NEGATIVE_TRIPLE_FAMILY", start_hash, checkpoint))
    # Attempt 3: provenance-free structural reverse with exact re-encoding proof.
    attempt = copy.deepcopy(checkpoint)
    srev = structural_reverse_c023(attempt)
    if srev["status"] == "MORPH_PASS":
        terminal = _try_source_terminal(srev["source"], int(attempt["n"]))
        if terminal["terminal"]:
            ledger.append({"morph": MORPH_CATALOG[2], "status": "MORPH_PASS_TERMINAL", "source_class": terminal["source_class"], "reencoding_exact": True})
            return {**terminal, "ledger": ledger, "checkpoint_hash": start_hash, "attempt_count": 3}
        ledger.append(_rollback_record(MORPH_CATALOG[2], "MORPH_PASS_NONTERMINAL_ROLLED_BACK", terminal["source_class"], start_hash, checkpoint))
        return {"terminal": False, "status": "OPEN_GENERAL_SOURCE_3CNF", "source_class": terminal["source_class"], "ledger": ledger, "checkpoint_hash": start_hash, "attempt_count": 3}

    ledger.append(_rollback_record(MORPH_CATALOG[2], "MORPH_FAIL_ROLLED_BACK", srev["reason"], start_hash, checkpoint))
    return {
        "terminal": False,
        "status": "OPEN_NO_AUTHORIZED_MORPH",
        "ledger": ledger,
        "checkpoint_hash": start_hash,
        "attempt_count": 3,
    }
