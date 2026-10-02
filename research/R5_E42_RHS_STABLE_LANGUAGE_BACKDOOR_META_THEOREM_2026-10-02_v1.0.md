# R5 E42 — RHS-Stable Kernel-Language Backdoor Meta-Theorem

Date: 2026-10-02

Status:
`EXACT_GENERIC_COLUMN_DELETION_BACKDOOR__RHS_STABLE_POLYNOMIAL_LANGUAGES_INHERIT_FPT_NEIGHBORHOODS`

Scientific ceiling:

```text
R5 E34 and R5 E39 use the same exact mechanism:

  delete/fix a small set of exceptional Boolean coordinates,
  then solve the residual kernel language with a branch-dependent right-hand side.

This note abstracts that mechanism.

For every kernel language L whose Boolean linear feasibility problem

  R x = h,  x in {0,1}^E

is polynomial for every admissible residual right-hand side h, deleting t columns
to reach L yields an exact

  O(2^t poly(n))

algorithm.

Thus every future RHS-stable polynomial global language automatically comes with an
FPT deletion-backdoor neighborhood.

P_VS_NP = OPEN.
```

## 1. Generic setting

Let

```text
R in Z^{m x n}
```

be an explicit integer orthogonal representation satisfying

```text
ker_Q(R)=ker_Q(A).
```

Exact-One is equivalent to

```text
R(3x-1)=0,
x in {0,1}^n.
```

If

```text
R1 == 0 mod 3
```

rowwise, define

```text
b=(R1)/3.
```

Then the problem is

```text
R x=b,
x in {0,1}^n.
```

If the divisibility test fails, return UNSAT.

## 2. RHS-stable polynomial kernel language

Call a representation class `L` **RHS-stable polynomial** if there is a
deterministic polynomial algorithm which, given

```text
S in L,
h in Z^{rows(S)},
```

decides exactly whether

```text
S z=h,
z in {0,1}^{cols(S)},
```

and reconstructs a witness when one exists.

The definition is deliberately stronger than solving only the centered homogeneous
instance. It requires stability under the branch-dependent right-hand sides created
by fixing exceptional coordinates.

Examples already established in Fundamentum include:

```text
TU representations:
  integral box LP with arbitrary integral RHS;

signed-graphic two-endpoint representations:
  R5 E37/E39 generalized f-factor with arbitrary integral RHS.
```

## 3. Column-deletion backdoor

Partition the columns of `R` into

```text
E = exceptional columns,
G = good columns,
```

with

```text
|E|=t
```

and assume the good submatrix

```text
R_G
```

belongs to an RHS-stable polynomial language `L`.

Write

```text
R=[R_E R_G],
x=(x_E,x_G).
```

For an exceptional assignment

```text
a in {0,1}^E,
```

the residual problem is exactly

```text
R_G x_G = b-R_E a,
x_G in {0,1}^G.
```

The right-hand side depends on the branch, but RHS stability guarantees that the
residual instance remains polynomially decidable.

## 4. Exact meta-theorem

Enumerate all

```text
2^t
```

assignments `a` to the exceptional coordinates. For each branch invoke the
polynomial solver for `L` on

```text
h_a=b-R_E a.
```

A global witness exists iff at least one branch has a residual witness.

Therefore:

### Theorem RHS-STABLE-BACKDOOR

```text
boxed:
If deleting t columns from an explicit kernel-equivalent representation R leaves
an RHS-stable polynomial language L, then Exact-One is decidable exactly in
O(2^t poly(n)).
```

SAT reconstruction concatenates the exceptional assignment and residual witness.
UNSAT is certified by the complete branch tree together with the polynomial
language obstruction on every leaf.

Consequences:

```text
t=O(1)      -> polynomial;
t=O(log n)  -> polynomial.
```

No claim is made when `t` is superlogarithmic.

## 5. Existing JANUS instances of the theorem

### R5 E34 — distance to TU

After fixing the exceptional columns, the remaining TU matrix with box constraints
and an integral residual RHS is solved exactly by integral LP machinery.

Thus E34 is an instance of RHS-STABLE-BACKDOOR.

### R5 E39 — distance to signed graph

After fixing exceptional columns, every remaining column has two signed endpoints.
R5 E39 proves that arbitrary integral residual RHS becomes an ordinary graph
`f`-factor degree target.

Thus E39 is another instance of the same theorem.

The two branches differ only in the polynomial leaf language.

## 6. Why RHS stability matters

A language may be easy only for one special homogeneous or highly symmetric
right-hand side. Such a result does not automatically support a deletion backdoor:
fixing exceptional coordinates generally changes the RHS.

Therefore future global-language notes should explicitly record one of

```text
RHS-STABLE
```

or

```text
SPECIAL-RHS-ONLY.
```

Only the first class inherits E42 for free.

This prevents a subtle but important false inference in future router design.

## 7. Router abstraction

The global-language layer may now be expressed as

```text
recognize/certify exact language L
    -> solve directly if polynomial;

recognize/certify deletion backdoor E to RHS-stable L
    -> branch only on E;
    -> solve every residual leaf in L.
```

So each new RHS-stable language creates two results at once:

```text
1. the exact base terminal;
2. an O(2^t poly(n)) neighborhood parameterized by deletion distance t.
```

This is useful because the post-E38 frontier cannot hope to make all three-endpoint
representations polynomial. Instead the router can accumulate wider polynomial
languages and their certified FPT neighborhoods.

## 8. Updated research target

After E42, the highest-value next result is a genuinely new RHS-stable polynomial
language inside the fully peeled three-endpoint sector.

If such a language `L_3` is found, E42 immediately yields a distance-to-`L_3`
terminal without another bespoke proof.

Conversely, an explicit family remaining far from every currently known RHS-stable
language after exact quotienting would become a stronger representation-complexity
firewall.

```text
P_VS_NP = OPEN.
```
