# JANUS Exact-One: exact solution for high-treewidth, low-XOR-nullity instances

Status: research Draft PR #571; 28 October 2026. No claim P=NP.

## Theorem

Let F be a conjunction of signed linear/cubic Exactly-One clauses on n Boolean variables. Turn every exact-one clause into its necessary GF(2) equation, noting that each occurrence of a negative literal complements its bit, and repeated variable occurrences cancel modulo 2. Suppose the consistent resulting affine system has rank r and nullity k=n-r.

Then the algorithm research/exactone_affine_nullity.py decides F exactly in

    O(poly(L) + 2^k * poly(L))

time and builds a SAT witness or a checkable UNSAT certificate of size

    O(poly(L) + 2^k * log(m+1))

where L is the encoded input length and m the number of original clauses. This is polynomial if k is bounded by a constant; more generally it is polynomial whenever k=O(log L), provided the implementation resource cap permits the enumeration. For general instances, k may grow linearly with n, and the method does not imply a polynomial general SAT solver.

This method has no dependence on graph treewidth and works on graphs with arbitrarily many cycles and arbitrarily high treewidth when parity nullity is small.

## Soundness and certificates

Each original Exact-One assignment satisfies the extracted GF(2) system. Gaussian elimination yields a canonical list of affine pivot equations, from which each possible full assignment arises by a choice of the k free coordinates. The algorithm checks *original* Exactly-One clauses, not just parity, for each affine candidate. SAT returns a full assignment satisfying the original clauses. UNSAT without a parity conflict enumerates all 2^k affine candidates and retains the index of an original clause violated by each; therefore no model exists. A pure GF(2) inconsistency yields a shorter certificate: an XOR combination of original source clauses equal to 0=1. A limit overflow gives OPEN_NULLITY_CAP, never a false UNSAT.

The independent verifier does not invoke the solver's elimination routine. It checks every stored pivot row by XOR of its original clause sources, checks row reducedness and that the rows span all original necessary parity equations, then independently checks each candidate-rejection record or full satisfying witness. It rejects a forged certificate even if the output JSON checksum is recomputed.

Research computational guard: free dimension at most 10 (default 4). This guard limits execution cost; it is not part of the mathematical theorem. Running time and certificate sizes are polynomial for fixed k regardless of graph width. No Rowan API calls.

## Infinite high-width SAT and UNSAT family

Variables: one central hub h and m leaf variables u1...um (m>=4).

For every pair 1<=i<j<=m, add the cubic Exactly-One constraint

    h + ui + uj = 1

over Boolean *integer* values. The primal graph is a complete graph on m+1 vertices, hence its treewidth is exactly m, unbounded as m grows. Nevertheless, the GF(2) relaxation forces h=1 and all ui equal, leaving only one free Boolean bit (k=1) for every m>=4.

SAT case: choosing all ui=0 and h=1 satisfies all clauses. The other affine candidate ui=1 violates the original Exact-One semantics (three true literals), so the actual SAT model is uniquely reconstructible.

UNSAT case: add one further cubic Exactly-One clause u1+u2+u3=1. Its parity forces ui=1, and the original hub/pair equations then become exactly-three rather than exactly-one. The affine system is still consistent (k=0), but the resulting unique candidate violates original Exact-One constraints. Hence this high-width UNSAT instance receives a complete rejection certificate.

The provided benchmark m=65 forms a 66-variable primal clique with treewidth 65 and 2080 cubic hub-pair clauses, plus one more in the UNSAT case. This construction has Theta(m^2) original clauses (so it is a polynomial-size family).

## Contrast with the previous JANUS width solver

- Width DP: FPT parameter = treewidth of a witnessed elimination order w, runtime poly(L) * 2^(w+1). It covers many low-width but high-nullity instances.
- Affine nullity solver: FPT parameter = k=n-rank of necessary XOR equations, runtime poly(L) * 2^k. It covers high-width but low-nullity instances.
- General Exact-One: neither parameter is guaranteed small; no uniform polynomial-time decision algorithm has been established.

The two methods can be invoked separately and a result promoted to proved SAT/UNSAT only after its original-clause, independently checkable certificate passes. Their intersection or union of solved instances is not a polynomial universal decision algorithm when both parameters are unbounded.

## Reproduce

    python research/exactone_affine_nullity.py --self-test
    python research/exactone_affine_nullity.py --input /tmp/example.json --max-free-dimension 4 --output /tmp/result.json

The unit suite has >500 small original-clause SAT/UNSAT comparisons against an independent truth-table enumerator, high-width SAT and UNSAT tests, a strict OPEN large-nullity gate, and a rehashed fraudulent UNSAT-certificate negative control.

## Lapis and Rowan

The math result is transmitted by the actual pinned Lapis universal converter as annotation-only IR and independently re-verified in Fundamentum from the original input. A previously collected real Rowan BBC1 science receipt is translated separately, with no attempt to reinterpret pTM, lDDT or molecular observations as Boolean constraints, SAT answers or physics-based proof. No new Rowan compute, no paid credits, no production changes. P_VS_NP=OPEN.
