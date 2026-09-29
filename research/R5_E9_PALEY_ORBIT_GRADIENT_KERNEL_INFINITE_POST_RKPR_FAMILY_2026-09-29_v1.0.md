# R5 E9 — Infinite Paley-Orbit Gradient-Kernel Post-RKPR Family

Date: 2026-09-29

Status:
`JANUS_EXACT_INFINITE_CONNECTED_LINEAR_CUBIC_POST_RKPR_HIGH_NULLITY_UNSAT_FAMILY__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY11_GRADIENT_KERNEL_POST_RKPR_UNSAT_TERMINAL_2026-09-29_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_PROJECTIVE_RATIO_PINNING_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_SOURCE_KERNEL_POLYNOMIAL_NAVIGATION_SHELL_2026-09-28_v1.0.md`

Scientific ceiling:

```text
There is an infinite family of connected square linear cubic Positive 1-in-3
sources which survive RKPR with no zero/proportional rational-kernel rows and
have rational nullity at least sqrt(2n)-1.

Every member of this particular family is nevertheless UNSAT by a polynomially
checkable gradient-potential cycle certificate.

Therefore:
post-RKPR + connected + linear + cubic does NOT imply O(log n) rational nullity.
High nullity by itself still does NOT imply algorithmic hardness.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Number-theoretic parameter

Let `q>3` be a prime satisfying

```text
q = 3 mod 8.
```

Then `q=3 mod 4`, so `-1` is a quadratic non-residue modulo `q`.  Also

```text
(-2/q)=1,
```

because for `q=3 mod 8` both Legendre symbols `(-1/q)` and `(2/q)` equal `-1`.
Hence

```text
r := -2 mod q
```

is a nonzero quadratic residue.

Let `QR(q)` denote the nonzero quadratic residues.  Fix any `s0 in QR(q)` and let

```text
O = {s0, r s0, r^2 s0, ...}
```

be its multiplicative orbit under `r=-2`.  Write

```text
L = |O| = ord_q(-2).
```

The orbit is contained in `QR(q)`.

Dirichlet's theorem on primes in arithmetic progressions gives infinitely many primes
`q=3 mod 8`, hence this construction gives infinitely many source sizes.

## 2. Variables and constraints

Variables are directed arcs

```text
X(t,s),
```

with

```text
t in Z_q,
s in O,
```

representing the Paley-tournament arc

```text
t -> t+s.
```

There are

```text
n = q L
```

variables.

For every `(t,s)` create one Exact-One constraint

```text
C(t,s) = {
  X(t,s),
  X(t+s,s),
  X(t+2s, r s)
},
```

where all vertex coordinates are modulo `q` and `r=-2`.
Geometrically this is the directed triangle

```text
t -> t+s -> t+2s -> t,
```

whose three directed differences are

```text
s, s, -2s.
```

All three are quadratic residues, so the triangle lies in the Paley tournament.
There are exactly `qL=n` constraints.

## 3. Square cubic property

Every row has three variables by construction.

Fix a variable `X(u,d)`.  It occurs exactly three times:

1. as the first edge of `C(u,d)`;
2. as the second edge of `C(u-d,d)`;
3. as the closing edge of the unique `C(t,s)` with
   `r s=d` and `t+2s=u`.

Because multiplication by `r` permutes `O`, the third occurrence exists and is unique.
Therefore every column also has degree three.

Hence the incidence matrix `A_q,O` is square and cubic:

```text
A in {0,1}^{n x n},
row degree = column degree = 3.
```

## 4. Linearity

Every source row is a directed 3-cycle of a tournament.  Two distinct directed
triangles in a tournament cannot share two directed arcs: two shared arcs already
determine the same three vertices and the unique tournament orientation of the third
pair.

The parameterization has no duplicated row for `q>3`.  In `C(t,s)` the directed
difference `s` occurs twice whereas `-2s` occurs once; since `s != -2s` for `q>3`,
that repeated difference determines `s`, and then the directed triangle determines `t`.

Thus distinct source rows intersect in at most one variable.  The source is linear.

## 5. Levi connectedness

Fix `s in O`.  Constraint `C(t,s)` contains both

```text
X(t,s)
and
X(t+s,s).
```

Therefore, in the Levi graph, all variables `X(t,s)` with fixed difference `s` lie in
one component: repeated addition of nonzero `s` visits all `q` vertices because `q` is
prime.

The same constraint also contains

```text
X(t+2s, r s),
```

so the difference class `s` is connected to the difference class `r s`.  Since `O` is
one multiplicative orbit under `r`, all difference classes in `O` connect.
Every constraint is incident to these variables.

Hence the full Levi graph is connected.

## 6. Gradient space lies in the kernel

For a rational vertex potential

```text
p: Z_q -> Q,
```

define

```text
y_s(t) = p(t+s)-p(t).
```

For one constraint,

```text
y_s(t)
+ y_s(t+s)
+ y_{r s}(t+2s)
```

is

```text
[p(t+s)-p(t)]
+ [p(t+2s)-p(t+s)]
+ [p(t)-p(t+2s)]
= 0,
```

because `r s=-2s` makes the third arc `t+2s -> t`.
Thus every gradient lies in `ker_Q(A)`.

The underlying variable graph contains, for every fixed nonzero `s in O`, the directed
`q`-cycle of steps `+s`, so it is connected on the `q` potential vertices.  Therefore
the gradient space has dimension exactly

```text
q-1.
```

Hence

```text
nullity_Q(A) >= q-1.
```

## 7. Fourier theorem: the kernel is exactly the gradient space

Extend scalars to `C`.  Because the equations are translation-invariant in `t`, decompose
an arc signal into additive Fourier modes

```text
chi_k(t) = zeta^(k t),
k in Z_q,
```

where `zeta=exp(2 pi i/q)`.

For one frequency write

```text
y_s(t)=a_s chi_k(t).
```

The constraint equation becomes

```text
(1 + chi_k(s)) a_s + chi_k(2s) a_{r s} = 0,
```

or equivalently

```text
a_{r s}
= - a_s (1+chi_k(s)) / chi_k(2s).
```

Since `chi_k(2s)` is nonzero, one value `a_s` determines all amplitudes around the
single multiplicative orbit `O`.  Therefore each frequency contributes kernel dimension
at most one.

### Frequency k=0

Here `chi_0=1`, so

```text
a_{r s} = -2 a_s.
```

After one complete orbit of length `L`,

```text
a_s = (-2)^L a_s.
```

As an ordinary complex scalar `(-2)^L != 1`, so `a_s=0`.  Thus the zero frequency
contributes no kernel dimension.

### Frequencies k != 0

Take the Fourier gradient of potential `p(t)=chi_k(t)`:

```text
a_s = chi_k(s)-1.
```

This is nonzero for every nonzero `s`, because `q` is prime and `k != 0`.  It satisfies
the recurrence exactly:

```text
(chi_k(s)-1)(1+chi_k(s))
+ (chi_k(-2s)-1) chi_k(2s)

