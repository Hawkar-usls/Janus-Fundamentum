# TRUMP exact interface quotient basis — theorem candidate

Date: 2026-09-15

Authority: `CANDIDATE_THEOREM__SUBJECT_TO_INDEPENDENT_CHECK__NO_GLOBAL_PROMOTION`

Frozen preregistration:
`research/TRUMP_EXACT_INTERFACE_QUOTIENT_BASIS_PREREGISTRATION_2026-09-15.json`

Frozen prereg Git blob SHA-1:
`43edbbb423fab4015f48410389ea41322ffde354`

Frozen prereg commit:
`eb4539f4cd8553cb5835b1ab1ffc9db31b3f1d25`

## Definitions

Let `B` be a Boolean interface of size `k`, with raw assignment space

\[
\Sigma_B = \{0,1\}^k.
\]

Let `D_B` be the frozen family of exact downstream observations that the transfer/reconstruction contract is allowed to ask after the interface is exposed.

Define downstream equivalence

\[
\sigma \sim_D \tau
\iff
\forall d\in D_B,\; d(\sigma)=d(\tau).
\]

A quotient `q_B : Sigma_B -> Q_B` is **adequate** when

\[
q_B(\sigma)=q_B(\tau) \Rightarrow \sigma\sim_D\tau.
\]

It is **complete/minimal with respect to `D_B`** when the converse also holds.

---

# U1 — unrestricted exact downstream semantics admits no universal compression

## Theorem U1

For every `k >= 1`, there exists an exact downstream query contract `D_k` of description size `O(k)` such that every adequate quotient of `Sigma_k={0,1}^k` has exactly `2^k` equivalence classes.

## Construction

Take the coordinate-query family

\[
D_k=\{d_1,\ldots,d_k\},\qquad d_i(\sigma)=\sigma_i.
\]

The contract consists of `k` fixed exact Boolean projections and therefore has linear description size.

## Proof

Let `sigma != tau`. Then there exists a coordinate `i` such that `sigma_i != tau_i`. Hence

\[
d_i(\sigma)\neq d_i(\tau).
\]

Therefore `sigma` and `tau` are not downstream-equivalent. Since this holds for every distinct pair, every `~_D` equivalence class is a singleton. Any adequate quotient must refine `~_D`, so it cannot merge any two raw assignments. Thus

\[
|Q_B|\ge |\Sigma_B| = 2^k.
\]

The identity quotient realizes equality, so the minimal exact quotient has exactly `2^k` classes. QED.

## Scope firewall for U1

U1 is a representation/query-contract barrier only. It does **not** prove:

- a lower bound for arbitrary SAT algorithms;
- a proof-system lower bound beyond its explicit representation contract;
- `P != NP`;
- impossibility of compression for restricted downstream algebras.

It proves only that no single exact quotient scheme can promise polynomially many classes for every unrestricted downstream exact contract while preserving all allowed observations.

---

# P1 — exact affine-syndrome quotient on a strict frozen subclass

## Affine-interface subclass

Fix a binary matrix

\[
A\in GF(2)^{r\times k}
\]

with rank `rho <= r`. Define the syndrome invariant

\[
h_A(\sigma)=A\sigma\in GF(2)^r.
\]

The subclass contract requires **before solving** that every downstream exact observation `d in D_B` is supplied together with an exact factor map `g_d` satisfying

\[
d(\sigma)=g_d(h_A(\sigma))
\quad\text{for all }\sigma\in\Sigma_B.
\]

The contract also restricts any interface-local feasibility/reconstruction relation to an affine system over `GF(2)` whose consistency and preimage reconstruction are solvable by Gaussian elimination.

No claim is made for a downstream observation that reads information outside the frozen syndrome basis.

## Theorem P1

Assume:

1. `A` is part of the frozen instance and is constructed/read in polynomial time;
2. every downstream observation factors exactly through `h_A`;
3. interface-local feasibility and preimage reconstruction are affine over `GF(2)` and polynomial-time solvable;
4. the image of `h_A` has polynomial size in the original instance length `L`, equivalently
   \[
   2^\rho \le poly(L);
   \]
   in particular this holds for `rho = O(log L)`;
