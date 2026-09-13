from q_boundary_census import scalar_slots, is_q_node


def node(role, core, stage, opcode="TOEPLITZ_VECTOR_PRODUCT"):
    return {
        "semantic_role": role,
        "determinant_core_role": core,
        "stage_d": stage,
        "opcode": opcode,
    }


def synthetic_frontier(last_child, slots, q_cut):
    active = []
    for p, end in enumerate(last_child):
        if p <= q_cut < end:
            active.append(p)
    return active, sum(slots[p] for p in active)


def main():
    checks = []
    assert scalar_slots([]) == 1
    assert scalar_slots([2, 3]) == 6
    assert scalar_slots([744, 744]) == 553536
    checks.append("SCALAR_SLOT_RULE")
    assert is_q_node(node("BERKOWITZ_SHARED_STAGE_Q_D1", "SHARED", 1, "VECTOR_CONCAT_SLICE"))
    assert is_q_node(node("BERKOWITZ_SHARED_D002_Q", "SHARED", 2))
    assert is_q_node(node("BERKOWITZ_C0_D744_Q", "C0", 744))
    assert is_q_node(node("BERKOWITZ_C1_D617_Q", "C1", 617))
    assert not is_q_node(node("BERKOWITZ_SHARED_D002_DOT_J000", "SHARED", 2, "DOT_PRODUCT"))
    assert not is_q_node(node("BERKOWITZ_SHARED_D002_Q", "SHARED", 0))
    checks.append("Q_ROLE_BINDING")
    active, total = synthetic_frontier([3, 2, 3, -1], [2, 3, 5, 7], 1)
    assert active == [0, 1]
    assert total == 5
    checks.append("AFTER_Q_LIVE_PREDICATE")
    failed = False
    try:
        scalar_slots([2, 0])
    except ValueError:
        failed = True
    assert failed
    checks.append("INVALID_SHAPE_REJECTION")
    import json
    print(json.dumps({
        "schema": "TRUMP_EXACT_BERKOWITZ_Q_BOUNDARY_CONTROL_TESTS_V1",
        "status": "PASS_ALL_FROZEN_CONTROLS",
        "checks": checks,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