= chi_k(2s)-1 + 1-chi_k(2s)
= 0.
```

So every nonzero frequency contributes exactly one dimension.
There are `q-1` such frequencies.  Therefore

```text
nullity_C(A)=q-1.
```

The matrix has rational entries, so rank is invariant under extension from `Q` to `C`:

```text
nullity_Q(A)=q-1.
```

Since the rational gradient subspace already has dimension `q-1`, it follows that

```text
ker_Q(A) = gradient space.
```

This equality is symbolic for every prime parameter in the family; it is not inferred
from finite numerical experiments.

## 8. Exact post-RKPR cleanliness

Choose a rational gradient basis by fixing one potential gauge, e.g. `p(0)=0`.
The kernel coordinate functional belonging to arc `u->v` is

```text
p(v)-p(u).
```

No coordinate row is zero.

Two distinct such rows can be rationally proportional only if the corresponding edge
incidence functionals `e_v-e_u` have the same unordered pair of endpoints.  The reverse
orientation cannot also occur because all permitted differences lie in `QR(q)` while
`-1` is a non-residue, so `-QR(q)` is disjoint from `QR(q)`.

Therefore distinct kernel rows are never proportional:

```text
zero rows                     = 0
proportional distinct rows    = 0
RKPR equality merges          = 0
RKPR ratio pins               = 0
RKPR illegal-ratio terminals  = 0
```

Every family member survives the complete local RKPR quotient unchanged.

## 9. Exact UNSAT theorem

Assume an Exact-One witness exists:

```text
A x = 1,
x in {0,1}^n.
```

Because every source row has degree three,

```text
y = 3x-1
```

satisfies

```text
A y=0,
y in {-1,2}^n.
```

By the kernel theorem, `y` is a vertex gradient.
Fix any `s in O`.  The arcs

```text
t -> t+s,
for t in Z_q,
```

form one directed `q`-cycle because `q` is prime and `s != 0`.
Gradient values telescope around this cycle, so

```text
sum_t y_s(t)=0.
```

If exactly `k` of these `q` values equal `2`, the remaining `q-k` equal `-1`, hence

```text
sum_t y_s(t)
= 2k-(q-k)
= 3k-q.
```

Zero would require

```text
3k=q.
```

But `q>3` is prime, so `3` does not divide `q`.  Contradiction.
Therefore every member of the family is UNSAT.

This UNSAT proof is polynomially checkable once the orbit/gradient certificate is given.
It does not enumerate Boolean assignments or kernel topes.

## 10. Nullity growth

Recall

```text
n=qL,
L <= |QR(q)|=(q-1)/2,
nullity_Q(A)=q-1.
```

Therefore

```text
n <= q(q-1)/2 < q^2/2,
```

so

```text
q > sqrt(2n)
```

and consequently

```text
nullity_Q(A)
= q-1
> sqrt(2n)-1.
```

Thus along this infinite family

```text
nullity_Q(A) = Omega(sqrt(n)),
```

which is asymptotically larger than every `O(log n)` bound.

Hence the following hoped-for theorem is false:

```text
connected + linear + cubic + post-RKPR
=> nullity_Q(A)=O(log n).
```

The falsifier is stronger than a finite control: it is an explicit infinite family.

## 11. Concrete first members

For the orbit `O=< -2 >` starting at `1`:

```text
q=11: L=5,  n=55,  nullity=10
q=19: L=9,  n=171, nullity=18
q=43: L=7,  n=301, nullity=42
q=59: L=29, n=1711, nullity=58
```

The `q=11` member is the previously frozen Paley(11) source.  The `q=19` member is the
171x171 exact design found independently before the general orbit formula was recognized.
The `q=43` member demonstrates that the theorem does not require `-2` to generate all
of `QR(q)`: selecting a single multiplicative orbit already yields one connected square
cubic component with exact gradient kernel.

## 12. External anti-loop boundary

Paley tournaments and their quadratic-residue definition are classical.  The standard
facts used here are only:

- for primes `q=3 mod 4`, quadratic residues orient a tournament;
- the Legendre-symbol identity `(-2/q)=1` for `q=1 or 3 mod 8`;
- Dirichlet's theorem gives infinitely many primes `q=3 mod 8`.

Open-access literature searches also recover the standard Paley-tournament definition
and its classical pseudorandom/doubly-regular context.  No novelty claim is made for
those ingredients, Fourier diagonalization, or Dirichlet's theorem.

The exact JANUS result being frozen is their source-specific combination with:

```text
square cubic Exact-One incidence,
linearity,
Levi connectedness,
exact rational gradient kernel,
RKPR cleanliness,
Omega(sqrt(n)) nullity,
and the {-1,2} cycle UNSAT contradiction.
```

## 13. Consequence for the live universal-algorithm search

This theorem closes another shortcut:

```text
POST-RKPR HIGH NULLITY
cannot be ruled out by linearity or connectedness alone.
```

However this family also exposes a more useful positive target:

```text
large nullity + structured kernel representation
can still admit a polynomial UNSAT terminal.
```

The live universal question should therefore move from scalar nullity bounds to
**kernel representation complexity**:

```text
Given a post-RKPR linear cubic source, can one always either
(a) find a polynomially recognizable structured representation of ker_Q(A)
    yielding a boundary witness / UNSAT certificate,
