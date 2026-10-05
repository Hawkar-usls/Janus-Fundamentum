# R5 E85 — Conditioned U2,4 Minor Normal Form

Date: 2026-10-06

Status:
`U24_MINOR_EQUALS_BOUNDARY_PIN_AND_PROJECT__C4FREE_RESIDUAL_ZERO_HOLE_NORMAL_FORM_PROVED`

Scientific ceiling:

```text
E85 DOES NOT EXCLUDE U_{2,4} FROM ALL C4-FREE RXC3 BOUNDARY MATROIDS.

IT PROVES THAT EVERY SUCH MINOR MUST APPEAR AS A FOUR-PORT CONDITIONED
ExactOne_3/Equality_3 BOUNDARY RELATION AFTER A SPECIFIC 0/1 PINNING PATTERN,
AND THAT UNIT PROPAGATION REDUCES THE CONDITIONED WITNESS TO A NARROW
SUBCUBIC "ZERO-HOLE" NORMAL FORM.

AN EXPLICIT UNRESTRICTED 5-PORT NONBINARY TANNER WITNESS IS GIVEN; IT
REALIZES THE NORMAL FORM WITH ONE CHECK-SIDE ZERO HOLE, BUT IT CONTAINS
TANNER C4s AND IS OUTSIDE THE LINEAR-SOURCE CLASS.

P_VS_NP = OPEN.
```

## 1. Starting point

E83 proved that every exact Tanner boundary relation (D) satisfying delta
exchange has a canonical ordinary matroid

[
M(D)=D*P,
]

where (P) is the complete set of variable-side boundary coordinates.

Tutte's theorem then says that (M(D)) is binary iff it has no
(U_{2,4})-minor. E84 attacked the strongest direct four-port realization and
proved a residual-cubic normal form, then exhausted all direct C4-free cases
through (12	imes12) without finding (S5/U_{2,4}).

The remaining representation escape hatch is therefore a **minor-only**
obstruction: (M(D)) may have more than four boundary elements and reveal
(U_{2,4}) only after deletion/contraction of other elements.

## 2. Minor-to-pinning lemma for basis families

Let (M) be a matroid with basis family (mathcal B), and let (e) be one
ground element.

### Deletion

If (e) is not a coloop, the bases of (M\e) are exactly the bases of (M)
that avoid (e), projected to the remaining ground set.

If (e) is a coloop, every basis contains (e), and deleting (e) removes
that forced coordinate from every basis.

Thus deletion is always:

[
oxed{	ext{pin }e	ext{ to one fixed membership bit, then project }e.}
]

### Contraction

If (e) is not a loop, the bases of (M/e) are obtained from bases containing
(e), with (e) removed.

If (e) is a loop, no basis contains (e), and contraction simply removes the
forced-zero coordinate.

Thus contraction is also:

[
oxed{	ext{pin }e	ext{ to one fixed membership bit, then project }e.}
]

Iterating proves:

[
oxed{
	ext{Every matroid minor basis family is obtained by a fixed 0/1 pinning
of eliminated elements followed by projection.}
}
]

This is the exact basis-family form of the standard deletion/contraction
definition of matroid minors. Standard sources also state that restriction is
deletion and contraction is its dual operation.

## 3. Undoing the canonical Tanner twist

Let

[
M=D*P.
]

Suppose a four-element surviving ground set (R) supports a minor
isomorphic to (U_{2,4}).

By Section 2 there is a fixed membership pattern on (E-R) such that the
projected basis family is exactly (U_{2,4}).

Undoing the twist is coordinatewise XOR with (P). Therefore the same
operation on the original exact boundary relation (D) is just boundary
pinning with the corresponding XOR-adjusted bits.

The surviving four-port relation is

[
oxed{
D_R = U_{2,4} * (Pcap R).
}
]

So every nonbinary exact Tanner delta interface has a **conditioned four-port
witness**. There is no need to reason about arbitrary abstract minors after
this reduction.

This also matches Tutte's unique excluded-minor characterization of binary
matroids.

## 4. Five possible survivor orientations

Let

[
p=|Pcap R|in{0,1,2,3,4}.
]

The four-port conditioned family is one of five orientation classes

[
U_{2,4}*(Pcap R),
]

distinguished only by the number (p) of variable-side survivor coordinates.

For any basis (B) of (U_{2,4}), (|B|=2). If

[
F=B	riangle(Pcap R),
]

then the Tanner signed boundary quantity is

