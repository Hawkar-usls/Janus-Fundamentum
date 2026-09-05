# JANUS TRUMP R50G14 — V7 hub-cycle ancestry bifurcation

## Scope

Assume a W<=4 source F on exactly seven variables and a pivot v whose exact R47J candidate is nonterminal and unsafe. R50G12/R50G13 already force the final normalization state H_v to satisfy

- Vars(H_v) = Vars(F) \\ {v}, hence |Vars(H_v)| = 6;
- max-width(H_v) = 5;
- a canonical width-5 clause C_v has a unique external variable h(v) in H_v.

This note classifies how C_v can have been created. It does **not** prove that a V7 hub cycle is impossible.

## 1. No variable-eliminating normalization step can occur after the initial DP

Exact DP on v introduces no fresh variables. Since the final state contains all six variables other than v, the forced DP state must already contain all six of them. Any later R33 unit propagation, pure-literal autarky, or BVE removes at least one current variable and no frozen normalization rule can reintroduce it. Therefore none of those rules can occur on an unsafe V7 trace.

Subsumption and BCE only delete clauses. RUP replaces a clause by a proper subclause. Neither creates a wider clause. Thus after the initial DP there is no width-creating rule.

## 2. Every final width-5 clause has an initial-DP ancestor

Let C be a width-5 clause of H_v. Trace it backward through the normalization sequence. Clause deletion cannot create C. RUP can only replace an ancestor A by a proper subclause. With no later BVE, C must therefore be contained in some clause A of the initial forced DP formula.

The source is W<=4, so an untouched source clause has width at most four. Hence any such ancestor A with |A|>=5 must be a cross-pivot DP resolvent.

Each parent has width at most four. After deleting v/-v from the parents, their residuals have size at most three each, so every non-tautological cross-pivot resolvent has width at most six. Since |C|=5:

\[
5 \le |A| \le 6.
\]

Only two ancestry types remain.

### DIRECT5

If |A|=5, then C=A because C is a five-literal subclause of a five-literal clause. The unique external hub h(v) is absent from this DP resolvent. Its parent geometry is one of the already closed R50G11 width-5 shapes: 4x3 or 3x4 with disjoint residuals, or 4x4 with exactly one residual overlap.

### RUP6_DROP_HUB

If |A|=6, then A uses all six variables remaining after v is eliminated. Since C has width five and H_v retains all six formula variables, A\\C consists of exactly one literal whose variable is the unique external hub h(v). The only W4 parent geometry capable of producing width six is 4x4 with disjoint three-literal residuals.

Because no post-DP rule other than RUP can replace a clause by a proper subclause, the A -> C ancestry contains a certified RUP removal of that hub literal.

Thus every V7 unsafe hub edge carries one of two exact source certificates:

\[
\boxed{\text{DIRECT5} \quad\text{or}\quad \text{RUP6\_DROP\_HUB}.}
\]

## 3. Hub-cycle bifurcation

For a V7 all-doors-closed obstruction, R50G13 gives a total no-self-loop hub map h on seven variables and therefore at least one directed cycle. Label every cycle edge by the ancestry type above. Then exactly one of two cases holds:

1. **ALL_DIRECT5_CYCLE** — every edge is realized already by a width-5 source DP resolvent omitting the next hub;
2. **RUP_BEARING_CYCLE** — at least one edge contains an exact width-6 4x4-disjoint resolvent and a replayable RUP certificate deleting the next hub literal.

This is the next safe reduction. The follow-up attack should treat the two cases separately rather than search arbitrary V7 formulas.

## Firewall

R50G14 does not establish V7 hub-cycle impossibility, does not eliminate V7 immediate-BVE, and does not change U_mu, SAT-in-P, or P-vs-NP status.