5. the downstream tree/message solver invoked for one syndrome value is polynomial in `L`;
6. adequacy, factor-map completeness, reconstruction, and replay are independently checked.

Then exact transfer over the interface can be performed in polynomial total time by enumerating the reachable syndrome image rather than all `2^k` raw assignments.

## Proof

Two assignments with the same syndrome satisfy

\[
h_A(\sigma)=h_A(\tau).
\]

For every frozen downstream query `d`, exact factorization gives

\[
d(\sigma)=g_d(h_A(\sigma))
          =g_d(h_A(\tau))
          =d(\tau).
\]

Hence syndrome equality implies downstream equivalence, so `h_A` is an adequate quotient.

The set of reachable syndromes is `im(A)`, a vector space of size

\[
|im(A)|=2^\rho.
\]

A row-reduced basis for `A`, its rank, image basis, consistency tests, and a preimage for each queried reachable syndrome are obtained by Gaussian elimination in polynomial time. Under assumption 4 there are only polynomially many syndrome classes. For each class, run the frozen polynomial downstream transfer/message procedure once. If a class is accepting, reconstruct a raw interface assignment by solving the frozen affine preimage constraints and then apply the existing exact downstream reconstruction.

Thus

\[
T_{construct}+T_{discover}+T_{solve}+T_{reconstruct}+T_{verify}
\le poly(L)+2^\rho\,poly(L)
\le poly(L).
\]

All raw assignments in one syndrome fiber are intentionally indistinguishable under the frozen subclass contract, so no exact downstream information in scope is discarded. QED.

## Minimality/completeness caveat

P1 proves **adequacy** of the syndrome quotient under the explicit factor-through-`A` contract. It does not automatically prove that every distinct syndrome must remain distinct. Minimality requires the frozen downstream family to separate those syndrome values. A smaller quotient is allowed if an independently proven coarser complete basis exists.

---

# Falsifiers

## F2/F3 — omitted-observable collision

Let `e_j` be a nonzero vector in `ker(A)` and suppose an added downstream query reads a coordinate changed by `e_j`. Then for any `sigma`,

\[
h_A(\sigma)=h_A(\sigma+e_j)
\]

but the added coordinate query differs. Adequacy fails immediately. The correct outcome is `OPEN_UNSUPPORTED_INTERFACE_ALGEBRA` or explicit rejection of the candidate basis, never silent merging.

## F5 — exponential discovery is forbidden

It is not sufficient to enumerate all `2^k` assignments, compute their downstream transcripts, and only then discover that the transcripts collapse to `poly(L)` classes. Such a procedure violates the lifecycle bound at discovery/construction time.

## F6 — hash/canonical identity is not semantics

A hash may bind a signature or proofpack after the mathematical quotient is established, but hash equality/naming cannot justify merging two assignments.

---

# Exact validation architecture imported from the mechanism harvest

The candidate deliberately separates:

1. `IDENTITY` — exact frozen `B`, `A`, query family, factor maps, and reconstruction relation;
2. `DERIVATION` — recompute syndrome/messages from frozen leaves;
3. `ADEQUACY` — prove factorization of every allowed downstream query;
4. `COMPLETENESS_BASIS` — no undeclared downstream observable may be used after compression;
5. `AUTHORITY` — candidate cannot self-promote the basis;
6. `REPLAY` — independent checker recomputes the evidence;
7. `LIFECYCLE` — discovery/solve/reconstruction/verification counted in original input size.

This architecture is inspired by the inspected AIFC semantic-abstraction/completeness/replay separation, while the actual quotient theorem above is a new TRUMP mathematical object and is not claimed to have been supplied by AIFC.

---

# Candidate verdict if independently checked

If U1 and P1 both survive independent checking, the permitted scoped statement is:

`PASS_U1_AND_P1_SCOPED_SEPARATION`

meaning:

- unrestricted exact downstream semantics can force `2^|B|` distinguishable classes;
- a strict affine-syndrome interface subclass admits polynomial exact transfer when its syndrome image is polynomial and every downstream/reconstruction obligation factors through that frozen invariant.

Nothing in this candidate changes `P_VS_NP = OPEN` or proves `GENERAL_SAT_IN_P`.