# R5 E49 — Unique-Claw-State 2-SAT Terminal

Date: 2026-10-02

Status:
`EXACT_LOCAL_STATE_COMPATIBILITY__AT_MOST_ONE_CLAW_TRIPLE_PER_VERTEX_REDUCES_TO_2SAT__MULTICLAW_BACKDOOR_FPT`

Scientific ceiling:

```text
FOR A SQUARE+CUBIC+LINEAR CARRIER, EVERY EXACT-ONE WITNESS INDUCES AT EACH
CONFLICT VERTEX v ONE LOCAL STATE ON N[v]:

  SEL: v=1 and all neighbors are 0;
  UNS_T: v=0 and T is an independent 3-subset of N(v), with exactly T selected.

A GLOBAL WITNESS EXISTS IFF ONE LOCAL STATE CAN BE CHOSEN FOR EVERY VERTEX SO
THAT ALL LOCAL 0/1 ASSIGNMENTS AGREE ON OVERLAPS.

IF EVERY VERTEX HAS AT MOST ONE CLAW-LEAF TRIPLE T, EVERY LOCAL DOMAIN HAS SIZE
AT MOST TWO. THE OVERLAP-COMPATIBILITY PROBLEM IS THEN EXACTLY 2-SAT.

MORE GENERALLY, IF ONLY t VERTICES HAVE TWO OR MORE CLAW TRIPLES, BRANCHING ON
THEIR LOCAL STATES LEAVES A 2-SAT RESIDUAL, GIVING AN FPT TERMINAL.

P_VS_NP = OPEN.
```

## 1. Setting

Let `A` be square+cubic+linear and let `G=G_A` be its conflict graph.
By R5 E47, `G` is 6-regular. By R5 E45, Exact-One witnesses are independent
sets of size `n/3`.

R5 E48 proves more: if a vertex `v` is unselected, then its three selected
neighbors form an independent 3-subset of `N(v)`.

## 2. Local witness states

For every vertex `v`, define its closed scope

```text
C_v={v} union N(v).
```

Define one selected state

```text
SEL_v:
  x_v=1,
  x_u=0 for every u in N(v).
```

For every independent triple

```text
T subset N(v), |T|=3,
```

define one unselected state

```text
UNS_(v,T):
  x_v=0,
  x_u=1 for u in T,
  x_u=0 for u in N(v)-T.
```

Because `deg(v)=6`, there are at most

```text
1+binom(6,3)=21
```

local states per vertex.

## 3. Every Exact-One witness induces local states

Let `S` be a global Exact-One witness.

If `v in S`, independence gives

```text
S cap N(v)=empty,
```

so the restriction to `C_v` is `SEL_v`.

If `v not in S`, R5 E48 gives exactly three distinct selected neighbors, one from
each of the three source rows through `v`; they are pairwise nonadjacent because
`S` is independent. Thus the restriction is one `UNS_(v,T)` state.

Therefore every global witness induces exactly one local state at every vertex.

## 4. Compatible local states reconstruct a global witness

Conversely, suppose one local state is chosen for each vertex and every pair of
chosen states agrees on every original variable in the intersection of their
closed scopes.

Pairwise agreement defines a unique global Boolean vector `x` because every local
state assigns only 0/1 values to original variables.

Fix any source row

```text
{v,a,b}.
```

If `x_v=1`, the `SEL_v` local state forces `x_a=x_b=0`.

If `x_v=0`, the local state at `v` selects an independent 3-subset of its six
neighbors. The two co-variables `a,b` from the same source row are adjacent to one
another, so an independent triple contains at most one of them. Since the six
neighbors of `v` are partitioned into the three adjacent source-pairs and the
independent triple has size three, it contains exactly one vertex from each pair.
Hence exactly one of `a,b` is selected.

Thus every source row contains exactly one selected variable.

Therefore:

### Theorem LOCAL-STATE-GLUE

```text
A is Exact-One SAT
iff
there is one local witness state per conflict vertex such that all chosen states
agree on overlaps.
```

This is an exact reformulation, not a relaxation.

## 5. Unique-claw regime

Let

```text
c(v)=#{ independent triples T subset N(v) }.
```

The local domain size is exactly

```text
1+c(v).
```

