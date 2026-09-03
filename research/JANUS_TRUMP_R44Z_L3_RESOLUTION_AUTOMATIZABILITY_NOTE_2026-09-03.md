# JANUS TRUMP R44Z — direct L3 barrier: Resolution proof search

## Target obligation

`L3_POLYNOMIAL_DISCOVERY_AND_LOCAL_WORK`

The question is not whether a short proof exists. The question is whether one fixed deterministic algorithm can **find** the exact proof/decomposition in polynomial total work.

## Known theorem

Atserias and Müller proved that automating Resolution is NP-hard: finding a Resolution refutation only polynomially longer than a shortest one is NP-hard. In particular, Resolution is not polynomial-time automatizable unless `P = NP`.

Reference: Albert Atserias and Moritz Müller, *Automating Resolution is NP-Hard*, Journal of the ACM 67(5), Article 31 (2020), DOI `10.1145/3409472`; preliminary version FOCS 2019 / arXiv:1904.02991.

Thus the implication

`POLYNOMIAL-SIZE RESOLUTION REFUTATION EXISTS => POLYNOMIAL-TIME RESOLUTION PROOF SEARCH`

is not an admissible TRUMP lemma. Proving the right-hand side in general would already imply `P=NP`.

## Exact consequence for TRUMP

The Resolution-only version of L3 is **not an easier missing implementation detail**. It is already a final-front complexity problem.

This preserves the earlier R43 distinction:

`RESOLUTION PROOF SIZE != RESOLUTION PROOF DISCOVERY`.

It also strengthens the R44Y firewall:

`SHORT CERTIFICATE EXISTENCE != DETERMINISTIC POLYNOMIAL CERTIFICATE DISCOVERY`.

## Transfer firewall

This theorem is about Resolution. It must not be silently exported to another proof system merely because that system p-simulates Resolution or is polynomially equivalent in proof size.

To transfer an automatizability barrier one needs an **effective proof-search preserving simulation/reduction**, with the transformation and its complexity explicitly proved. Therefore:

`P_SIMULATION != SEARCH_SIMULATION`.

In particular, TRUMP must treat Extended Resolution / Extended Frege as a separate L3 theorem front rather than claiming that the Resolution result settles them automatically.

## Additional support

Mertz, Pitassi and Wei, *Short Proofs Are Hard to Find*, ICALP 2019, DOI `10.4230/LIPIcs.ICALP.2019.84`, gives further hardness/non-automatizability results for Resolution and related systems under standard complexity assumptions. These are supporting context; the Atserias–Müller NP-hardness theorem is sufficient for the R44Z route barrier.

## Scientific boundary

R44Z blocks one proof-discovery architecture. It does **not** prove that all exact proof languages are non-automatizable and does not prove `P != NP`.

`P_VS_NP = OPEN`.