[
|Fcap P|-|Fcap N|=p-2.
]

Thus all six conditioned states automatically have the exact signed invariant
required by E83.

The direct E84 (S5) case is the special orientation (p=2).

## 5. Unit propagation normal form

Now condition all eliminated boundary coordinates to the pinning pattern from
Section 3 and propagate ExactOne/Equality constraints to a fixed point.

The following reductions are deterministic.

### Variable-side pins

A pinned boundary incidence of an Equality_3 variable fixes the value of that
entire variable. All three incidences of that variable become fixed.

Therefore no active residual variable can retain any pinned incidence.

Every active residual variable keeps all of its active/free incidences from the
original cubic variable constraint.

### Check-side pin 1

A check-side boundary incidence pinned to 1 already satisfies its ExactOne
check. Every other incidence of that check is forced to 0 and propagation
continues.

### Check-side pin 0

A check-side incidence pinned to 0 merely removes one available incidence from
the check.

After fixed-point propagation, an active ExactOne check may therefore retain
one such fixed-zero missing incidence. Two fixed-zero holes would leave only
one active incidence and force it to 1, so that check would not remain active.

Hence all surviving hidden pins can be represented as **check-side zero holes**.

### C4-freeness

Propagation only fixes/removes vertices or incidences. It never adds an
internal Tanner edge.

Therefore a C4-free source remains C4-free after the reduction.

Thus every hypothetical linear-source (U_{2,4})-minor has a residual witness
with:

```text
* four free survivor ports;
* active Equality variables, with no hidden pins;
* active ExactOne checks;
* some checks carrying one fixed-zero hole;
* no other fixed coordinates;
* C4-free internal incidence geometry;
* exact four-port relation U2,4 * (P intersect R).
```

This is the E85 **conditioned zero-hole normal form**.

## 6. Survivor ports lie on distinct same-side vertices

The family (U_{2,4}*(Pcap R)) separates every pair of coordinates: for any
two survivor positions there are feasible states in which their bits differ.

Therefore two variable-side survivor ports cannot belong to the same Equality
variable.

Similarly, for any two check-side survivor ports, the six-state family contains
a state in which both are 1. Two such ports therefore cannot belong to the
same ExactOne check.

So same-side survivor ports lie on distinct Tanner vertices.

## 7. Exact counting identities for the residual witness

Let

[
a=#	ext{ active checks},qquad
b=#	ext{ active variables},
]

and let

[
p=#	ext{ variable-side free survivor ports},qquad
q=4-p.
]

Let (h) be the number of retained check-side zero holes.

Active variables have no hidden pins, so counting their three incidences gives

[
m+p=3b,
]

where (m) is the number of active internal Tanner edges.

On the check side, the four free survivor incidences contribute (q), while
each zero hole removes one active incidence from an originally cubic check:

[
m+q=3a-h.
]

Eliminating (m) and using (q=4-p) yields

[
oxed{
h=3(a-b)+2p-4.
}
]

The exact signed-balance identity remains valid on the residual active
network:

[
|Fcap P|-|Fcap N|=3|Y_F|-a.
]

For the (U_{2,4})-minor family the left side is (p-2), hence every one of
the six states uses exactly

[
oxed{
|Y_F|=rac{a+p-2}{3}.
}
]

Therefore

[
oxed{
a+p-2equiv0pmod3.
}
]

These constraints are universal for every conditioned (U_{2,4}) residual
witness.

## 8. Orientation-specific minimum zero-hole counts

Write (d=a-b). From

[
h=3d+2p-4ge0
]

the first arithmetically possible zero-hole counts are:

```text
p=0 : h>=2, first at d=+2
p=1 : h>=1, first at d=+1
p=2 : h>=0, first at d= 0
p=3 : h>=2, first at d= 0
p=4 : h>=1, first at d=-1
```

This explains precisely why E84 saw only the (p=2,h=0,a=b) direct lane.

A minor-only escape need not resemble E84's cubic residual graph. The smallest
new lane is already (p=1,h=1).

## 9. Explicit unrestricted five-port conditioned witness

E85 freezes the connected Tanner cluster with 7 checks, 6 variables and
internal edges

```text
(0,1) (0,2) (0,5)
(1,0) (1,3) (1,4)
(2,1) (2,2) (2,5)
(3,0) (3,1)
(4,4) (4,5)
(5,3)
(6,0) (6,3) (6,4)
```

Its raw boundary arity is five:

```text
4 check-side ports
1 variable-side port.
```

