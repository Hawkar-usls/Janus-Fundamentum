# E12C5 R4 · independent sealed challenge handoff (not yet executed)

## What this is

This is a **ready-to-share procedure** for an external scientific witness, not an
attestation of independence. R4's eight published GitHub benchmark sources are
**public development evidence, NOT the sealed challenge**. No external
administrator or second independent provider is currently connected.

Frozen developer assets:
- Pre-registered protocol: `E12C5_R4_PREREG.json`, Git blob SHA
  `6ae53231ee55c912720525896bfdf978a4b7fb8e`.
- Candidate code at the first R4 evaluation start: repository commit
  `069aebfeb445a9a7798d7ec7069587234f0145bc`.
- Same-admin measurement: GitHub run [41615017387](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41615017387).
- Model is fit only on thirteen R1–R3 original source SHAs; no self-tuning against
  the external cohort is permitted.

## Sealed test operator obligations

1. Before sharing even the family-level instance choices or seeds, select and
   hold at least **20 previously unused CNF originals** across **4 unrelated
   generator families**, including XOR-rich, mixed XOR+CNF, ordinary planted
   CNF and difficult UNSAT with externally verified proof. Group related
   instances and their isomorphisms together to avoid train/test leakage.
2. Commit to `SHA256(canonical_source_manifest)` on an external platform and
   sign a dated manifest with the custodian's own administrator identity.
   Do **not** send unpublished labels, the actual sources or any GitHub token
   to JANUS before the candidate and thresholds are frozen.
3. Freeze the exact model artifact SHA and all source-code SHAs, unchanged
   preprocessing, baseline version pins, per-task CPU/RAM/host limits and
   selection thresholds. Source installation and test administration must be
   under credentials, machine and administrator **separate from Hawkar-usls**.
4. Run JANUS and stronger independent baselines (CryptoMiniSat native-XOR
   when exact cover is certified, CryptoMiniSat original CNF, CaDiCaL, and
   another contemporary solver if available) on the **same CNF**. Randomize
   run order, use at least 5 cold repeats per arm and host, and record
   exact model, original source SHA, UTC, environment, CPU/wall, memory
   and censored outcomes. No cherry-picked cases or replacements.
5. For each SAT claim independently replay the returned model against **every
   original CNF clause**. For UNSAT require a portable independently checked
   proof (e.g., LRAT/DRAT when supported); an own-admin XOR contradiction
   replay is not an external independent certificate.
6. Publish every result including timeouts, abstentions, failed sources
   and unsupported families, not only cases where JANUS was fast.
   If any source is revealed to developers early, discard the whole
   affected related group from **blind** evaluation, retain it as development.
7. Only once the external operator has independently signed SHA-linked
   results may a research review decide whether the experiment qualifies
   as source-family-specific progress. No autonomous promotion to C023,
   no claim of generic 3-SAT speedup, no claim of P=NP.

## Predeclared external primary success measure

Compare selector's full-cold median time with the minimum successful 5/5
median of **external competitors**, never its own GF(2) ablation. Require
full SAT witness replay, no more than 10% regret on every source, and
at least 20% speedup on at least two independently held-out **families**
at both independently administered environments. Treat resource-censored
baselines as **unknown**, never infinite performance gains. Report the
proportion of cases where the selector safely abstains.

This is a prospective additional challenge threshold, **not** a retroactive
reinterpretation of the existing R4 GitHub-run scientific gate.

## Current status

- External custodian: **OPEN / NOT CONNECTED**.
- Sealed input manifests: **NOT RECEIVED**.
- Independently administered wall/CPU measurements: **NOT PERFORMED**.
- Official external witness approval: **NONE**.
- R4 GitHub run and E12C4 live loop remain separate from this procedure.
