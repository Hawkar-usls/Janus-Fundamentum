# R5 E32 — Root-Kernel / Mod-3 Potential Terminal

Date: 2026-10-02

Status:
`EXACT_GLOBAL_ROOT_KERNEL_NORMAL_FORM__MOD3_POTENTIAL_DECISION__E18_E19_E31_UNIFIED`

Scientific ceiling:

```text
THIS NOTE GIVES A GLOBAL POLYNOMIAL SAT/UNSAT TERMINAL FOR EVERY SOURCE WHOSE
RATIONAL KERNEL IS EXACTLY A GRAPHIC VERTEX-POTENTIAL / TENSION SPACE.

IF
  ker_Q(A) = { y_e = t_tail(e)-t_head(e) },
THEN EXACT-ONE IS EQUIVALENT TO A MOD-3 DIFFERENCE SYSTEM ON THE GRAPH:
  phi_head = phi_tail + 1 mod 3.

THE SYSTEM IS SOLVABLE BY GRAPH PROPAGATION.
A SOLUTION RECONSTRUCTS AN ACTUAL {-1,2}-VALUED KERNEL VECTOR.
AN INCONSISTENCY IS AN EXACT UNSAT CERTIFICATE.

THIS UNIFIES THE ROOT-KERNEL MECHANISM BEHIND R5 E18, R5 E19, AND R5 E31.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be a square+cubic Exact-One source and put

```text
K = ker_Q(A).
```

Suppose we have a directed graph

```text
H=(V,E),
E=[n],
```

with one oriented edge for every source coordinate, and suppose the exact kernel is

```text
boxed:
K = { y in Q^E : y_(u->v)=t_u-t_v for some t in Q^V }.
```

Equivalently, if `D_H` is the oriented edge/vertex incidence matrix whose edge row is

```text
e_u-e_v,
```

then

```text
col(D_H)=K.
```

This equality is directly verifiable in polynomial time once `H` is supplied: build
`D_H`, reduce one redundant vertex column per connected component, and check equality
of the two rational column spaces by exact rank tests.

We call such a certificate a **root-kernel representation**.

## 2. Exact-One in centered coordinates

As throughout R5 E10 onward,

```text
x in {0,1}^n,
A x = 1
```

is equivalent to

```text
y = 3x-1,
y in K intersect {-1,2}^n.
```

Under the root-kernel hypothesis this means finding vertex potentials `t_v` such
that every oriented edge obeys

```text
t_u-t_v in {-1,2}.
```

The two allowed centered values satisfy

```text
-1 == 2 mod 3,
 2 == 2 mod 3.
```

Therefore every Boolean witness necessarily satisfies

```text
t_u-t_v == -1 mod 3,
```

or equivalently

```text
boxed:
phi_v = phi_u + 1 mod 3
```

for every oriented edge `u->v`, where `phi=t mod 3`.

## 3. Necessity

Assume Exact-One SAT and let

```text
y_e=t_u-t_v in {-1,2}.
```

Reducing modulo three gives

```text
t_u-t_v == 2 == -1 mod 3.
```

Hence

```text
phi_v = phi_u+1 mod 3
```

on every edge.

Thus the mod-3 potential system is necessary.

## 4. Sufficiency

Conversely suppose there exists

```text
phi:V -> Z_3
```

with

```text
phi_v=phi_u+1 mod 3
```

for every oriented edge `u->v`.

Choose the standard integer representatives

```text
0,1,2
```

for the vertex colors and call them `t_v`.

Along an oriented edge only three transitions are possible:

```text
0 -> 1 : t_u-t_v = -1,
1 -> 2 : t_u-t_v = -1,
2 -> 0 : t_u-t_v =  2.
```

Therefore every edge difference lies in

```text
{-1,2}.
```

The vector

```text
y_e=t_u-t_v
```

lies in the root kernel by construction, so

```text
x=(y+1)/3
```

is Boolean and satisfies

```text
A x=1.
```

Hence the mod-3 potential system is sufficient.

## 5. Theorem ROOT-MOD3

Combining the two directions:

```text
boxed:
If ker_Q(A) is exactly a root/tension space of a directed graph H, then

