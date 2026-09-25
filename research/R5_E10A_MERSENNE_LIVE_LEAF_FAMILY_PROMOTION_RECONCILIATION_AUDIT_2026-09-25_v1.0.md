# R5 E10A — Mersenne Live-Leaf Family Promotion / Cross-Route Reconciliation Audit

Date: 2026-09-25

Authority:
`INTERNAL_REUSE__CROSS_ROUTE_RECONCILIATION__NO_NEW_MATH__GLOBAL_SOLVER_PROMOTION_HOLD`

Immediate chain:

```
PA-0014
  -> NM-0019
  -> NM-0020
  -> NM-0021
```

Cross-route predecessor:

```
R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM
R5_E9_COMMUTING_TWO_PERMUTATION_KERNEL_ISLAND
R5_E9_Z3_PHASE_COBBOUNDARY_ISLAND
PA-0001-PERFECT-KERNEL
```

## 1. Exact audit question

After NM-0020 and NM-0021, determine exactly what the Mersenne family proves
about the higher-lift strategy, and whether the same family supplies evidence
that the original cubic Exact-One / shortest-f decision problem is difficult.

The audit must not confuse:

```
large q_graph
```

with

```
hardness of the exact distinguished-f decision problem.
```

No new theorem is authorized by this artifact.  It reconciles already sealed
JANUS results and rechecks the current public literature before rebinding the
global frontier.

## 2. Internal anti-duplication result

The live Mersenne family is

```
M_L = M([I+P_x+P_y | 1]),
L = 2^k-1, k>=3.
```

PA-0014 gives

```
q_graph(M_L)
>=
(L^2-2L+3)/2
=
Omega(|E(M_L)|).
```

NM-0020 proves, for every such L,

```
M_L is 3-connected
and has no exact 3-separation.
```

NM-0021 proves, for every such L,

```
S8 <=minor M_L.
```

Therefore the Mersenne sequence is an unbounded family of literal
cubic-lineage, S8-containing, terminal live leaves with linear q_graph.

This exactly realizes Exit A in PA-0014.  Hence the candidate universal
structural bound

```
every unresolved cubic-lineage live leaf has q_graph=O(log n)
```

is false.

The higher-lift FPT theorem NM-0018 remains correct:

```
explicit q-lift
->
2^O(q) poly(n) exact shortest-f.
```

What fails is the attempt to make this automatically polynomial on all live
cubic-lineage leaves by proving a universal q=O(log n) bound.

## 3. Cross-route reconciliation: the same Mersenne family is an E9 P-island

The earlier E9 exact normal form applies to the same cubic incidence operator

```
A_L = I + S_x + S_y.
```

R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM already proves over Q:

```
3 does not divide L  => dim_Q ker(A_L)=0,
3 divides L          => dim_Q ker(A_L)=2.
```

It also proves:

```
Ax=1, x Boolean
iff
Az=0, z=3x-1 in {-1,2}^n,
```

and gives an exact `O(2^d poly(n))` solver for rational nullity `d`.

For Mersenne `L=2^k-1`:

```
k odd  => L = 1 mod 3,
k even => L = 0 mod 3.
```

Hence:

### k odd

```
dim_Q ker(A_L)=0.
```

The E9 nonsingular filter certifies UNSAT for the Exact-One equation.

### k even

```
dim_Q ker(A_L)=2.
```

The E9 low-nullity solver is polynomial.  More strongly, the already sealed
toroidal residue construction

```
x_(i,j)=1 iff i-j=r mod 3
```

gives an explicit Exact-One witness for any fixed `r in Z_3`.

Thus every Mersenne member lies in an already known JANUS polynomial island,
despite

```
q_graph(M_L)=Omega(|E|).
```

## 4. Consequence: q_graph is not a standalone complexity currency

The combined internal result is:

```
UNBOUNDED TERMINAL S8 LIVE LEAVES
+
q_graph = Omega(n)
+
DIRECT EXACT QUERY IN P ON THIS FAMILY.
```

Therefore large graphic-lift codimension alone is not evidence that the
original Exact-One / shortest-f query is difficult.

This does NOT refute NM-0018 and does NOT prove a polynomial algorithm for
arbitrary unbounded-q lifts.  It refutes only the strategy

