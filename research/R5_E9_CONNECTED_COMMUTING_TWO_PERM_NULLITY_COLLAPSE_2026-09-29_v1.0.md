# R5 E9 — Connected Commuting Two-Permutation Nullity Collapse

Date: 2026-09-29

Status:
`JANUS_EXACT_THEOREM__COMMUTING_CONNECTED_BRANCH_NULLITY_0_OR_2`

## 1. Setting

Let

```text
A = I + P + Q
```

where `P,Q` are permutation matrices on a finite set `Omega`. Assume

```text
PQ = QP
```

and the action of `<P,Q>` on `Omega` is transitive (equivalently, the normalized two-permutation carrier is connected).

No SAT assumption is needed.

## 2. Theorem

### Theorem CCN-1

Under the hypotheses above,

```text
nullity_Q(A) in {0,2}.
```

Equivalently, a connected commuting two-permutation carrier can never have rational nullity larger than two.

Therefore every connected normalized source with

```text
nullity_Q(I+P+Q) >= 3
```

must satisfy

```text
PQ != QP.
```

This is a structural terminal only. It is not a universal polynomial solver for the noncommuting branch.

## 3. Proof

Let `H=<P,Q>`. Since `P,Q` commute, `H` is abelian. A transitive abelian permutation action has the following standard quotient form: if `K` is the stabilizer of one point, then all point stabilizers equal `K`, `K` is normal, and the induced action of

```text
G = H/K
```

on `Omega` is regular. Thus identify `Omega` with the finite abelian group `G`. Let `p,q in G` be the images of `P,Q`; they generate `G`.

Over `C`, the characters `chi in G^` form an eigenbasis for every translation operator. On the character vector for `chi`,

```text
A = I + P + Q
```

has eigenvalue

```text
lambda_chi = 1 + chi(p) + chi(q).
```

Because `G` is finite, `chi(p)` and `chi(q)` lie on the unit circle. If `lambda_chi=0`, then three unit complex numbers

```text
1, chi(p), chi(q)
```

sum to zero. Equality in the elementary equilateral-triangle condition on the unit circle forces

```text
{chi(p), chi(q)} = {omega, omega^2},
```

where `omega=exp(2*pi*i/3)`.

Since `p,q` generate `G`, a character is uniquely determined by the ordered pair `(chi(p),chi(q))`. Hence at most two characters can have zero eigenvalue: the candidate with values `(omega,omega^2)` and its complex conjugate `(omega^2,omega)`.

If one candidate is a valid character of `G`, complex conjugation gives the other. The two candidates are distinct. Therefore

```text
nullity_C(A) in {0,2}.
```

Finally `A` has rational entries, so its rank is unchanged by extension of scalars from `Q` to `C`. Hence

```text
nullity_Q(A)=nullity_C(A) in {0,2}.
```

QED.

## 4. Why connectedness is necessary

Drop transitivity and nullity adds across invariant components.

On `Z_3`, choose translations

```text
p=1, q=2.
```

Then

```text
I+P+Q = J_3
```

has rank one and nullity two. The disjoint union of two such components is still commuting but has nullity four.

Therefore the theorem is genuinely a connected/transitive statement.

## 5. Relation to the directed perfect-code normal form

The existing JANUS theorem

```text
CUBIC-LINEAR EXACT-ONE
= directed perfect-code existence
  on a 2-in/2-out union of two permutation arc sets
```

already identifies the commuting connected branch with strongly connected 2-valent abelian Cayley digraphs.

Yu–Yang–Fan–Ma (Discrete Applied Mathematics 357 (2024), 236–240; arXiv:2310.19017) classify perfect codes in that abelian branch. CCN-1 is a different, source-internal spectral statement: it proves that the commuting branch cannot support high rational nullity at all.

The literature binding is corroborative; the proof above is self-contained.

## 6. Consequence for the live R5 E9 gate

The current difficult regime includes

```text
connected
+ A=I+P+Q
+ nullity_Q(A)=omega(log n)
+ post-RKPR hard residual
+ linear cubic Levi carrier.
```

CCN-1 removes the entire commuting possibility from that regime:

```text
high-nullity connected residual
=> genuinely noncommuting two-permutation action.
```

This is useful pruning, but it does not bound the noncommuting branch and does not prove a polynomial boundary-direction selector.

## 7. Anti-loop / scope firewall

Do **not** promote any of the following:

```text
commuting connected => universal SAT solved         FALSE
noncommuting => high nullity                        FALSE
high nullity => post-RKPR hostile family exists     NOT PROVED
CCN-1 => P=NP                                       FALSE
```

The exact promotion is only

```text
connected + PQ=QP => nullity_Q(I+P+Q) in {0,2}.
```

## 8. Ceiling

```text
CONNECTED COMMUTING NULLITY COLLAPSE = PROVED
CONNECTED HIGH-NULLITY => NONCOMMUTING = PROVED
NONCOMMUTING POST-RKPR GLOBAL QUOTIENT = OPEN
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```
