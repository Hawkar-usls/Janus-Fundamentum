# R5 E9 — Paley full-orbit post-RKPR sqrt-nullity barrier

Date: 2026-09-29
Status: THEOREM / STRUCTURAL FALSIFIER
Authority: non-authoritative research layer

## Scope

This note closes the shortcut

```text
POST_RKPR + LINEAR_CUBIC_SOURCE  =>  rational_nullity = O(log n)
```

without making any claim that P=NP or P!=NP.

The construction is an infinite family of square linear cubic Exact-One source matrices which are already clean under the rational-kernel projective-ratio quotient (RKPR), while their rational nullity is at least order sqrt(n).

The result is pre-component-decomposition: this note does **not** prove that the chosen member is connected for every field size. Finite connected controls exist, but no infinite connected-subfamily theorem is claimed here.

## 1. Paley tournament carrier

Let q be a prime power with

```math
q \equiv 7 \pmod {12},\qquad q>7,
```

and let `F_q` be the finite field of order q. Let

```math
Q=(F_q^*)^2
```

be the subgroup of nonzero squares. Then

```math
|Q|=m=(q-1)/2,
```

and `m` is odd and divisible by 3.

Define the Paley tournament `T_q` on `F_q` by

```math
u\to v \iff v-u\in Q.
```

Because `q \equiv 3 (mod 4)`, `-1` is a nonsquare, so exactly one orientation is present for every unordered pair.

The affine square group

```math
G = F_q \rtimes Q,
\qquad x\mapsto ax+b,
```

acts transitively on tournament arcs.

## 2. Cyclic-triangle translation classes

A cyclic triangle is a directed 3-cycle of `T_q`.

The Paley tournament is doubly regular. Every arc belongs to

```math
(q+1)/4
```

cyclic triangles. Since the tournament has

```math
E=q(q-1)/2
```

arcs, the total number of cyclic triangles is

```math
F = \frac{E(q+1)}{12}
  = \frac{q(q^2-1)}{24}.
```

The translation group `F_q` acts freely on cyclic triangles. Indeed, a nonzero translation has order equal to the field characteristic, which is greater than 3 under `q \equiv 7 (mod 12)`, and therefore cannot stabilize a 3-element vertex set.

Hence the number of translation classes is

```math
N = F/q = \frac{q^2-1}{24}.
```

The square group `Q` acts on these translation classes by scaling.

## 3. A full Q-orbit must exist

Take a translation class `[C]` of a cyclic triangle. Suppose its stabilizer in `Q` is nontrivial. Then for some `a != 1` in `Q`, scaling by `a` fixes `[C]`; equivalently, an affine map

```math
x\mapsto ax+b
```

permutes the three vertices of `C`.

Because `|Q|=m` is odd, the induced nontrivial permutation cannot have order 2. It must be a 3-cycle. Therefore `a` has order 3. The cyclic group `Q` has a unique subgroup of order 3.

Fix one nontrivial cube root `omega in Q`. Any translation class with nontrivial stabilizer can, after translating the unique affine fixed point to 0, be represented by a set

```math
{t, omega t, omega^2 t},\qquad t\ne0.
```

There are at most

```math
(q-1)/3 = 2m/3
```

such translation classes.

But for `q>7`,

```math
N=\frac{q^2-1}{24} > \frac{q-1}{3}.
```

Therefore at least one cyclic-triangle translation class has trivial stabilizer in `Q`. Its `Q`-orbit has the full size

```math
m=(q-1)/2.
```

Call one such full orbit `O`.

## 4. The square cubic source A_q

Let `F_O` contain every translation of every cyclic-triangle class in `O`.

Because `O` has `m` translation classes and each class has `q` distinct translates,

```math
|F_O| = qm = \frac{q(q-1)}2 = E.
```

Index rows by faces in `F_O` and columns by all arcs of `T_q`. Define

```math
(A_q)_{C,e}=1 \iff e\in C.
```

Every row has exactly 3 ones.

The face set `F_O` is invariant under `G`, while `G` is transitive on arcs. Thus every column has the same degree `d`. Counting incidences gives

```math
E d = 3|F_O| = 3E,
```

hence

```math
d=3.
```

Therefore `A_q` is square and cubic:

```math
A_q\in\{0,1\}^{n\times n},\qquad
n=\frac{q(q-1)}2,
```

with every row sum and every column sum equal to 3.

