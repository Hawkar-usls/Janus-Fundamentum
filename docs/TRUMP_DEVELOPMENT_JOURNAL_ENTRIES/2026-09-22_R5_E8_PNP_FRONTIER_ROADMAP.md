# R5 E8 — P vs NP Frontier Roadmap

Date: 2026-09-22  
Authority: `ANTI_LOOP_ROADMAP__NO_D1_PROMOTION`  
Repository: `Hawkar-usls/Janus-Fundamentum`  
PR: `#510`  
Branch: `codex/r5-e8-direct-contract-20260921-82493a57`

## 0. Global scientific ceiling

```text
P_VS_NP
=
OPEN

D1
=
NOT_ADMITTED

GENERAL_SAT_IN_P
=
NOT_PROVED
```

Finite diagnostics never promote a polynomial theorem. Every asymptotic promotion requires an arbitrary-size proof.

---

## 1. DONE — do not reopen

### 1.1 Prior-art mechanics

Do not claim novelty for:

- Shannon projection `exists x f = f[x=0] OR f[x=1]`;
- AIG/circuit existential quantification;
- structural hashing / strashing;
- AIG quantifier scheduling;
- one-step size-aware greedy quantifier scheduling;
- FRAIG / SAT sweeping / BDD sweeping as practical semantic compaction;
- generic binary branching `t -> 2^t` distinguishability arguments.

Authority:

`research/R5_B1B1C5B2B2_E8_AIG_QE_AND_INTERNAL_ANTI_DUPLICATION_SOURCE_AUDIT_2026-09-22_v1.0.md`

### 1.2 Internal Janus predecessors

Do not rediscover under new names:

- `C023_FORMULA_CACHING_CALCULUS`: exact residual/cache DAG mechanics;
- `C023R_REACHABLE_COSET_AND_EXECUTION_DAG_GATE`: serial-diamond / multiplicity proof skeleton;
- `TRUMP_EXACT_INTERFACE_QUOTIENT_BASIS_THEOREM_CANDIDATE`: U1 coordinate-separation `2^k` skeleton;
- `TRUMP_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO_THEOREM`: factorized-payload escape;
- `TRUMP_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_THEOREM`: bounded-output guarded elimination;
- `CAPTAIN_OBVIOUS_C023R_REPRESENTATION_CORRECTION_AND_TAIL_BALANCE`: semantic irrelevance is not syntactic disappearance.

Before opening a new E8 mechanism, compare it against these artifacts.

---

## 2. DONE — frozen computational object

### Exact frozen structural-AIG selector

Executable authority:

`research/tools/r5_e8_frozen_structural_aig_executor.py`

Frozen semantics:

```text
STATE
=
structural AIG DAG
with complemented edges

ALLOWED
=
restriction
Shannon projection
CONST
IDEMPOTENCE
COMPLEMENT
COMMUTATIVE canonicalization
structural interning
garbage collection

FORBIDDEN
=
SAT oracle
semantic equivalence oracle
FRAIG
SAT sweeping
BDD sweeping
hidden existential relabeling

GREEDY KEY
=
(projected_reachable_nodes,
 cone_size,
 variable_id)
```

The one-step exact selector is polynomial in the current live DAG size.

---

## 3. DONE — finite exact diagnostics

### 3.1 Finite greedy myopia

A minimized signed 2-CNF kernel proves on a finite exact instance:

```text
one-step exact greedy
!=
global peak optimum
```

Authority:

`research/R5_B1B1C5B2B2_E8_GREEDY_EXACT_STRUCTURAL_PROJECTOR_FINITE_MYOPIA_SEED_2026-09-22_v1.0.json`

This is diagnostic only and does not falsify the universal polynomial-peak theorem.

### 3.2 Cyclic shared payload

Family:

```text
F_m =
AND_i [
  (x_i OR z_i OR NOT z_{i+1})
  AND
  (NOT x_i OR z_{i+2} OR NOT z_{i+3})
]
```

Finite large peaks exist, but arbitrary-`m` linear selector prefix has not been proved.

---

## 4. DONE — scheduler/amplifier separation

Old target:

```text
one recursive gadget
must both force scheduling
and recursively self-copy
```

Replaced by:

```text
SCHEDULER
+
AMPLIFIER
```

