# R5 E8 — Related Payload Cone-Gap Scope Repair Theorem

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_THEOREM__FROZEN_POWER_OF_TWO_CYCLIC_FAMILY__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_NET_PROJECTION_CHARGE_AND_STEP0_THEOREM_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_ODD_PREFIX_KAPPA_ZERO_LEMMA_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_PAYLOAD_BACKBONE_RIGIDITY_2026-09-22_v1.0.json`
- `research/R5_B1B1C5B2B2_E8_ODD_SELECTOR_BRANCH_INJECTIVITY_LEMMA_2026-09-22_v1.0.md`
- `research/tools/r5_e8_frozen_structural_aig_executor.py`

## 1. Scope correction

The originally tempting sufficient statement

```text
For every m=2^r >= 4,
for every related payload z,
choose an unresolved odd support selector o:

A_z - A_o >= s_z + 4
```

is false.

The exact `m=4` state after the already-proved first greedy choice `x_1` supplies a base exception.

For the remaining odd selector `x_3`:

```text
A_{x3}=9
sigma_{x3}=10
kappa_{x3}=0
E_{x3}=-1
cost(x3)=29
```

while, for example:

```text
z_1:
A_z=16
A_z-A_{x3}=7
s_z+4=8

z_3:
A_z-A_{x3}=5
s_z+4=6.
```

Therefore:

```text
RELATED_PAYLOAD_CONE_GAP
ORIGINAL_SCOPE_m>=4
=
FALSIFIED.
```

This falsifies only the sufficient cone-gap sublemma.

It does **not** falsify the odd-selector scheduler theorem: the same frozen state has `E_{x3}=-1` while the best payload primary net charge is `E=1`, so `x_3` is selected.

Together with the arbitrary-r step-0 theorem:

```text
m=4 DIRECT BASE
=
x_1 -> x_3

PROVED.
```

## 2. Repaired scope

The repaired theorem is:

```text
R5_E8_RELATED_PAYLOAD_CONE_GAP_V1

For every m=2^r >= 8,
on every odd-selector-only prefix state,
for every payload z that still has
at least one unresolved odd support selector o,

A_z - A_o
>=
s_z + 4.
```

A payload satisfying this condition is called `RELATED`.

A payload whose two odd support selectors have both already been projected is called `ORPHAN`.

## 3. Local occurrence count

For an occurrence of payload `z` in selector support block `G_i`, define

```text
c_i(z)
=
number of frozen local clause-AND gates
in that 3-literal clause that depend on z.
```

Because the selector literal is first and the two payload literals are then ordered by frozen variable id:

```text
c_i(z) in {1,2}.
```

If `z` is the first payload literal in the clause, `c_i=2`.

If `z` is the second payload literal, `c_i=1`.

For a fixed payload `z), its four support blocks are

```text
Supp(z)
=
{o,p,e,f},
```

where `o,p` are the two odd support selectors and `e,f` are the two even support selectors.

The payload-backbone rigidity bookkeeping parameter satisfies exactly

```text
sum_{i in Supp(z)} c_i
=
4 + s_z.
```

## 4. Exact cancellation against a related unresolved odd selector

Fix a related payload `z` and choose one unresolved odd support selector `o`.

The selector `o` occurs in exactly two frozen 3-clauses of block `G_o`.

Across those clauses there are four selector-dependent local clause-AND gates.

The payload `z` occurs in exactly one of those two clauses and occupies `c_o` of the four selector-dependent clause gates.

The block root `G_o` and every live structural ancestor above `G_o` depend simultaneously on `o` and `z`.

Therefore all common upper/backbone structure cancels from the cone set difference and:

```text
|Cone(o) \ Cone(z)|
=
4 - c_o.
```

This is exact.

## 5. Case A — the second odd support p is unresolved

The other three support blocks `p,e,f` contribute local gates that depend on `z` but not on `o`:

```text
(c_p+1)
+
(c_e+1)
+
(c_f+1)

=
(c_p+c_e+c_f)+3

=
(4+s_z-c_o)+3

=
s_z+7-c_o.
```

Because `p` is odd, its first frozen block-tree parent is

```text
H_p
=
AND(G_p,G_{p+1}).
```

The sibling `G_{p+1}` is one of the even support blocks of `z`.

Hence `H_p` depends on `z`, does not depend on `o`, and remains a live nonconstant frozen structural gate.

Therefore

```text
|Cone(z) \ Cone(o)|
>=
s_z+8-c_o.
```

Subtracting the exact opposite set difference:

```text
A_z-A_o

=
|Cone(z)\Cone(o)|
-
|Cone(o)\Cone(z)|

>=
(s_z+8-c_o)
-
(4-c_o)

=
s_z+4.
```

Case A is proved.

## 6. Case B — the second odd support p has already been projected

The two even support blocks are never projected on an odd-only prefix and contribute

```text
c_e+c_f+2
```

local `z)-only gates.

For the projected odd support `p`, exactly one of its two residual payload clauses `A_p,B_p` contains `z`.

That live two-literal residual contributes one additional `z)-only clause gate.

Thus before counting upper block-tree contribution:

