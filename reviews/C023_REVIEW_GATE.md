# C023 review gate

Review H138-H140 separately.

## H138
- prove production Policy-0A and JANUS-FC_local certificate equivalence;
- check unit propagation, local Resolution order and budgets;
- check exact residual equality and completed-before-use cache targets;
- charge canonicalization, lookup, construction and replay.

## H139
- separate decisions from inherited unit consequences;
- specify the reusable reason language;
- state whether weakening, lemmas, restarts or variable extensions are allowed;
- prove polynomial reason extraction rather than post-hoc existence.

## H140
- verify the smart graph-tautology encoding and actual input length;
- prove robustness of the Formula-Caching lower bound under Policy-0A local Resolution;
- charge weakening/subsumption lookup work;
- keep exact Boolean caching distinct from clause-learning systems with polynomial graph-tautology proofs;
- alternatively prove a direct MAJ3 residual-DAG lower bound.

No C023 result resolves P versus NP or lower-bounds unrestricted SAT algorithms.
