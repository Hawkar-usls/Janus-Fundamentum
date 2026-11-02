# JANUS · TIME-SAT-004D9A: offline external custodian handoff

**Research-only; NOT a live independent witness.** Parent draft: PR #595, original 004D9 policy has **zero** approved public keys/cases and MUST remain frozen, empty and unchanged.

## Scope and scientific distinction

004D9A is a small offline, auditable helper for a THIRD PARTY who controls new SAT source selection, complete satisfying models, and their signing key outside Hawkar-usls/JANUS. This assistant's GitHub CI and synthetic keys never count as external evidence.

- Cryptographic Ed25519 signature proves possession of a signing key and binds the exact source/model SHA-256, but does NOT prove outside administrative control, novelty or independent custody.
- The signed model must satisfy EVERY clause of the exact original SHA-pinned CNF, not just carry an upstream SAT label. No accepted model is inferred from UNSAT or timeout.
- Independent verification of UNSAT proof including empty clause remains an **independent TIME-SAT-004C obligation**. This SAT data signing kit does not discharge it.

## Custodian-only commands (run on the custodian's own computer, not JANUS)

Require Python 3.12 and package cryptography==46.0.3; code file:
experiments/time_sat_004_external/external_custodian_offline_004d9a.py

1. Generate the external Ed25519 key once on an independently owned computer:

    python external_custodian_offline_004d9a.py keygen --issuer independent-lab-identifier --private-key /outside-repo/private.pem --public-identity /outside-repo/public-identity.json

2. Select a previously unseen, privately held SAT original.cnf and complete original-model.json containing one signed integer per original source variable. Create a **pre-release** signed hash commitment without sharing either data file:

    python external_custodian_offline_004d9a.py precommit --issuer independent-lab-identifier --candidate-id independent-case-001 --private-key /outside-repo/private.pem --cnf /private/original.cnf --model /private/original-model.json --out-commitment /public/precommit.json --out-signed-receipt /public/signed-receipt.json

The model JSON format is a single object with property signed_model, a complete list of signed nonzero DIMACS variable assignments. The offline tool verifies EVERY original clause before signing. Limits: <=5000 vars, <=30000 clauses, <=120000 literals, <=128MiB source, <=200KB model. It refuses existing-key overwrite, creates private keys with mode 0600, and checks against saving a private key in a Git worktree. No network calls or automatic release. Never publish private.pem, model or source during the precommit phase.

## Mandatory freeze/reveal sequence

1. External custodian controls at least three novel SAT families, privately chooses instances and verifies their SAT models. Do not release CNF/model to JANUS during selection. Public already-seen competitions are external-origin controls, NOT blinded holdouts.
2. Custodian sends ONLY public identity and signed precommit metadata (candidate IDs, source/model SHA-256, dimensions) plus proof of outside control via out-of-band identity review. That evidence is not itself sufficient to claim administrative independence.
3. An independent reviewer confirms that the key custodian and dataset are outside JANUS control, and JANUS separately commits an **immutable NEW** research lockfile binding custodian identity, approved public key, all candidate SHAs, algorithm code/HEAD, fixed budget, negative-result policy, and release sequence. **Do not edit the original empty 004D9 lockfile and do not reveal CNF/model before freeze**.
4. Only after accepted lockfile freeze, custodian reveals the same original CNF bytes, complete model and matching Ed25519 signed receipt. The 004D9 reader validates hash, approved key and source model before bounded source-only resolution and exact GF(2) rank. Every locked case, including 0-rank, error and timeout, is retained unchanged.
5. If genuinely independent new rank on verified-SAT cases appears, predeclare a separate real end-to-end matched cost benchmark; do not infer performance from GF(2) rank alone. 004C, 004D, 004E and 004F remain open until individually verified.

## Candidate outreach, DRAFT ONLY, NOT SENT

To: organizers@satcompetition.org

Subject: Request for independent sealed SAT-instance validation — exploratory XOR research

Hello,

We are conducting an exploratory reproducible study of exact source-entailed XOR constraints in Boolean CNF. Existing public results include negative cases, and we do not claim a general SAT speedup or a P=NP proof.

Could you advise on an independent researcher or institution willing to select a small set of verified SAT CNFs (ideally three distinct families), keep original CNFs and complete satisfying models sealed while a frozen research protocol is committed, and later return signed SHA-256/Ed25519 custody metadata and source data for blinded evaluation? We can provide a minimal offline, open-source SAT-model checking and signing helper, or accommodate an independently implemented equivalent. Custodian identity and key control would be reviewed separately, and full original-CNF model validity checked on every instance.

We do not seek release of unpublished benchmark data before commitments are frozen, and we make no assumption of funding, endorsement or participation. Positive, null and negative results would all be reported.

Research context: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/595

If another SAT research contact is more suitable for a small independent evaluation, a referral would be appreciated.

Thank you.

## Remaining gates

- Independent trusted key/identity and externally signed frozen case lockfile: **NOT OBTAINED**.
- Distinct externally held verified SAT CNF/model instances: **ZERO**.
- Independent third-party 004C UNSAT proof witness: **OPEN** (different requirement).
- Dual-host synthetic signer/intake interoperability: this PR's CI only, NEVER real external validation.
- Production C023 and main: **UNCHANGED**. Paid Rowan: NONE. Persistent owner NAS/PC load: NONE.

Status: 004D PARTIAL · 004C OPEN · 004E OPEN · 004F NOT READY.
