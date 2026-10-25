# BABEL-41 — proof-carrying UNIVERSAL Exact-One SCL SAT/UNSAT decider, EXPONENTIAL worst-case

**25 October 2026. Research-only.** Stacked on BABEL-40 Draft PR #566 at exact HEAD \`ecae1f8700c50b08a6eab424ea64d41616690819\`. Responds directly to the requirement that an original valid input always reach either SAT with a physical witness or UNSAT with independently checkable proof, without \`UNKNOWN\`. **This does NOT satisfy the REQUIRED POLYNOMIAL-TIME guarantee and hence DOES NOT prove P=NP.** Source code + CI provide an executable end-to-end reference and an independently validated UNSAT proof contract for ALL valid SCL, not merely recognized gadget joins. This is the classical Exact Cover / Algorithm X branching idea, not claimed novel.

## 1. UNIVERSAL input / proof interpretation (no externally supplied decomposition)

Given ANY input with n variable indices and n original positive Exact-One rows, validate it as SCL: 3 distinct literals per row, each original variable in exactly three rows, pair-linearity (each pair of variables in at most one row). Connectedness is NOT required; the algorithm accepts disconnected SCL as well. Invalid inputs are rejected as malformed, NEVER considered verified UNSAT.

Construct the **dual exact-cover hypergraph**: universe consists of the n original rows; for every original variable v, its selected row-set \`C_v\` is the triple of rows containing v. A Boolean assignment x with Exact-One in every row is EQUIVALENT, bijectively, to a disjoint collection \`{C_v:x_v=1}\` that partitions all n rows. Therefore a SAT model has exactly **n/3 selected variables**, and if n is not divisible by3 the input is immediately UNSAT. This is an exact polynomial-time semantics-preserving reduction in BOTH directions. **General exact cover by 3-sets is known NP-complete; its standard search recurrence does not imply polynomial time.** Background: https://mathworld.wolfram.com/ExactCoverProblem.html . No unverified complexity-equivalence claim is made for the PARTICULAR square cubic linear connected subclass.

## 2. Full original-input search recurrence and polynomial-cost propagation

Maintain a set T of original variables committed TRUE (bitmask); all other variable values are either FALSE by exact-one propagation or still UNASSIGNED. Every true v covers exactly three distinct original rows. For all true variables, reject immediately if two cover the same row. For each covered row, force its two other variables FALSE. For every uncovered row r, enumerate its not-yet-forced-false candidate variables, rejecting a row with zero candidates and forcing a candidate TRUE if it is the only remaining choice; repeat the exact implications to a fixed point. If all original rows are covered, replay EVERY original Exact-One row and output the complete physical SAT assignment.

Otherwise choose a currently uncovered row with the fewest remaining candidates (necessarily exactly 2 or3 after propagation), and branch on EVERY candidate variable v being TRUE. Memoize explored true-bit states and their terminal contradictions or complete branch choices. **If all branches are UNSAT**, output a complete UNSAT proof DAG. This is a complete decision: each SAT solution must choose exactly one of the candidates for the selected uncovered row, and every propagated assignment is a logical consequence of Exact-One. Conversely any emitted witness is independently checked against the original rows.

**All-n complexity theorem with no hidden oracles:** Each accepted TRUE variable accounts for three distinct previously uncovered rows, so every consistent branch path has at most n/3 selected variables and at most n/3 binary/ternary decisions. A conservative upper bound is

    T_decision(n) <= poly(n) · 3^(n/3)
    memory including UNSAT proof DAG <= poly(n) · 3^(n/3).

Bitsets use O(n)-bit integers, each closure scans O(n²) bit operations per iteration, and any sequence of positive unit propagation commits at most n/3 true variables, so each closure is polynomial. The DAG has ≤O(3^(n/3)) nodes, with O(n)-bit keys and at most three child links per branching node. Hashing, allocation, full original row verification, proof construction and serialization are included in the exponential upper bound. A SAT witness has only n bits.

**DO NOT MISSTATE:** This is NOT an n^C bound for a universal fixed C. The exact solver always returns SAT or UNSAT but can be exponentially expensive; the fully recorded UNSAT certificate also can be exponentially large. Thus this work closes the "no terminal UNKNOWN" engineering requirement **only at exponential cost**; it DOES NOT close polynomial discovery, polynomial intermediate states, polynomial total runtime, or short UNSAT proof construction.

## 3. Independent proof DAG verification, not a printed solver status

A SAT result contains the original Boolean true-mask and fixed source digest. Independently replay all original Exact-One rows, the fact |T|=n/3 and the original legal input. A matching SAT witness is a polynomial-time correctness certificate.

A certified UNSAT answer includes either:

1. \`DIVISIBILITY\` with n%3!=0, proved by exact total degree3 counting; OR
2. \`COMPLETE_EXACT_ONE_REFUTATION\`, with a SHA256 digest of the **exact original ordered rows**, a root state \`T=0\`, and an exhaustive DAG of reachable TRUE-bit states.

The **independent** checker in \`experiments/babel41/verify_universal_proof.py\` does NOT call the producer's closure/branching method. It represents assignments as native Python sets and independently derives every FALSE variable from covered rows, every forced TRUE unit, every contradiction and the available candidates in every uncovered row. At each proof DAG internal node it permits ANY actual uncovered row (no reliance on producer's particular heuristic) but requires **ALL** currently viable true-candidate branches to be included and recursively refuted. A leaf is accepted ONLY if the checker directly derives an Exact-One contradiction on the original rows. If a reachable state is SAT, if ANY child is missing, if a leaf is unjustified, if keys/digest are tampered with or if proof nodes form a cycle, reject the receipt.

Thus the checker independently proves UNSAT by complete induction on the finite decision tree, up to memoized DAG sharing. It runs in \`poly(n, certificate-size)\` time: *polynomial in the potentially EXPONENTIAL certificate length, not necessarily polynomial in n*. That difference is fundamental for the user's P=NP acceptance criterion.

## 4. Independent controls and falsification discipline

- Connected affine SCL9: exact three physical SAT models by independent full 2^9 enumeration. Producer returns a verified witness.
- Fano SCL7: UNSAT by n%3 immediately.
- Certified BABEL24 connected U=SCL27: exactly one model, independently checked via the rational nullspace enumerator of BABEL32.
- BABEL40 legal connected signed-flux SCL54 (both +3 and −3 physical local states): exact one global SAT model by prior full binary parity enumeration; independent new universal DPLL must reconstruct exactly that model, without supplied port decomposition or labels.
- Three disjoint legal Fano components SCL21: n%3==0, but each Fano component is impossible. The producer MUST emit the actual complete UNSAT branch-DAG, and a separate set-based proof checker MUST replay every branch and reject several deliberately tampered receipts. This tests UNSAT not derivable from global n%3 alone.
- This broad all-input fallback is not a substitute for the faster admitted BABEL31–40 paths. A portfolio may try certified special cases first and fall back, but still has worst-case exponential complexity unless the fallback is eliminated by an ALL-n polynomial theorem.

### Explicit ordered disconnected family demonstrating exponential exploration by THIS procedure

The exponential upper bound is not merely a formal worst-case expression. Let \`Q\` be the certified legal SCL9 affine model with exactly THREE SAT assignments and \`Z\` the disjoint union of THREE legal Fano7 instances (21 rows total, globally UNSAT even though 21 is divisible by3). For every t≥1, put t independent copies of Q **first in row order**, then Z last. The resulting formula \`F_t\` is a perfectly legal, possibly DISCONNECTED, square cubic linear positive Exact-One system of n=9t+21 variables and rows.

At the start, every row has three available literals. The producer's "minimum eligible candidates, then smallest row-index" heuristic enters the first Q before the trailing Z. Its propagation and deeper branching resolve the first Q before moving to later rows, and so on. Because each Q component has THREE distinct SAT assignments and no decisions in one Q affect another, this ordered complete UNSAT proof tree contains at least \`3^t\` distinct valid partial true-bit prefixes reaching the final UNSAT tail. The exact proof DAG keeps these distinct masks separate, and must visit at least \`3^t\` different states. This proves an **exponential lower bound on this PARTICULAR DPLL strategy** on a valid (DISCONNECTED) SCL family, independently of P vs NP. Small t=1,2,3 are independently replayed through the complete UNSAT verifier in CI.

Important firewalls: This is not a computational lower bound on ALL algorithms, is not a lower bound for any other proof system and is not directly a lower bound on the user's stricter CONNECTED SCL target. Faster methods could detect the Fano contradiction first, and different DPLL heuristics could avoid this exact example. The experiment's finite t controls alone are not the asymptotic proof; the independent-component product argument establishes all-t behavior of the specified deterministic branching heuristic.

## 5. The actual unresolved universality theorem

The user's original task remains:

    Construct an algorithm that for EVERY legal connected SCL F of size n:
      deterministically computes SAT+witness or UNSAT,
      preserving exact original semantics,
      with TOTAL T_construct+T_solve+T_reconstruct+T_verify <= n^C
      for ONE universal C independent of F.

BABEL-41 gives only the decision **totality** and exact certificate property. The missing and potentially deepest mathematical result is an all-input polynomial-size representation of the exhaustive branch DAG (or an entirely different polynomial decider) with constructive polynomial discovery and verification. Proof-system state lower bounds cannot be improperly transferred to SAT computational hardness, and no recognized class, experiment, successful CI or restatement of an exponential algorithm establishes P=NP.

\`\`\`
BABEL41_VALID_ANY_SCL_INPUT_TOTAL_SAT_OR_UNSAT = PROVED
BABEL41_ORIGINAL_SCL_TO_EXACT_COVER_BY_3 = PROVED_BIJECTION
BABEL41_SAT_PHYSICAL_WITNESS = POLY_VERIFIABLE
BABEL41_UNSAT_COMPLETE_REFUTATION_DAG = INDEPENDENTLY_VERIFIABLE
BABEL41_UNSAT_DAG_SIZE_POLYNOMIAL_IN_INPUT = NOT_PROVED
BABEL41_FULL_ALGORITHM_WORST_CASE = EXPONENTIAL_UPPER_BOUND
BABEL41_ALL_N_POLYNOMIAL_DISCOVERY_COMPOSITION = NOT_PROVED
BABEL41_UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
\`\`\`
