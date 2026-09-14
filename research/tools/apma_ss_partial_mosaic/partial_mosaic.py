import copy, hashlib, json

from research.tools.apma_ss_portfolio.apma_ss_portfolio import structural_reverse_c023
from research.tools.apma_ss_provenance.apma_ss_controller import solve_source

MORPH_SEQUENCE = ("2CNF", "HORN3", "DUAL_HORN3")


def _norm_clause(clause):
    return tuple(sorted((int(x) for x in clause), key=lambda x: (abs(x), x)))


def _canon_clauses(clauses):
    return tuple(sorted(_norm_clause(c) for c in clauses))


def _clause_matches(kind, clause):
    c = _norm_clause(clause)
    if kind == "2CNF":
        return len(c) <= 2
    if kind == "HORN3":
        return len(c) == 3 and sum(1 for x in c if x > 0) <= 1
    if kind == "DUAL_HORN3":
        return len(c) == 3 and sum(1 for x in c if x < 0) <= 1
    raise ValueError(kind)


def _carrier_solver_kind(kind):
    return {"2CNF": "2CNF", "HORN3": "HORN", "DUAL_HORN3": "DUAL_HORN"}[kind]


def make_state(source):
    source = _canon_clauses(source)
    if any(not (1 <= len(c) <= 3) for c in source):
        raise ValueError("source must be width 1..3 CNF")
    return {
        "carriers": {},
        "residual": source,
        "source": source,
        "ledger": (),
    }


def _state_payload(state):
    return {
        "carriers": {k: [list(c) for c in _canon_clauses(v)] for k, v in sorted(state["carriers"].items())},
        "residual": [list(c) for c in _canon_clauses(state["residual"])],
        "source": [list(c) for c in _canon_clauses(state["source"])],
        "ledger": list(state.get("ledger", ())),
    }


def state_hash(state):
    raw = json.dumps(_state_payload(state), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def propose_extract(state, kind):
    residual = _canon_clauses(state["residual"])
    selected = tuple(c for c in residual if _clause_matches(kind, c))
    remainder = tuple(c for c in residual if not _clause_matches(kind, c))
    return {"kind": kind, "selected": selected, "residual": remainder}


def verify_proposal(state, proposal):
    kind = proposal.get("kind")
    if kind not in MORPH_SEQUENCE:
        return False
    old_residual = _canon_clauses(state["residual"])
    selected = _canon_clauses(proposal.get("selected", ()))
    remainder = _canon_clauses(proposal.get("residual", ()))
    expected_selected = tuple(c for c in old_residual if _clause_matches(kind, c))
    expected_remainder = tuple(c for c in old_residual if not _clause_matches(kind, c))
    if selected != expected_selected or remainder != expected_remainder:
        return False
    if any(not _clause_matches(kind, c) for c in selected):
        return False
    return _canon_clauses(selected + remainder) == old_residual


def commit_proposal(state, proposal):
    if not verify_proposal(state, proposal):
        raise ValueError("proposal failed exact verification")
    nxt = copy.deepcopy(state)
    kind = proposal["kind"]
    before = state_hash(state)
    nxt["carriers"][kind] = _canon_clauses(proposal["selected"])
    nxt["residual"] = _canon_clauses(proposal["residual"])
    event = {"morph": "EXTRACT_" + kind, "status": "COMMITTED", "before_hash": before}
    nxt["ledger"] = tuple(state.get("ledger", ())) + (event,)
    return nxt


def verify_full_recomposition(state):
    parts = []
    for clauses in state["carriers"].values():
        parts.extend(clauses)
    parts.extend(state["residual"])
    return _canon_clauses(parts) == _canon_clauses(state["source"])


def _vars(clauses):
    return {abs(lit) for c in clauses for lit in c}


def solve_mosaic(state, n):
    statuses = {}
    for kind in MORPH_SEQUENCE:
        clauses = state["carriers"].get(kind, ())
        if not clauses:
            continue
        solved = solve_source(clauses, n, _carrier_solver_kind(kind))
        statuses[kind] = {"sat": solved["sat"], "witness": solved["witness"], "variables": tuple(sorted(_vars(clauses)))}
        if solved["sat"] is False:
            return {"status": "CERTIFIED_UNSAT_BY_CARRIER", "carrier": kind, "carrier_statuses": statuses}
    if state["residual"]:
        return {"status": "OPEN_EXACT_RESIDUAL", "carrier_statuses": statuses}
    active = [k for k in MORPH_SEQUENCE if k in statuses]
    if not active:
        return {"status": "CERTIFIED_SAT_EMPTY", "carrier_statuses": statuses}
    if len(active) == 1:
        only = active[0]
        return {"status": "CERTIFIED_SAT_SINGLE_CARRIER", "carrier": only, "carrier_statuses": statuses}
    shared = []
    for i, a in enumerate(active):
        va = set(statuses[a]["variables"])
        for b in active[i + 1:]:
            inter = sorted(va & set(statuses[b]["variables"]))
            if inter:
                shared.append({"a": a, "b": b, "shared": inter})
    if shared:
        return {"status": "OPEN_CROSS_CARRIER_INTERACTION", "shared_interfaces": shared, "carrier_statuses": statuses}
    return {"status": "CERTIFIED_SAT_DISJOINT_CARRIERS", "carrier_statuses": statuses}


def compile_source_mosaic(source, n):
    state = make_state(source)
    for kind in MORPH_SEQUENCE:
        proposal = propose_extract(state, kind)
        if not verify_proposal(state, proposal):
            return {"status": "MORPH_FAIL_INTERNAL_VERIFICATION", "kind": kind, "state": state}
        state = commit_proposal(state, proposal)
    if not verify_full_recomposition(state):
        return {"status": "MORPH_FAIL_RECOMPOSITION", "state": state}
    decision = solve_mosaic(state, n)
    return {"status": decision["status"], "state": state, "decision": decision}


def compile_image_mosaic(image):
    rev = structural_reverse_c023(image)
    if rev["status"] != "MORPH_PASS":
        return {"status": "OPEN_IMAGE_REVERSE_FAILED", "reason": rev["reason"]}
    out = compile_source_mosaic(rev["source"], int(image["n"]))
    out["reverse_certificate"] = rev["certificate"]
    return out
