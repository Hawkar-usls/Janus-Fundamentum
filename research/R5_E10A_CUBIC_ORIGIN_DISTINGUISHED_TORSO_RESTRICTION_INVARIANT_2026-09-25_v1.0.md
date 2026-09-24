# R5 E10A — Cubic-Origin Distinguished-Torso Restriction Invariant

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_PLACEMENT_INVARIANT__ARBITRARY_LITERAL_TORSO_UNIVERSALITY_FALSIFIED__NO_SOLVER_CLAIM`

Authorizing audit:
`PA-0007-CUBIC-ORIGIN-INTERFACE-GLOBAL-OBJECTIVE-COUPLING`

Continuation of:
`NM-0011-CUBIC-ORIGIN-DISTINGUISHED-F-MINOR-UNIVERSALIZATION`

Checker:
`experiments/r5_e10a_cubic_origin_distinguished_torso_restriction_invariant.py`

## 1. Why this gate differs from NM-0011

NM-0011 proved that every loopless distinguished binary target `(N,p)` is a
minor of a polynomial-size cubic parent

```
P=M([I+P+Q|1])
```

with the parent distinguished element `f` mapped to `p`.

That theorem is allowed to use contraction.  PA-0007 correctly froze the
stronger requirement that a target be the literal real part of a decomposition
torso/interface.  The distinction is decisive.

## 2. Source-bound deletion fact

For a represented binary matroid, the cocycle space is the row space.
Deleting coordinates punctures that row space.  Equivalently, if
`A subseteq E(P)`, then

```
C*(P|A) = { D intersect A : D in C*(P) }.
```

This is standard binary code/matroid deletion-puncturing semantics.  Kashyap's
code-decomposition language source-binds the minor correspondence.  The
deletion-basis behavior is also explicit in the binary-matroid cocycle-basis
literature.

In a source-valid 1/2/3-sum decomposition, the nonvirtual elements belonging to
one torso are actual parent elements.  After all virtual separator elements are
removed, the real torso is exactly the restriction of the parent to those
actual elements.

Thus literal placement is deletion-only on the real torso, even though an
arbitrary minor may additionally use contractions.

## 3. Parent star design recalled

NM-0010 proved that every exact cubic parent has a spanning star of cocycles

```
D_1,...,D_n
```

such that

```
f in D_i,
|D_i|=4,
|D_i-{f}|=3,
span(D_i)=C*(P).
```

Let `A` be the actual-element set of a literal torso and assume `f in A`.
Put

```
N_real = P|A.
```

Puncture every star cocycle:

```
D_i^A = D_i intersect A.
```

Because `f in A`, every `D_i^A` is nonzero, contains `f`, and has size at
most four.  Puncturing commutes with linear span, hence

```
C*(N_real)
=
span { D_i^A : i=1,...,n }.
```

### Theorem — DISTINGUISHED_TORSO_4_COCYCLE_SPAN

Every real restriction of a literal decomposition torso of a cubic
`M([I+P+Q|1])` parent that retains the distinguished element `f` satisfies

```
C*(N_real)
=
span {
  D in C*(N_real) :
  f in D and |D| <= 4
}.
```

In particular,

```
cogirth(N_real) <= 4.
```

This theorem does not impose local cubicity, local `I+P+Q`, or a local
`n/3` bound on the torso.

## 4. Why contractions escape the invariant

Contraction is shortening rather than puncturing in the cocycle code.  It can
replace the inherited low-weight generating family by linear combinations
needed to cancel contracted coordinates.

Therefore there is no contradiction with NM-0011:

```
DISTINGUISHED MINOR UNIVERSALITY
=
TRUE

