def _normalize_clause(clause):
    lits = set(int(x) for x in clause)
    if any(-x in lits for x in lits):
        return None
    c = tuple(sorted(lits, key=lambda x: (abs(x), x)))
    if not (1 <= len(c) <= 3):
        raise ValueError("width must be 1..3 after tautology removal")
    return c


def classify_clause(clause):
    c = _normalize_clause(clause)
    if c is None:
        return "TAUTOLOGY", None
    if len(c) <= 2:
        return "2CNF", c
    positives = sum(1 for lit in c if lit > 0)
    if positives <= 1:
        return "HORN3", c
    return "DUAL_HORN3", c


def compile_identity_mosaic(source):
    carriers = {"2CNF": [], "HORN3": [], "DUAL_HORN3": []}
    cleaned = []
    for clause in source:
        kind, c = classify_clause(clause)
        if kind == "TAUTOLOGY":
            continue
        cleaned.append(c)
        carriers[kind].append(c)
    return {
        "source_clean": tuple(sorted(cleaned)),
        "carriers": {k: tuple(sorted(v)) for k, v in carriers.items()},
    }