The scheduler only needs to force a linear-size selector prefix.

The amplifier converts that prefix into exponentially many frozen structural branch roots.

Authority:

`research/R5_B1B1C5B2B2_E8_GREEDY_PREFIX_AMPLIFIER_COMPOSITION_GATE_2026-09-22_v1.0.json`

---

## 5. DONE — power-of-two tree geometry

Restrict to the infinite subfamily:

```text
m = 2^r
```

No theorem requires all integer `m`.

### Balanced-tree carry-boundary lemma

For the frozen balanced builder:

```text
m = 2^r
=>
complete block tree
no carry tail

m = 2^r + 1
=>
G_m is carried as shallow tail

m = 2^r + 2
=>
(G_{m-1},G_m) becomes the shallow carried tail pair
```

This explains why `9/10, 17/18, 33/34` are structurally anomalous candidates without requiring a modulo-8 explanation.

Authority:

`research/R5_B1B1C5B2B2_E8_CYCLIC_POWER_OF_TWO_SELECTOR_PREFIX_GATE_2026-09-22_v1.0.json`

---

## 6. DONE — odd-selector amplifier side

For `m=2^r >= 4`, while even selector blocks remain unresolved:

```text
t distinct odd-selector projections
=>
at least 2^t
distinct reachable
nonconstant,
noncomplement
structural branch-root refs
```

This is now a scoped symbolic lemma, not merely finite evidence.

Authority:

`research/R5_B1B1C5B2B2_E8_ODD_SELECTOR_BRANCH_INJECTIVITY_LEMMA_2026-09-22_v1.0.md`

Therefore:

```text
AMPLIFIER SIDE
=
CLOSED
FOR ODD-SELECTOR PREFIXES
```

---

## 7. CURRENT OPEN CORE — do this next

### R5_E8_ODD_PREFIX_NET_CHARGE_THEOREM_V1

New exact accounting authority:

`research/R5_B1B1C5B2B2_E8_NET_PROJECTION_CHARGE_AND_STEP0_THEOREM_2026-09-22_v1.0.md`

For every currently reachable trial variable:

```text
cost(v)
=
N + A_v - sigma_v - kappa_v.
```

Hence with

```text
E_v
=
A_v - sigma_v - kappa_v
```

the frozen greedy key is exactly

```text
(E_v, A_v, variable_id).
```

The arbitrary-`r` initial step is now closed:

```text
m=2^r >= 4
=>
first frozen greedy winner = x1.
```

The remaining theorem is:

```text
For every odd-only prefix state before
all odd selectors are eliminated:

I. kappa_v = 0
   for relevant odd-selector/payload trials;

II. there exists unresolved odd selector o
    such that for every payload z:

    A_z - A_o
    >=
    sigma_z - sigma_o;

III. if equality holds,
     A_o < A_z.
```

This is equivalent to proving the remaining odd selector beats every payload under the exact frozen key.

### Consequence: R5_E8_ODD_SELECTOR_GREEDY_PREFIX_THEOREM_V1

Target:

```text
For every m = 2^r >= 4,

before selecting any payload variable,
the frozen exact greedy projector
selects all m/2 odd selector variables.
```

Equivalent useful proof target:

```text
For every odd-prefix state S_t:

min_key(
  unresolved odd selectors
)
<
min_key(
  unresolved payload variables
)
```

where

```text
key(v)
=
(
  projected_reachable_nodes,
  cone_size,
  variable_id
)
```

Lexicographic equality in the first coordinate must be resolved by the exact cone-size and id tie-breaks.

### Finite pattern already observed

```text
m=4:
1,3

m=8:
1,7,3,5

m=16:
1,15,5,9,3,11,7,13

m=32:
1,31,9,17,7,21,15,25,
19,3,11,27,5,23,13,29
```

The `m=32` observation remains diagnostic, not theorem evidence.

---

## 8. Required proof program

### Stage A — exact state normal form / kappa lemma

Derive a symbolic description of the frozen live DAG after an arbitrary prefix of odd selector eliminations and prove that projection of every relevant comparator drops no old variable-independent reachable node:

```text
kappa_v = 0.
```

Do not separately derive the total projected size `N_t`; the exact charge identity cancels the common `N_t` term.