```
universal polynomiality
via
universal q_graph=O(log n) on every live leaf.
```

The correct lesson is that a universal solver must exploit structure more
directly tied to the exact two-letter / Exact-One semantics.

## 5. Exact surviving cubic normal form

Every connected cubic monotone 1-in-3 incidence graph is 3-regular bipartite.
By the standard bipartite edge-colouring theorem, its edges decompose into
three perfect matchings.  After row/column normalization its incidence matrix
has the exact form

```
A = I + P + Q
```

for two permutations P,Q.

Therefore the two-permutation form by itself is not a tractability
restriction; it is an exact normal form for the cubic source class.

The already removed polynomial islands include:

```
low rational nullity,
commuting / abelian overlays,
Z3 phase-coboundary PASS,
other previously certified polynomial subclasses.
```

The precise remaining object is the one already audited by PA-0001:

```
CONNECTED
2-IN / 2-OUT
TWO-PERMUTATION / SCHREIER DIGRAPH

PERFECT-KERNEL EXISTENCE

P,Q NONCOMMUTING
Z3 PHASE FAIL
NO 1D ZERO-MODE
LOW-NULLITY LANE REMOVED
KNOWN ABELIAN / SPECIAL CLASSES REMOVED.
```

Equivalently:

```
Omega
=
S disjoint-union P^-1 S disjoint-union Q^-1 S.
```

## 6. Public-source refresh

The 2024 Wang--Yuan--Zhao paper remains the exact canonical-language donor:
it distinguishes perfect kernel from perfect solution and perfect directed
code, and for Cayley digraphs gives the translate-partition characterization
of a perfect kernel.

Yu--Yang--Fan--Ma (2024) completely classify the strongly connected
2-valent **abelian** Cayley-digraph perfect-code case.  This is stronger than
our internal commuting lane but does not close the nonabelian residual.

A September 2026 targeted refresh also checked recent perfect-code work,
including Cameron--Yap--Zhou (2026) on Cayley graphs of finite abelian groups.
The newly located work strengthens abelian / undirected / special-family
knowledge; no located result closes the exact directed nonabelian
two-generator, phase-inconsistent perfect-kernel residual frozen by PA-0001.

This is a targeted source refresh, not an absolute novelty certification.

## 7. Audit decision

Freeze:

```
PA-0014 EXIT A
=
SATISFIED BY NM-0020 + NM-0021

UNIVERSAL CUBIC-LINEAGE LIVE-LEAF
q_graph=O(log n)
=
FALSIFIED

MERSENNE FAMILY AS HARDNESS WITNESS
=
REJECTED

REASON
=
THE SAME FAMILY IS ALREADY AN E9
LOW-RATIONAL-NULLITY / Z3-PHASE POLYNOMIAL ISLAND

q_graph AS STANDALONE HARDNESS CURRENCY
=
REJECTED

NM-0018 HIGHER-LIFT FPT THEOREM
=
PRESERVED

ACTIVE DIRECT ALGORITHMIC FRONTIER
=
R5_E9_NONABELIAN_PHASE_INCONSISTENT_PERFECT_KERNEL_GATE_V1

AUTHORITATIVE SOURCE AUDIT
=
PA-0001-PERFECT-KERNEL

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

## 8. Next work allowed without duplication

The next mathematical work should stay inside the already source-audited
PA-0001 residual.

Two useful directions are distinct and must not be conflated:

1. **Solver / contraction direction.**
   Find a polynomial exact contraction, quotient, decomposition, or direct
   solver for the frozen nonabelian phase-inconsistent perfect-kernel residual,
   with witness reconstruction.

2. **Survivor-hardness diagnostic.**
   Determine whether a known NP-hard cubic Exact-One source can be reduced,
   while preserving YES/NO exactly, into instances that survive all current
   P-island preprocessors (noncommuting, phase FAIL, no 1D zero mode, large
   rational nullity, known special classes removed).

A hardness-survival result would only show that the preprocessors have not
already removed the NP-hard core.  It would not prove P!=NP.

Do not reopen Mersenne terminality, family-wide S8 existence, or universal
q_graph=O(log n) as an algorithmic route without a new audit and a genuinely
changed theorem scope.
