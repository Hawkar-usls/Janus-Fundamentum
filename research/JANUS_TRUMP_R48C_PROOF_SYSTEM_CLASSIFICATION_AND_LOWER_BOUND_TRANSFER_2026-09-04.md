# JANUS TRUMP R48C — Proof-System Classification and Lower-Bound Transfer Frontier

Status: **SYMBOLIC CLASSIFICATION FRONTIER; NO P-vs-NP CLAIM**

## Question

Before trying to prove universal polynomial envelope coverage for the frozen TRUMP grammar, determine whether the grammar already lies inside a proof system for which hard UNSAT families are known.

The frozen R47M/R47J authority is:

1. exact Davis–Putnam variable elimination;
2. R33 certified reductions;
3. R35B single-literal RUP vivification;
4. R42 subsumption-aware BVE;
5. R34 complete-affine-CNF recognition followed by verified GF(2) elimination;
6. declared polynomial terminal solvers for Horn and 2-CNF.

No new variables are introduced by these mechanisms.

## Part A — affine-inactive UNSAT trajectories are resolution-translatable

Consider a finite UNSAT trajectory on which R34 never returns an affine terminal.

The following frozen mechanisms admit direct polynomial Resolution accounting.

### A1. Tautology deletion

A deleted tautological clause is never needed by a later Resolution refutation. Any refutation of the remaining formula is already a refutation from a subset of the original clauses.

### A2. Pure-literal autarky deletion

For UNSAT transfer, deleting clauses satisfied by a pure literal only removes clauses. If the reduced formula is refuted, the same refutation is valid from the original formula because all remaining clauses are original/previously derived clauses.

SAT preservation is handled separately by the existing reconstruction trace and is not needed for an UNSAT Resolution lower-bound transfer.

### A3. Subsumption deletion

Deleting a clause subsumed by a retained smaller clause only removes a redundant premise. A later refutation from the retained set remains a valid refutation from the larger original set.

### A4. Blocked-clause elimination as used by R33

R33 only **deletes** a blocked clause; it does not add blocked clauses or extension variables. Therefore an UNSAT refutation of the reduced formula uses a subset of the preceding clauses and can be reused unchanged as a refutation from the preceding formula.

This observation is deliberately narrower than claims about proof systems allowing blocked-clause *addition*.

### A5. Unit propagation with reconstruction trace

R33 selects an existing unit literal `l`.

- Clauses containing `l` are deleted.
- Every surviving clause obtained by deleting `-l` from a parent `C ∨ -l` is derivable by one ordinary Resolution inference from the parent and the unit clause `(l)`.

Hence one R33 unit-propagation step can be translated with at most one Resolution inference per shortened clause.

### A6. Exact DP and R33/R42 BVE

For pivot `x`, every retained non-tautological resolvent

`(P \ {x}) ∪ (N \ {-x})`

is exactly one ordinary Resolution inference from one positive parent and one negative parent.

Unaffected clauses are copied and subsumed clauses are deleted. Thus an explicit exact-DP/BVE record with `r` retained resolvents has an ordinary Resolution derivation overhead polynomial in the explicit record size (indeed, one direct inference per resolvent before bookkeeping/deletions).

### A7. R35B RUP strengthening

R35B replaces a clause by a one-literal strengthening only when unit propagation on the negation of the proposed strengthened clause derives conflict. Its independent checker replays that UP conflict.

RUP additions are polynomially translatable to Resolution derivations. This is standard in proof logging: after eliminating proper RAT steps, RUP additions can be replaced by Resolution inferences; no extension variable is needed for the RUP step itself.

For R35B this gives a polynomial Resolution derivation of every accepted strengthened clause from the current formula. The old source clause can then be ignored.

### A8. Horn UNSAT terminal

The frozen Horn solver is forward chaining. Every derived positive fact can be mirrored by resolving the responsible Horn clause with the already-derived unit facts corresponding to its negative body. A violated all-negative Horn clause then resolves with those facts to the empty clause.

Thus a frozen Horn UNSAT terminal has a polynomial-size ordinary Resolution refutation.

### A9. 2-CNF UNSAT terminal

The frozen 2-SAT solver detects a variable `x` for which `x` and `-x` lie in one implication SCC.

