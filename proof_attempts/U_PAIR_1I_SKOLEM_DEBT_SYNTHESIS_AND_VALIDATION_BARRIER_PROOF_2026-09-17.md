# U-PAIR-1I — Skolem debt synthesis and validation barrier

Date: 2026-09-17

Status:
`PASS_DEBT_ACCOUNTING_SOUNDNESS__FAIL_SKOLEM_RULE_EXISTENCE_OR_GENERIC_VALIDATION_AS_AN_INDEPENDENT_TERMINATION_MECHANISM`

## 0. Authority and claim ceiling

This is a successor proof-attack on the independently open `GENERAL_SAT` surface. It does not modify the v3.23 connected-mixed authority and does not promote `GENERAL_SAT_IN_P`.

The frozen U-PAIR-1I representation is:

- canonical GF(2) RREF;
- hash-consed bounded-fanin Boolean DAG;
- definitional auxiliaries;
- exact existential projection;
- existential debt for every eliminated unresolved semantic choice that has no checked reconstruction rule.

The candidate potential is

`Phi = live_original_semantic_bits + undischarged_existential_debt_items`.

The question attacked here is whether universal debt discharge can be justified by the mere existence of polynomial-size Skolem rules plus a generic independent checker.

## 1. Closed-instance Skolem rules are always small on SAT instances

Let `F(x_1,...,x_n)` be a closed Boolean SAT instance.

If `F` is satisfiable, choose any satisfying assignment `a in {0,1}^n`. Define the zero-input rule vector

`f_i() = a_i`.

The whole reconstruction object contains only `n` constant bits and therefore has size `O(n)`.

Hence a superpolynomial lower bound on Skolem *representation size* cannot be the first universal obstruction for closed SAT instances. The hard obligation is to **find** such constants without already solving the SAT instance.

For UNSAT instances there is no SAT witness to reconstruct; a terminal algorithm instead needs a complete exact UNSAT certificate.

## 2. Uniform synthesis is already SAT solving

### Theorem 1

Suppose a deterministic algorithm `A` runs in polynomial time and, given any closed Boolean relation `F(X)`, returns a valid zero-input Skolem vector `f()` whenever `F` is satisfiable.

Then SAT is decidable in deterministic polynomial time.

### Proof

Run `A(F)` and evaluate `F(f())`.

- If `F` is satisfiable, Skolem validity for the zero-boundary relation requires `F(f())=1`.
- If `F` is unsatisfiable, `F(a)=0` for every assignment `a`, so in particular `F(f())=0`.

Thus the single polynomial-time test `F(f())` decides SAT exactly. QED.

This is a barrier/equivalence statement. It does **not** show that such synthesis is impossible; proving such a universal polynomial synthesis algorithm would itself close the target.

## 3. Generic Skolem-rule validation is coNP-complete

For polynomial-size Boolean DAGs define

`SKOLEM_VALID(R,f)` iff

`forall y [ (exists x R(x,y)) -> R(f(y),y) ]`.

### Lemma 2 — membership in coNP

Invalidity has a polynomial witness `(y,x)` satisfying

`R(x,y)=1`

and

`R(f(y),y)=0`.

The DAGs `R` and `f` can be evaluated in polynomial time, so the complement is in NP. Therefore `SKOLEM_VALID` is in coNP.

### Lemma 3 — coNP-hardness

Let `G(y)` be an arbitrary 3CNF. Construct the bounded-fanin Boolean DAG

`R_G(x,y) = x OR NOT G(y)`

and fix the proposed Skolem rule

`f(y)=0`.

For every `y`, choosing `x=1` makes `R_G` true, hence

`exists x R_G(x,y)=1`.

But

`R_G(f(y),y)=R_G(0,y)=NOT G(y)`.

Therefore

`f is valid`

iff

`forall y NOT G(y)`

iff

`G is UNSAT`.

UNSAT for 3CNF is coNP-complete, so `SKOLEM_VALID` is coNP-hard. Together with Lemma 2 it is coNP-complete. QED.

The construction remains inside the frozen representation class: `R_G` is a polynomial-size bounded-fanin DAG. If needed, it can be Tseitin-compiled with polynomial overhead to 3CNF and then mapped exactly to the established `PAIR+OR_3` selector normal form.

## 4. Consequences for U-PAIR-1I

A generic deterministic polynomial-time checker that accepts exactly the valid arbitrary Skolem rules would decide a coNP-complete language in P. Since P is closed under complement, that would imply `P=NP`.

Likewise, if every valid arbitrary rule were guaranteed to possess a polynomial-size certificate verifiable in deterministic polynomial time, then the coNP-complete language `SKOLEM_VALID` would be in NP, implying `NP=coNP`.

Therefore an independent checker cannot simply be assumed for arbitrary rules. A permitted discharge must instead be backed by a **frozen structured proof calculus** whose local verification is polynomial, and the universal route still needs a theorem that proof construction and proof size stay polynomial on every input.

## 5. Positive controls remain valid

The barrier does not invalidate easy debt discharge cases:

- unit-forced variable -> constant rule;
- affine RREF pivot -> linear GF(2) rule;
- free variable -> fixed default constant;
- local OR control -> constant satisfying rule under an independently checked local precondition.

These are useful admissible controls, but they do not compose into a universal theorem by themselves.

## 6. Frozen verdict

`SKOLEM_DEBT_V1` survives as a **sound accounting ledger**: unresolved elimination creates debt and aliases cannot erase debt.

What fails is the hoped-for shortcut:

`polynomial-size Skolem rule exists -> polynomial-time rule can be synthesized and generically validated`.

That implication is false as a justified proof step.

Successor gate:

`U-PAIR-1J__PROOF_CARRYING_LOCAL_SKOLEM_DISCHARGE_WITH_FROZEN_CALCULUS`

The next candidate must freeze an exact discharge calculus before hostile testing, with polynomial-time local checking and an independently proved polynomial bound on derivation size, synthesis time, reconstruction time and UNSAT replay.

Scientific firewall:

`GENERAL_SAT_IN_P = NOT_PROVED`

`P_VS_NP = OPEN`

`P_EQ_NP = NOT_PROVED`