```text
LOCAL_z_only

>=
c_e+c_f+3

=
s_z+7-c_o-c_p.
```

To reach the target it remains to supply

```text
c_p+1
```

additional upper `z)-only gates.

### 6.1 Parity of the odd-support occurrence profile

For the cyclic family with power-of-two `m`:

```text
j even
=>
c_o=c_p=1

j odd
=>
c_o=c_p=2.
```

This includes the cyclic wrap cases because the odd support positions are exactly the blocks in which the frozen payload ordering gives the same local rank to `z_j`.

### 6.2 j even

Here:

```text
c_p+1
=
2.
```

Let `p` be the already-projected odd support.

Its paired sibling `p+1` is one of the two unresolved even support blocks containing `z`.

The projection of `p` created the two live local parent refs

```text
H_p^0
=
AND(R_p^0,G_{p+1})

H_p^1
=
AND(R_p^1,G_{p+1}).
```

They are:

- distinct;
- nonconstant;
- independent of `o`;
- dependent on `z` through the unresolved even anchor `G_{p+1}`.

Later odd-selector projections do not eliminate these refs.

Hence they supply exactly the required two additional `z)-only upper gates.

Therefore the cone gap follows for even `j`.

### 6.3 j odd and m>=8

Here:

```text
c_p+1
=
3.
```

Take the old branch value of projected selector `p` whose residual `R_p` contains `z`.

In that branch all four cyclic-consecutive support positions

```text
{o,p,e,f}
```

carry `z)-dependence.

For the complete dyadic block tree with `m=2^r>=8`, these four cyclic-consecutive support positions with odd endpoint cannot collapse into the path from `o` to the root.

A direct dyadic-position check gives at least three live internal block-tree gates in the union of the four support root paths that:

- contain a `z)-dependent support descendant;
- do not contain block `o);
- hence depend on `z` and not on `o`.

One convenient finite geometry split is:

- non-wrap `j ≡ 1 (mod 4)`;
- non-wrap `j ≡ 3 (mod 4)`;
- the same two cases with the choice of which odd support is `o`;
- cyclic wrap at `j=1`;
- cyclic wrap at `j=3`.

In every case, the local support occupies two adjacent level-1 pairs plus at least one further dyadic ancestor outside the `o -> root` path.

The requirement `m>=8` is exact here: at `m=4` the third such upper gate need not exist, which is precisely the base exception recorded in Section 1.

Thus:

```text
UPPER_z_only
>=
3
=
c_p+1.
```

Case B is proved for odd `j` and `m>=8`.

## 7. Repaired cone-gap theorem

Combining Cases A and B:

```text
For every m=2^r>=8,
for every odd-only prefix state,
for every RELATED payload z,
and for either remaining unresolved odd support selector o chosen as above,

A_z-A_o
>=
s_z+4.
```

Therefore:

```text
R5_E8_RELATED_PAYLOAD_CONE_GAP_V1
REPAIRED_SCOPE_m>=8
=
PROVED.
```

## 8. Net-charge consequence

Previously proved:

```text
kappa_z=0

sigma_z <= s_z+12

sigma_o >= 8.
```

Also `kappa_o=0` on this odd-prefix regime.

Hence:

```text
E_z-E_o

=
(A_z-A_o)
-
(sigma_z-sigma_o)

>=
(s_z+4)
-
((s_z+12)-8)

=
0.
```

Thus a related payload cannot strictly beat its unresolved odd support selector on the primary net-charge key.

If primary net charge ties, then:

```text
A_z-A_o
>=
s_z+4
>=
4
```

so:

```text
A_o < A_z.
```

The odd selector therefore wins the frozen secondary cone-size tie-break.

Consequently, for `m>=8):

```text
EVERY RELATED PAYLOAD
IS EXCLUDED
FROM THE GREEDY WINNER SET.
```

For `m=4`, the complete odd prefix is already closed directly:

```text
x_1 -> x_3.
```

## 9. Remaining payload class

The only unresolved scheduler obstruction is now:

```text
ORPHAN PAYLOAD z

iff

both odd support selectors of z
have already been projected.
```

The next and only scheduler theorem target is:

```text
R5_E8_ORPHAN_PAYLOAD_BARRIER_V1

While at least one odd selector remains unresolved,
no orphan payload can beat all unresolved odd selectors
under the exact frozen key

(E_v,A_v,variable_id).
```

## Claim ceiling

```text
ORIGINAL_RELATED_PAYLOAD_CONE_GAP_m>=4
=
FALSIFIED_BY_m4_BASE_EXCEPTION

m4_ODD_PREFIX_BASE
=
PROVED_DIRECTLY

REPAIRED_RELATED_PAYLOAD_CONE_GAP_m>=8
=
PROVED

RELATED_PAYLOADS
=
CLOSED_AS_GREEDY_WINNERS

ORPHAN_PAYLOAD_BARRIER
=
OPEN

ODD_SELECTOR_GREEDY_PREFIX
=
OPEN

ARBITRARY_N_GREEDY_LOWER_BOUND
=
OPEN

P_VS_NP
=
OPEN
```
