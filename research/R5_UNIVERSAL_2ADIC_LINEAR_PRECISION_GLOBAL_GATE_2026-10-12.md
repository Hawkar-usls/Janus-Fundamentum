# R5 — All-Cubic High-Precision 2-Adic Nonzero Gate: Linear Bit Window, Not a Solver

Date: 2026-10-12 (Europe/Kyiv).
Authority: exact cubic graph -> SCL direct bridge (PR #515) and
PR #516 successive verified source arithmetic and flow audits.

**Goal remains unchanged:** a deterministic all-input bit-time
polynomial `SolveLinearCubicXSAT` returning verified SAT witness or UNSAT
on every legal positive square-cubic-linear Exact-One instance.

**Result status: new quantitative *exact reduction/anti-cheat gate*,
NOT a polynomial-time algorithm and NOT a proof of P=NP.**

## I. Global exact high-precision 2-adic decision equivalence

Let G be ANY connected simple cubic graph with v=2h >=4 vertices.
Let F(G) count proper 3-edge-colourings with the THREE colours
distinguishable. The colour-name permutation action S3 is free, so
F(G) is divisible by 6. Let C(G):=F(G)/6 be the positive integer number
of unlabelled 1-factorizations, and zero when G is uncolourable.

M. P. Ivanov, "An exact bound on the number of proper 3-edge-colorings
of a connected cubic graph," Zapiski Nauchnykh Seminarov POMI 497
(2020), 26--52, established (vertices=2h):

    F(G) <= 2^h + 8    when h even,
    F(G) <= 2^h + 4    when h odd.

Primary publication abstract:
https://www.mathnet.ru/eng/znsl7026

For every h>=2 these inequalities imply:

    0 <= C(G) = F(G)/6 < 2^h.

Therefore the **SINGLE** 2-adic residue of the NORMALIZED count
in the ring Z/(2^h) is IDENTICAL to its full exact integer count:

    C(G) mod 2^h = C(G).

Hence the uniform exact decision identity

    G is 3-edge-colourable
       iff C(G) mod 2^h != 0.

The required modulus has only h+1=O(v) binary digits. So neither
integer word size, exact CRT reconstruction, nor exponential-digit
precision is the obstruction in this pathway.

**Computational gate:** An algorithm that EVALUATES
C(G) mod 2^h in time poly(v) for EVERY connected simple cubic G
would decide cubic 3-edge-colourability in deterministic polynomial
time, and by Holyer NP-completeness would imply P=NP.
No such evaluator is constructed in JANUS; writing the expression
"mod 2^h" is a complexity-preserving reformulation only.

For an already-disconnected cubic graph, deciding connected
components is polynomial, and the graph is 3-edge-colourable iff
every component is. This does not address the hard connected core.

**Comparison:** without importing Ivanov, a trivial bound
F(G)<=3^m with m=3v/2 already gives a modulus with O(v) digits.
Ivanov improves the explicit global bit threshold to v/2,
not the asymptotic polynomial-vs-exponential runtime status.

## II. Quantitative linear-precision lower family

A predecessor all-q theorem constructs connected simple
G_t=Prism_3 +_3 t copies of K3,3 by a legal cubic 3-edge sum.
The exact factorization gives

    v_t=6+4t,
    F(G_t)=6*2^t,
    C(G_t)=2^t>0.

An explicit proper 3-edge-colouring is constructed and directly
verified in the predecessor runnable code. Thus, for EVERY t>=1:

    C(G_t) mod 2^s =0 for EVERY 1<=s<=t,
    C(G_t) mod 2^(t+1) = 2^t !=0.

These are actual SAT graphs with false zero residues at EVERY
insufficient 2-adic precision <=t.

Since t=(v_t-6)/4, a modular-only SAT test working solely by
checking whether the count is nonzero modulo 2^s MUST in the
worst case use linearly many bits. No O(log v) bit precision
or any fixed bit precision can be uniformly sufficient.

On the direct SCL embedding, the incidence matrix has size

    n_SCL = 3|E| = 9v_t/2 = 27+18t.

Thus the false-zero threshold corresponds to
    s <= (n_SCL-27)/18.
The Ivanov upper exactness threshold is
    s = v_t/2 = n_SCL/9.

Both bounds are LINEAR in SCL input size; this is a
**precision-window theorem for this particular 2-adic count
proposal**, NOT a generic time/space lower bound for all
polynomial SAT solvers. High precision is **not** itself
a superpolynomial resource because its bit count is linear.

## III. Validation and provenance

Executable (exact finite controls; no implicit poly-time
claimed for independent matching counts):

    python experiments/r5_universal_full_precision_2adic_decision_frontier.py

Validation includes K4, K3,3, cube, prism P5, Petersen,
Isaacs flower J5, and fixed SAT20, using an independent
complete perfect-matching/even-2-factor enumerator.

On the explicit connected family t=1,2,3,4,8,16,
the script constructs actual proper edge colour witnesses
and proves the claimed residue loss at precision t; it uses
the prior ALL-t 3-sum counting theorem for exact counts.

IMPORTANT: applying the Ivanov numerical upper bound to
small exact finite controls is a consistency audit, not a
new proof of Ivanov's published universal theorem.

### Gate ledger

ALL_CONNECTED_CUBIC_COUNT_2ADIC_EXACT_AT_H_BITS =
    PROVED_USING_IVANOV_2020_PUBLISHED_BOUND.
LINEAR_PRECISION_LOWER_FAMILY_FOR_MODULAR_NONZERO =
    PROVED_CONSTRUCTIVE_ALL_T.
LEGAL_SCL_SOURCE_EMBEDDING_OF_FAMILY = PREDECESSOR_PROVED.
MODULUS_SIZE_OBSTRUCTION = REMOVED_AT_BIT_LENGTH_LEVEL.
UNIFORM_POLY_EVALUATOR_OF_NORMALIZED_COUNT_MOD_2POW_H =
    NOT_CONSTRUCTED.
ALL_INPUT_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Next permitted decisive attack:
Find a proof-carrying algorithm to evaluate that SINGLE residue
on every connected simple cubic G in poly(v) BIT TIME without
enumerating cyclic flows, perfect matchings, graph deletions or
exponentially many dynamic programming boundary states.
This is a sufficient target for P=NP, not a theorem already won.