A directed implication path `x -> -x` corresponds to a chain of binary clauses whose successive Resolution derivation yields unit `-x`; the reverse path yields unit `x`; resolving these two units yields the empty clause.

Thus a frozen 2-CNF UNSAT terminal has a polynomial-size ordinary Resolution refutation.

## Affine-inactive translation lemma

Let `pi` be a frozen TRUMP UNSAT trajectory of total explicit certificate/transition size `S` such that no R34 affine terminal occurs.

By composing A1–A9, every persisted or terminal clause needed by `pi` can be translated into an ordinary Resolution derivation from the original CNF with size polynomial in `S`.

Therefore:

\[
\boxed{\text{POLY-SIZE AFFINE-INACTIVE TRUMP UNSAT RUN}\Rightarrow\text{POLY-SIZE RESOLUTION REFUTATION}.}
\]

This statement is about proof-size translation. It does **not** assert that every possible frozen TRUMP run is affine-inactive.

## Part B — R34 is the escape hatch from ordinary Resolution

R34 recognizes a whole CNF exactly when every clause-support group is a complete parity bundle. It then converts those bundles to GF(2) equations and performs Gaussian elimination with an independently checked linear certificate.

This is genuinely stronger than ordinary Resolution on the recognized affine language.

Classical Tseitin contradictions over bounded-degree expander graphs have exponential ordinary-Resolution refutations, while a Tseitin CNF written as complete constant-width parity bundles is exactly the kind of input recognized by R34 and is solved by Gaussian elimination in polynomial time.

Therefore the full frozen grammar cannot be globally classified as merely ordinary Resolution.

The correct firewall is:

\[
\boxed{\text{NONAFFINE PATH}\subseteq\text{RESOLUTION-TRANSLATABLE},\qquad
\text{AFFINE TERMINAL}=\text{SEPARATE GF(2) AUTHORITY}.}
\]

## Part C — what classical lower bounds do and do not give us

### C1. Davis–Putnam lower bound

Galil (1977) constructs contradictory CNFs for which Davis–Putnam generates exponentially many distinct clauses under **every** variable-elimination order.

This decisively rules out any argument of the form

`EXACT DP ALONE + CHOOSE A BETTER VARIABLE ORDER => UNIVERSAL POLYNOMIALITY`.

It does **not** by itself lower-bound the full frozen R47M grammar because R33/RUP/SA-BVE/affine terminals can alter or close the state between projections.

### C2. Ordinary Resolution lower bounds

There are exponential ordinary-Resolution lower bounds for standard families including Tseitin contradictions on constant-degree expanders and sparse pigeonhole/perfect-matching principles.

By the affine-inactive translation lemma, such a lower bound transfers to frozen TRUMP **only after** one proves that every candidate polynomial trajectory for the chosen family remains outside the R34 affine terminal.

Therefore a valid killer family must satisfy two independent requirements:

1. exponential Resolution hardness;
2. **AFFINE-EVASION INVARIANT**: every reachable state allowed by the frozen polynomial grammar remains non-affine until contradiction is certified by non-affine machinery.

Testing non-affinity on finitely many instances is not sufficient; the transfer requires a symbolic invariant or an explicit family theorem.

### C3. Resolution over parities / Res(oplus)

A tempting shortcut is to classify the whole grammar inside `Res(oplus)` and import known lower bounds.

This is currently not enough for an unrestricted universal refutation:

- strong exponential lower bounds are known for tree-like and regular Res(oplus);
- recent work gives exponential lower bounds for dag-like Res(oplus) under substantial depth bounds;
- as of the current proof-complexity frontier, a general superpolynomial size lower bound for unrestricted dag-like Res(oplus) remains a major open problem.

The frozen TRUMP trajectory has polynomially bounded operational height only conditionally, but its translated proof depth has not yet been proved to lie inside the depth regimes covered by the strongest current Res(oplus) lower bounds.

Therefore:

\[
\boxed{\text{DO NOT CLAIM A GENERAL RES(\oplus) LOWER-BOUND TRANSFER YET}.}
\]

## Part D — two legitimate next attacks

### Route D1 — affine-evasive Resolution-hard family

Construct or import a bounded-width 3-CNF family `H_n` with known exponential Resolution lower bound and prove:

