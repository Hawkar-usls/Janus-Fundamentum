# C025 unified adversarial test plan

The combined engine must be attacked as a single organism, not as isolated methods.

## Tier 0: correctness / refusal

- trivial SAT / UNSAT;
- failed-literal-UP forced move;
- SAT core with no cheap forced move must not be called UNSAT;
- UNSAT core with no implemented proof must be `OPEN`, not guessed;
- no candidate extension may advance state without a verifier-accepted certificate.

## Tier 1: method-composition regressions

- residual normalization followed by certified question;
- certificate-portfolio closure followed by residual merge;
- extension introduction followed by recompression and independent progress replay;
- witness recovery through a chain containing both merges and extension macros;
- corrupted macro/proof/root fingerprint rejection.

## Tier 2: adversarial structural families

- blocked equality under hostile and interleaved orders;
- pigeonhole;
- Tseitin;
- pebbling;
- random hard UNSAT;
- candidate-multiplicity explosion;
- large-root-support ER3 macros;
- cheap verification / expensive discovery controls.

## Required accounting

Every case records proposal work, discovery work, verification work, state bytes, proof bytes, extension bytes/count, residual states, question count, recompression work, and witness recovery work.

A finite PASS never promotes a universal polynomial claim.
