# JANUS TRUMP R50G25M — semantic binary-cover no-go result

## Sealed execution

GitHub Actions run `34036862384` on head `ef48ba0c112a5b3a6108b647c595e748f1c63aaf` completed **SUCCESS**.

The exact frozen-domain verdict is:

`EXPLICIT_NO_GO_FOR_SEMANTICS_PRESERVING_EXISTING_VARIABLE_BINARY_COVER`

## Counts

All `1212` frozen target states are SAT under the exact <=6-variable validation oracle.

- semantics-preserving existing-variable binary cover exists: `516`;
- explicit no-go target states: `696`;
- semantic equivalence failures in the oracle/checking code: `0`.

Among the 696 first unsupported requirements:

- BCE: `600`;
- BVE: `96`.

For the 516 targets where a semantics-preserving binary cover exists, the downstream micro scheduler reaches:

- `DIRECT_EMPTY_CNF`: `516`;
- residuals: `0`.

Admissible-cover size histogram on those 516 targets:

- size 2: `25`;
- size 3: `153`;
- size 4: `228`;
- size 5: `110`.

## Smallest recorded no-go witness

State hash:

`6cf77b7f1acf5a0ca16edf24adb9ec936557a0418a00368ac2b494946c8fdd1e`

Target CLV:

`(9,25,6)`

Exact target model count:

`14`

Current BCE/BVE requirement count:

`12`

Existing-variable binary clauses entailed by the target and therefore admissible as semantics-preserving conjuncts:

`6`

First unsupported requirement:

- kind: `BCE`;
- clause: `[2,3,5]`;
- blocking literal: `5`;
- opposite-parent count: `1`.

All six admissible existing-variable binary clauses were checked and none pays this BCE incidence requirement.

Because `T |= (C1 AND ... AND Ck)` implies `T |= Ci` for every conjunct, the absence of any entailed binary support for this requirement proves that **no conjunction of existing-variable binary clauses equivalent to this T can cover that requirement**.

## Scope firewall

This no-go is exact only for the strategy:

`add semantics-preserving binary clauses over variables already present in T`.

It does **not** exclude:

- extension variables;
- non-additive equivalence-preserving transformations;
- resolution/RUP-derived clauses of larger width;
- definitional encodings with reconstruction;
- other collapse doors that do not try to pay BCE/BVE incidence debt by binary strengthening.

It is not a universal 3CNF impossibility theorem.

`SAT_IN_P = NOT_PROVED`

`P_VS_NP = OPEN`

`TRUMP_finished = false`

## Next gate

`R50G25N_ALTERNATE_NONADDITIVE_OR_DERIVED_CLAUSE_COLLAPSE_DOOR`

The next attack should use the smallest no-go witness first. It should ask whether the unsupported BCE debt can be neutralized by a semantics-preserving **derived** operation rather than by arbitrary strengthening. Priority order:

1. RUP/resolution-derived clauses, including width > 2, with proof certificates;
2. equivalence-preserving local rewrites / variable elimination with reconstruction;
3. extension-variable encoding only if the first two fail.

No family expansion is needed to perform this forensic attack.
