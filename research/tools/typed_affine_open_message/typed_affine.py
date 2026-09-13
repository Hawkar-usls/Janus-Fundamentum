from collections import defaultdict

from research.tools.query_factorized_quotient.query_factorized import (
    TAUTOLOGY, UNSAT_STATE, normalize_clause, normalize_formula
)


def _eval_clause(clause, assignment):
    return any(assignment[abs(l)] if l > 0 else not assignment[abs(l)]
               for l in clause)


def _support_bundle_relation(bundle, support):
    support = tuple(support)
    points = []
    for bits in range(1 << len(support)):
        a = {v: bool((bits >> i) & 1) for i, v in enumerate(support)}
        if all(_eval_clause(c, a) for c in bundle):
            points.append(bits)
    return tuple(points)


def _rref_bitrows(rows, ncols):
    rows = sorted(set(rows))
    pivot = 0
    for col in range(ncols):
        hit = next((i for i in range(pivot, len(rows)) if (rows[i] >> col) & 1), None)
        if hit is None:
            continue
        rows[pivot], rows[hit] = rows[hit], rows[pivot]
        p = rows[pivot]
        for i in range(len(rows)):
            if i != pivot and ((rows[i] >> col) & 1):
                rows[i] ^= p
        pivot += 1
        if pivot == len(rows):
            break
    var_mask = (1 << ncols) - 1
    for row in rows:
        if (row & var_mask) == 0 and ((row >> ncols) & 1):
            return None
    rows = [r for r in rows if r & var_mask]
    rows.sort(key=lambda r: (next((i for i in range(ncols) if (r >> i) & 1), ncols), r))
    return tuple(rows)


def _local_affine_basis(bundle, support):
    support = tuple(support)
    d = len(support)
    points = _support_bundle_relation(bundle, support)
    if not points:
        return UNSAT_STATE
    valid = []
    for mask in range(1, 1 << d):
        vals = {((mask & p).bit_count() & 1) for p in points}
        if len(vals) == 1:
            rhs = next(iter(vals))
            valid.append(mask | (rhs << d))
    basis = _rref_bitrows(valid, d)
    if basis is None:
        return UNSAT_STATE
    accepted = []
    for p in range(1 << d):
        if all((((row & ((1 << d) - 1) & p).bit_count() & 1) == ((row >> d) & 1)) for row in basis):
            accepted.append(p)
    if tuple(accepted) != points:
        return None
    return basis

def parse_exact_affine_bundles(clauses):
    formula = normalize_formula(clauses)
    if formula == UNSAT_STATE:
        return {"status": "UNSAT", "rows": (), "variables": (), "stats": {"normalized_unsat": 1}}
    bundles = defaultdict(list)
    for clause in formula:
        support = tuple(sorted({abs(l) for l in clause}))
        if len(support) > 3:
            return {"status": "UNRESOLVED", "reason": "support_width_gt_3"}
        bundles[support].append(clause)
    global_rows = []
    variables = set()
    stats = defaultdict(int)
    for support in sorted(bundles):
        bundle = tuple(bundles[support])
        basis = _local_affine_basis(bundle, support)
        if basis == UNSAT_STATE:
            return {"status": "UNSAT", "rows": (), "variables": tuple(sorted(variables | set(support))), "stats": {**dict(stats), "local_unsat_bundle": 1}}
        if basis is None:
            return {"status": "UNRESOLVED", "reason": "non_affine_support_bundle", "support": support,
                    "stats": dict(stats)}
        variables.update(support)
        d = len(support)
        for row in basis:
            coeffs = tuple(support[i] for i in range(d) if (row >> i) & 1)
            rhs = (row >> d) & 1
            global_rows.append((coeffs, rhs))
        stats["affine_bundles"] += 1
        stats["source_clauses"] += len(bundle)
        stats["local_basis_rows"] += len(basis)
    return {"status": "AFFINE", "rows": tuple(global_rows),
            "variables": tuple(sorted(variables)), "stats": dict(stats)}

def _encode_rows(rows, order):
    pos = {v: i for i, v in enumerate(order)}
    out = []
    for coeffs, rhs in rows:
        bits = 0
        for v in coeffs:
            bits ^= 1 << pos[v]
        out.append(bits | ((rhs & 1) << len(order)))
    return out


def _decode_rows(rows, order):
    out = []
    n = len(order)
    for row in rows:
        coeffs = tuple(order[i] for i in range(n) if (row >> i) & 1)
        rhs = (row >> n) & 1
        out.append((coeffs, rhs))
    return tuple(out)


def project_affine_rows(rows, boundary):
    boundary = tuple(dict.fromkeys(boundary))
    all_vars = sorted({v for coeffs, _ in rows for v in coeffs})
    bset = set(boundary)
    internal = [v for v in all_vars if v not in bset]
    border = [v for v in boundary if v in set(all_vars)]
    order = internal + border
    encoded = _encode_rows(rows, order)
    n = len(order)
    work = list(encoded)
    pivot = 0
    for col in range(len(internal)):
        hit = next((i for i in range(pivot, len(work)) if (work[i] >> col) & 1), None)
        if hit is None:
            continue
        work[pivot], work[hit] = work[hit], work[pivot]
        p = work[pivot]
        for i in range(len(work)):
            if i != pivot and ((work[i] >> col) & 1):
                work[i] ^= p
        pivot += 1
        if pivot == len(work):
            break
    internal_mask = (1 << len(internal)) - 1
    boundary_rows = [r for r in work if (r & internal_mask) == 0]
    if not border:
        for row in boundary_rows:
            if ((row >> n) & 1) and (row & ((1 << n) - 1)) == 0:
                return {"status": "UNSAT", "rows": (), "boundary": boundary}
        return {"status": "AFFINE", "rows": (), "boundary": boundary}
    shifted = []
    for row in boundary_rows:
        coeff = (row >> len(internal)) & ((1 << len(border)) - 1)
        rhs = (row >> n) & 1
        shifted.append(coeff | (rhs << len(border)))
    canon = _rref_bitrows(shifted, len(border))
    if canon is None:
        return {"status": "UNSAT", "rows": (), "boundary": boundary}
    return {"status": "AFFINE", "rows": _decode_rows(canon, border),
            "boundary": boundary}


def build_typed_affine_message(clauses, boundary):
    parsed = parse_exact_affine_bundles(clauses)
    if parsed["status"] != "AFFINE":
        return parsed
    projected = project_affine_rows(parsed["rows"], boundary)
    projected["source_stats"] = parsed.get("stats", {})
    projected["source_variables"] = parsed.get("variables", ())
    projected["message_coefficients"] = sum(len(c) for c, _ in projected.get("rows", ()))
    return projected

def affine_message_accepts(message, assignment):
    if message["status"] == "UNSAT":
        return False
    if message["status"] != "AFFINE":
        raise ValueError("message is unresolved")
    for coeffs, rhs in message["rows"]:
        lhs = 0
        for v in coeffs:
            lhs ^= int(bool(assignment[v]))
        if lhs != rhs:
            return False
    return True
