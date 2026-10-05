# R5 E72 — E12 Multi-Field Rank Middle-Band Firewall

Date: 2026-10-05

Status:
`E12_HARDNESS_IMAGE_HAS_LINEAR_Q_NULLITY_AND_LINEAR_F2_F3_RANK_NULLITY_MARGINS__RANK_MAGNITUDE_DICHOTOMY_FIREWALLED`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT SHOWS THAT THE ENTIRE R5 E12 RXC3 HARDNESS IMAGE ALREADY LIES LINEARLY DEEP
INSIDE THE SIMULTANEOUS Q/F2/F3 RANK-NULLITY MIDDLE BAND.

A SECOND IMPLICATION OF THE FORM

    "ALL RELEVANT RANKS/NULLITIES ARE LARGE => EASY STRUCTURAL DECOMPOSITION"

CANNOT BE JUSTIFIED AS AN EASY SIDE CONDITION SEPARATE FROM THE HARD CORE.
IF SUCH AN IMPLICATION IS TRUE UNIVERSALLY, ITS PROOF MUST ACT INSIDE THE E12
NP-HARD IMAGE ITSELF.

P_VS_NP = OPEN.
```

## 1. Why E72 is the correct anti-loop after E70/E71

E61 gives `2^d_Q poly(n)`. E70 gives

```text
2^min(r_2,d_2) poly(n),
```

and E71 gives, in particular,

```text
3^min(r_3,d_3) poly(n).
```

A tempting next dichotomy is that failure of all small-parameter routes should
force an easy decomposition.  E72 tests that directly against the E12/RXC3
hardness bridge.

## 2. Source and target notation — important scope correction

Let `R` be the `q x q` incidence matrix of an RXC3 source:

```text
rows    = source elements,
columns = source triples.
```

Every source triple has size three and every source element occurs in exactly
three triples, so `R` is square and row/column cubic.  **The RXC3 source is not
assumed linear.**  In particular, the frozen E17 q=6 source has source triples
sharing two elements.

The R5 E12 gadget is the **linearizing transformation**.  Its natural target
matrix `B` is square-cubic-linear and has

```text
N = 17q.
```

Let `H` be the source 3-uniform hypergraph and let `c(H)` be its number of
connected components.  For a field `K`, write `r_K` and `d_K` for rank and
nullity.

## 3. Characteristic not three: Q and F2

R5 E17 proved over the rationals that the one-gadget internal `15 x 17` matrix
has rank 13, nullity 4, two visible port dimensions, and two zero-port local
gauge dimensions.  The six port coordinates satisfy

```text
L1=L2=L3=a,
P1=P2=P3=b.
```

E72 replay verifies the identical quotient over `F2` (with `F5` as an extra
characteristic-not-three control).  Globally the boundary equations are

```text
R a = 0,
R b = 0.
```

Therefore, for `K=Q` and `K=F2`,

```text
boxed:
d_K(B) = 2q + 2 d_K(R).
```

For the binary rank,

```text
r_2(B)
 = 17q-[2q+2(q-r_2(R))]
 = 13q+2r_2(R),
```

hence

```text
boxed:
d_Q(B)>=2q,
d_2(B)>=2q,
r_2(B)>=13q,
min(r_2(B),d_2(B))>=2q.
```

## 4. Characteristic three changes the one-gadget quotient

Over `F3`, the internal gadget has

```text
rank_F3(J_int)=12,
nullity_F3(J_int)=5.
```

The six-port projection has dimension three while the zero-port local gauge is
still two-dimensional.  An exact parameterization is

```text
L=(a,b,-a-b),
P=(c,c+a-b,c-a+b).
```

Equivalently,

```text
L1+L2+L3=0,
P1+P2+P3=0,
P2-P1=L1-L2.
```

## 5. Position matrices and the global F3 quotient

Order each source triple as `(u,v,w)` and let `M1,M2,M3` be its first-, second-
and third-position incidence matrices.  Thus

```text
R=M1+M2+M3.
```

Put

```text
U=M1-M3,
V=M2-M3.
```

In characteristic three, `-2=1`, so

```text
boxed:
R=U+V.
```

For gadget parameter vectors `a,b,c in F3^q`, the unprimed boundary equations
are

```text
Ua+Vb=0.
```

The primed boundary equations are

```text
Rc+V(a-b)=0.
```

Using `Ua+Vb=0` and `R=U+V`,

```text
V(a-b)=Va-Vb=Va+Ua=Ra,
```

so the primed system is

```text
R(c+a)=0.
```

With `k=c+a`, the visible global variables split into

```text
(a,b) in ker[U V]
```

and

```text
k in ker_F3(R).
```

## 6. Why rank[U V] = q-c(H) without source linearity

For each ordered source triple `(u,v,w)`, replace it by the two oriented edges

```text
w -> u,
w -> v.
```

If two source triples overlap heavily this construction can create parallel
edges.  That is harmless: it is an oriented **multigraph** with the same
connected components as `H`, and `[U V]` is its oriented vertex-edge incidence
matrix up to column ordering/signs.

The standard spanning-forest theorem for an oriented incidence matrix holds over
any field, including multigraphs with parallel edges:

```text
rank = |V|-number_of_components.
```

Therefore

```text
rank_F3[U V] = q-c(H),
nullity_F3[U V] = q+c(H).
```

Adding the independent `d_3(R)` source-kernel variables and the `2q` zero-port
gadget gauges gives

```text
boxed:
d_3(B)=3q+c(H)+d_3(R).
```

Consequently

```text
r_3(B)
 = 13q+r_3(R)-c(H).
