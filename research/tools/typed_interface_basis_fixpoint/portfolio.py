from collections import deque

from research.tools.typed_interface_basis_fixpoint.c0372_protocol import (
    complete_affine_consequence_negotiation,
)


def module_variables(module):
    if module["kind"] == "HORN":
        return {abs(l) for c in module["clauses"] for l in c}
    if module["kind"] == "AFFINE":
        out = set()
        for mask, _ in module["rows"]:
            bit = 1
            var = 1
            while bit <= mask:
                if mask & bit:
                    out.add(var)
                bit <<= 1
                var += 1
        return out
    raise ValueError("unsupported module kind")


def interaction_components(modules):
    supports = [module_variables(m) for m in modules]
    unseen = set(range(len(modules)))
    components = []
    while unseen:
        seed = unseen.pop()
        q = deque([seed])
        comp = [seed]
        support = set(supports[seed])
        changed = True
        while changed:
            changed = False
            for j in list(unseen):
                if support & supports[j]:
                    unseen.remove(j)
                    comp.append(j)
                    support |= supports[j]
                    changed = True
        components.append(tuple(sorted(comp)))
    return tuple(components)


def solve_component(modules, work_budget=10_000_000):
    variables = sorted(set().union(*(module_variables(m) for m in modules)))
    local = {v: i + 1 for i, v in enumerate(variables)}
    horn = []
    affine = []
    for module in modules:
        if module["kind"] == "HORN":
            for clause in module["clauses"]:
                horn.append(tuple(local[abs(l)] if l > 0 else -local[abs(l)] for l in clause))
        else:
            for mask, rhs in module["rows"]:
                new_mask = 0
                for v in module_variables(module):
                    if mask & (1 << (v - 1)):
                        new_mask |= 1 << (local[v] - 1)
                affine.append((new_mask, rhs))
    variable_count = len(variables)
    result = complete_affine_consequence_negotiation(
        tuple(horn), tuple(affine), variable_count, work_budget
    )
    return {
        "module_count": len(modules),
        "variable_count": variable_count,
        "terminal": result["terminal"]["status"],
        "basis_rows": len(result.get("basis", {}).get("rows", ())),
        "cost": result.get("cost", {}),
    }
def run_portfolio(modules, work_budget=10_000_000):
    components = interaction_components(modules)
    records = []
    for ids in components:
        records.append(solve_component([modules[i] for i in ids], work_budget))
    conflicts = [r for r in records if r["terminal"] == "CERTIFIED_CONFLICT"]
    if conflicts:
        terminal = "CERTIFIED_CONFLICT"
    elif any(r["terminal"] in {"OPEN_BUDGET", "OPEN_LANGUAGE"} for r in records):
        terminal = "OPEN_TYPED_FIXPOINT"
    else:
        terminal = "OPEN_TYPED_FIXPOINT"
    return {
        "terminal": terminal,
        "component_count": len(records),
        "stored_component_records": len(records),
        "total_basis_rows": sum(r["basis_rows"] for r in records),
        "component_records": records,
    }
