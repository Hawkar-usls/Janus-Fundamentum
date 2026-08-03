# C024 — Root handoff graph lemmas

Status: **PURE_IMPLICATIONS_PROVED / GT_ROOT_REACHABILITY_OPEN**  
Scope: a component-spanning clause `C` with an unshielded non-tail bridge literal `l : A -> B` at a branch handoff.

Let deleting the undirected pivot edge of `l` split the clause graph into a tail side `S` containing `A` and a head side `T` containing `B`. Let `s` be the selected comparison variable and let its relation edge be contracted by the branch assignment.

## 1. Pivot-assignment extinction

### Lemma R1

If `s = |l|`, then neither child can carry the same tracked bridge-literal occurrence:

```text
polarity satisfying l  -> C is satisfied and deleted;
polarity falsifying l  -> literal l is deleted from the residual clause.
```

The remainder of the clause may survive, but the lineage `(C,l)` is extinct.

```text
ROOT_ROUTE_PIVOT_EXTINCTION = PROVED
```

This uses only ordinary CNF restriction semantics.

## 2. Cross-cut bridge destruction

### Lemma R2

Assume the selected relation edge joins one quotient component in `S` to one quotient component in `T`. Branch contraction identifies these two components. After deleting the original pivot `l`, the formerly disjoint pivot sides now share the contracted quotient node. Therefore `l` is no longer a bridge in every surviving residual containing it.

The selected variable need not occur in `C`; contraction alone destroys bridgehood.

```text
ROOT_ROUTE_CROSS_CUT_NONBRIDGE = PROVED
```

This is the same pure contraction fact used in the inherited-pair branch-route theorem.

## 3. Head-merge canonical shielding

### Lemma R3

Assume:

1. the tail endpoint component is singleton `{A}`;
2. the head endpoint component is singleton `{B}`;
3. the selected edge joins `B` to another quotient component `X` lying in the head side `T`;
4. the selected variable occurs as a literal `f` in `C`.

Then:

```text
polarity satisfying f:
    C is deleted;

polarity falsifying f:
    f is removed and B,X are contracted;
    if l ceases to be a spanning non-tail bridge, the outcome is already safe;
    otherwise the head component has size at least two while A remains singleton.
```

In the last case the original root non-minimality clause `N_A` is untouched at `A` and contains the complementary literal `-l` plus a parallel quotient edge from `X` to `A`. Hence `-l` is component-spanning but non-bridge.

```text
ROOT_ROUTE_HEAD_MERGE_SHIELD = PROVED
```

The implication is conditional only on the four explicit geometric/source hypotheses; it does not assume the Policy-0A frequency rule.

## 4. Two-node tail-wing handoff

### Lemma R4

Assume:

1. the tail bridge side is exactly `S={A,X}`;
2. the selected literal `f` is the unique clause edge internal to `S`.

Then one polarity satisfies and deletes `C`; the opposite polarity removes `f`, contracts `A,X`, and makes `l` tail-singleton safe.

```text
ROOT_ROUTE_TWO_NODE_TAIL_WING = PROVED
```

This is the previously proved Two-Node Tail-Wing Handoff Lemma and applies equally at root and non-root states.

## 5. Safe root-route cover

The four proved implications give a complete safe cover **provided** every reachable root unshielded occurrence belongs to one of these certified templates:

```text
R1  selected variable is the bad pivot;
R2  selected edge crosses the bad bridge cut;
R3  selected clause literal merges the singleton head inside the head side;
R4  selected clause literal is the unique internal edge of a two-node tail wing.
```

These templates are mutually compatible as a cover; a case satisfying more than one may be charged to any applicable implication.

## 6. Remaining GT-specific root theorem

### Root Template Reachability

Prove for arbitrary `n` that every root immediate-local unshielded occurrence produced by the exact frozen Policy-0A pass satisfies at least one of `R1`–`R4` for the deterministic selected comparison.

Potential falsifiers are exact:

1. an internal-head selected edge not touching the bad head endpoint;
2. an internal-head edge absent from the source clause, with the bad bridge surviving unshielded;
3. an internal-tail selected edge whose tail side has more than two nodes or contains another internal clause edge;
4. a selected edge lying on one bridge-cut side but outside both endpoint templates;
5. any child classified safe without a replayable extinction, non-bridge witness, tail-singleton role, or canonical `N_A` shield.

The root route template checker classifies all exact root occurrences through `GT_12` directly against these conditions.

## 7. Consequence

If Root Template Reachability is proved, the root half of T2b closes without a global frequency inequality. Together with Non-Root Wing Reachability, the proved pure branch-route classification, and T1/T2a, this yields the exact-key temporal induction.

## Claim boundary

R1–R4 are proved as pure CNF/quotient-graph implications under their explicit hypotheses. Their complete realization is under exact finite verification through `GT_12`. Root Template Reachability for arbitrary `n`, Non-Root Wing Reachability for arbitrary `n`, T3, the global cache lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
