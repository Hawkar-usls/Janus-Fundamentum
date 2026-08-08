# Reproducing the A3 ternary-DP result

## Authority

Start from exact evidence commit:

`5ee79fc82613f24e621595afa0119312a2f52660`

Do not substitute the publication branch itself for the theorem authority. The publication branch is a human-readable projection of the frozen proof/evidence chain.

## Checks to reproduce

1. Verify the admission receipt at `research_targets/audits/A3_KCLASS_ENDPOINT_DP_V1_1_ADMISSION_0E505F46.json`.
2. Verify that its proof head is `0e505f460ec63cbb358c7f66cde18ab8a52684d3`.
3. Run the repository's A3 k-class endpoint-DP producer/verifier and require zero counterexamples and all tamper controls rejected.
4. Independently implement the endpoint event model. A singleton class has one atomic event; a repeated class has ordered start/finish events.
5. Independently enumerate small legal endpoint orders and compare their exact bottleneck width against the ternary DP.
6. For the recorded all-repeated `k=5` control, require 113400 valid endpoint orders, 243 states, and 810 directed transitions.
7. Recompute the subset-rank table `rho(X)` directly by finite-field row reduction rather than trusting certificate values.
8. Check every state width with `rho(S)+rho(K\P)-rho(K)`.

## Independence recommendations

For a genuinely external reproduction, use a fresh implementation rather than importing the project's producer. Different finite-field linear algebra code is preferable. Record the source commit, interpreter/compiler versions, raw outputs, and SHA-256 digests of all generated receipts.

A successful reproduction establishes evidence about correctness. It does not by itself prove historical literature novelty; novelty requires a separate literature/reviewer judgment.
