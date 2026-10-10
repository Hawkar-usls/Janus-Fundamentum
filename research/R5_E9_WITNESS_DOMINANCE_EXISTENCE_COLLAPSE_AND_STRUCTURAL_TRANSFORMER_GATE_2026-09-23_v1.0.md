# R5 E9 — Witness-Dominance Existence Collapse and Structural-Transformer Synthesis Gate

**Date:** 2026-09-23  
**Status:** exact meta-theorem + source-bound donor map; new algorithmic gate OPEN.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Why unrestricted witness-map existence is not yet an algorithmic invariant

Let a block B have residual branches

[
R_alpha(Y)=F[alpha](Y),qquad alphain{0,1}^B,
]

and choose a representative assignment (alpha^*). Put

[
S_alpha=operatorname{Mod}(R_alpha),qquad
T=S_{alpha^*}.
]

Suppose we ask only for arbitrary functions

[
mu_alpha:S_alpha	o T.
]

### Theorem WD-EXISTENCE-COLLAPSE

The following are equivalent:

1. for every (alpha), a function (mu_alpha:S_alpha	o T) exists;
2. either (T
eqarnothing), or (S_alpha=arnothing) for every (alpha);
3. (operatorname{SAT}(F)iff operatorname{SAT}(R_{alpha^*})).

#### Proof

If (T
eqarnothing), choose any (tin T); the constant map (smapsto t) works for every source set.

If (T=arnothing), a function (S_alpha	oarnothing) exists iff (S_alpha=arnothing). Thus maps for all branches exist iff all branches are empty, i.e. iff F is UNSAT.

This is exactly the condition that F and the representative residual have the same satisfiability status. ∎

### Consequence

The bare existential statement

> there exists a polynomial-size / polynomially verifiable witness map

is too weak as a universal algorithmic target.

On a satisfiable representative branch, a satisfying assignment itself gives a polynomial-size constant-map certificate.

On an unsatisfiable representative branch, establishing maps from all other branches is equivalent to establishing that all those branches are empty.

Therefore the algorithmic content lies in **deterministic synthesis from structure**, not map existence or certificate size alone.

## 2. Corrected target: structural witness transformers

A **structural witness transformer family** M consists of a compact parameter object θ and a map

[
mu_	heta:{0,1}^{Y}	o{0,1}^{Y}
]

with the following mandatory properties.

### Synthesis contract

Given the residual syntax, a deterministic algorithm must in polynomial time either:

- construct θ and a local proof that the transformation is sound, or
- return FAIL.

The synthesis algorithm may not:
- call SAT/UNSAT on a general residual;
- be given a target satisfying assignment;
- enumerate exponentially many θ;
- hide a general semantic implication query.

### Map contract

For every source witness in the certified domain,

[
ymodels R_alpha
Longrightarrow
mu_	heta(y)models R_{alpha^*}.
]

The map must be polynomial-time computable and witness reconstruction must remain polynomial.

### Global progress contract

A successful grouped contraction fixes/removes B, so

[
Phi(F)=#	ext{live Boolean choice dimensions}
]

drops by (|B|).

Thus at most n successful variable-dimension contractions can occur.

## 3. Source-native donor hierarchy

The literature already contains several proper subclasses of this architecture.

### 3.1 Autarkies

An autarky is a partial assignment whose touched clauses are already satisfied.
It gives a direct witness-preserving contraction and polynomial reconstruction.

Matching/linear autarky systems provide polynomially computable subclasses.

### 3.2 Blocked clause elimination

If a clause C is blocked by literal l, deleting C preserves satisfiability.

A model of the reduced formula that falsifies C is repaired by flipping the variable of l.
The blocking condition guarantees that all clauses containing the opposite literal remain satisfied.

This is a genuine local non-implicational witness-repair map.

Recognition is polynomial.

### 3.3 CNF homomorphisms / endomorphisms

Formula homomorphisms and retractions give structural satisfiability-preserving contractions and connect to autarkies.

