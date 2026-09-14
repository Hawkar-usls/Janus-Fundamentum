# TRUMP Journal Entry — C023R MAJ3 Cache-Fiber Diagnostic Result

Date: 2026-09-14
Authority: `DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION`

## Branch / commits

Branch: `research/trump-c023r-maj3-cache-fiber-invariant-diagnostic-2026-09-14`

- prereg freeze: `00e0f7d5a4f3e57a1c2f057012a9bc0a03fe1794`
- runner freeze: `925edd62e6eeb8907f65ff35883badaf0e230a58`
- result + algebraic note: `6b969d50d61c314f137351913bab22bd78bd7160`

Hashes:
- prereg SHA-256: `10d35eade5cbfaa625496d6b1de50b15296893cbdc7482ac08271f50b532e752`
- runner SHA-256: `a7cdae67240e590ffb56584828f916b431e6632e18e0f66fc44c03f91f19bfaf`
- result SHA-256: `1d4da1dae5c1e8fb7c0cbae7f261a6f66e9e192b2aa161928cfc9a218b1a0b3d`
- algebraic note SHA-256: `02bc7616a9c53267d0b80aa22998bb6104fb525802c3a62704db64ca5e3d7827`

## Frozen method

Strict rule: `ALGEBRA_ONLY__NO_HEURISTICS`.
Finite measurements are allowed only as exact identity checks / falsifiers. They may not select or justify an asymptotic law.

## Exact finite identities

On historical revealed MAJ3-lifted K4:

- cached calls: `4117`
- cached unique states: `2427`
- exact cache hits: `888`
- no-cache recursive calls: `15671`
- no-cache expanded states: `11620`
- exact DAG-path state occurrence sum: `11620`
- `m_max = 128`
- cached state-local cost: `785744`
- unfolded state-local cost: `1692243`
- frozen no-cache state-local cost: `1692243`

Thus both preregistered identities passed exactly:

`sum_R m(R) = no-cache expanded states`

and

`sum_R m(R)c(R) = frozen no-cache state-local work`

for the explicit ledger `expanded-state + Resolution attempts/additions + branch edges`.

## Algebraic obstruction discovered

The cache key is formed after exact restriction + exhaustive unit propagation and before local Resolution.

Exact truth-table CNF commutes with restriction.
For one MAJ3 block:

- one fixed `0` leaves AND of the other two bits;
- one fixed `1` leaves OR;
- two equal fixed bits force a constant output;
- two different fixed bits leave exactly the remaining bit;
- a fully assigned block has four internal assignments per fixed MAJ3 output.

For fully eliminated lifted edges `H`, fixed edge outputs `z` affect the remaining Tseitin parity constraints only through the mod-2 vertex syndrome `B_H z`.
Therefore equal syndromes are cosets of the graph cycle space:

`dim ker(B_H) = |E(H)| - |V(H)| + c(H)`.

For fixed remaining restrictions, the semantic restriction map can therefore have

`4^{|E(H)|} * 2^{beta(H)}`

complete internal assignments in one residual-syndrome preimage.

This is a semantic preimage-capacity theorem, not an execution-fiber lower bound: frozen deterministic Policy-0A may visit only a subset because MAJ3 can become stifled before all coordinates are branched.

## Consequence

The simple route

`residual injectivity -> subexponential cache fibers`

is blocked. MAJ3 + Tseitin cycle-space can erase linearly many history bits exactly.

The remaining theorem obligation is execution-specific:

> Bound the number of reachable deterministic Policy-0A contexts per MAJ3-stifling / cycle-space residual coset on one frozen infinite MAJ3-lifted expander-Tseitin family.

Only a proved `2^{o(n)}` bound (polynomial is stronger) would preserve the C022 exponential lower bound through caching.

## Recovered old blocker

C022 never froze one explicit infinite constant-degree expander family. Repository history still lists this as an unresolved gate. Therefore no asymptotic C023R theorem may be promoted until a concrete family and its linear Resolution-width premise are source-bound and frozen.

## Frontier effect

- C022 historical no-cache lower-bound chain: unchanged.
- C023 cached lower bound: still OPEN.
- C023R cache-fiber route: sharpened, but now blocked by `REACHABLE_REPRESENTATIVES_PER_COSET` plus explicit expander-family freeze.
- APMA unseen-invariant frontier: unchanged; C023R remains a revealed calibration/diagnostic line only.
- `SAT_IN_P = NOT_PROVED`.
- `P_VS_NP = OPEN`.