It is also linear as a 3-uniform hypergraph: two distinct directed triangles cannot share two tournament arcs. Sharing two arcs would force the same three vertices and therefore the same directed triangle.

## 5. Gradient kernel of dimension q-1

For a potential

```math
p:F_q\to\mathbb Q,
```

define the arc vector

```math
y_{u\to v}=p(v)-p(u).
```

Every selected row is a directed cycle

```math
u\to v\to w\to u,
```

so

```math
y_{u\to v}+y_{v\to w}+y_{w\to u}=0.
```

Thus every gradient vector lies in `ker_Q(A_q)`.

The map `p -> y` has kernel exactly the constant potentials, because the underlying tournament contains one arc between every pair of vertices. Consequently its image has dimension

```math
q-1.
```

Therefore

```math
\boxed{\nu_{\mathbb Q}(A_q)\ge q-1.}
```

Since

```math
n=\frac{q(q-1)}2,
```

this is

```math
\boxed{
\nu_{\mathbb Q}(A_q)
\ge
\frac{\sqrt{8n+1}-1}{2}
=
\Theta(\sqrt n).
}
```

## 6. RKPR is already exhausted

RKPR looks for a zero rational-kernel coordinate row or two distinct coordinate rows that are rationally proportional.

Restrict coordinate evaluation to the gradient subspace above. For an arc `e=(u,v)`, its evaluation functional is

```math
L_e(p)=p(v)-p(u).
```

This functional is nonzero.

For two distinct tournament arcs `e=(u,v)` and `f=(a,b)`, if

```math
L_e = lambda L_f
```

as rational functionals, then

```math
e_v-e_u = lambda(e_b-e_a).
```

The supports force the same unordered endpoint pair. A tournament contains only one oriented arc on that pair, hence `e=f` and `lambda=1`.

Therefore distinct arc coordinates are already nonzero and projectively distinct on a subspace of the full kernel. They cannot become proportional when the domain is enlarged to the full kernel.

Hence the entire family is post-RKPR clean:

```text
zero kernel-coordinate rows: 0
nontrivial rational proportional coordinate pairs: 0
```

This conclusion does not require the gradient space to be the whole kernel.

## 7. Infinite family

There are infinitely many admissible field sizes without using an unproved number-theoretic conjecture. For example,

```math
q_k = 7^{2k+1},\qquad k\ge1,
```

satisfies

```math
q_k\equiv7\pmod{12}
```

and tends to infinity.

Thus the construction yields infinitely many post-RKPR linear cubic sources with

```math
\nu_{\mathbb Q}(A_q)=\Omega(\sqrt n).
```

## 8. Finite exact controls

Prime-field controls were constructed for `q=19,31,43`.

For full multiplicative orbits of translation classes:

```text
q=19: n=171, a full orbit exists; one control has rank_mod_101=153, nullity=18.
q=31: n=465, full orbits exist; controls attain rank_mod_101=435, nullity=30.
q=43: n=903, full orbits exist; controls attain rank_mod_101=861, nullity=42.
```

For those controls, the modular rank plus the explicit `(q-1)`-dimensional rational gradient kernel pins the rational nullity exactly to `q-1` whenever the modular nullity is `q-1`.

Connected controls occur at `q=19`, `q=31`, and for some full orbits at `q=43`. This finite observation is **not** promoted to an infinite connected-family theorem.

## 9. Consequence for the live route

The implication

```text
post-RKPR
+ linear cubic hypergraph
=> rational nullity O(log n)
```

is false.

More strongly, these premises permit

```math
\nu_{\mathbb Q}(A)=\Omega(\sqrt n).
```

Therefore the universal algorithm cannot obtain polynomiality by routing every post-RKPR linear source through the existing `2^nu` rational-nullity enumerator.

Any surviving nullity-collapse theorem needs an additional premise not present here, for example a genuinely stronger global decomposition/connectedness/expansion condition whose correctness must itself be proved.

## 10. Firewall

This theorem does **not** prove:

- P=NP;
- P!=NP;
- that these instances are hard for every algorithm;
- that every selected full orbit is connected;
- that rational nullity itself is the source of NP-hardness;
- that no other polynomial quotient exists.

It proves exactly one structural barrier:

```math
\boxed{
\text{POST-RKPR + LINEAR CUBIC}
\not\Rightarrow
\nu_{\mathbb Q}(A)=O(\log n).
}
```

The live target remains a global quotient/selection mechanism that survives this family rather than a generic nullity bound.