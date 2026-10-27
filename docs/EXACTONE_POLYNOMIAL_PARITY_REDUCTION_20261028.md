# JANUS Fundamentum: checkable polynomial Exact-One reduction

**Theorem (limited claim).** For every finite instance consisting of a conjunction of 1- or 3-literal EXACT-ONE clauses over n Boolean variables (literals may be negative or repeated), the implementation exactone_parity_preprocessor.py terminates in polynomial time. It returns either a sound certificate of UNSAT or a partial assignment A and residual exact-one instance F' such that, for every total Boolean assignment X, F(X) is satisfied iff X extends A and F'(X) is satisfied. No claim is made that F' always shrinks, that F' can be solved in polynomial time, or that P=NP.

## Operator

1. Interpret a clause (l1,...,lk), k in {1,3}, as an exact-one sum of Boolean literals equal to 1. With known values, a clause with more than one true literal or no possible true literal is a contradiction. If one literal is already true, all remaining literals are forced false; if none is true and only one unassigned literal remains, it is forced true.
2. Every EXACT-ONE clause necessarily satisfies the parity (XOR) of its literals equal to 1 mod 2. Replace each negated literal by x XOR 1 and combine occurrences mod 2. Substitute existing assignments.
3. Run Gaussian elimination over GF(2), tracking the XOR of original clause indices for each derived row. A row 0=1 witnesses UNSAT; a unit row x_i=b forces x_i=b. Any such event is returned with its source-clause XOR lineage.
4. Repeat until a contradiction, complete satisfaction, or fixed point. Delete satisfied clauses and assigned literals; duplicate identical residual clauses are deduplicated.

**Why this is sound:** Each exact-one model satisfies every parity equation. XOR combinations of those equations and substitutions of previously justified variable assignments remain necessary. Forced Boolean assignments and contradiction rows are therefore valid. Clause inferences are direct consequences of exact-one semantics. By induction over the certificate event list, assignments are model preserving; substituting them yields an exactly equivalent residual on remaining variables. The standalone verifier replays each clause inference or independently XORs its source clauses; it deliberately does not call Gaussian elimination.

**Polynomial bound:** Let L=n+total number of literal occurrences+1 and m=number of clauses. At most n assignments occur. In each iteration, scanning clauses is O(L); Gaussian elimination uses at most m rows of n-bit bitsets, at most O(mn^2) row XOR operations, each O(n) bit cost, and a backward pass within the same conservative envelope O(L^4) per iteration. Hence total O(L^5) elementary bit operations (intentionally loose); space O(L^3) bits, including at most m-bit lineage masks. The certificate contains at most n justifications of at most m indices each, and is polynomially independently verifiable. The exponential reference enumeration in tests is not part of the operator.

## Guaranteed nontrivial reduction on one explicitly characterized class

Each disjoint five-variable gadget contains the three cubic clauses:

~~~text
EXACT1(a,b,c)
EXACT1(a,b,d)
EXACT1(c,d,e)
~~~

The XOR of the first two implies c=d. XOR with the third forces e=1. Exact-one propagation forces c=d=0. The remaining requirement is EXACT1(a,b). Thus three of five variables are always eliminated while exactly preserving satisfying assignments. For k disjoint gadgets, 3k of 5k variables are forced and 2k remain. This is a strict reduction for this specified family only; it is not a worst-case guarantee for arbitrary instances.

## Execution

~~~bash
python research/exactone_parity_preprocessor.py --self-test
python research/exactone_parity_preprocessor.py --input /path/to/cubic_instance.json --output /tmp/reduction.json
~~~

JSON example: {"n":5,"clauses":[[1,2,3],[1,2,4],[3,4,5]]}.
Positive DIMACS literal i denotes x_i, negative -i denotes NOT x_i; variables indexed 1..n.

The offline tests compare original and reduced complete sets of satisfying assignments via a separate exponential reference enumerator on 327 deterministic curated/random cases, including negated literals and duplicate occurrences. It independently verifies source-XOR certificates and rejects a tampered certificate.

## Scientific boundary and Rowan

No Rowan API calls or credits are used by this mathematics. The current Rowan SDK supports scientific chemistry/protein workflows; SAT is not an advertised Rowan workflow. A protein structure-confidence or molecular pKa result cannot be treated as a SAT witness. The independent protected Rowan read-only API check is at https://github.com/Hawkar-usls/Janus/actions/runs/40593971749 (attempt 2, auth verified). Neither read-only authorization nor BBC1 archive results establishes free weekly billing capacity for a new calculation. The allowed new spend is zero in this research branch.

**Open obstruction:** Find a uniformly polynomially bounded reduction of all residual cubic Exact-One instances to a family with complete polynomial-time decision and witness reconstruction. Polynomial preprocessing alone does not close this obstruction. P_VS_NP=OPEN.
