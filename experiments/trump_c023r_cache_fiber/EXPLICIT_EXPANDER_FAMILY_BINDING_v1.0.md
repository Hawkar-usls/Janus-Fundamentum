# C022/C023R explicit expander-family binding v1.0

Authority: `SOURCE_BOUND_THEOREM_INPUT_BINDING__NO_PROMOTION_OF_C022_OR_C023R`
Method: `EXACT_ALGEBRA_ONLY__NO_HEURISTICS`

## Frozen finite field and constants

Use `F4 = F2[a]/(a^2+a+1)`. Fix

`epsilon = a`, `b1 = 0`, `b2 = 1`.

Then `f(y)=y^2+y+a` is irreducible over `F4`. Let `alpha` be its root in `F16`.
Exact enumeration in the 16-element field verifies that both `alpha` and `alpha+1` are non-cubes, satisfying the Batra–Saxena–Shringi/Morgenstern irreducibility premise.

For every integer `t>=0`, define

`d_t = 2*3^t`,
`g_t(x) = x^(2*3^t) + x^(3^t) + a`,
`K_t = F4[x]/(g_t)`.

By the cited irreducibility lemma, every `g_t` is irreducible of even degree `d_t`.
## Frozen Cayley graph family

Let `L_t = x^(3^t) in K_t`, so `L_t^2 + L_t + a = 0`.
The five exact `(gamma,delta)` solutions in `F4^2` of

`gamma^2 + gamma*delta + a*delta^2 = 1`

are, using the same `a` notation:

`(0,a), (1,0), (1,a+1), (a,a), (a,a+1)`.

For each pair define the Morgenstern generator

`Gamma(gamma,delta) = [[1, gamma+delta*L_t], [(gamma+delta*L_t+delta)*x, 1]]`

as in Theorem 3.1 (Morgenstern 1994, Theorem 5.13 as restated by Batra–Saxena–Shringi).

Freeze

`G_t = Cay(PSL(2,K_t), Gamma_t)`.

The source theorem states that this is a `q+1=5` regular Ramanujan graph. The paper's graph convention is undirected, regular and connected.
## Generator distinctness / simple-edge compatibility

The five `(gamma,delta)` pairs are distinct. If two projective generator matrices were equal, their top-left entries `1` force the projective scalar to equal `1`. Equality of the top-right entries then gives

`gamma_i + delta_i*L_t = gamma_j + delta_j*L_t`.

Since `L_t` has degree 2 over `F4` (`L_t^2+L_t+a=0` is irreducible), `{1,L_t}` is linearly independent over `F4`, hence `gamma_i=gamma_j` and `delta_i=delta_j`. Thus the generators are pairwise distinct in `PSL(2,K_t)`.

No generator is the identity: `gamma+delta*L_t=0` would force `gamma=delta=0`, which is not one of the five solutions. Therefore for every group element `h`, the neighbors `Gamma_i h` are pairwise distinct and different from `h`. The Cayley graph is compatible with the simple-edge representation expected by the historical MAJ3 generator.

## Exact spectral-to-edge-expansion derivation

Let `N_t=|V(G_t)|`. Since `G_t` is 5-regular Ramanujan,

`lambda_2 <= 2*sqrt(5-1)=4`,

so the Laplacian spectral gap is at least `1`.
For any vertex set `S`, set `x=1_S-(|S|/N_t)1`. Then

`x^T L x = |E(S,V\S)|`

and `||x||^2=|S|(N_t-|S|)/N_t`. Rayleigh's inequality yields

`|E(S,V\S)| >= (5-lambda_2)*|S|(N_t-|S|)/N_t`.

For `N_t/3 <= |S| <= 2N_t/3`, this is at least `2N_t/9`. Hence the Ben-Sasson–Wigderson expansion parameter obeys

`e(G_t) >= 2N_t/9`.
## Exact Tseitin-width consequence

Ben-Sasson–Wigderson Theorem 4.4 states for connected `G` and odd-weight charge `f`:

`w(tau(G,f) |- 0) >= e(G)`.

Therefore, for every frozen `G_t` and every odd-weight charge vector,

`w(tau(G_t,f) |- 0) >= 2N_t/9`.

Since `G_t` is 5-regular, its edge-variable count is `M_t=5N_t/2`, so equivalently

`w >= (4/45) M_t`.

Thus the historical C022 premise `base Resolution width = Omega(number of base variables)` is bound to one explicit infinite graph family with an explicit constant.

## Encoding-length normalization

The base degree is fixed at five, so the Tseitin CNF has `Theta(N_t)` variables and clauses. MAJ3 lifting replaces each edge variable by three variables. Each lifted vertex relation uses five MAJ3 blocks, hence 15 Boolean gadget coordinates; its complete truth-table CNF has at most `2^15` clauses, a constant independent of `t`. Therefore the lifted encoding length is `Theta(N_t)`.

## What this closes and what it does not

Closed historical input obligation:

`C022_EXPLICIT_CONSTANT_DEGREE_EXPANDER_FAMILY_AND_LINEAR_WIDTH_BINDING`.

Still not promoted:

- the C022 H135 universal trace-to-Resolution induction remains `FORMALIZING` pending its own independent mathematical review;
- the 2026 lifting theorem hypotheses remain independently auditable;
- C023 exact-caching lower bound remains OPEN;
- C023R still requires a theorem about reachable representatives per MAJ3-stifling/cycle-space coset.

## Sources

- Morgenstern 1994, Theorem 5.13, as source-bound through Batra–Saxena–Shringi Theorem 3.1 and Lemmas 3.2–3.3.
- Ben-Sasson–Wigderson, Theorem 4.4: Tseitin Resolution width is at least the medium-cut expansion of the graph.

## Firewalls

`EXPLICIT_FAMILY_BINDING != C022_PROVED`.
`LINEAR_BASE_WIDTH != CACHED_POLICY_LOWER_BOUND`.
`C023R != P_NE_NP`.
`P_VS_NP = OPEN`.

## Frozen deterministic encoding / labeling contract

The graph theorem alone does not determine Policy-0A, because its branch tie-break depends on variable identifiers. Freeze the following encoding before any reachability theorem.

1. Encode `F4` coefficients by `0<1<a<a+1`, i.e. integer codes `0,1,2,3`.
2. Encode `K_t=F4[x]/(g_t)` elements by their unique degree-`<d_t` coefficient vector, lexicographically by the above F4 codes.
3. In characteristic two, the center of `SL(2,K_t)` is trivial (`lambda^2=1` has only `lambda=1`), hence `PSL(2,K_t)=SL(2,K_t)`. Encode a vertex by its 2x2 determinant-one matrix tuple `(A,B,C,D)` and rank all such tuples in lexicographic K_t order as vertex IDs `0,...,N_t-1`.
4. Order the five generators by the frozen encoded `(gamma,delta)` list:
   `[(0,a),(1,0),(1,a+1),(a,a),(a,a+1)]`.
5. Generate every Cayley adjacency `h -> Gamma_i h`, convert it to the undirected pair `(min(id(h),id(Gamma_i h)), max(...))`, remove the duplicate traversal copy, and lexicographically sort the resulting edge list.
6. Use the historical MAJ3 lifting convention: the j-th sorted edge receives gadget variables `(3j+1,3j+2,3j+3)` in that coordinate order.
7. Freeze the odd Tseitin charge to `charge(vertex 0)=1` and `charge(v)=0` for every other vertex.

This contract fixes the exact CNF bytes modulo the already frozen canonical clause ordering. No graph relabeling, generator permutation, charge relocation, or gadget-coordinate permutation is permitted after the reachability theorem is preregistered.