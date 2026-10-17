#!/usr/bin/env python3
from itertools import product, combinations

COLORS = (0, 1, 2)
ALL = frozenset(COLORS)


def all_edges(vertices):
    return {tuple(sorted(e)) for e in combinations(vertices, 2)}


CASES = [
    {
        "name": "isolated_degree3",
        "V": (0,),
        "E": set(),
        "boundary": {0: ("a", "b", "c")},
        "blocks": (),
    },
    {
        "name": "single_K2",
        "V": (0, 1),
        "E": {(0, 1)},
        "boundary": {0: ("a", "b"), 1: ("c", "d")},
        "blocks": (("K2", (0, 1)),),
    },
    {
        "name": "K2_path3",
        "V": (0, 1, 2),
        "E": {(0, 1), (1, 2)},
        "boundary": {0: ("a", "b"), 1: ("c",), 2: ("d", "e")},
        "blocks": (("K2", (0, 1)), ("K2", (1, 2))),
    },
    {
        "name": "triangle",
        "V": (0, 1, 2),
        "E": all_edges((0, 1, 2)),
        "boundary": {0: ("a",), 1: ("b",), 2: ("c",)},
        "blocks": (("K3", (0, 1, 2)),),
    },
    {
        "name": "odd_C5",
        "V": (0, 1, 2, 3, 4),
        "E": {(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)},
        "boundary": {0: ("a",), 1: ("b",), 2: ("c",), 3: ("d",), 4: ("e",)},
        "blocks": (("ODD", (0, 1, 2, 3, 4)),),
    },
    {
        "name": "triangle_plus_K2",
        "V": (0, 1, 2, 3),
        "E": all_edges((0, 1, 2)) | {(2, 3)},
        "boundary": {0: ("a",), 1: ("b",), 2: (), 3: ("c", "d")},
        "blocks": (("K3", (0, 1, 2)), ("K2", (2, 3))),
    },
    {
        "name": "K2_star3",
        "V": (0, 1, 2, 3),
        "E": {(0, 1), (0, 2), (0, 3)},
        "boundary": {0: (), 1: ("a", "b"), 2: ("c", "d"), 3: ("e", "f")},
        "blocks": (("K2", (0, 1)), ("K2", (0, 2)), ("K2", (0, 3))),
    },
    {
        "name": "K4_terminal",
        "V": (0, 1, 2, 3),
        "E": all_edges((0, 1, 2, 3)),
        "boundary": {0: (), 1: (), 2: (), 3: ()},
        "blocks": (("K4", (0, 1, 2, 3)),),
    },
]


def boundary_names(case):
    out = []
    for v in case["V"]:
        for b in case["boundary"].get(v, ()):
            if b not in out:
                out.append(b)
    return tuple(out)


def degree_H(case, v):
    return sum(1 for e in case["E"] if v in e)


def sanity_case(case):
    for v in case["V"]:
        assert degree_H(case, v) + len(case["boundary"].get(v, ())) == 3, (case["name"], v)


def extension_exists(case, bcol):
    V = case["V"]
    for vals in product(COLORS, repeat=len(V)):
        c = dict(zip(V, vals))
        ok = True
        for u, v in case["E"]:
            if c[u] == c[v]:
                ok = False
                break
        if not ok:
            continue
        for v in V:
            for b in case["boundary"].get(v, ()):
                if c[v] == bcol[b]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def block_domains(kind):
    if kind == "K2":
        return tuple(frozenset((c,)) for c in COLORS)
    if kind in ("K3", "ODD"):
        return tuple(ALL - frozenset((c,)) for c in COLORS)
    if kind == "K4":
        return (ALL,)
    raise ValueError(kind)


def bad_certificate_exists(case, bcol):
    blocks = case["blocks"]
    domains = [block_domains(kind) for kind, _ in blocks]
    for chosen in product(*domains) if domains else [()]:
        good = True
        for v in case["V"]:
            incident = [chosen[i] for i, (_, vs) in enumerate(blocks) if v in vs]
            for i in range(len(incident)):
                for j in range(i + 1, len(incident)):
                    if incident[i] & incident[j]:
                        good = False
                        break
                if not good:
                    break
            if not good:
                break
            union = frozenset().union(*incident) if incident else frozenset()
            used_outside = {bcol[b] for b in case["boundary"].get(v, ())}
            L = ALL - used_outside
            if union != L:
                good = False
                break
        if good:
            return True
    return False


