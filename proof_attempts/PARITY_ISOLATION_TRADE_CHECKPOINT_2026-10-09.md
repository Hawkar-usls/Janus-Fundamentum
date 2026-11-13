# Parity / Isolation / Trade checkpoint — 2026-10-09

TARGET_REPO = Hawkar-usls/Janus-Fundamentum
PREDECESSOR_MAIN_SHA = e7d6790d533f9acd3c4fe7f2439542dfbfa3361c
STATUS_CLASS = PROOF_ATTEMPT_CHECKPOINT
P_VS_NP = OPEN

## Claim ceiling

This checkpoint does **not** establish P = NP and does **not** establish a deterministic polynomial-time solver for the square+cubic+linear Positive Exact-One target.

It records a sequence of local proofs and one explicit parsimonious equality gadget that sharpen the weighted-parity / isolation route. Any claim that depends on a full deterministic isolating-family theorem remains OPEN.

## 1. Parsimonious linear EQUAL3 gadget

Boundary terminals: a,b,c.
Internal variables: u,v,x1,x2,x3,x4,x5,x6,x7,x8.

Exact-One clauses:

1. (u,x1,x2)
2. (u,x3,x7)
3. (u,x6,x8)
4. (v,x6,x7)
5. (v,x2,x3)
6. (v,x1,x8)
7. (a,x3,x4)
8. (a,x2,x5)
9. (b,x1,x4)
10. (b,x5,x8)
11. (c,x5,x6)
12. (c,x4,x7)

### Degree / linearity certificate

- deg(a)=deg(b)=deg(c)=2.
- deg(u)=deg(v)=deg(x1)=...=deg(x8)=3.
- Any two clauses intersect in at most one variable.

Thus the gadget is 3-uniform, linear, terminal-degree (2,2,2), and internally cubic.

### Exact support / parsimony proof

Solving the 12 Exact-One equations yields:

- x1=x2=x3=x6=x7=x8,
- x4=x5,
- u=v=1-2x8,
- a=b=c=1-x5-x8.

Booleanity of u forces x8=0. Hence u=v=1 and x1=x2=x3=x6=x7=x8=0.
Then x5 is the only free Boolean variable, with x4=x5 and a=b=c=1-x5.

Therefore the gadget has exactly two satisfying assignments:

- boundary 111, with x4=x5=0;
- boundary 000, with x4=x5=1.

All other boundary states have zero extensions.

Hence the boundary signature is exactly

[1,0,0,0,0,0,0,1]

and both allowed boundary states have exactly one extension.

CLAIM = PARSIMONIOUS_CUBIC_LINEAR_EQUAL3_GADGET
EVIDENCE = SYMBOLIC_PROOF
STATUS = PROVED_LOCALLY

## 2. Lower-bound notes for smaller direct cubic EQUAL3 gadgets

The following were derived during the search and should be independently replayed before promotion beyond this checkpoint:

- m<=4: impossible; m=4 exhaustive direct search found no target signature.
- m=5: exhaustive direct search found no target signature.
- m=6: structural obstruction from the number of internal-only clauses at boundary 111.
- m=7: parity obstruction from the forced 2-regular graph on zero-internal vertices.
- m=8,9: ruled out by the necessary condition 3|S|=m-4 at boundary 111, hence m ≡ 1 (mod 3) is necessary.

These are retained as PROOF-ATTEMPT / REPLAY-REQUIRED notes until a repository verifier is added.

## 3. Parsimonious occurrence-splitting bridge

Given a cubic monotone Positive 1-in-3 instance, replace the three occurrences of every source variable by three clones and constrain the three clones with the gadget above.

Each clone then has degree:

1 source-clause incidence + 2 equality-gadget incidences = 3.

Every new internal gadget variable has degree 3.
Every clause has size 3.
If source clauses are occurrence-split, distinct gadgets are disjoint, and the equality gadget is linear, the resulting instance is linear.

Since every source variable contributes three clones plus ten internal variables, and each source clause count equals the source variable count in a cubic 3-uniform source, the transformed instance is square by incidence counting.

Most importantly, the gadget is parsimonious, so the entire reduction preserves the exact number of satisfying assignments.

CLAIM = PARSIMONIOUS_CUBIC_SQUARE_LINEAR_BRIDGE
STATUS = PROOF_ATTEMPT
REMAINING_EXTERNAL_DEPENDENCY = exact source theorem / reduction chain must be pinned to a stable bibliographic object before admission.

## 4. Isolation compatibility

Any parsimonious reduction preserves the distinction:

- zero witnesses -> zero witnesses;
- one witness -> one witness.

Therefore any unique-witness instance produced by an upstream isolation step remains unique after the parsimonious bridge.

This proves compatibility with isolation; it does **not** derandomize isolation.

CLAIM = ISOLATION_COMPATIBILITY
STATUS = PROVED_CONDITIONALLY_ON_PARSIMONIOUS_SOURCE_CHAIN

## 5. Hypergraph perfect-matching reformulation

For a square, cubic, linear Positive Exact-One instance, interpret clauses as hypergraph vertices and variables as 3-uniform hyperedges incident to the three clauses containing that variable.

A satisfying assignment is exactly a perfect matching of this 3-uniform, 3-regular, linear hypergraph.

This is the preferred language for the current parity/isolation route.

## 6. Trade structure lemma

Let M,N be perfect matchings. For every clause affected by M Δ N, connect the unique edge from M\N covering the clause to the unique edge from N\M covering the clause.