Required output:

- exact surviving block/tree shape;
- exact class of Shannon-OR nodes introduced;
- exact structural sharing that remains possible;
- no semantic simplification assumptions.

### Stage B — odd-selector local charge profile

For unresolved odd selectors derive:

```text
A_o
sigma_o
E_o = A_o - sigma_o
```

under the `kappa_o=0` invariant.

Goal: characterize the bounded local simplification saving while allowing the common Shannon backbone to grow.

### Stage C — payload local charge profile

For every unresolved payload `z_j`, derive:

```text
A_z
sigma_z
E_z = A_z - sigma_z
```

under the same `kappa_z=0` invariant.

Target comparison:

```text
A_z - A_o
>=
sigma_z - sigma_o.
```

### Stage D — compare all competitors by net charge

For every prefix length `0 <= t < m/2`, prove existence of unresolved odd selector `o` such that for every payload `z`:

```text
DeltaCone
=
A_z - A_o

>=

sigma_z - sigma_o
=
DeltaSaving.
```

Therefore `E_o <= E_z`. If equality holds, prove `A_o<A_z`; selector IDs already dominate payload IDs on the tertiary tie-break.

No ignored competitors are allowed.

### Stage E — arbitrary-n conclusion

If Stages A-D succeed:

```text
t = m/2

Peak(F_m)
>=
2^(m/2)

L
=
O(m log m)

therefore

Peak(F_m)
>=
2^(Omega(L/log L)).
```

Then:

```text
R5_E8_GREEDY_PROJECTOR_PEAK_THEOREM_V1
=
FALSIFIED
```

This falsifies the exact frozen greedy candidate only.

It does **not** prove `P != NP`.

---

## 9. Failure branches

### If the odd-prefix theorem fails symbolically

Record exactly:

- first prefix class where payload can beat all selectors;
- winning payload key;
- best selector key;
- structural cause;
- whether the failure is primary projected-size or cone tie-break related.

Then:

```text
ODD_SELECTOR_PREFIX THEOREM
=
FALSIFIED
```

Do not infer anything about general structural AIG QE or P vs NP.

### If the cyclic family factors

Before claiming amplification, test the already-sealed factorized-payload conditions.

If exact cross-independence holds, return to the sealed factorized portfolio theorem; do not relabel factorization as a new E8 mechanism.

### If output is only polynomial on a scoped guard

Return the guarded-bounded-output verdict.

Do not promote a bounded-output route into a general solver.

---

## 10. What not to do now

Until the odd-selector theorem resolves:

```text
NO new representation hunt

NO new selector design

NO new AIG scheduling heuristic

NO new broad literature inventory

NO transfer from OBDD/resolution lower bounds

NO semantic equivalence simplifier

NO finite-run polynomial promotion

NO P=NP / P!=NP claim
```

The only authorized work is theorem analysis of the frozen power-of-two cyclic family, plus finite diagnostics used solely to discover/probe symbolic invariants.

---

## 11. Promotion ladder

### Level 0 — finite diagnostic
Observed traces only.

### Level 1 — scoped symbolic lemma
Arbitrary-size statement under explicit preconditions.

### Level 2 — exact counterfamily theorem
Arbitrary-size family plus frozen exact greedy trace and superpolynomial peak.

### Level 3 — candidate consequence
Exact frozen greedy polynomial-peak theorem is falsified.

### Level 4 — D1
Still **not reached**. A different universal polynomial SAT mechanism would still be required.

### Level 5 — P=NP
Only if a complete uniform polynomial SAT algorithm with full construction/solve/reconstruction/verification proof is established.

---

## 12. Current one-line frontier

```text
DONE:
prior-art audit
+ frozen executor
+ finite myopia
+ scheduler/amplifier split
+ power-of-two tree geometry
+ odd-prefix branch amplification

OPEN:
prove or falsify

FOR m=2^r:
all m/2 odd selectors beat every payload
under the exact frozen greedy key.
```


---

## 13. UPDATE — net projection charge identity and arbitrary-r step 0

Authority:

`research/R5_B1B1C5B2B2_E8_NET_PROJECTION_CHARGE_AND_STEP0_THEOREM_2026-09-22_v1.0.json`

### Exact identity

