# Fundamentum receives JANUS Lapis Rowan candidate packets

The writer is Hawkar-usls/janus-lapis Draft PR #32, in:
https://github.com/Hawkar-usls/janus-lapis/pull/32

The collector remains Hawkar-usls/Janus; nothing here performs or requests Rowan calculations. This gate tests structural consistency of a compact candidate with its original local provider receipt and Lapis output hashes. It does not independently authenticate the provider and does not promote a hypothesis or proof.

Run locally after an approved source receipt has been retrieved:

~~~bash
python tools/verify_lapis_rowan_candidate.py --bundle /secure/translated-bundle --source-receipt /secure/original-rowan-receipt.json
python -m unittest discover -s tools -p 'test_verify_lapis_rowan_candidate.py' -v
~~~

Status STRUCTURALLY_VALID_UNAUTHENTICATED permits *only* inspection as an untested empirical research candidate. BLOCKED rejects tampering, inconsistent provider metrics, mismatched source references, injected executable operators, cross-domain proof claims and weakened scientific boundaries.

The formal Exact-One/P-NP track is strictly separate. Do not synthesize SAT witnesses, proofs, protein fitness, calibrated DeltaDeltaG, empirical results or an algorithm from model-confidence scores.

A same-SHA cache hit can reduce repeat downstream transformation, not credit cost of Rowan workflows already run. No public export of the original Rowan receipt is required. All execution, provider spend, token budget, evidence promotion, meta-registry writing and cross-repository dispatch remain disabled here.
