#!/usr/bin/env python3
"""R5 E78: exact equality-gluing identity for linear-delta boundary modules.

E77 found source-aligned clusters whose exact projected boundary supports are
linear delta-matroids.  E78 freezes the composition identity needed to turn
such a decomposition into a solver.

Let Tanner vertices be partitioned into clusters.  Every cut incidence edge e
appears as a boundary stub in exactly two clusters.  If F_t is the selected
boundary-edge set of cluster t, global consistency requires the two copies of
e to carry the same bit.  Equivalently

    F_1 xor F_2 xor ... xor F_m = empty.

Thus Exact-One feasibility is equivalent to empty-set membership in the
iterated delta-sum of the exact cluster boundary relations, after loop-extending
them to the common cut-edge ground set.

External theorem (Koana-Wahlstrom, STACS 2025): delta-sum of represented linear
delta-matroids is again linear and its representation is constructible in
randomized O(n^omega) field operations.  Therefore a polynomial-time
constructible partition into polynomially represented linear-delta boundary
modules is a sufficient condition for a randomized polynomial Exact-One solver.

This checker verifies the SET-SYSTEM gluing identity exactly on the E77 optimal
partitions:
  * frozen q=6 RXC3 source: parts [1,1,10], no compatible gluing, UNSAT;
  * connected linear q=9 source: parts [1,1,1,15], exactly one compatible
    gluing, matching the unique Exact-One cover {1,7,8}.

Scientific ceiling: this is a CONDITIONAL meta-solver theorem.  It does not
prove that every E12 target admits such a polynomially constructible linear-delta
decomposition.  P_VS_NP remains OPEN.
"""

from itertools import product

from r5_e77_source_aligned_delta_composition_frontier import (
    Q6_SETS,
    Q9_SETS,
    source_matrix,
    exhaustive_delta_clusters,
    min_max_partition,
)


def cluster_labelled_relation(A, mask):
    """Return (ground, family) using global Tanner-edge labels (check,var)."""
    q = len(A)
    C = [i for i in range(q) if (mask >> i) & 1]
    V = [j for j in range(q) if (mask >> (q+j)) & 1]
    Cset, Vset = set(C), set(V)

    internal_nei = {i: [j for j in V if A[i][j]] for i in C}
    crossing_from_check = {
        i: [(i,j) for j in range(q) if A[i][j] and j not in Vset]
        for i in C
    }
    crossing_from_var = {
        j: [(i,j) for i in range(q) if A[i][j] and i not in Cset]
        for j in V
    }

    ground = set()
    for xs in crossing_from_check.values():
        ground.update(xs)
    for xs in crossing_from_var.values():
        ground.update(xs)

    family = set()
    # Equality_3 gives one bit y_j for each included variable vertex.
    for ymask in range(1 << len(V)):
        y = {j: (ymask >> t) & 1 for t,j in enumerate(V)}

        base = set()
        for j in V:
            if y[j]:
                base.update(crossing_from_var[j])

        partial = [base]
        feasible = True
        for i in C:
            s = sum(y[j] for j in internal_nei[i])
            if s > 1:
                feasible = False
                break
            if s == 1:
                # ExactOne check already satisfied internally; all cut stubs 0.
                continue
            choices = crossing_from_check[i]
            if not choices:
                feasible = False
                break
            partial = [z | {e} for z in partial for e in choices]

        if feasible:
            family.update(frozenset(z) for z in partial)

    return frozenset(ground), frozenset(family)


def crossing_edges(A, parts):
    q = len(A)
    owner = {}
    for t,row in enumerate(parts):
        mask = row["mask"]
        for u in range(2*q):
            if (mask >> u) & 1:
                assert u not in owner
                owner[u] = t
    assert len(owner) == 2*q

    cut = set()
    for i in range(q):
        for j in range(q):
            if A[i][j] and owner[i] != owner[q+j]:
                cut.add((i,j))
    return frozenset(cut)


def xor_sets(items):
    out = set()
    for S in items:
        out.symmetric_difference_update(S)
    return frozenset(out)


def iterated_delta_sum(families):
    """Set-system delta-sum, forgetting multiplicity."""
    current = {frozenset()}
    for F in families:
        current = {a ^ b for a in current for b in F}
    return frozenset(current)


def compatible_tuples(families):
    """Boundary tuples whose cut-edge bits agree at their two endpoints."""
    out = []
    for choice in product(*[tuple(F) for F in families]):
        if not xor_sets(choice):
            out.append(choice)
    return out


def exact_one_solutions(A):
    q = len(A)
    out = []
    for bits in product((0,1), repeat=q):
        if all(sum(A[i][j]*bits[j] for j in range(q)) == 1 for i in range(q)):
            out.append(bits)
    return out