A is Exact-One SAT
iff
there exists phi:V(H)->Z_3 with
phi_head(e)=phi_tail(e)+1 for every edge e.
```

The right-hand side is just a graph difference-constraint system over `F_3`.

It is solved by choosing one color per connected component and propagating along
edges.  A conflict is detected when an already-colored vertex receives a different
required color.

Thus, after a root-kernel certificate is exposed and verified, the Exact-One branch
runs in

```text
O(|V|+|E|)
```

field operations, plus the polynomial exact rank work needed to verify the kernel
representation.

No exponential kernel enumeration is required.

## 6. Cycle form

The mod-3 potential system is consistent exactly when every closed walk has zero
signed edge sum modulo three.

Traverse an edge in its displayed orientation with sign `+1` and against its
orientation with sign `-1`.  Then consistency is equivalent to

```text
sum_walk sign(e) == 0 mod 3
```

for every closed walk.

A propagation conflict therefore produces a short exact UNSAT certificate:

```text
one closed walk whose signed orientation sum is nonzero mod 3.
```

In kernel-row language this is a nonlocal root-circuit obstruction.

## 7. SAT reconstruction

When the propagation succeeds, the color map itself is a compact global normal
form.

The centered witness is

```text
y_e = rep(phi_tail(e)) - rep(phi_head(e)),
```

with representatives in `{0,1,2}`.

Each edge value is `-1` or `2`, and the Boolean witness is

```text
x_e = (y_e+1)/3.
```

Equivalently, an edge is selected exactly when its color transition is

```text
2 -> 0.
```

This makes witness reconstruction linear-time once the potential is known.

## 8. R5 E18 is closed globally

R5 E18 uses the root kernel on all directed arcs of `K_7`:

```text
y_ij=t_i-t_j.
```

Both orientations of every unordered pair are present.

For an opposite pair

```text
i->j,
j->i
```

the mod-3 rules demand simultaneously

```text
phi_j=phi_i+1,
phi_i=phi_j+1.
```

Combining gives

```text
0=2 mod 3,
```

a contradiction.

Therefore ROOT-MOD3 returns UNSAT immediately.

This recovers the E18 projective-ratio obstruction in one global potential language.

## 9. R5 E19 Paley root kernel is closed globally

R5 E19 identifies the full kernel of the 55-variable Paley quotient with

```text
r_ij=e_i-e_j
```

on the oriented Paley tournament arcs.

A transitive triangle, for example

```text
0 -> 3,
3 -> 1,
0 -> 1,
```

would force

```text
phi_3=phi_0+1,
phi_1=phi_3+1=phi_0+2,
phi_1=phi_0+1,
```

which is inconsistent.

Thus ROOT-MOD3 returns UNSAT.

This recovers the E20 non-diagonal three-coordinate obstruction as a special local
manifestation of one global graph-potential inconsistency.

## 10. R5 E31 is solved globally

For the E31 tripartite family orient the complete cross-part graph cyclically:

```text
A -> B,
B -> C,
C -> A.
```

The exact kernel proved in E31 is precisely

```text
X_ab = alpha_a-beta_b,
Y_bc = beta_b-gamma_c,
Z_ca = gamma_c-alpha_a.
```

So it is a root-kernel space.

Assign

```text
phi(A)=0,
phi(B)=1,
phi(C)=2.
```

Every edge increases the color by one modulo three.

ROOT-MOD3 therefore returns SAT and reconstructs

```text
X centered = -1,
Y centered = -1,
Z centered =  2,
```

which is exactly the E31 witness

```text
X=0,
Y=0,
Z=1.
```

This explains why E31 remains easy despite

```text
nullity_Q = Theta(sqrt(n)),
q=n,
treewidth = Omega(sqrt(n)).
```

Its global kernel language is graphic and collapses to a three-color potential.

## 11. Router update

The post-E31 algebraic router gains the branch

```text
RKG0  compute exact rational kernel K
RKG1  expose / receive a candidate directed graph H on the coordinate set
RKG2  verify col(D_H)=K by exact rational rank tests
RKG3  solve phi_head=phi_tail+1 mod 3
RKG4  conflict -> exact UNSAT certificate
RKG5  success  -> reconstruct {-1,2} kernel vector and Boolean SAT witness
```

The branch is exact once `H` is provided.

Recognizing an arbitrary graphic/root representation from a raw rational kernel
matrix is a separate algorithmic layer and is not claimed complete here.  The
known E18, E19, and E31 families expose their graph representation canonically.

## 12. New universal frontier

E32 shows that the post-E31 hard core must avoid yet another compact global normal
form.

A genuine survivor now needs all earlier conditions plus

```text
its effective rational kernel is not reducible to a verified graphic tension space
with a solvable mod-3 potential system.
```

The next useful question is therefore broader:

```text
GLOBAL KERNEL-LANGUAGE RECOGNITION

Which other polynomially recognizable linear-space classes turn
K intersect {-1,2}^n
into a tractable finite-domain potential / flow / parity problem?
```

The immediate next candidates are

```text
cographic / flow spaces,
signed-graphic spaces,
low-rank sums of graphic tension spaces,
and bounded-width sums after exact quotienting.
```

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e32_root_kernel_mod3_potential.py
```