\[
\boxed{\forall F\in Reach_{R47M}(H_n),\ R34(F)=NOT\_RECOGNIZED.}
\]

Then any hypothetical polynomial frozen TRUMP UNSAT trajectory would translate to a polynomial Resolution refutation, contradicting the known lower bound.

This would be an explicit lower bound on the **current frozen grammar**, not a statement that SAT is outside P.

Candidate families to investigate first:

- sparse graph pigeonhole / perfect matching principles;
- gadget-lifted constant-width formulas designed to resist affine structure.

Plain Tseitin is a bad candidate because R34 intentionally closes complete parity bundles.

### Route D2 — bounded-depth Res(oplus) transfer

Instead classify every frozen inference, including R34, inside a concrete Res(oplus) derivation and derive an explicit upper bound `D_TRUMP(N)` on the depth of the translated proof.

If

\[
D_{TRUMP}(N)
\]

falls inside a regime for which a published superpolynomial Res(oplus) lower bound exists on a compatible constant-width family, then that family refutes universal polynomiality of the frozen grammar.

If the translation depth is too large, the lower bound cannot be imported and this route stays open.

## Part E — relation to R48B weighted envelope

R48B asks for a polynomial local amortization coefficient `a(N)` controlling persisted representation growth.

R48C adds a logically independent obstruction:

even if representation growth is polynomially bounded, a proof-complexity hard family can still forbid a polynomial complete trajectory for the current proof authority.

Therefore universal completion now requires **both**:

1. polynomial representation/work envelope;
2. proof-authority coverage strong enough to escape every known hard family.

Formally:

\[
\boxed{\text{POLYNOMIAL ENVELOPE}\neq\text{UNIVERSAL PROOF COVERAGE}.}
\]

## External references

1. Z. Galil, *On the complexity of regular resolution and the Davis-Putnam procedure*, Theoretical Computer Science 4(1), 1977, DOI 10.1016/0304-3975(77)90054-8.
2. E. Ben-Sasson and A. Wigderson, *Short Proofs are Narrow — Resolution Made Simple*, JACM 48(2), 2001 / ECCC TR99-022.
3. B. Kiesl, A. Rebola-Pardo, M. J. H. Heule, *Extended Resolution Simulates DRAT*, IJCAR 2018; and *Simulating Strong Practical Proof Systems with Extended Resolution*, Journal of Automated Reasoning 2020. Relevant point: RUP additions can be eliminated in favor of Resolution derivations during the simulation.
4. K. Efremenko, M. Garlik, D. Itsykson, *Lower Bounds for Regular Resolution over Parities*, SIAM Journal on Computing 54(4), 2025 / ECCC TR23-187.
5. F. Byramji and R. Impagliazzo, *Lower Bounds for Bit Pigeonhole Principles in Bounded-Depth Resolution over Parities*, ECCC TR25-118, 2025.
6. S. Bhattacharya and A. Chattopadhyay, *Exponential Lower Bounds on the Size of ResLin Proofs of Nearly Quadratic Depth*, ECCC TR25-106, 2025.

## Frozen epistemic firewall

- `AFFINE_INACTIVE_TRUMP_UNSAT_TO_RESOLUTION_TRANSLATION = SYMBOLICALLY_ESTABLISHED_FOR_CURRENT_RULES`
- `FULL_TRUMP_TO_ORDINARY_RESOLUTION = FALSE_AS_A_CLASSIFICATION_BECAUSE_R34_ADDS_GF2_AUTHORITY`
- `GALIL_DP_LOWER_BOUND_TRANSFERS_TO_FULL_R47M = NOT_ESTABLISHED`
- `ORDINARY_RESOLUTION_LOWER_BOUND_TRANSFERS_IF_AFFINE_EVASION_INVARIANT_PROVED = CONDITIONAL_THEOREM`
- `GENERAL_UNRESTRICTED_RES_OPLUS_LOWER_BOUND_TRANSFER = NOT_AVAILABLE`
- `R48B_POLYNOMIAL_ENVELOPE = INDEPENDENT_FROM_PROOF_AUTHORITY_COVERAGE`
- `O4_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_EQ_NP = NOT_PROVED`
- `P_NE_NP = NOT_PROVED`
- `P_VS_NP = OPEN`
- `TRUMP_finished = false`