Assume

```text
c(v)<=1
```

for every vertex.

Then every local domain has size one or two.

A size-one domain means `v` has no claw triple and is forced to `SEL_v`, recovering
R5 E48.

A size-two domain consists of

```text
SEL_v
```

and one unique unselected claw state.

Introduce one Boolean state bit `z_v` for every size-two domain; singleton domains
are fixed constants.

## 6. Overlap compatibility is 2-SAT

Take two vertices `v,w` whose closed scopes intersect.

For any pair of local states `(a,b)`, compatibility is a deterministic yes/no test:
compare their 0/1 values on

```text
C_v cap C_w.
```

If one pair `(a,b)` is incompatible, forbid that pair.
For Boolean state bits this is the ordinary 2-CNF clause

```text
(z_v != a) OR (z_w != b).
```

Do this for every incompatible pair and every overlapping pair of local scopes.
Singleton-domain choices become unit clauses.

The resulting formula is 2-SAT.

By LOCAL-STATE-GLUE:

```text
boxed:
If every conflict vertex has at most one claw triple, Exact-One is decidable
exactly in deterministic polynomial time by 2-SAT.
```

SAT reconstruction reads the chosen local states and glues their common original
variable values. UNSAT is certified by the 2-SAT implication contradiction.

## 7. Complexity

Each conflict vertex has degree six, so its local state list is computed by at most
20 triple tests.

Each closed scope has size seven. Only vertices at graph distance at most two can
have overlapping closed scopes, so each local state variable participates in only
`O(1)` scope-overlap checks in the frozen bounded-degree carrier.

Even without using that constant-degree refinement, checking all vertex pairs is
polynomial.

Thus the entire terminal is polynomial.

## 8. Multiclaw backdoor

Let

```text
B={v : c(v)>=2},
|B|=t.
```

Each exceptional vertex has at most 21 local states.

Branch on one local state for every vertex in `B`. Reject a branch immediately if
two chosen exceptional states disagree on an overlap.

Every remaining vertex has domain size at most two. Exceptional choices may delete
incompatible residual states or force singleton choices, but they never enlarge a
residual domain.

Hence every branch reduces to 2-SAT.

Therefore:

```text
boxed:
T=O(21^t poly(n))
```

for an explicit multiclaw backdoor `B`.

Consequences:

```text
t=O(1) -> polynomial,
t=O(log n) -> polynomial.
```

The base 21 can be replaced instance-by-instance by the product of actual local
domain sizes of the exceptional vertices.

## 9. Exact controls

The companion checker contains two square+cubic+linear controls.

### SAT control

Rows:

```text
036
125
028
237
014
456
167
478
358
```

The vertices `0,5,7` have no claw triple; every other vertex has exactly one, namely
with leaves `{0,5,7}`.

The generated 2-SAT instance reconstructs the Exact-One witness

```text
{0,5,7}.
```

### UNSAT control

For the Fano `K7` conflict graph, every vertex has zero claw triples and therefore
every local domain is singleton `SEL`.

Adjacent singleton states disagree immediately, so the generated 2-SAT system is
UNSAT.

## 10. Relation to E48

R5 E48 uses only the distinction

```text
c(v)=0 versus c(v)>=1.
```

E49 retains the entire local state when

```text
c(v)=1
```

and shows that all such binary local choices can be coordinated globally by 2-SAT.

Thus E49 strictly strengthens the one-shot non-claw forcing terminal.

## 11. Updated frontier

A genuine post-E49 survivor must now have a superlogarithmic population of
vertices with genuine local witness ambiguity:

```text
#{v : c(v)>=2} = omega(log n)
```

for the displayed conflict graph, unless another earlier router branch closes it.

So the unresolved cubic linear core must support not merely claws, but many vertices
with multiple distinct independent neighbor triples, while simultaneously avoiding
all kernel-language, quotient, separator, arithmetic, line-graph, chordal, and
other polynomial terminals.

This identifies the next graph-side complexity parameter:

```text
MULTICLAW AMBIGUITY.
```

The next attack should determine whether large multiclaw ambiguity necessarily
creates another tractable global structure or whether the E12 hard carrier can
sustain it at linear density.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e49_unique_claw_state_2sat.py
```
