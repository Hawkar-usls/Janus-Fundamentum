# R5 E20 — Kernel 3-Circuit Saturation

Date: 2026-10-02

Status:
`EXACT_3CIRCUIT_RELATION_CLASSIFICATION__POLYNOMIAL_LOCAL_UNSAT_AND_PROPAGATION_TERMINAL__E19_FIREWALL_LOCALLY_CLOSED`

Scientific ceiling:

```text
THIS NOTE ADDS AN EXACT POLYNOMIAL KERNEL-CIRCUIT TERMINAL.
EVERY MINIMAL 3-CIRCUIT OF KERNEL ROWS INDUCES ONE OF EXACTLY 12 BOOLEAN RELATIONS.
ALL BUT THE EQUAL-COEFFICIENT EXACT-ONE TYPE ARE DIRECTLY TRACTABLE BY
UNSAT / FORCING / EQUALITY / BINARY COMPLEMENT PROPAGATION.

THE R5 E19 CONNECTED PALEY 3-LIFT FIREWALL IS CLOSED BY A THREE-VARIABLE
FORBIDDEN KERNEL CIRCUIT.

THIS DOES NOT YET GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be a square+cubic+linear Exact-One source after the exact quotient steps of
R5 E17--E19.  Let

```text
K = ker_Q(A)
```

and let

```text
B in Q^{n x d}
```

be any basis matrix whose columns span `K`.  Write `b_i` for row `i` of `B`.
Every centered Boolean witness has the form

```text
y = B t,
y_i in {-1,2}.
```

The R5 E18 projective rules already settle zero rows and 2-circuits
(proportional kernel rows).  We therefore inspect minimal dependencies among
three nonzero pairwise nonproportional rows.

## 2. Kernel 3-circuit

A triple `(i,j,k)` is a kernel 3-circuit when

```text
rank{b_i,b_j,b_k}=2
```

and no pair is proportional.  Its dependence is unique up to nonzero scaling:

```text
c_1 b_i + c_2 b_j + c_3 b_k = 0,
```

with

```text
c_1 c_2 c_3 != 0.
```

Applying the same linear functional `t` gives every Boolean witness the exact
local condition

```text
c_1 y_i + c_2 y_j + c_3 y_k = 0,
y_i,y_j,y_k in {-1,2}.
```

With

```text
x_r=(y_r+1)/3 in {0,1},
S=c_1+c_2+c_3,
```

this is equivalent to

```text
3(c_1 x_i+c_2 x_j+c_3 x_k)=S.
```

Thus a bit pattern with selected subset `T subset {1,2,3}` is allowed exactly when

```text
sum_{r in T} c_r = S/3.
```

This gives a finite exact relation on three Boolean variables.

## 3. Complete 12-type classification

Assume all `c_r` are nonzero.

### Case A: S=0

Then both

```text
000
111
```

are allowed.  No singleton can be allowed, because that would force one
`c_r=0`.  No two-element subset can be allowed, because with total sum zero this
would force the complementary coefficient to be zero.

Hence the relation is exactly

```text
{000,111}.
```

This is the equality relation

```text
x_i=x_j=x_k.
```

### Case B: S != 0 and two singleton patterns are allowed

If, for example, `100` and `010` are allowed, then

```text
c_1=S/3,
c_2=S/3.
```

Therefore also

```text
c_3=S-c_1-c_2=S/3.
```

So

```text
c_1=c_2=c_3
```

and all three singleton patterns are allowed:

```text
{100,010,001}.
```

This is exactly the ordinary 1-in-3 relation.

### Case C: one singleton and one pair pattern

This is impossible for a minimal 3-circuit.

If the singleton is contained in the pair, subtraction of the two subset-sum
equalities forces another coefficient to zero.

If the singleton is disjoint from the pair, the two allowed subsets partition all
three positions, so each has sum `S/3`; adding gives

```text
S=2S/3,
```

contradicting `S != 0`.

### Case D: two pair patterns are allowed

Any two 2-subsets of a 3-set share one coordinate.  Suppose the allowed patterns
are

```text
110,
101.
```

Then

```text
c_1+c_2=S/3,
c_1+c_3=S/3,
```

so `c_2=c_3`.  Writing this common value as `q`, the first equality gives

```text
2c_1+q=0.
```

Thus, up to scaling,

```text
(c_1,c_2,c_3)=(1,-2,-2).
```

The relation is exactly

```text
{110,101},
```

which means

```text
x_1=1,
x_2=1-x_3.
```

Permuting coordinates gives exactly three such relation types.

### Case E: at most one pattern is allowed

The relation is either empty or a singleton.  Empty means immediate UNSAT;
a singleton fixes all three Boolean values.

Therefore every minimal 3-circuit induces exactly one of the following 12 relation
types:

```text
1  EMPTY relation                         -> UNSAT
6  singleton relations                    -> force all three bits
1  {000,111}                              -> equality class
3  forced-one + binary-complement pairs   -> x_a=1, x_b=1-x_c
1  {100,010,001}                          -> Exact-One
```

No other relation is possible.

## 4. KCIRC3 polynomial terminal

After R5 E18 KPROJ preprocessing, enumerate all triples of kernel rows.
For each pairwise nonproportional rank-two triple:

```text
1. compute its unique rational dependency c;
2. enumerate the eight {-1,2} assignments;
3. classify the induced Boolean relation.
```

A naive implementation uses

```text
O(n^3 poly(n))
```

exact arithmetic, hence is polynomial.

The branch actions are exact:

```text
KCIRC3-EMPTY
    no local alphabet assignment
    -> UNSAT certificate.

