# TRUMP Journal Entry — Explicit q=4 Morgenstern Family Binding

Date: 2026-09-14
Authority: `SOURCE_BOUND_THEOREM_INPUT_BINDING__NO_SCIENTIFIC_PROMOTION`

## Purpose

Close the historical C022 dangling input obligation "freeze one constant-degree expander family and its linear Resolution-width premise" without changing the historical FORMALIZING status of C022.

## Frozen family

Use `F4 = F2[a]/(a^2+a+1)` and freeze `epsilon=a`, `b1=0`, `b2=1`.
For every `t>=0` define

`d_t=2*3^t`,
`g_t(x)=x^(2*3^t)+x^(3^t)+a`,
`K_t=F4[x]/(g_t)`.

Batra–Saxena–Shringi Lemmas 3.2–3.3, specialized to q=4, give irreducibility of all `g_t` from the finite non-cube premise. An exact F4/F16 checker verifies that premise for the frozen constants.

The five generator pairs solving

`gamma^2 + gamma*delta + a*delta^2 = 1`

are

`(0,a), (1,0), (1,a+1), (a,a), (a,a+1)`.

With the Morgenstern matrices from Theorem 5.13 / Batra–Saxena–Shringi Theorem 3.1, freeze

`G_t = Cay(PSL(2,K_t), Gamma_t)`.

The cited theorem gives a connected 5-regular Ramanujan graph family.

## Graph-model compatibility

The five generators are pairwise distinct projective matrices: equality would force projective scalar 1 from the top-left entry, then linear independence of `{1,L_t}` over F4 forces identical `(gamma,delta)`. None is identity. Hence every group vertex has five distinct non-loop neighbors, matching the historical simple-edge MAJ3 representation.

## Linear expansion and width

Ramanujan gives `lambda_2<=2*sqrt(4)=4` for degree 5, hence Laplacian gap at least 1. For any medium set `N/3<=|S|<=2N/3`, Rayleigh gives

`|E(S,V\S)| >= |S|(N-|S|)/N >= 2N/9`.

Therefore Ben-Sasson–Wigderson expansion satisfies `e(G_t)>=2N_t/9`. Their Theorem 4.4 gives for odd-weight Tseitin charge:

`w(tau(G_t,f) |- 0) >= 2N_t/9`.

Since the 5-regular graph has `M_t=5N_t/2` edge variables,

`w >= (4/45) M_t`.

The base C022 width premise is therefore source-bound with an explicit linear constant on one explicit infinite family.

## Encoding normalization

Base Tseitin size is Theta(N_t). MAJ3 lifting gives 3 variables per edge; every degree-5 vertex relation has 15 gadget coordinates, so complete truth-table CNF contributes at most 2^15 clauses per vertex. Lifted input length remains Theta(N_t).

## Reproducibility

Diagnostic branch: `research/trump-c023r-maj3-cache-fiber-invariant-diagnostic-2026-09-14`
Binding commit: `be82a2bf83d933e62ae70a5dcc4fc392121ff5b1`

SHA-256:
- family binding: `86a3592614205310adda2c03a467bb40641e4fc2338eb1b7d62d3bbdc8680116`
- finite-field checker: `2704b68bf6af9f06153f5199510e46beda70923578697535d4be60b1fd9c487b`
- finite constant-check result: `c4c4e8fdb29c23229567a691c628b2ce537fdab33a7aca121f8070e62cb429d9`

## Authority effect

Closed: `C022_EXPLICIT_CONSTANT_DEGREE_EXPANDER_FAMILY_AND_LINEAR_WIDTH_BINDING`.

Not closed:
- H135 universal Policy-0T trace-to-Resolution review;
- independent audit of the registered 2026 lifting-theorem premise;
- C023 cached-policy lower bound;
- C023R reachable-representatives-per-coset theorem.

No claim about P vs NP changes.