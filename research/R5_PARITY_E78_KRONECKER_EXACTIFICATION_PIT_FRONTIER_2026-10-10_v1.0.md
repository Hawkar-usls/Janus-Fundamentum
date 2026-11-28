# R5 Parity — Kronecker exactification of E78 delta-sum composition

Date: 2026-10-10

Status:
PROVED SYMBOLIC EXACTIFICATION / DETERMINISTIC POLYNOMIAL EVALUATION OPEN

P_VS_NP = OPEN.

## 0. Repository anti-loop

Checked current main against the PR #515 base.

Base of PR #515:
  e7d6790d533f9acd3c4fe7f2439542dfbfa3361c

Current main:
  18c2a9a5dca8bf57d422a1397758027dd9a2c0ed

The only main-side delta is:
  registry/PHYSARIUS_INTERNAL_REPO_HRAIN_LIVE_v1.json

Therefore there is no new mathematical overlap with this parity/delta-sum route.

Existing relevant route:
* E74 blocks local support-preserving Pfaffian/matchgate compilation.
* E78 proves exact equality gluing = iterated delta-sum and gives a conditional
  randomized polynomial meta-solver from represented linear-delta modules.
* E79 reconstructs every frozen binary-even module from a seed + pair flips and
  identifies universal binary-delta constructibility as an open theorem.

This note does not restart those routes.

## 1. Where E78 randomization enters

Koana-Wahlstrom Lemma 16 constructs a delta-sum representation by adding, for
each ground element v, a constant-size triangle gadget with fresh variables

  y_{v,1}, y_{v,2}, y_{v,3}.

The resulting relevant principal Pfaffians are multivariate polynomials in
these fresh variables. Random field evaluation plus Schwartz-Zippel yields the
epsilon-approximate numeric representation used in E78.

Over the rational-function field F(Y), before evaluation, this construction is
exact: a target feasible set is present iff its principal Pfaffian polynomial
is not identically zero.

## 2. Multilinearity

Each fresh y-variable occurs on a single skew edge of the triangle gadget.
A Pfaffian monomial is a perfect matching, so that edge can be used at most
once.

Hence every relevant Pfaffian polynomial is multilinear in all fresh
variables.

## 3. Kronecker substitution lemma

Enumerate all fresh variables as y_0,...,y_{m-1} and substitute

  y_j := t^(2^j).

For any multilinear monomial

  prod_{j in S} y_j

the image is

  t^(sum_{j in S} 2^j).

Binary expansion is unique, so distinct multilinear monomials map to distinct
powers of t.

Therefore the substitution is injective on the vector space of multilinear
polynomials:

  P(Y) == 0
  iff
  P(t^(1), t^(2), t^(4), ..., t^(2^(m-1))) == 0.

Consequently every principal-Pfaffian zero/nonzero predicate of the symbolic
E78 construction is preserved exactly.

Thus one E78 delta-sum can be represented deterministically and exactly over
F(t) by a skew matrix whose fresh entries are succinct monomials t^(2^j).

No Schwartz-Zippel error is needed at the semantic level.

## 4. Why this is not yet a polynomial algorithm

The maximum exponent is exponential, although its binary encoding has only
O(m) bits.

After contractions/pivots or repeated compositions, matrix entries can become
rational functions with exponentially many dense terms if expanded.

They can be retained as polynomial-size arithmetic circuits, but then exact
rank/Pfaffian testing requires deterministic polynomial identity testing for
the resulting structured circuits.

Equivalently, the old random-evaluation gap has been moved to:

  STRUCTURED E78 PFAFFIAN PIT

Input:
  exact binary-even module representations plus the E78 triangle-gluing
  construction with Kronecker monomial tags.

Task:
  decide deterministically in polynomial bit complexity whether the required
  principal Pfaffian is identically zero, and recover a witness when nonzero.

A generic claim that "powers of two derandomize E78 in polynomial time" is
therefore NOT justified.

## 5. Relation to LowestParityExponent

The previous superincreasing-isolation checkpoint used powers of two on SAT
variables and reduced SAT to LowestParityExponent of the global solution
polynomial.

The present result is narrower and better aligned with the existing repo:

* powers of two are useful as an injective symbolic substitution;
* they remove evaluation collisions exactly;
* they do not by themselves provide an efficient zero-test.

Therefore the active algebraic target should be structured Pfaffian PIT on the
E78/E79 composition, not a generic valuation algorithm for the full SAT
generating polynomial.

## 6. Claim boundary

E78_KRONECKER_SYMBOLIC_EXACTIFICATION = PROVED.
SCHWARTZ_ZIPPEL_SEMANTIC_NECESSITY = REMOVED.
DETERMINISTIC_STRUCTURED_PFAFFIAN_PIT = OPEN.
UNIVERSAL_BINARY_DELTA_CONSTRUCTIBILITY = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