For any unresolved trial variable `v` in the frozen executor:

```text
cost(v)
=
N + A_v - sigma_v - kappa_v
```

where:

```text
A_v
=
old reachable dependent AND gates

sigma_v
=
(2A_v+1)
-
new reachable trial nodes

kappa_v
=
old v-independent nodes
that disappear from the projected result
```

Therefore within one current state:

```text
E_v
=
A_v - sigma_v - kappa_v
```

is the exact primary greedy charge, and the frozen key can be compared as:

```text
(E_v, A_v, variable_id).
```

### Step 0 is closed for all m=2^r

For every selector:

```text
A_x     = r+5
sigma_x = 8
kappa_x = 0
E_x     = r-3
```

For any payload `z`:

```text
A_z     = T_z + s_z + 8
sigma_z = s_z + 12
kappa_z = 0
E_z     = T_z - 4
```

with:

```text
T_z >= r+1.
```

Hence:

```text
E_z >= r-3 = E_x.
```

If primary charge ties, then:

```text
A_z >= r+9 > r+5 = A_x.
```

Therefore every selector beats every payload at the initial state, and selector-id tie breaking chooses:

```text
x1.
```

So:

```text
R5_E8_POWER_OF_TWO_STEP0_SELECTOR_THEOREM_V1
=
PROVED
```

### New sole open theorem

Replace the old full projected-DAG comparison by:

```text
R5_E8_ODD_PREFIX_NET_CHARGE_THEOREM_V1
```

Target:

```text
For every odd-only prefix state
before all odd selectors are removed,

there exists unresolved odd selector o

such that for every payload z:

(E_o,A_o,o)
<
(E_z,A_z,z)
lexicographically.
```

Preferred proof route:

```text
1. prove kappa_payload = 0

2. odd-selector kappa need not be zero;
   positive kappa only helps selector

3. prove for a suitable odd selector o:

   A_z - A_o
   >=
   sigma_z - sigma_o

4. on E ties prove A_o < A_z

5. if E and A both tie,
   selector id automatically wins
```

Do **not** count the full `N_t` separately unless forced.

Do **not** reopen the amplifier: odd-prefix branch amplification is already closed.

Do **not** open a new family or representation before this theorem resolves.


## 13. 2026-09-22 net-charge checkpoint

```text
NET_PROJECTION_CHARGE_IDENTITY
=
PROVED

POWER_OF_TWO_STEP0_SELECTOR_WIN
=
PROVED_ARBITRARY_R

FULL_N_t_PROJECTED_DAG_COUNTING
=
NO_LONGER_REQUIRED

CURRENT OPEN CORE
=
KAPPA_ZERO
+
DELTA_CONE >= DELTA_SAVING

AMPLIFIER/P3
=
CLOSED_AND_FROZEN

NEW FAMILY / NEW REPRESENTATION HUNT
=
FORBIDDEN UNTIL THIS GATE RESOLVES

P_VS_NP
=
OPEN
```


## 14. Related-payload scope repair and orphan frontier

The sufficient related-payload cone gap was too strong at the smallest base:

```text
m=4:
RELATED_PAYLOAD_CONE_GAP(s_z+4)
=
FALSE
```

but the exact scheduler base remains:

```text
x1 -> x3
=
PROVED_DIRECTLY.
```

For every `m=2^r>=8` the repaired theorem is:

```text
RELATED payload z
+
unresolved odd support o

=>

A_z-A_o >= s_z+4
```

and, using payload-backbone rigidity and `kappa=0`, every related payload is excluded from the frozen greedy winner set.

Authority:

`research/R5_B1B1C5B2B2_E8_RELATED_PAYLOAD_CONE_GAP_SCOPE_REPAIR_2026-09-22_v1.0.md`

The only remaining payload class is now:

```text
ORPHAN(z)
iff
both odd support selectors of z
have already been projected.
```

Current and only open scheduler target:

```text
R5_E8_ORPHAN_PAYLOAD_BARRIER_V1

while some odd selector remains,
no orphan payload can beat
all unresolved odd selectors

under

(E_v,A_v,variable_id).
```

Until this resolves:

```text
NO new family
NO new representation
NO P3/amplifier work
NO reopening related-payload cone gap
NO full N_t counting
```
