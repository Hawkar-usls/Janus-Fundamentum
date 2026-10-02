# R5 E39 — Distance-to-Signed-Graphic Backdoor

Date: 2026-10-02

Status:
`EXACT_FPT_DISTANCE_TO_SIGNED_GRAPH_KERNEL_LANGUAGE__BRANCH_EXCEPTIONAL_COLUMNS_THEN_F_FACTOR`

Scientific ceiling:

```text
R5 E38 shows a sharp unrestricted sparsity wall:
  support <=2 signed columns -> polynomial,
  support 3 all-positive columns -> NP-complete.

This note identifies the exact tractable neighborhood of that wall.

If an integer orthogonal representation R with ker_Q(R)=ker_Q(A) has only t
exceptional columns and every other column has exactly two nonzero entries from
{+1,-1}, then Exact-One is decidable in

  O(2^t poly(n)).

Each branch fixes only the exceptional Boolean coordinates; the remaining system
reduces exactly to the R5 E37 signed-graph f-factor problem with a branch-dependent
right-hand side.

Thus t=O(log n) gives a deterministic polynomial terminal.

P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
R in Z^{m x n}
```

be an integer matrix satisfying

```text
ker_Q(R)=ker_Q(A).
```

Partition the column set into

```text
E = exceptional columns,
G = signed-graphic columns,
```

with

```text
|E|=t.
```

Assume every column in `G` has exactly two nonzero entries and both are in

```text
{+1,-1}.
```

No restriction is imposed on the exceptional columns beyond integrality.

Exact-One is equivalent to

```text
R(3x-1)=0,
x in {0,1}^n.
```

Equivalently,

```text
R x = (R1)/3.
```

## 2. Global modular gate

Because `R x` is integral for Boolean `x`, a necessary condition is

```text
R1 == 0 mod 3
```

rowwise.

If this fails, return UNSAT immediately.

Assume henceforth that

```text
b=(R1)/3 in Z^m.
```

## 3. Branch only on exceptional columns

Write

```text
x=(x_E,x_G),
R=[R_E R_G].
```

For a fixed assignment

```text
a in {0,1}^E,
```

the residual system is

```text
R_G x_G = b - R_E a.
```

Define

```text
b^(a)=b-R_E a.
```

Thus the original instance is SAT iff at least one of the `2^t` residual systems

```text
R_G x_G=b^(a),
x_G in {0,1}^G
```

is SAT.

No relaxation has been introduced: every global Boolean witness determines exactly
one exceptional branch, and every residual witness together with its branch gives a
global witness.

## 4. Generalized signed-graph reduction with arbitrary integral RHS

Interpret each good column as a signed graph edge with two endpoints and endpoint
signs from

```text
(+,+), (+,-), (-,+), (-,-).
```

For each original row/vertex `v`, let

```text
d^-(v)
```

be the number of negative incidences among the good columns only.

R5 E37 used the special right-hand side `(R_G 1)/3`.  The same gadget proof works
for any integral target vector `h`.

For a Boolean assignment on good edges,

```text
(R_G x_G)_v
```

is transformed into ordinary selected degree

```text
deg_F(v)=(R_G x_G)_v+d^-(v).
```

Therefore the residual system

```text
R_G x_G=h
```

is exactly equivalent to an ordinary graph f-factor instance with

```text
boxed:
f_h(v)=h_v+d^-(v).
```

The four E37 edge gadgets are unchanged. Mixed-sign edges receive one selector
vertex of prescribed degree one; same-sign edges remain direct graph edges with the
appropriate interpretation of the selection bit.

If some target degree is outside its possible range, the branch is immediately
UNSAT; otherwise invoke the ordinary polynomial f-factor algorithm.

## 5. Exact FPT theorem

For each exceptional assignment `a`:

```text
1. compute h=b-R_E a;
2. construct the E37 signed-graph f-factor instance for R_G x_G=h;
3. solve it in polynomial time;
4. if SAT, reconstruct x_G and return (a,x_G).
```

There are exactly

```text
2^t
```

branches.

Hence:

### Theorem DSG-BACKDOOR

```text
boxed:
If ker_Q(R)=ker_Q(A) and deleting t columns from R leaves a signed-graphic
matrix with exactly two {+1,-1} nonzeros in every remaining column, then
Exact-One is decidable exactly in O(2^t poly(n)).
```

Consequences:

```text
t=O(1)      -> polynomial;
t=O(log n)  -> polynomial;
t=Theta(n)  -> the theorem gives no polynomial guarantee.
```

SAT reconstruction is exact. UNSAT is certified by exhaustion of the `2^t`
exceptional assignments together with the polynomial factor obstruction on every
branch.

## 6. Relation to E38 hardness

R5 E38 shows that an unrestricted support-three representation is already
NP-complete because one may take

```text
R=A
```

for the R5 E12 square+cubic+linear carrier.

For that raw representation every column is exceptional relative to the E37
signed-graphic class, so the trivial backdoor size can be

```text
t=n.
```

Thus E39 does not contradict E38. It identifies the natural FPT neighborhood around
the sharp support-two tractability boundary.

A universal polynomial theorem would need to prove that every hard-carrier kernel
admits some equivalent representation with

```text
t=O(log n),
```

or else expose another global language for the large-`t` remainder. No such theorem
is claimed here.

## 7. Representation dependence and certificate form

The parameter is attached to an explicit orthogonal representation `R`, not only to
`A`.

A certificate for the E39 branch contains

```text
R,
proof/check of ker_Q(R)=ker_Q(A),
exceptional column set E,
and verification that every column outside E has exactly two nonzeros in {+1,-1}.
```

Given this certificate, the backdoor size `t=|E|` and every branch are directly
verifiable.

Searching globally for the minimum possible `t` over all equivalent representations
is a separate problem and is not assumed polynomial here.

## 8. Router update

The global-language layer now has a sharp sequence:

```text
GL0  TU representation                         -> E33
GL1  distance-to-TU                            -> E34
GL2  root/tension potentials                   -> E32
GL3  unsigned graph f-factor                   -> E36
GL4  signed graph f-factor                     -> E37
GL5  t-column distance to signed graph         -> E39, O(2^t poly(n))
GL6  unrestricted three-endpoint representation-> E38 hardness wall
```

The next useful question is no longer whether three-endpoint representations are
tractable in general; E38 answers no unless P=NP.

The new structural target is instead:

```text
CAN THE R5 E12 HARD CARRIER BE FORCED TO HAVE LARGE DISTANCE t FROM EVERY
SIGNED-GRAPH-EQUIVALENT ORTHOGONAL REPRESENTATION?
```

If yes, that produces a representation-complexity firewall.
If no, a universal compression into `t=O(log n)` would yield a polynomial algorithm
and hence P=NP.

```text
P_VS_NP = OPEN.
```
