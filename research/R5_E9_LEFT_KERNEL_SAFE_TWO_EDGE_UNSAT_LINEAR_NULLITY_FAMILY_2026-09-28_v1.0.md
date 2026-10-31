# R5 E9 — Left-kernel-safe two-edge lifts: UNSAT prime family with linear rational nullity

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_SIZE_UNSAT_HOSTILE_FAMILY__NULLITY_NOT_A_UNIVERSAL_SAT_CURRENCY__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE FALSIFIES THE SHORTCUT
  3-CUT-IRREDUCIBLE + UNBALANCED + LARGE rational nullity => SAT.

IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_SINGULAR_UNSAT_3CUT_IRREDUCIBLE_ODD_CYCLE_CONTROL_2026-09-28_v1.0.md`
- `research/R5_E9_TWO_EDGE_TWIST_3CUT_IRREDUCIBLE_LINEAR_NULLITY_FAMILY_2026-09-28_v1.0.md`
- `research/R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_left_kernel_safe_two_edge_unsat_linear_nullity.py`

## 1. Two-edge lift notation

Let `A` be an `n x n` cubic Exact-One incidence matrix. Choose two nonincident incidences

```text
e=(r,j),
f=(s,l),
```

with `r!=s`, `j!=l`, and let

```text
E = e_r e_j^T + e_s e_l^T,
P = A-E.
```

The two-edge crossed 2-lift is

```text
Ahat = [P E
        E P].