or
(b) prove that every remaining unstructured kernel has another polynomial quotient?
```

That remains open.

## 14. Checker

Executable regression:

`experiments/r5_e9_paley_orbit_gradient_kernel_infinite_family.py`

It reconstructs the first members and verifies exact finite consequences including:

- orbit closure under `-2`;
- square cubic incidence;
- linearity;
- Levi connectedness;
- gradient annihilation;
- exact modular ranks matching `n-(q-1)` on `q=11,19,43`;
- RKPR-clean gradient coordinate rows;
- the cycle UNSAT divisibility contradiction.

The infinite theorem itself is the symbolic proof above; finite regression is not used
as a substitute for it.

## 15. Ceiling

```text
INFINITE PARAMETER SET q=3 mod 8 primes       = PROVED (Dirichlet)
SQUARE CUBIC                                   = PROVED
LINEAR                                         = PROVED
CONNECTED                                      = PROVED
NULLITY_Q                                      = q-1
KERNEL_Q                                       = GRADIENT SPACE
RKPR                                           = CLEAN
EXACT-ONE STATUS                               = UNSAT
NULLITY GROWTH                                 > sqrt(2n)-1
POST-RKPR O(log n) NULLITY HYPOTHESIS          = FALSIFIED
UNIVERSAL POLYNOMIAL SOLVER                    = NOT PROVED
E8_D1                                          = EMPTY
P_VS_NP                                        = OPEN
```