```

Every nonempty source component contributes at least one source rank, so
`r_3(R)>=c(H)`.  Hence

```text
boxed:
d_3(B)>=3q,
r_3(B)>=13q,
min(r_3(B),d_3(B))>=3q.
```

For connected sources,

```text
boxed:
d_3(B)=3q+1+d_3(R).
```

## 7. Linear-depth middle-band theorem for the E12 image

Since `N=17q`, every E12 target obeys

```text
boxed:
d_Q(B) >= 2N/17,

boxed:
min(r_2(B),d_2(B)) >= 2N/17,

boxed:
min(r_3(B),d_3(B)) >= 3N/17.
```

Thus the current rank/nullity exact envelopes are exponentially large when read
purely through these parameters on the E12 image:

```text
2^d_Q,
2^min(r_2,d_2),
3^min(r_3,d_3).
```

These are lower bounds on the sizes of those **specific parameterized search
envelopes**, not lower bounds on the true computational complexity of E12
instances.

## 8. Frozen replay controls

Companion checker:

```text
experiments/r5_e72_e12_multifield_rank_middle_band_firewall.py
```

### Frozen E12 q=6 RXC3 source

The source is cubic but not assumed linear:

```text
q=6,
c(H)=1,
d_Q(R)=0,
d_2(R)=0,
d_3(R)=1.
```

Target:

```text
N=102,
d_Q(B)=12,
d_2(B)=12,
d_3(B)=20,
r_2(B)=90,
r_3(B)=82.
```

### Connected q=9 extra control

This additional source happens to be linear and has

```text
d_Q(R)=1,
d_2(R)=1,
d_3(R)=2,
c(H)=1.
```

Target replay:

```text
N=153,
d_Q(B)=20,
d_2(B)=20,
d_3(B)=30,
r_2(B)=133,
r_3(B)=123.
```

### Disconnected 2 x q=6 control

The disjoint union of two frozen q=6 sources has

```text
q=12,
c(H)=2,
d_3(R)=2.
```

The formula predicts

```text
d_3(B)=36+2+2=40,
```

and replay verifies it.  This freezes the component term rather than silently
assuming source connectedness.

## 9. External anti-loop

The source problem is Restricted Exact Cover by 3-Sets (RX3C/RXC3), in which
every element occurs in exactly three triples.  The classical NP-complete
restriction is associated with:

* Teofilo F. Gonzalez, "Clustering to Minimize the Maximum Intercluster
  Distance", Theoretical Computer Science 38 (1985), 293-306,
  DOI `10.1016/0304-3975(85)90224-5`.

The oriented-incidence ingredient is the standard theorem

```text
rank(oriented incidence matrix) = |V|-components
```

over an arbitrary field; the spanning-forest proof is insensitive to parallel
edges.

The project-specific content is the exact E12 local quotient that transports
these facts into the target formulas.

## 10. What survives E72

E72 firewalls scalar rank/nullity **magnitudes** as the missing second
implication.  It does not firewall richer polynomial structure.

A successful universal theorem now has to exploit the dependency space itself,
not merely its dimension.  Candidate axes include:

```text
* canonical quotient of local gauge modes with a provably decreasing measure;
* support geometry of cross-field dependencies;
* Smith/integer relation structure beyond rank counts;
* interaction of the F2 top-shell condition with F3 Boolean subset-sum;
* a dependency algebra that remains polynomially representable even when all
  relevant ranks/nullities are linear.
```

Most importantly, every E73 proposal must be attacked on the E12 image first.
If a quotient merely recovers the RXC3 source, it is not progress toward a
universal polynomial solver.

Scientific status:

```text
P_VS_NP = OPEN.
```
