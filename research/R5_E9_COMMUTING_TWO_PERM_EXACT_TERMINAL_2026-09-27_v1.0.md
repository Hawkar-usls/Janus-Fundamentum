# R5 E9 — Exact Terminal for the Commuting Two-Permutation Branch

Date: 2026-09-27

Status:
`JANUS_EXACT_POLYNOMIAL_TERMINAL__SCOPED_TO_COMMUTING_NORMALIZATION`

Scientific firewall:

```text
THIS CLOSES ONLY THE BRANCH IN WHICH A VALID NORMALIZATION A=I+P+Q HAS PQ=QP
AND THE NORMALIZED LEVI GRAPH IS CONNECTED.

IT DOES NOT PROVE THAT EVERY HARD CARRIER ADMITS SUCH A NORMALIZATION.
IT DOES NOT PROVE P=NP.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parent checkpoint:
- `R5_E9_SEMANTIC_CHECKPOINT_OET_IRREDUCIBLE_HIGH_NULLITY_2026-09-27_v1.0.md`

Executable regression:
- `experiments/r5_e9_commuting_two_perm_terminal.py`

## 1. Frozen setting

Let

\[
A=I+P+Q
\]

be a normalized connected cubic square carrier from the existing two-permutation theorem, with permutations `p,q` represented by `P,Q`. Assume

\[
PQ=QP.
\]

Connectedness of the normalized Levi graph is equivalent to transitivity of

\[
\Gamma=\langle p,q\rangle
\]

on the `n` coordinates.

Because `p,q` commute, `Gamma` is abelian. A transitive abelian permutation group is regular: if an element fixes one point, commutativity plus transitivity makes it fix every point, hence it is the identity permutation.

Therefore the coordinate set can be identified with the finite abelian group `Gamma` itself, acting by translations.

## 2. Fourier diagonalization

Over `C`, the regular representation of a finite abelian group has the character basis

\[
\widehat\Gamma=\operatorname{Hom}(\Gamma,\mathbb C^\times).
\]

For a character `chi`, the translation operators `P,Q` act diagonally. Up to the harmless inverse convention for left/right translation, the eigenvalue of `A` is

\[
\lambda_\chi=1+\chi(p)+\chi(q).
\]

Hence `chi` contributes to the kernel exactly when

\[
1+u+v=0,
\qquad
u=\chi(p),\ v=\chi(q),
\qquad |u|=|v|=1.
\]

### Unit-circle lemma

If `|u|=|v|=1` and `1+u+v=0`, then

\[
\{u,v\}=\{\omega,\omega^2\},
\qquad \omega=e^{2\pi i/3}.
\]

Proof: `u+v=-1` is real. Thus `v=\bar u`; writing `u=e^{i\theta}` gives `2\cos\theta=-1`, so `theta` is `2pi/3` or `4pi/3` modulo `2pi`.

Because `p,q` generate `Gamma`, a character is uniquely determined by the ordered pair

\[
(\chi(p),\chi(q)).
\]

There are therefore at most two kernel characters, corresponding to

```text
(omega, omega^2)
(omega^2, omega).
```

They occur together by complex conjugation.

Since rank is unchanged under the field extension `Q -> C`, rational and complex nullities agree.

### Theorem CTP-1

\[
\boxed{
PQ=QP\ \text{and connectedness}
\Longrightarrow
\nu_{\mathbb Q}(I+P+Q)\in\{0,2\}.
}
\]

In particular, a connected commuting normalization can never belong to the current `omega(log n)` high-nullity residual.

## 3. Exact SAT/UNSAT dichotomy

Every cubic square incidence matrix satisfies

\[
A\mathbf 1=3\mathbf 1.
\]

If `nu_Q(A)=0`, the already-proved full-rank terminal applies:

```text
nullity = 0 => BOOLEAN UNSAT.
```

Suppose `nu_Q(A)=2`. Then there is a character with

\[
\chi(p)=\omega,
\qquad
\chi(q)=\omega^2
\]

(or the conjugate orientation).

Equivalently, there is a homomorphism

\[
\phi:\Gamma\to\mathbb Z_3
\]

with

\[
\phi(p)=1,
\qquad
\phi(q)=2.
\]

For every coordinate `g`, the normalized source triple is

\[
\{g,pg,qg\}.
\]

Its three colors are

\[
\phi(g),\quad \phi(g)+1,\quad \phi(g)+2,
\]

so it contains each residue class modulo 3 exactly once.

Therefore each color class is an Exact-One witness. There are exactly three such witnesses, one for each additive shift / chosen color.

### Theorem CTP-2

For a connected commuting normalization:

\[
\boxed{
\nu_{\mathbb Q}(A)=0 \iff \operatorname{EX1}(A)=\text{UNSAT},
}
\]

and

\[
\boxed{
\nu_{\mathbb Q}(A)=2 \iff \operatorname{EX1}(A)=\text{SAT},
}
\]

with exactly three Boolean Exact-One witnesses in the SAT case.

Thus this branch is completely decided; no kernel enumeration is necessary.

## 4. Linear-time constructive algorithm after normalization

The character language is useful for the proof, but the solver can be purely combinatorial.

Try the two orientations

```text
orientation + : c(p(i)) = c(i)+1 mod 3, c(q(i)) = c(i)+2 mod 3
orientation - : c(p(i)) = c(i)+2 mod 3, c(q(i)) = c(i)+1 mod 3
```

Starting from one coordinate with color zero, propagate colors through `p,q,p^{-1},q^{-1}` and reject an orientation on the first inconsistency.

Because the action is connected/transitive, propagation visits all `n` coordinates.

- If neither orientation is consistent, `nullity=0` and the instance is UNSAT.
- If an orientation is consistent, the three color classes are the three Exact-One witnesses.

Time after the two-permutation normalization:

```text
commutation check = O(n)
transitivity check = O(n)
Z3 propagation = O(n)
witness construction = O(n)
witness verification = O(n)
```

So the terminal is deterministic polynomial time (indeed linear in the normalized permutation representation).

## 5. Exact controls

### UNSAT control — Fano `7_3`

On `Z_7`, take

```text
p(i)=i+1 mod 7
q(i)=i+3 mod 7.
```

Then

```text
A=I+P+Q
```

is the cyclic Fano incidence matrix with row support `i+{0,1,3}`. It is connected, cubic, linear and commuting. Exact rational elimination gives

```text
rank_Q(A)=7
nullity_Q(A)=0
Boolean Exact-One witnesses=0.
```

### SAT control — `TD(3,3)` / affine `9_3`

On `Z_3 x Z_3`, take

```text
p(x,y)=(x+1,y)
q(x,y)=(x,y+1).
```

Then `A=I+P+Q` is connected, cubic, linear and commuting, with

```text
rank_Q(A)=7
nullity_Q(A)=2
Boolean Exact-One witnesses=3.
```

The witnesses are exactly the three color classes of, e.g.,

\[
\phi(x,y)=x+2y\pmod 3.
\]

## 6. External source binding

Only standard background is imported:

- a transitive abelian permutation group is regular;
- the regular representation of a finite abelian group is diagonalized by its character/Fourier basis.

The JANUS-specific consequence `nullity in {0,2}` and the exact three-color SAT terminal are derived above directly from `A=I+P+Q`.

## 7. Hard-frontier consequence

The active high-nullity core can now add the certified exclusion

```text
[P,Q] != 0
```

for the currently chosen valid normalization. More precisely:

```text
if a normalized connected carrier has PQ=QP
=> solve exactly in O(n) after normalization;
else
=> continue to the noncommuting hard core.
```

Do not strengthen this to

```text
carrier has no alternative commuting normalization
```

unless a polynomial search/canonicalization theorem over all three-matching decompositions is separately proved.

## 8. Ceiling

```text
CONNECTED COMMUTING TWO-PERM NULLITY DICHOTOMY = PROVED
NULLITY IN {0,2}                              = PROVED
NULLITY 0 => UNSAT                            = PROVED
NULLITY 2 => SAT WITH EXACTLY 3 WITNESSES     = PROVED
LINEAR-TIME Z3 PROPAGATION TERMINAL            = PROVED

NONCOMMUTING HIGH-NULLITY CORE                 = OPEN
UNIVERSAL POLYNOMIAL SAT SOLVER                = NOT PROVED
E8_D1                                           = EMPTY
P_VS_NP                                         = OPEN
```