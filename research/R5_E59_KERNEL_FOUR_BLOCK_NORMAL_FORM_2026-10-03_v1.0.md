# R5 E59 — Kernel Four-Block Normal Form / Exact Defect Set

Date: 2026-10-03

Status:
`GLOBAL_EXACT_NORMAL_FORM__EVERY_BINARY_KERNEL_WORD_SPLITS_INTO_THREE_EQUAL_ACTIVE_BLOCKS_PLUS_ONE_DEFECT_BLOCK`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A POLYNOMIAL ALGORITHM.

IT SHARPENS E58 FROM A NUMERICAL MAX-WEIGHT CAP INTO AN EXACT GLOBAL
GEOMETRIC NORMAL FORM VALID FOR EVERY ARBITRARY, NONCOMMUTING PERMUTATION
PAIR (P,Q).

LET

    A = I + P + Q

over F_2 and let k in ker(A).  Put

    K  = supp(k),
    PK = supp(Pk),
    QK = supp(Qk).

AT EVERY COORDINATE THE MEMBERSHIP TRIPLE IN (K,PK,QK) HAS EVEN PARITY,
SO ONLY FOUR STATES ARE POSSIBLE:

    000, 110, 101, 011.

THEY GIVE A CANONICAL PARTITION

    V = A0 disjoint_union B0 disjoint_union C0 disjoint_union D,

WITH

    K  = A0 disjoint_union B0,
    PK = A0 disjoint_union C0,
    QK = B0 disjoint_union C0,

AND

    |A0| = |B0| = |C0| = |K|/2.

THE FOURTH BLOCK IS THE EXACT DEFECT SET

    D = {v : k_v=(Pk)_v=(Qk)_v=0},

AND

    |D| = n - 3|K|/2.

THEREFORE

    EXACT-ONE SAT

IFF

    THERE EXISTS k in ker_F2(A) WITH D=empty

IFF

    THERE EXISTS k in ker_F2(A) WITH
        K union PK union QK = V

IFF

    |K|=2n/3.

AT ZERO DEFECT THE THREE ACTIVE BLOCKS HAVE SIZE n/3 AND THE COMPLEMENT
x=1+k IS THE EXACT-ONE SOLUTION.