After suppressing clause-nodes, every connected difference component is a simple connected cubic bipartite graph:

- bipartition = (M\N) versus (N\M);
- cubicity = each selected hyperedge covers three clauses;
- simplicity = linearity forbids two variables from sharing two clauses.

Each connected component can be flipped independently, producing another perfect matching.

CLAIM = CUBIC_BIPARTITE_TRADE_COMPONENT_LEMMA
STATUS = PROVED_LOCALLY

## 7. Minimum-face circulation consequence

Fix a weight vector w and let M,N be distinct minimum-weight perfect matchings.

Decompose M Δ N into connected trade components C1,...,Cr.

The total weight change from M to N is zero.
If some component had negative change, flipping only that component would produce a matching lighter than M, contradicting minimality.
Likewise no component can have positive change because the total change is zero and all component changes are nonnegative.

Therefore each connected trade component has zero circulation individually.

CLAIM = MINIMUM_FACE_ZERO_CIRCULATION_PER_COMPONENT
STATUS = PROVED_LOCALLY

## 8. Bounded hashing lemma for an explicit polynomial trade set

Let D be an explicitly known family of L=n^{O(1)} nonzero trade vectors d in {-1,0,1}^n.

Choose a prime p>(n-1)L and p>2.
For t in F_p define

w_t(i) = t^i mod p.

For each nonzero trade d, define

f_d(t)=sum_i d_i t^i.

Because p>2 and the coefficients are in {-1,0,1}, f_d is a nonzero polynomial of degree < n, hence has at most n-1 roots in F_p.

The union of roots across all d in D has size < p. Therefore some t avoids every root simultaneously, and

< w_t , d > != 0 (mod p)

for every d in D.

All weights lie in [0,p-1]=n^{O(1)}.

CLAIM = BOUNDED_HASH_FOR_EXPLICIT_POLY_TRADE_FAMILY
STATUS = PROVED_LOCALLY

## 9. Kernel / trade correspondence

For two Exact-One solutions x,y,

k = x XOR y

lies in ker_{F2}(A).

In every row of A, the support of k has even size; because each row has size 3, the row intersection is 0 or 2.

For solution differences, the active support components inherit the same bipartition x\y versus y\x as the perfect-matching trade graph.

Thus the dangerous kernel words for the parity route and the hypergraph trade objects are two views of the same difference structure.

CLAIM = KERNEL_TRADE_CORRESPONDENCE
STATUS = PROVED_LOCALLY

## 10. Regular/MFMC shortcut is not automatically available

The structural class "square + row-degree 3 + column-degree 3 + linear" contains the 7x7 incidence matrix of the Fano plane.

Therefore the whole matrix class cannot simply be declared regular/MFMC.

Any import of regular-matroid near-circuit counting machinery must first prove an additional property of the **matching-trade subset**, not of the ambient binary matroid class.

STATUS = OBSTRUCTION_RECORDED

## 11. Girth-doubling mechanism

Suppose the current minimum-matching face has minimum nontrivial trade size g.
If a new bounded weight vector has nonzero circulation on every relevant trade of size <=2g, then in the refined minimum face any surviving difference component must have size >2g.

Therefore the minimum trade size more than doubles per successful refinement round.

This gives a natural O(log n)-round isolation framework **provided** the required relevant trade sets can be handled at each round.

CLAIM = TRADE_GIRTH_DOUBLING
STATUS = PROVED_CONDITIONALLY_ON_SHORT_TRADE_HITTING

## 12. Current bottleneck

The current sufficient theorem target is:

SCL3PM POLYNOMIAL ISOLATING FAMILY THEOREM

For every square, 3-uniform, 3-regular, linear hypergraph H, construct in polynomial time a family

W(H)={w^(1),...,w^(q)}

with q=n^{O(1)} and each edge weight n^{O(1)}, such that whenever H has a perfect matching, at least one weighting in W(H) has a unique minimum-weight perfect matching.

Why this would be sufficient:

- each weighting has only polynomially many possible total weights;
- exact-weight parity queries can enumerate those totals;
- for an isolating weighting, the unique minimum-weight level has odd parity;
- combined with a polynomial-time parity solver for the target, this would yield a deterministic polynomial-time SAT decision procedure through the parsimonious bridge.

THIS THEOREM IS NOT PROVED HERE.

## 13. Next admissible research target

TRADE_SMOOTH_COUNT_OR_SEPARATOR_DICHOTOMY:

Attempt to prove that either

1. the relevant near-minimum cubic-bipartite trades are polynomially enumerable / polynomially bounded in number, or
2. a large family of such trades forces an explicit small-separator or product decomposition that can be solved independently and recombined.

This is currently the narrowest deterministic-isolation bottleneck identified by this checkpoint.

## Evidence taxonomy

PROVED_LOCALLY:
- explicit m=10 parsimonious cubic-linear EQUAL3 gadget;
- cubic-bipartite trade component structure;
- independent component flip;
- zero circulation of each component inside a minimum-weight face;
- bounded polynomial hashing for any explicit polynomial-size trade family;
- kernel/trade correspondence.

REPLAY_REQUIRED:
- exhaustive small-m direct gadget search counts and all claimed minimality bounds not backed by a committed verifier yet.

OPEN:
- polynomial-time parity solver for the target;
- polynomial-size bounded isolating family;
- trade smooth-count / separator dichotomy;
- deterministic oddification;
- P vs NP.

## Strongest statement not established

P_VS_NP = OPEN.
No universal polynomial-time SAT solver is established.
No deterministic polynomial-time isolation theorem is established.
