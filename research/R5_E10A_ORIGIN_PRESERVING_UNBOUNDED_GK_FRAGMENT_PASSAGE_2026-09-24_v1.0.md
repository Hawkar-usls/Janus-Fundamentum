# R5 E10A — Origin-Preserving Unbounded GK Fragment Passage

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_ORIGIN_CLASS_BARRIER_AFTER_REAUDIT__NO_SOLVER_OR_HARDNESS_CLAIM`

Authorizing re-audit:
`PA-0005-R1-ORIGIN-PRESERVING-PARITY-REGULAR`

Continuation of:
`NM-0008-OPTIMAL-FACE-BLOSSOM-PARITY-DP`

Checker:
`experiments/r5_e10a_origin_preserving_parity_regular_preimage.py`

## 1. Question

A generic skew-symmetric counterexample is not automatically authoritative for
the E10A carrier.  The current object originates from an undirected unit-weight
graph with two GF(2) signature rows.

The required firewall is:

```
TRANSFORMED-SPACE COUNTEREXAMPLE
!=
ORIGIN-CLASS COUNTEREXAMPLE
```

unless an explicit preimage is supplied.

This note supplies such a preimage for the unbounded GK fragment-passage
obstruction.

## 2. Unit-weight GF(2)^2 base family G_m

Fix any integer `m>=2`.  Every edge has unit weight and a label
`(alpha,beta) in GF(2)^2`.

Create four principal s--t routes.

### Cheap 00 route

```
s - v - w - t
```

All three edges have label `00`, so its cost is 3.

### Long target 01 route Q_m

```
s-x1-y1-x2-y2-...-y_(m-1)-x_m-t
```

It has exactly `2m` edges.  Give only `s-x1` beta label one and give
every edge alpha label zero.  Hence its total label is `01`.

### Two cheap alpha-one controls

Add internally disjoint two-edge routes

```
s-p10-t
s-p11-t
```

with total labels `10` and `11`, respectively.

### Long bud connectors

Let `L=4m+5`.

For every `i=1,...,m`, add two internally vertex-disjoint length-L paths
from `w` to `x_i`, using fresh vertices:

- `A_i`: total label `00`;
- `B_i`: total label `10`.

All connector beta labels are zero.

The connector paths are longer than the target route and therefore cannot
improve any of the four displayed label optima.

## 3. Exact four-label costs

Every s--t path that avoids the connectors lies on one of the four principal
routes.  Every path that uses a connector has length at least `L>2m`.

Therefore

```
d_00 = 3
d_01 = 2m
d_10 = 2
d_11 = 2.
```

For every `m>=2`,

```
d_01 > max(d_00,d_10,d_11).
```

Thus the family lies inside the post-NM-0008 promise: `01` is the certified
unique strict maximum.

## 4. Alpha double cover

Take the ordinary two-sheet alpha cover.

A base edge `uv` of alpha label `a` lifts to

```
u^j -- v^(j xor a),  j in {0,1}.
```

The deck involution exchanges the two sheets.

Fix the alpha-zero terminal pair `s^0,t^0`.  The remaining target condition is
exactly beta parity one.

The lifted cheap 00 route has cost 3.  The lifted Q_m has cost `2m` and beta
parity one.

All weights and beta labels are inherited symmetrically.

## 5. Rudolph vertex split and endpoint gadget

Replace each cover vertex `z` by `z^-,z^+`, add the zero-cost zero-beta
internal arc

```
i_z : z^- -> z^+,
```

and replace a cover arc `u->v` by

```
u^+ -> v^-.
```

Add the standard fresh complementary endpoint pair `a,bar(a)`; gadget arcs
have weight and beta zero.

The path maps preserve:

- total weight;
- beta XOR;
- regularity;
- polynomial witness reconstruction.

Hence the construction is an explicit preimage under the exact E10A bridge.

## 6. An origin-valid GK bud tau_m

Let `C_m` consist of `w`, all `x_i), and every fresh connector vertex.

In split space define the symmetric node set `V_tau` as follows:

- include `(w^0)^+` and `(w^1)^-`;
- for every other cover vertex above a name in `C_m`, include both split
  polarities in both sheets.

Equivalently, start with all split copies over `C_m` and remove exactly the
mate pair

```
(w^0)^-
(w^1)^+.
```

Take the base arc

```
e_tau = i_(w^0) : (w^0)^- -> (w^0)^+.
```

Its mate is the anti-base arc `i_(w^1)`.

Let `E_tau` contain every split internal arc and every split transfer arc
of the connector network whose two ends lie in `V_tau`.  In particular,
for every included non-w split vertex both polarities are incident with
`E_tau`; the base and anti-base arcs themselves are not in `E_tau` because
their outside endpoints were removed.  The set `E_tau` is symmetric, and
the set of nodes incident with it is exactly `V_tau`.

This is a GK bud in the literal sense of Section 2.2.

The base tail is outside `V_tau`, the base head is inside, and the source
prefix through the cheap route reaches the base tail without meeting
`V_tau`.