P_VS_NP = OPEN.
```

## 1. Convention

We treat `P,Q` as permutation matrices acting on vectors.  Thus `PK` below means

```text
PK = supp(P k),
```

not an independently chosen set image convention.

For the companion checker's row notation

```text
(Ak)_i = k_i + k_{p(i)} + k_{q(i)},
```

we have

```text
supp(Pk)=p^{-1}(K),
supp(Qk)=q^{-1}(K).
```

This distinction matters only for notation; all statements below are matrix-action
invariant.

## 2. Four possible coordinate states

Take

```text
k in ker_F2(A),
A=I+P+Q.
```

Then

```text
k + Pk + Qk = 0  (mod 2).
```

At every coordinate `v`, the three bits

```text
(k_v,(Pk)_v,(Qk)_v)
```

therefore have even parity.

Among three bits, the only even-parity states are

```text
000,
110,
101,
011.
```

In particular, `111` is impossible, as are the three one-hot states.

Define

```text
A0 = K  intersect PK,
B0 = K  intersect QK,
C0 = PK intersect QK,
D  = V \ (K union PK union QK).
```

Because `111` is forbidden, the three intersections are pairwise disjoint.  The four
states therefore give the exact partition

```text
boxed:
V = A0 disjoint_union B0 disjoint_union C0 disjoint_union D.
```

Moreover, directly from the state table,

```text
boxed:
K  = A0 disjoint_union B0,
PK = A0 disjoint_union C0,
QK = B0 disjoint_union C0.
```

## 3. The three active blocks have equal size

Permutation matrices preserve Hamming weight, so

```text
|K|=|PK|=|QK|.
```

Using the block decompositions,

```text
|A0|+|B0| = |A0|+|C0|,
|A0|+|B0| = |B0|+|C0|.
```

Hence

```text
boxed:
|A0|=|B0|=|C0|=:m.
```

Consequently

```text
boxed:
|K|=2m,
```

and the active union has size

```text
|A0 union B0 union C0|=3m=3|K|/2.
```

Therefore

```text
boxed:
|D| = n - 3|K|/2.
```

This recovers the E58 cap immediately:

```text
|D|>=0
=>
|K|<=2n/3.
```

But E59 gives more than the inequality: it identifies the entire missing mass as a
canonical coordinate set `D`.

## 4. D is exactly the E56 defect set

Let

```text
x=1+k
```

over `F_2`; as Boolean vectors this is the coordinatewise complement.

Because `A1=1 mod 2`, `x` satisfies

```text
A x = 1 mod 2.
```

E56 showed that every integer row sum of `x` is either `1` or `3`.

A coordinate `v` belongs to `D` iff

```text
k_v=(Pk)_v=(Qk)_v=0.
```

After complementing, the corresponding row triple for `x` is

```text
1,1,1.
```

Thus

```text
boxed:
D = the set of E56 triple-covered / row-sum-3 defects.
```

In particular,

```text
boxed:
|D|=t_3(x).
```

Combining with E56's

```text
3|x|=n+2t_3(x)
```

and `|x|=n-|K|` gives the same identity

```text
2|D|=2n-3|K|.
```

So E56 and E58 are not merely compatible bounds; E59 supplies their common defect
object.

## 5. Exact-One is zero defect

By E59,

```text
D=empty
```

iff

```text
|K|=2n/3.
```

At zero defect,

```text
V=A0 disjoint_union B0 disjoint_union C0
```

with

```text
|A0|=|B0|=|C0|=n/3.
```

Since

```text
K=A0 union B0,
```

the complement `x=1+k` has support

```text
S=C0.
```

Also

```text
supp(Px)=V\PK=B0,
supp(Qx)=V\QK=A0.
```

Therefore

```text
boxed:
V = supp(x) disjoint_union supp(Px) disjoint_union supp(Qx).
```

Equivalently,

```text
x+Px+Qx=1
```

over the integers.

Thus

```text
boxed:
Exact-One SAT(A)
iff
exists k in ker_F2(A) with D(k)=empty.
```

## 6. One-permutation defect formula

The kernel equation gives

```text
Qk = k + Pk  (mod 2).
```

Therefore

```text
QK = K symmetric_difference PK.
```

In particular,

```text
K union PK union QK = K union PK.
```

Hence the defect set can be read using only one normalized permutation once kernel
membership is known:

```text
boxed:
D(k)=V \ (K union PK).
```

Coordinatewise,

```text
boxed:
v in D(k)
iff
k_v=0 and (Pk)_v=0.
```

Thus zero defect is exactly the positive 2-CNF cycle-cover condition

```text
boxed:
k_v OR (Pk)_v = 1
for every v,
```

subject to the homogeneous linear system

```text
(I+P+Q)k=0 over F_2.
```

Equivalently, in the row convention `(Pk)_i=k_{p(i)}`, every cycle of `p` must carry
a binary word with no adjacent `00` pair.

This is an exact universal reformulation, not a relaxation.

## 7. Cycle-cover statistics

On the directed cycle cover of `P`, classify directed edges by the consecutive bit pair

```text
00, 01, 10, 11.
```

Let their global counts be

```text
a,b,b,c,
```

where the two transition counts are equal because every component is a directed cycle.

Now

```text
wt(k+Pk)=2b.
```

But the kernel equation gives

```text
k+Pk=Qk,
```

and `Q` preserves weight, so

```text
2b=|K|.
```

The number of `1` vertices is also

```text
b+c=|K|,
```

so

```text
c=b.
```

Finally,

```text
n=a+2b+c=a+3b,
|K|=2b.
```

Therefore

```text
boxed:
a=n-3|K|/2=|D|.
```

So `D` is exactly the set/count of `00` edges along the normalized `P` cycle cover.
The E58 maximum-weight problem is equivalently

```text
minimize the number of 00 adjacencies on P-cycles
subject to (I+P+Q)k=0.
```

Exact-One is the zero-energy endpoint.

## 8. Why this is a better universal target

E55 localized the hardness to SWITCH4/FREE8.

E56 replaced those local types by an affine binary weight floor.

E58 removed the affine RHS and converted the problem to a homogeneous kernel weight cap.

E59 now exposes an exact defect geometry:

```text
binary linear kernel
+
three equal active blocks
+
explicit defect block D
```

with the entire unresolved task reduced to

```text
find k in ker_F2(I+P+Q) such that D(k)=empty.
```

The next algorithmic question is therefore no longer "what is the right objective?".
It is:

```text
CAN WE ELIMINATE D BY A POLYNOMIAL AUGMENTATION / DECOMPOSITION THEOREM
FOR THE SPECIAL PERMUTATION KERNEL?
```

A candidate universal solver must prove one of the following kinds of statements:

```text
A. If D is nonempty and a zero-defect kernel word exists, a polynomially findable
   augmenting kernel move strictly decreases |D|.

B. The kernel and P-cycle cover admit a polynomial canonical decomposition on which
   min |D| is additive.

C. There is a polynomial dual certificate proving min |D|>0 when zero defect is
   impossible.
```

Any such theorem must survive the E12 hardness images; bounded-radius local search or
subclass-only arguments are not enough.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e59_kernel_four_block_normal_form.py
```
