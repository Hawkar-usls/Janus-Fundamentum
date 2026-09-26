# R5 E9 — Odd-Hole Full-Boundary Delta-Matroid Barrier

Date: 2026-09-26

Authority:
`JANUS_DERIVED_EXACT_REPRESENTATION_BARRIER_AFTER_PA0019__NO_COMPLEXITY_LOWER_BOUND`

Authorizing audit:
`PA-0019-ODD-HOLE-FULL-BOUNDARY-MATCHING-REALIZABILITY`

Predecessors:

```
PA-0018-CONFLICT-ODD-HOLE-HYPERGRAPH-MATCHING-SOURCE-AUDIT
NM-0023-CONFLICT-ODD-HOLE-COVERAGE-SELECTOR-CONSERVATION
PA-0019-ODD-HOLE-FULL-BOUNDARY-MATCHING-REALIZABILITY
```

Checker:
`experiments/r5_e9_odd_hole_full_boundary_delta_matroid_barrier.py`

## 1. Full boundary

For an induced odd hole of length `k>=5`,

```
C_i = {v_i,v_{i+1},w_i},
D_i = {v_i,a_i,b_i},
```

with indices modulo `k`, define the exact projected relation

```
R_full^k(w,a,b)
=
exists v
[
  for all i: v_i+v_{i+1}+w_i=1
  and
  for all i: v_i+a_i+b_i=1
].
```

PA-0019 established that ordinary matching realization of this grouped block
must first pass the delta-matroid symmetric-exchange test.

## 2. Two feasible boundary points

Fix any index `j`.

### Point X

Take

```
v_i=0 for every i,
w_i=1 for every i,
a_i=0 for every i,
b_i=1 for every i.
```

Every `C_i` and every `D_i` has exactly one selected variable, so
`X in R_full^k`.

### Point Y

Take

```
v_j=1,
v_i=0 for i!=j.
```

Choose the external boundary as

```
w_{j-1}=w_j=0,
w_i=1 otherwise,

a_i=0 for all i,

b_j=0,
b_i=1 otherwise.
```

Again every source clause is exact-one, hence `Y in R_full^k`.

The two feasible sets differ in exactly three boundary coordinates:

```
X symmetric_difference Y
=
{ w_{j-1}, w_j, b_j }.
```

All three belong to `X\Y`.

## 3. Uniform symmetric-exchange failure

Use the delta-matroid symmetric-exchange axiom on

```
e = w_{j-1}.
```

The only possible `f` values are the three elements of
`X symmetric_difference Y`.

### f=e

Only `w_{j-1}` is removed from X.

All `b_i=1` remain.  The equations

```
v_i+a_i+b_i=1
```

with `a_i=0,b_i=1` force `v_i=0` for every i.  Then every belt equation
forces `w_i=1`, contradicting `w_{j-1}=0`.

### f=w_j

Both `w_{j-1}` and `w_j` are removed, while `b_j=1` remains.

Thus `D_j` forces `v_j=0`.  The two zero belt ports then require
`v_{j-1}=1` and `v_{j+1}=1`.  But `w_{j-2}=1`, so

```
v_{j-2}+v_{j-1}+w_{j-2} >= 2,
```

contradicting exact-one.  The indices are distinct for `k>=5`.

### f=b_j

Remove `w_{j-1}` and `b_j`, leaving `a_j=0`.

For every `i!=j`, `b_i=1` forces `v_i=0`.  At j, `a_j=b_j=0`
forces `v_j=1`.

But `w_j=1` remains, so

```
v_j+v_{j+1}+w_j = 1+0+1 = 2,
```

again impossible.

Therefore no permitted exchange exists.

Hence, uniformly for every odd `k>=5`,

```
boxed(R_full^k is not a delta-matroid).
```

The same argument in fact only needs `k>=5`; oddness is inherited from the
conflict-hole scope.

## 4. Matching-realizability consequence

PA-0019 source-binds Kazda--Kolmogorov--Rolínek:

```
matching-realizable Boolean boundary relation
=>
even delta-matroid
=>
delta-matroid.
```

Since `R_full^k` fails symmetric exchange,

```
boxed(
R_full^k is not ordinary-matching-realizable
for every odd k>=5.
)
```

There is also a weaker parity diagnostic: `X` has weight `2k`, whereas
`Y` has weight `2k-3`, so the relation contains feasible sets of both
parities.  The symmetric-exchange witness above is stronger because it rules
out delta-matroid structure itself, not only evenness.

## 5. Exact finite controls

The checker independently instantiates `k=5,7,9`.

For each size it verifies:

- X and Y are genuine full-boundary projections of source assignments;
- the symmetric difference is exactly
  `{w_(j-1),w_j,b_j}`;
- for `e=w_(j-1)`, every allowed `f` fails feasibility;
- feasible-set parity is already mixed.

Thus the implementation replay and the all-k proof agree.

## 6. What this closes

The closest grouped donor from PA-0018/PA-0019 was:

```
odd-hole block
->
one ordinary matching boundary gadget
->
blossom / even-delta-matroid machinery.
```

That route is now blocked at theorem level for the **full source boundary**.

This does not contradict the belt-only result:

```
R_belt^k
=
matching-realizable.
```

The obstruction is exactly the additional third-occurrence interface carried
by the `D_i` clauses.

## 7. What this does NOT prove

This is a representation barrier, not a computational lower bound.

It does not rule out:

- a non-matching symbolic quotient;
- grouped witness dominance;
- a different polynomial carrier;
- an instance-level decomposition using additional global structure;
- a future polynomial algorithm for the whole residual.

Therefore it gives no `P!=NP` conclusion.

## 8. Verdict

Freeze:

```
NM-0024
FULL ODD-HOLE BOUNDARY DELTA-MATROID TEST
=
FAIL UNIFORMLY FOR EVERY ODD k>=5

FULL BOUNDARY ORDINARY MATCHING REALIZABILITY
=
BLOCKED

BELT-ONLY MATCHING REALIZABILITY
=
PRESERVED / SOURCE-BOUND

MATCHING / BLOSSOM GROUPED QUOTIENT
=
CLOSED AS A UNIVERSAL ODD-HOLE ROUTE

NEXT REPRESENTATION
=
CHANGED OBJECT; FRESH PRE-MATH AUDIT REQUIRED

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