```

Its signed block is

```text
S=A-2E.
```

Over `Q`, the fiber sum/difference change of basis gives

```text
Ahat ~ A direct_sum S,
```

so

```text
nu_Q(Ahat)=nu_Q(A)+nu_Q(S).
```

## 2. Exact left-kernel semantic-safety theorem

### Theorem LKS-1

Assume there exists `y in ker_Q(A^T)` with

```text
y_r != y_s.
```

Then

```text
Ahat is Exact-One SAT  iff  A is Exact-One SAT.
```

Moreover every lifted model projects to a base model.

### Proof

The reverse implication is diagonal lifting: if `Ax=1`, then `(x,x)` satisfies `Ahat(x,x)^T=(1,1)^T`.

For the forward implication, let `(u,v)` be a Boolean lifted model and put

```text
h=u-v in {-1,0,1}^n.
```

Subtracting the two lifted row systems gives

```text
(A-2E)h=0,
```

hence

```text
Ah=2(h_j e_r + h_l e_s).
```

Every column of `A` has sum three, so left-multiplying by `1^T` yields

```text
3 sum_q h_q = 2(h_j+h_l).
```

The right side lies in `{-4,-2,0,2,4}`; the only multiple of three in this set is zero. Therefore

```text
h_j+h_l=0.
```

If `h_j=h_l=0`, then `Eh=0` and the first lifted equation is

```text
Pu+Ev = Au-Eu+Ev = Au-Eh = Au = 1,
```

so `u` is a base model.

Otherwise `h_l=-h_j` with `h_j in {+1,-1}`. Left-multiplying `Ah=2h_j(e_r-e_s)` by `y^T` gives

```text
0 = 2 h_j (y_r-y_s),
```

contradicting `y_r!=y_s`.

Thus the nonzero defect case is impossible and every lifted model projects to a base model. QED.

## 3. A safe pair always exists on every singular cubic carrier

### Lemma LKS-2

If `A` is singular over `Q`, a pair satisfying LKS-1 can be found deterministically in polynomial time.

### Proof

Compute any nonzero

```text
y in ker_Q(A^T)
```

by exact Gaussian elimination.

`y` cannot be constant. If `y=c 1`, then because each column sum is three,

```text
A^T y = 3c 1,
```

which vanishes over `Q` only for `c=0`, contradicting `y!=0`.

Hence choose rows `r,s` with `y_r!=y_s`. Pick any incidence `(r,j)`. Row `s` contains three distinct columns, so choose an incidence `(s,l)` with `l!=j`. The two incidences are nonincident in the Levi graph and satisfy LKS-1.

All steps are polynomial. QED.

This lemma is constructive; use the lexicographically first valid choices to make the recursion canonical.

## 4. Nullity amplification after the safe choice

Let

```text
k=nu_Q(A).
```

Since `E` has rank at most two,

```text
rank(A-2E) <= rank(A)+2,
```

hence

```text
nu_Q(S) >= k-2.
```

Therefore every left-kernel-safe two-edge lift obeys

```text
boxed(k_next >= 2k-2).
```

For `k>=3`, singularity of the signed block is automatic.

## 5. Structural preservation

The parent two-edge-twist theorem proves that on a cubic graph with no edge cut below three and only vertex-star 3-cuts, any two nonincident crossed edges have frustration index exactly two, and the connected 2-lift again has no nontrivial edge cut of size at most three.

Thus the present left-kernel-safe pair simultaneously gives:

```text
Exact-One SAT equivalence,
connectedness,
3-cut irreducibility.
```

A graph cover preserves cubic bipartiteness and cannot create a new 4-cycle below the base girth, so linearity of the cubic hypergraph is also preserved.

If the base is UNSAT, every descendant is UNSAT by LKS-1. By the already-proved balanced set-partitioning terminal, a cubic balanced matrix is SAT because `x=(1/3)1` is feasible and the polyhedron is integral. Therefore every UNSAT descendant is automatically unbalanced as well.

## 6. Exact bootstrap from the frozen UNSAT `15_3` control

Use the frozen `15_3` connected linear-cubic UNSAT matrix from
`R5_E9_SINGULAR_UNSAT_3CUT_IRREDUCIBLE_ODD_CYCLE_CONTROL`.
It has

```text
n_0=15,
nu_Q(A_0)=1,
UNSAT,
3-cut irreducible.
```

### Bootstrap step 1

Choose crossed incidences

```text
(0,12),
(2,9).
```

They are nonincident. An exact left-kernel vector separates rows `0` and `2`, so LKS-1 applies. Exact elimination gives

```text
nu_Q(A_0-2E_0)=1,
```

therefore

```text
n_1=30,
nu_Q(A_1)=2.
```

### Bootstrap step 2

On `A_1`, choose crossed incidences

```text
(0,5),
(1,1).
```

An exact basis of `ker_Q(A_1^T)` gives distinct row signatures

```text
row 0 : (23/6, -11/6),
row 1 : (17/6,  -5/6),
```

so LKS-1 applies again. Exact elimination gives

```text
nu_Q(A_1-2E_1)=1,
```

hence

```text
n_2=60,
nu_Q(A_2)=3.
```

Both descendants are UNSAT, connected, linear, cubic, unbalanced, and 3-cut irreducible by the theorems above.

## 7. Infinite recursion and linear nullity

For every stage `t>=2`, compute a nonzero left-kernel vector and choose the canonical LKS-2 pair. LKS-1 preserves UNSAT exactly, and the two-edge structural theorem preserves the prime residual.

Let `k_t=nu_Q(A_t)`. For all `t>=2`,

```text
k_(t+1) >= 2 k_t - 2.
```

Put

```text
h_t=k_t-2.
```

Since `k_2=3`,

```text
h_2=1,
h_(t+1) >= 2 h_t,
```

so

```text
h_t >= 2^(t-2).
```

Because every lift doubles the number of columns,

```text
n_t=15*2^t.
```

Therefore for every `t>=2`,

```text
boxed(
k_t >= 2 + 2^(t-2)
    = 2 + n_t/60.
)
```

Thus the family has linear rational nullity.

## 8. Main consequence

There is an explicit deterministic recursively constructible infinite family satisfying simultaneously

```text
connected,
linear,
cubic / square,
UNSAT,
unbalanced,
no nontrivial edge cut of size <=3,
nu_Q(A) >= 2+n/60.
```

Therefore all shortcuts of the form

```text
3-cut-irreducible + unbalanced + sufficiently large rational nullity => SAT
```

are false.

Together with the earlier SAT high-nullity families, rational nullity is now ruled out in both directions as a universal SAT/UNSAT currency on the present hard residual.

The exact FPT routers parameterized by small `k` or small `2n-3k` remain valid islands; they simply cannot close the universal middle band by a large-nullity SAT theorem.

## 9. Algorithmic anti-loop rule

From this point onward, do not reopen any proposed universal rule whose only global progress measure is raw rational nullity, even after balanced and genuine-3-cut preprocessing.

A valid universal continuation must use a semantic/global object that distinguishes the SAT and UNSAT linear-nullity prime families, or provide a different exact polynomial contraction.

## 10. Ceiling

```text
LEFT-KERNEL SAFE PAIR EXISTS ON EVERY SINGULAR CUBIC A
= PROVED / POLYNOMIALLY CONSTRUCTIVE

LEFT-KERNEL SAFE TWO-EDGE LIFT
SAT iff SAT
= PROVED

3-CUT PRIME / LINEAR / CUBIC PRESERVATION
= PROVED BY PARENT TWO-EDGE LIFT THEOREM

BOOTSTRAP
15,k=1 -> 30,k=2 -> 60,k=3
= EXACT / CHECKED

RECURSIVE NULLITY
k_t >= 2+n_t/60
= PROVED

INFINITE UNSAT PRIME LINEAR-NULLITY FAMILY
= PROVED

LARGE-NULLITY-IMPLIES-SAT RESIDUAL SHORTCUT
= FALSIFIED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