The exact boundary family is

```text
D = {1,2,4,8,19,21,22,25,26}.
```

It satisfies delta exchange.

The canonical twist is the single variable-side coordinate:

[
P=10000_2.
]

The matroid basis family is

```text
M(D) = {3,5,6,9,10,17,18,20,24}.
```

This is a rank-2 matroid on five elements in which exactly one pair is
parallel.

Deleting element 2 leaves all six pairs on the four survivors:

[
oxed{M(D)\2cong U_{2,4}.}
]

In the original Tanner relation, element 2 is check-side, so the exact same
operation is simply

[
oxed{	ext{pin boundary bit 2 to }0	ext{ and project it away}.}
]

The four-port conditioned family becomes

```text
{1,2,4,11,13,14}
```

which is exactly (U_{2,4}) twisted by the one surviving variable-side port.

Its residual parameters are

[
a=7,quad b=6,quad p=1,quad h=1,
]

and indeed

[
1=3(7-6)+2-4,
]

while all six states use

[
(7+1-2)/3=2
]

selected active variables.

So the E85 normal form is not vacuous.

## 10. Why the witness still does not kill the linear-source conjecture

The witness contains many Tanner C4s. For example multiple pairs of variables
share two included checks.

Therefore it is outside the square-cubic-linear RXC3 source class.

This sharply identifies the next question:

[
oxed{
	ext{Can any C4-free conditioned zero-hole normal form realize }
U_{2,4}*(Pcap R)?
}
]

The unrestricted answer is yes. The linear-source answer remains open.

## 11. Computational stress already performed

In addition to the exact frozen E84 census, a targeted search over thousands of
connected C4-free subcubic Tanner networks with 5–10 boundary coordinates and
sizes up to (12+12) found many delta interfaces, but no nonbinary one.

This is **not** promoted to theorem status and is intentionally not used as a
proof claim. It only supports choosing the zero-hole normal form, rather than a
generic random search, as the next exact target.

## 12. Impact on the representation route

Before E85:

```text
possible U2,4 minor = arbitrary abstract deletion/contraction pattern.
```

After E85:

```text
possible U2,4 minor
= four surviving boundary ports
+ one of five orientations p=0..4
+ ExactOne/Equality propagation
+ only check-side zero holes remain
+ exact arithmetic h=3(a-b)+2p-4
+ a+p-2 == 0 mod 3
+ C4-free geometry preserved.
```

That is a much smaller theorem target.

## 13. Next killer-test — E86

```text
ZERO-HOLE U24 LINEARITY KILLER

Enumerate/prove the E85 residual normal forms orientation by orientation.

Priority:
  p=1, h=1   (smallest new minor-only lane; explicit nonlinear witness exists)
  p=4, h=1
  p=0, h=2
  p=3, h=2
  p=2, h=3+ (E84 already closes h=0 through 12x12)

For each lane:

1. derive the residual graph/hypergraph normal form under C4-freeness;
2. either prove the six U2,4-twist states force a repeated variable-pair/check-pair,
   hence a Tanner C4;
3. or construct the first genuine C4-free conditioned U2,4 witness.
```

A proof that all five zero-hole lanes are impossible would establish:

[
oxed{
	ext{Every square-cubic-linear RXC3 exact delta interface is binary.}
}
]

That would close the representation front, but **not** the global algorithm
front: E81 still requires a recursive/overlapping represented decomposition.

## 14. Companion replay

```text
experiments/r5_e85_conditioned_u24_minor_normal_form.py
```

Frozen assertions:

```text
* deletion/contraction basis families replay as pin-and-project;
* the explicit 5-port Tanner family is delta;
* its canonical matroid basis family is rank 2;
* deleting one element gives exactly U2,4;
* Tanner pin bit2=0 gives exactly the corresponding twisted four-port U2,4 family;
* the witness satisfies the E85 count identities;
* the witness has Tanner C4s;
* orientation-specific minimum zero-hole counts are 2,1,0,2,1 for p=0..4.
```

Scientific status:

```text
E85 = PROVED MINOR-TO-PINNING REDUCTION
      + PROVED CONDITIONED ZERO-HOLE NORMAL FORM
      + EXPLICIT UNRESTRICTED MINOR-ONLY U24 WITNESS.

LINEAR_RXC3_CONDITIONED_U24 = OPEN.
DIRECT_U24_THROUGH_12x12 = EXCLUDED BY E84.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED BY E81.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