def selected_cut_edges_from_solution(A, parts, bits):
    cut = crossing_edges(A, parts)
    return frozenset((i,j) for i,j in cut if bits[j])


def verify_partition(name, A, expected_piece_sizes, expected_global_count,
                     expected_exact_support=None):
    q = len(A)
    rows = exhaustive_delta_clusters(A)
    mm, parts = min_max_partition(q, rows)
    assert sorted(r["size"] for r in parts) == expected_piece_sizes
    assert max(expected_piece_sizes) == mm

    relations = []
    grounds = []
    for row in parts:
        ground, fam = cluster_labelled_relation(A, row["mask"])
        assert fam
        # Relabeling boundary coordinates must preserve the relation cardinality
        # computed independently by E77.
        assert len(fam) == len(row["family"])
        grounds.append(ground)
        relations.append(fam)

    cut = crossing_edges(A, parts)
    assert set().union(*map(set, grounds)) == set(cut) if grounds else not cut

    # Every cut Tanner edge has exactly two boundary copies, one from each
    # endpoint cluster; internal edges have none.
    multiplicity = {e: sum(e in G for G in grounds) for e in cut}
    assert set(multiplicity.values()) <= {2}
    assert all(v == 2 for v in multiplicity.values())

    delta = iterated_delta_sum(relations)
    comp = compatible_tuples(relations)

    # Core E78 identity: empty in iterated symmetric-difference family iff a
    # globally consistent assignment of every cut edge exists.
    assert ((frozenset() in delta) == bool(comp))
    assert len(comp) == expected_global_count

    exact = exact_one_solutions(A)
    assert len(exact) == expected_global_count

    # Every global Exact-One solution restricts to one compatible boundary tuple.
    # For these frozen controls the mapping is injective and counts agree.
    induced = set()
    for bits in exact:
        target = selected_cut_edges_from_solution(A, parts, bits)
        candidates = []
        for F,G in zip(relations, grounds):
            candidates.append(frozenset(e for e in target if e in G))
        tup = tuple(candidates)
        assert all(tup[t] in relations[t] for t in range(len(parts)))
        assert not xor_sets(tup)
        induced.add(tup)
    assert len(induced) == len(exact) == len(comp)

    if expected_exact_support is not None:
        assert [tuple(i for i,z in enumerate(x) if z) for x in exact] == [tuple(expected_exact_support)]

    print(
        f"{name}: q={q} pieces={expected_piece_sizes} cut_edges={len(cut)} "
        f"relation_sizes={[len(F) for F in relations]} "
        f"delta_sum_size={len(delta)} empty_feasible={frozenset() in delta} "
        f"compatible={len(comp)} exact_one={len(exact)}"
    )
    return mm, parts, relations, delta


def pair_glue_identity_sanity():
    """Small symbolic sanity for delta-sum + zero-on-shared-interface."""
    # D1 ground {u,i}; D2 ground {v,i}.  Explicit equality-gluing keeps external
    # states when the membership of i agrees.
    u, i, v = "u", "i", "v"
    F1 = {frozenset(), frozenset({u,i})}
    F2 = {frozenset(), frozenset({i,v})}

    explicit = set()
    for a in F1:
        for b in F2:
            if ((i in a) == (i in b)):
                explicit.add(frozenset((a | b) - {i}))

    dsum = {a ^ b for a in F1 for b in F2}
    zero_restricted = {frozenset(s - {i}) for s in dsum if i not in s}
    assert explicit == zero_restricted == {frozenset(), frozenset({u,v})}


def main():
    pair_glue_identity_sanity()

    q6 = source_matrix(6, Q6_SETS)
    verify_partition(
        "RXC3_Q6_UNSAT",
        q6,
        expected_piece_sizes=[1,1,10],
        expected_global_count=0,
    )

    q9 = source_matrix(9, Q9_SETS)
    verify_partition(
        "LINEAR_Q9_SAT",
        q9,
        expected_piece_sizes=[1,1,1,15],
        expected_global_count=1,
        expected_exact_support=(1,7,8),
    )

    print("R5 E78 linear-delta equality-gluing meta-solver: PASS")
    print("set identity: equality gluing = delta-sum followed by zero restriction on shared interfaces")
    print("for a full Tanner-vertex partition: Exact-One SAT iff empty set is feasible in the iterated delta-sum")
    print("conditional algorithm: polynomially constructible represented linear-delta partition => randomized polynomial Exact-One solver")
    print("missing theorem: universal polynomial construction of such a decomposition on the E12 hardness image")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
