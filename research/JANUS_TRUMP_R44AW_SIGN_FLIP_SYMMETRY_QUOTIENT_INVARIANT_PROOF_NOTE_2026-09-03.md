# JANUS TRUMP R44AW — sign-flip symmetry quotient

## Exact invariant

For a CNF `F` on variables `x_1,...,x_n`, define `H(F) <= GF(2)^n` as the set of masks `h` such that flipping the sign of every occurrence of variable `x_i` whenever `h_i=1` leaves the clause multiset unchanged.

For every clause support `S`, width at most 3 gives at most eight possible sign patterns. The translation stabilizer of the local sign-pattern multiset is a subgroup of `GF(2)^S`. Enumerate it directly, convert membership in that local subgroup into linear equations, intersect all support constraints, and solve by Gaussian elimination. Hence a basis of `H(F)` is polynomial-time computable.

## Safe quotient theorem

Let `r=dim H(F)>0`, and row-reduce a basis so the pivot coordinates form an identity matrix. If `alpha` is a satisfying assignment and its pivot vector is `b`, xor `alpha` by the unique group element whose pivot vector is also `b`. Formula invariance implies the new assignment is still a model, and all pivot variables are now zero.

Therefore

`SAT(F) iff SAT(F[pivots=0])`.

This is an exact polynomial safe assignment of `r` variables at once, with no SAT oracle and no branching.

## Exact-width-3 rigid obstruction

For distinct variables `x_i,y,z`, define `Uplus(x_i;y,z)` as the four clauses

`(x_i OR y OR z)`, `(x_i OR y OR not z)`, `(x_i OR not y OR z)`, `(x_i OR not y OR not z)`.

Their conjunction is exactly equivalent to the unit `x_i`, while all clauses have width exactly 3. On this support, translation symmetry may flip `y,z` but cannot flip `x_i`.

For `n>=4`, with indices modulo `n`, set

`F_n = UNION_i Uplus(x_i; x_{i+1}, x_{i+2})`.

Then `F_n` is equivalent to `AND_i x_i`, hence has one model, the all-1 assignment. Any nonzero sign-flip formula symmetry would produce a second model, so `H(F_n)={0}`.

For `n>=6`, add on the distinct nonconsecutive support `{x_1,x_3,x_5}` the analogous four-clause gadget `Uminus(x_1;x_3,x_5)` with `not x_1` as the leading literal. The resulting exact 3CNF forces both `x_1` and `not x_1`, hence is UNSAT. The original consecutive support constraints remain present and individually force every flip coordinate to zero, so the UNSAT family also has `H={0}`.

Thus the invariant is a genuine new exact polynomial safe-descent primitive, but not a universal one.

Firewalls:
- `NONTRIVIAL_SYMMETRY => CERTIFIED_SAFE_DESCENT`
- `TRIVIAL_SYMMETRY != SAT`
- `TRIVIAL_SYMMETRY != UNSAT`
- `PARTIAL_EXACT_DESCENT != UNIVERSAL_DESCENT`
- `P_VS_NP=OPEN`.