For reachability inside the bud, the two connector paths per `x_i) are the
key.  Their cover lifts are

```
A_i^0 : w^0 -> x_i^0
A_i^1 : w^1 -> x_i^1
B_i^0 : w^0 -> x_i^1
B_i^1 : w^1 -> x_i^0.
```

Prefixes of `A_i^0` and `B_i^0` reach all sheet-zero / flipped connector
states from the base node.  To reach states on `A_i^1`, follow `B_i^0` to
`x_i^1` and then traverse the required prefix of `A_i^1` backwards.
Symmetrically, `A_i^0` followed by reversed `B_i^1` reaches the remaining
states, including the anti-base side.

Because the A and B connector interiors are disjoint, these paths never use an
arc together with its mate.  Hence all required internal paths are regular.

## 7. The target path crosses one positive fragment arbitrarily many times

The split lift of Q_m never uses the base or anti-base arc.

For every `x_i^0` it:

1. enters `V_tau` through one non-base boundary transfer arc;
2. leaves `V_tau` through another non-base boundary transfer arc.

Therefore it has exactly `2m` non-base boundary crossings.

For the Goldberg--Karzanov fragment characteristic function,

```
chi_tau . chi_Qm = -2m
```

and hence

```
k_tau(Q_m)
=
-1/2 (chi_tau . chi_Qm)
=
m.
```

Since `m` is arbitrary,

```
NO UNIVERSAL CONSTANT C
CAN BOUND k_tau
EVEN ON THE ACTUAL
UNIT-WEIGHT GF(2)^2 E10A ORIGIN CLASS.
```

## 8. Positive optimal fragment certificate

The scalar beta-unconstrained optimum for the fixed alpha-zero endpoints is the
cheap 00 route of cost

```
W=3.
```

Set

```
epsilon_tau = 1 - 3/(2m) > 0.
```

Under the GK fragment transformation:

- each ordinary unit boundary arc has transformed length
  `1-epsilon_tau = 3/(2m)>0`;
- the zero-length base and anti-base internal arcs obtain length
  `epsilon_tau>0`;
- connector-internal arcs are unchanged and nonnegative.

The cheap route has one base and one ordinary boundary crossing, so its net
fragment characteristic is zero and its transformed length remains 3.

The target path has `2m` ordinary boundary crossings, so

```
l*(Q_m)
=
2m(1-epsilon_tau)
=
3.
```

Any path using a connector pays at least `L=4m+5` on connector-internal unit
arcs alone.  The remaining principal routes do not give a cheaper fixed
alpha-zero regular path.

It remains to check the stronger condition needed for an LP certificate:
the ordinary (not regularity-filtered) shortest `a--bar(a)` path for the
transformed nonnegative lengths must also have value 3.

Every endpoint-gadget path has one of four first/last boundary choices.
The two regular choices project to alpha-zero `s--t` paths (or their
complemented reverses).  Among paths avoiding the long connectors, the only
alpha-zero principal routes are the cheap 00 route and `Q_m), and both have
transformed length 3.  A connector-using route pays at least `L=4m+5` on
unchanged connector-internal unit arcs.

The two nonregular endpoint choices project to a cover path between opposite
sheets of the same base endpoint, hence to a base closed path of total alpha
one.  Avoiding connectors, such a path must combine one of the two length-two
alpha-one control routes with an alpha-zero `s--t` route.  The latter has
transformed length at least 3, while the control route costs 2, so these
choices cost at least 5.  Connector-using choices are larger still.

Therefore the ordinary transformed shortest-path value is exactly 3.
Ordinary shortest-distance potentials for the transformed nonnegative
lengths consequently satisfy the GK LP inequalities with

```
epsilon_tau > 0
and
pi(bar(a)) = 3 = W.
```

The finite checker independently constructs the full split endpoint graph and
verifies this ordinary shortest value for `m=2,3,4,5`.

So the unbounded passage count occurs in a source-valid positive-fragment
optimal certificate, not merely in an arbitrary symmetric vertex subset.

## 9. Consequence

The transformed-space firewall is now discharged for this obstruction:

```
GENERIC GK CONTROL
->
EXPLICIT GF(2)^2 UNIT-WEIGHT PREIMAGE
=
PASS.
```

Therefore:

```
k_tau <= 1
=
FALSIFIED ON ORIGIN CLASS

k_tau <= C FOR ANY FIXED CONSTANT C
=
FALSIFIED ON ORIGIN CLASS.
```

This blocks constant-passage bud normalization as the missing deterministic
currency.

It does not prove that polynomial compression is impossible.  The passage count
itself has polynomial range, and a different structural contraction may avoid
storing passage history.

## 10. Next target

Do not broaden to arbitrary parity-regular skew graphs, and do not repair the
failure by accumulating full mate-history.

The next admissible question is:

```
Can repeated mate-conflict information on this
origin-valid family be eliminated structurally
by a polynomial exact contraction,
rather than stored as continuation history?
```

The reserved alternative remains the triple-dual common-pullback route.

## 11. Ceiling

```
ORIGIN PREIMAGE FOR k_tau=m
=
PASS THEOREM

UNBOUNDED k_tau INSIDE E10A ORIGIN CLASS
=
PASS BARRIER

CONSTANT-PASS BUD NORMALIZATION
=
FALSIFIED

GENERIC PARITY-REGULAR SKEW SOLVER
=
NOT A TARGET

DETERMINISTIC GF(2)^2 EXACT-LABEL PATH
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
