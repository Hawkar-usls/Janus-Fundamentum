# R5 E49 — Unique-Claw Propagation

Date: 2026-10-03

Status:
`EXACT_UNIQUE_CLAW_FORCING__THREE_UNCONDITIONAL_ZEROS__THREE_COMPLEMENT_RELATIONS__E48_STRICT_STRENGTHENING`

Scientific ceiling:

```text
THIS NOTE APPLIES TO THE FROZEN ALL-POSITIVE SQUARE+CUBIC+LINEAR E12 CARRIER.

IF A CONFLICT-GRAPH VERTEX v IS THE CENTER OF EXACTLY ONE INDUCED CLAW WITH
LEAF SET T_v, THEN EVERY EXACT-ONE WITNESS OBEYS

  x_w = 0       FOR ALL w IN N(v) \ T_v,
  x_u = 1-x_v   FOR ALL u IN T_v.

THUS ONE UNIQUE-CLAW VERTEX CREATES THREE UNCONDITIONAL FORCED-ZERO VARIABLES
AND THREE COMPLEMENT RELATIONS.

THIS IS A POLYNOMIAL PROPAGATION RULE STRICTLY STRONGER THAN THE E48
NON-CLAW FORCING GATE.

P_VS_NP = OPEN.
```

## 1. Setting

Use the same square+cubic+linear all-positive carrier and conflict graph `G_A` as in
R5 E48.

For any Exact-One witness `S`, R5 E15/E48 imply:

```text
v in S      -> no neighbor of v lies in S;
v notin S   -> exactly three neighbors of v lie in S, and those three are pairwise
               nonadjacent, hence are the leaf set of an induced claw centered at v.
```

## 2. Unique claw

Let `v` have exactly one induced claw in `G_A`; denote its leaf set by

```text
T_v subseteq N(v), |T_v|=3.
```

Because `deg(v)=6`, the remaining neighbor set

```text
Z_v=N(v)\T_v
```

also has size three.

Consider any Exact-One witness.

### Case A: v is selected

Then independence gives

```text
x_u=0 for every u in N(v).
```

In particular all `Z_v` vertices are zero and all `T_v` vertices equal `1-x_v=0`.

### Case B: v is unselected

R5 E48 says the three selected neighbors of `v` must form an induced claw leaf set.
By uniqueness, that set must be exactly `T_v`.

Therefore

```text
x_u=1 for u in T_v,
x_w=0 for w in Z_v.
```

Since now `x_v=0`, every `u in T_v` again satisfies

```text
x_u=1-x_v.
```

Combining both cases gives the theorem.

## 3. Theorem UNIQUE-CLAW

```text
boxed:
If v has exactly one induced claw with leaf set T_v, then every Exact-One witness
satisfies

  x_w=0 for all w in N(v)\T_v,
  x_u xor x_v = 1 for all u in T_v.
```

So the rule produces:

```text
3 unary zero assignments,
3 parity/complement identities.
```

No branching is required.

## 4. Polynomial closure

All induced claws centered at a vertex can be enumerated by checking the twenty
3-subsets of its six neighbors.

Whenever a vertex has exactly one claw:

```text
1. force N(v)\T_v to zero;
2. union v with each u in T_v through a complement edge;
3. run ordinary Exact-One row propagation;
4. repeat after any quotient/forcing changes.
```

The complement constraints are maintained by parity union-find. Contradictory parity
or forced values give exact UNSAT certificates.

Thus exhaustive UNIQUE-CLAW closure is polynomial.

## 5. Strict strengthening over E48

E48 acts only on vertices with zero claws.

E49 acts on vertices with exactly one claw, even when

```text
F_E48=empty.
```

The companion checker contains a 12-variable square+cubic+linear carrier with

```text
claw counts = [1,1,1,2,1,2,3,3,2,2,2,2].
```

Hence every vertex is a claw center and E48 forces nothing.

Nevertheless the four unique-claw vertices

```text
0,1,2,4
```

produce forced zeros and complement identities; ordinary Exact-One propagation then
reconstructs the unique witness

```text
{5,7,8,11}.
```

So E49 is demonstrably stronger than E48 on an actual carrier.

## 6. Router update

After E48:

```text
UCL0 enumerate claw leaf sets for each active conflict vertex;
UCL1 zero claws   -> E48 forced selected;
UCL2 one claw T  -> force N(v)\T=0 and x_u=1-x_v for u in T;
UCL3 parity/row propagate to closure;
UCL4 contradiction -> UNSAT;
UCL5 fully assigned -> verify and terminate;
UCL6 otherwise retain only the >=2-claw unresolved core.
```

Therefore after E49 the unresolved all-positive E12 core may be assumed, after
closure, to have at least two claw choices at every still-undecided vertex.

## 7. Scope caveat

As in E48, the proof uses the all-positive E12 conflict graph where selected
variables form an independent set. It must not be silently transferred to an
arbitrary signed-literal co-occurrence graph.

## 8. Frontier

A genuine post-E49 survivor must have enough local ambiguity that every unresolved
vertex supports at least two induced-claw leaf triples after all forcing and parity
quotients.

The next natural boundary is therefore the **two-claw local state sector**. A useful
next result would either reduce that sector to a polynomial 2-SAT/parity language,
or exhibit an explicit carrier showing that two claw choices per vertex can still
support irreducible global Exact-One complexity.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e49_unique_claw_propagation.py
```