KCIRC3-SINGLETON
    exactly one assignment
    -> fix the three variables.

KCIRC3-EQUALITY
    relation {000,111}
    -> identify the three Boolean variables.

KCIRC3-XOR
    two pair patterns
    -> force one variable to 1 and record complement relation on the other two.

KCIRC3-EXACTONE
    equal circuit coefficients
    -> add the implied exact-one triple as a redundant exact constraint.
```

After any forcing or quotient action, rerun the earlier cheap exact terminals and
repeat until a fixed point.  Each actual variable fixing/identification reduces the
unresolved representation, so the reduction loop can be implemented with
polynomially many major iterations.

The equal-coefficient case is deliberately not called tractable: it reproduces the
original hard Exact-One relation.

## 5. Polynomial UNSAT certificate

For `KCIRC3-EMPTY`, a certificate contains:

```text
(i,j,k),
(c_1,c_2,c_3),
a rational kernel basis B or independently checkable row-space data.
```

A verifier checks

```text
c_1 b_i+c_2 b_j+c_3 b_k=0,
all c_r != 0,
no pair of b_i,b_j,b_k is proportional,
```

then evaluates the eight alphabet assignments and confirms that none satisfies

```text
c_1 y_i+c_2 y_j+c_3 y_k=0.
```

This is a short exact polynomial certificate.

## 6. R5 E19 Paley firewall is locally closed

R5 E19 uses the `A_10` root kernel on Paley-11 tournament arcs:

```text
r_ij=e_i-e_j.
```

The Paley orientation contains the transitive triangle

```text
0 -> 3,
3 -> 1,
0 -> 1.
```

Its three root rows satisfy

```text
r_03+r_31-r_01=0.
```

Thus the unique circuit coefficients are

```text
(1,1,-1).
```

But for

```text
y_03,y_31,y_01 in {-1,2}
```

the equation

```text
y_03+y_31-y_01=0
```

has no solution.  Equivalently,

```text
R(1,1,-1)=empty.
```

Therefore the connected 165-variable E19 lift is rejected by `KCIRC3-EMPTY`
through its copy-constant root kernel.  The earlier E19 equality quotient to the
55-variable Paley base remains valid, but is not needed for this particular UNSAT
certificate.

So the E19 firewall teaches two distinct lessons:

```text
diagonal Schur moments are insufficient,
while non-diagonal relations among distinct kernel rows can be decisive.
```

## 7. Relation to source clauses

For every original Exact-One row `{i,j,k}`, the kernel rows automatically satisfy

```text
b_i+b_j+b_k=0.
```

Therefore every source clause is itself an equal-coefficient 3-circuit whenever
its three kernel rows are pairwise nonproportional.

Its induced relation is exactly

```text
{100,010,001}.
```

Hence KCIRC3 does not magically remove the NP-hard core: the hard relation appears
canonically inside the kernel matroid.

The gain comes from **additional** 3-circuits whose coefficient ratios are not
`1:1:1`.  Such circuits create constraints invisible at the level of the original
clause list and can force, identify, complement, or refute variables polynomially.

## 8. Router update

The post-E19 kernel branch becomes:

```text
K0  exact rational kernel
K1  zero-row UNSAT
K2  forbidden projective-ratio UNSAT
K3  projective forced assignments
K4  equality-class quotient
K5  rerun rank/cardinality/AF3/clique/commuting/separator terminals
K6  bounded-interface/local-gauge quotient
K7  KCIRC3 enumeration and propagation
K8  optional SCHUR-2 / moment UNSAT terminals
```

Moment feasibility is never promoted to SAT.

## 9. New hard-core requirement

A survivor after E20 must satisfy all previous E19 conditions and additionally:

```text
no empty kernel 3-circuit,
no singleton kernel 3-circuit,
no equality-producing kernel 3-circuit,
no forced-one+XOR kernel 3-circuit after propagation,
and every surviving minimal 3-circuit is equal-coefficient Exact-One type.
```

This is a substantially sharper object.

The next attack should therefore be on the first genuinely nonlocal layer:

```text
4-circuits and bounded-size kernel-circuit closure,
```

with the specific goal of determining whether a constant circuit radius is enough
or whether an explicit family survives every fixed radius.

A fixed radius `k` is still polynomial because `O(n^k)` subsets can be checked for
constant `k`.  It must not be promoted to a universal theorem without a proof that
some constant `k` suffices.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e20_kernel_3circuit_saturation.py
```