DISTINGUISHED LITERAL-PLACEMENT UNIVERSALITY
=
FALSE.
```

This is the exact structural gap requested by PA-0007.

## 5. Killer target Q4

Let `Q_m` be the complete four-labelled scaffold:

- underlying graph `K_m`;
- for each unordered pair `uv`, four parallel represented elements
  `e_(uv,g)`, one for each `g in GF(2)^2`;
- representation `[B_Km;S]`, where `B_Km` is reduced incidence and the two
  rows of `S` encode `g`.

Take `m=4`.  Then `Q_4` has 24 elements and rank five.

### 5.1 Cocycle weights

A cocycle is specified by a cut selector on `K_4` and a linear functional
`alpha in GF(2)^2`.

If `alpha=0`, a nonzero cut of `K_4` has three or four underlying edge
pairs, and each selected pair contributes all four labels.  The weight is
therefore 12 or 16.

If `alpha !=0`, exactly two of the four labels on every underlying edge pair
satisfy the cocycle equation, independently of the cut bit.  There are six
pairs, so the weight is 12.

Hence every nonzero cocycle of `Q_4` has weight

```
12 or 16.
```

Thus for every distinguished element `p`,

```
min{|D| : D in C*(Q4), p in D} = 12.
```

In particular `Q_4` violates DISTINGUISHED_TORSO_4_COCYCLE_SPAN maximally.

### 5.2 Three-connectivity

`Q_4` is a simple rank-five binary matroid on 24 elements.

If a 2-separation `(X,Y)` existed, then with both sides of size at least two
we would have

```
r(X)>=2,
r(Y)>=2,
r(X)+r(Y)<=6.
```

A simple binary rank-`r` set has at most `2^r-1` elements.  Under the above
rank-sum bound, the largest possible total is obtained from ranks two and four:

```
(2^2-1)+(2^4-1)=18 < 24.
```

Contradiction.  Therefore `Q_4` is 3-connected.

### 5.3 S8 is present as a restriction

Restrict `Q_4` to three vertices.  After deleting the unused incidence row
this is `Q_3`.

Using the standard S8 columns

```
[1,2,4,8,14,13,11,15],
```

the invertible linear map sending the four basis columns

```
(1,2,4,8) -> (1,2,5,9)
```

sends S8 to

```
[1,2,5,9,14,13,10,15],
```

all of which occur in `Q_3`.  Hence `Q_4` contains S8 as a restriction.

So the killer target lies exactly in the broad PA-0005 language:

```
two signature rows
+
3-connected
+
S8-containing.
```

## 6. Growing-family control

For general `Q_m`, `m>=4`:

- if the signature functional is zero, a nonzero cut contributes
  `4|delta(U)| >= 4(m-1)`;
- if it is nonzero, every one of `C(m,2)` underlying pairs contributes
  exactly two elements, giving `m(m-1)`.

Therefore

```
cogirth(Q_m)=4(m-1) > 4.
```

The placement obstruction is not an isolated accidental weight pattern.  The
complete four-labelled scaffold already fails it from `m=4` onward.  The
committed checker separately certifies the 3-connected S8-containing `Q_4`
member needed for the PA-0007 falsifier.

## 7. Source / anti-loop audit

The ingredients are standard:

- deletion/restriction punctures the cocycle row space;
- low-weight cocycle bases and their behavior under deletion are standard
  binary-matroid language;
- Truemper's induced-separation theory supplies sufficient conditions under
  which decompositions of minors induce decompositions of containing matroids,
  but it does not override the deletion invariant above.

No located source was found that states this JANUS-specific conjunction:
the NM-0010 distinguished 4-cocycle star, literal torso real-restriction
semantics, and the complete four-labelled `Q_4` falsifier.

This is a scoped derived theorem, not an absolute novelty claim for puncturing,
cocycle bases, or decomposition theory.

## 8. PA-0007 decision

Route A, as stated for arbitrary growing targets, is false:

```
ARBITRARY TARGET
->
LITERAL CUBIC-ORIGIN TORSO PLACEMENT
```

cannot hold because `Q_4` is an explicit admissible broad-class target that
violates a necessary placement invariant.

Route B therefore passes:

```
R5_E10A_CUBIC_ORIGIN_INTERFACE_GLOBAL_OBJECTIVE_COUPLING_GATE_V1
=
PASS_VIA_PLACEMENT_INVARIANT.
```

The invariant is stronger than required: it holds for every literal placement
before imposing the lower-bound-tight global objective.  Consequently it also
holds for every placement satisfying that objective.

The global `shortest_f=n/3+1` coupling is not claimed universal and need not
be used to refute arbitrary placement universality.

## 9. New frontier

Do not return to generic PA-0005 as if the cubic lineage were universal.

The actual surviving lineage has a new exact promise:

```
DISTINGUISHED_REAL_TORSO_4_COCYCLE_SPAN.
```

The next admissible mathematical gate is to exploit this promise
algorithmically or derive the next stricter image invariant:

```
R5_E10A_DISTINGUISHED_REAL_TORSO_4_COCYCLE_SPAN_CONTRACTION_GATE_V1.
```

Allowed exits:

1. deterministic polynomial shortest-f/interface algorithm on the promised
   two-row survivor;
2. strict witness-preserving contraction to a smaller known object;
3. a stronger source-valid cubic-placement invariant.

Forbidden:

- arbitrary-minor = placement;
- dropping the distinguished-f condition;
- reimposing local cubic degree or local n/3;
- returning to the unrestricted complete four-labelled scaffold;
- claiming P=NP from this structural separation.

## 10. Ceiling

```
DISTINGUISHED-f CUBIC MINOR IMAGE
=
UNIVERSAL (NM-0011)

ARBITRARY LITERAL TORSO PLACEMENT
=
FALSIFIED

DISTINGUISHED REAL TORSO 4-COCYCLE SPAN
=
PROVED NECESSARY

Q4
=
3-CONNECTED + S8-CONTAINING + TWO-ROW
AND VIOLATES THE INVARIANT

GLOBAL OBJECTIVE UNIVERSALIZATION
=
NOT PROVED / NOT NEEDED FOR THE FALSIFIER

DETERMINISTIC SOLVER
=
NOT PROVED

D1
=
EMPTY

P_VS_NP
=
OPEN
```