def kappa(kind, colour_set):
    if kind == "K2":
        return next(iter(colour_set))
    if kind in ("K3", "ODD"):
        return next(iter(ALL - colour_set))
    if kind == "K4":
        return None
    raise ValueError(kind)


def alldiff3(a, b, c):
    return len({a, b, c}) == 3


def local_normal_form_holds(case, bcol, chosen):
    blocks = case["blocks"]
    if len(case["V"]) == 1 and not blocks:
        bs = case["boundary"][case["V"][0]]
        return alldiff3(*(bcol[x] for x in bs))
    if len(blocks) == 1 and blocks[0][0] == "K4":
        return True

    kappas = [kappa(blocks[i][0], chosen[i]) for i in range(len(blocks))]
    for v in case["V"]:
        ids = [i for i, (_, vs) in enumerate(blocks) if v in vs]
        kinds = [blocks[i][0] for i in ids]
        ks = [kappas[i] for i in ids]
        outs = [bcol[b] for b in case["boundary"].get(v, ())]
        if len(ids) == 1 and kinds[0] == "K2" and len(outs) == 2:
            if not alldiff3(ks[0], outs[0], outs[1]):
                return False
        elif len(ids) == 1 and kinds[0] in ("K3", "ODD") and len(outs) == 1:
            if ks[0] != outs[0]:
                return False
        elif len(ids) == 2 and all(k == "K2" for k in kinds) and len(outs) == 1:
            if not alldiff3(ks[0], ks[1], outs[0]):
                return False
        elif len(ids) == 2 and sorted(kinds) in (["K2", "K3"], ["K2", "ODD"]) and len(outs) == 0:
            if ks[0] != ks[1]:
                return False
        elif len(ids) == 3 and all(k == "K2" for k in kinds) and len(outs) == 0:
            if not alldiff3(ks[0], ks[1], ks[2]):
                return False
        else:
            raise AssertionError((case["name"], v, kinds, outs))
    return True


def generic_certificate_local_nf_agree(case, bcol):
    blocks = case["blocks"]
    domains = [block_domains(kind) for kind, _ in blocks]
    generic_any = False
    local_any = False
    for chosen in product(*domains) if domains else [()]:
        generic = True
        for v in case["V"]:
            incident = [chosen[i] for i, (_, vs) in enumerate(blocks) if v in vs]
            if any(incident[i] & incident[j] for i in range(len(incident)) for j in range(i + 1, len(incident))):
                generic = False
                break
            union = frozenset().union(*incident) if incident else frozenset()
            used_outside = {bcol[b] for b in case["boundary"].get(v, ())}
            if union != ALL - used_outside:
                generic = False
                break
        local = local_normal_form_holds(case, bcol, chosen)
        generic_any |= generic
        local_any |= local
        if generic != local:
            raise AssertionError((case["name"], bcol, chosen, generic, local))
    return generic_any == local_any


def run_case(case):
    sanity_case(case)
    bnames = boundary_names(case)
    total = 0
    bad = 0
    for vals in product(COLORS, repeat=len(bnames)):
        bcol = dict(zip(bnames, vals))
        ext = extension_exists(case, bcol)
        cert = bad_certificate_exists(case, bcol)
        assert ext == (not cert), (case["name"], bcol, ext, cert)
        assert generic_certificate_local_nf_agree(case, bcol)
        total += 1
        bad += int(cert)
    return total, bad


def main():
    print("E8 v6.5 Gallai-tree bad-boundary block-label checker")
    grand = 0
    for case in CASES:
        total, bad = run_case(case)
        grand += total
        print(f"PASS {case['name']}: boundary assignments={total}, nonextendable={bad}")
    print(f"PASS all controls: {len(CASES)} Gallai shapes, {grand} boundary assignments")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