However Szeider's homomorphism proof systems for several natural complete source classes are polynomially equivalent to tree-like resolution.

Therefore plain homomorphism/retraction synthesis is not a safe candidate universal currency.

### 3.4 Propagation / substitution redundancy

PR/SR rules certify equisatisfiable clause transformations by explicit witnesses/substitutions rather than logical implication.

Buss–Thapen show that with new variables these systems are simulated by and simulate Extended Resolution.

Thus generic SR-with-extension is powerful but is not a new unexplored representation class; it reaches the ER frontier.

### 3.5 Dominance rule

The SAT-2024 dominance rule uses a substitution plus a strict ordering decrease:
if a model violating a strengthening clause can be transformed into a strictly smaller model, then a minimal model satisfies the strengthening.

Kołodziejczyk–Thapen show the associated proof system is equivalent to G1, one level above ER in a standard bounded-arithmetic/proof-complexity hierarchy.

This is especially relevant to JANUS because it replaces direct branch-to-representative mapping by a **well-founded repair map**.

## 4. Janus synthesis: ranked grouped witness contraction

The next candidate is therefore stronger than direct witness dominance.

For block B and representative condition C_B (for example B=α*), seek a polynomially synthesizable pair

[
(mu,ho)
]

where:

- (mu) is a structural assignment transformer;
- (ho) is a polynomially represented well-founded ranking.

Required local theorem:

[
ymodels Fwedge
eg C_B
Longrightarrow
mu(y)models F
quad	ext{and}quad
ho(mu(y))<ho(y).
]

Then any (ho)-minimal model of F must satisfy (C_B).

Therefore

[
SAT(F)iff SAT(Fwedge C_B).
]

After adding (C_B), substitute/fix the block and remove (|B|) live dimensions.

Crucially this proof does **not** require explicitly mapping every branch directly into one representative branch.

## 5. New active gate

### R5_E9_POLY_SYNTHESIZABLE_RANKED_WITNESS_TRANSFORMER_GATE_V1

Input:
arbitrary CNF F.

Goal:
find in deterministic polynomial time a nonempty block B, a canonical block condition C_B, and a structural pair (μ,ρ) satisfying the ranked repair theorem above.

PASS requires:

1. synthesis poly(|F|), not merely verification;
2. μ poly-time computable;
3. ρ has polynomial representation and comparison;
4. soundness check polynomial and structural/local;
5. C_B removes at least one live Boolean dimension;
6. formula/intermediate state remains polynomial;
7. witness reconstruction polynomial;
8. repeat until a known polynomial carrier / trivial instance;
9. no general SAT oracle;
10. no exponential search over substitutions/rankings.

## 6. Immediate experimental program

Construct a **WDR-lean kernel** by exhaustively applying every currently polynomially synthesizable repair rule:

- unit / pure / equivalence simplification;
- matching and linear autarkies;
- blocked clause elimination;
- no-growth variable elimination;
- signed symmetry/permutation dominance;
- certified local substitution-redundancy patterns;
- tractable connected components (Horn, dual-Horn, Krom, affine, etc.).

Every rule must log an explicit model-reconstruction step.

Then run this closure on frozen adversarial families:

- Tseitin expanders;
- pigeonhole families;
- DDD linear 4-regular NAE-3SAT;
- Krom+XOR3 universalizing gadgets;
- random 3SAT near threshold;
- Janus equality-channel controls.

The residue is the new object to study.

The next new mathematics should be derived from a motif that survives **all** existing polynomial repair rules, rather than invented without reference to the lean kernel.

## 7. Strategic conclusion

The survivor is no longer:

[
	ext{arbitrary witness map}.
]

It is:

[
oxed{	ext{deterministically poly-synthesizable structural repair/ranking rule}}
]

with strict Boolean-dimension progress.

This places the search precisely between:
- practical SAT preprocessing/model reconstruction,
- ER/SR redundancy,
- the stronger G1-level dominance principle,
- and a prospective universal polynomial contraction algorithm.

D1 = EMPTY.  
P_VS_NP = OPEN.
