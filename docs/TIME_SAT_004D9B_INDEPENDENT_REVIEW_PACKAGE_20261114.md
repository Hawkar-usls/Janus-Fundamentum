# JANUS TIME-SAT-004D9B — mathematical demonstration, third-party admission, full-cold baselines

Research-only reviewer supplement to [004D9A PR #596](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/596) and [external dependency #597](https://github.com/Hawkar-usls/Janus-Fundamentum/issues/597). No change to production C023, old frozen 004D9 policy, or official frozen negative R6 verdict.

## What is (and is not) mathematically new

The 004D6 step is **ordinary bounded propositional resolution** of the original, unmodified CNF. The full-sign-mask recognizer maps a family of clauses to an **entailed XOR**. Exact Gaussian elimination over GF(2) computes a **representation-relative rank increment** against XOR equations explicitly visible in the original CNF. These are known operations, *not* a new complete SAT inference calculus or proof of a complexity breakthrough.

There is no additional logical information beyond the original CNF: every valid derived clause and XOR is a logical consequence of that CNF. An increment of linear rank *relative only to the already extracted explicit XOR equations* can reveal a useful representation, but does not establish new information relative to arbitrary CNF reasoning, faster solving, or competitiveness against standard CryptoMiniSat XOR handling.

### Tiny case 1 — a verifiable positive representation-relative rank increment

Let variables 1,2,3 be x,y,z and 4 be w. Original source CNF:

    p cnf 4 5
    4 1 2 3 0
    4 1 -2 -3 0
    4 -1 2 -3 0
    4 -1 -2 3 0
    -4 0

The unit clause implies w = FALSE. Resolution on w converts the first four guarded clauses to:

    1 2 3 0
    1 -2 -3 0
    -1 2 -3 0
    -1 -2 3 0

These masks forbid even-parity assignments: **x XOR y XOR z = 1**.
An exhaustive 2^4 truth-table oracle independently checks that ALL satisfying
assignments of the original five clauses obey that parity. JANUS stores an
exact source-parent resolution DAG; a separate replayer checks each step.

The original explicit source parity includes w=0, but not the 3-variable
relation. Thus the derived equation is independent **relative to that
initial explicit parity basis**. Its novelty is only relative to what the
source-XOR extractor found, *not relative to what ordinary resolution can do*.

### Required negative controls

- An already explicit 3-variable XOR: no incremental coefficient rank.
- Two explicit XOR constraints whose elimination implies a third: the new
  syntactic XOR is a *dependent combination*, not new rank.
- A plain non-XOR CNF: deriving some resolvent does not license inventing XOR.

Run without an installed SAT solver:

    python experiments/time_sat_004_external/time_sat_004d9b_science_demo.py --out /tmp/janus-004d9b-math.json
    python -m unittest discover -s tests -p 'test_time_sat_004d9b_reviewer_package.py' -v

Every demonstration report includes the exact source SHA-256, original CNF,
models exhaustively enumerated, exact proof replayer outcome and coefficient/
augmented rank increments. This is **same-admin synthetic development**, never
a blinded independent replication or general scientific novelty claim.

## Explicit external trust admission — do NOT self-approve keys

The old 004D9 intake intentionally pins the empty policy Git blob
'83f17049fdcc663dd8acc8f878e0ca9bc73623cf' and MUST stay unchanged.

The separate 'time_sat_004d9b_trust_gate.py' provides the integration route
WITHOUT accepting an arbitrary CLI-supplied policy or public key:

1. Find an independent custodian who affirmatively accepts participation.
   Verify their institutional identity, dataset independence, public-key
   ownership and third-party reviewer out-of-band. An Ed25519 signature by
   itself cannot establish this identity or administrative independence.
2. Receive pre-release signed SHA-256 commitments for 3–8 previously unseen,
   independently chosen SAT instances from >=3 families, including complete
   satisfying models. Do NOT access original data until cohort and algorithm
   protocol are frozen.
3. Have a separately authorized human reviewer verify the external approval
   reference. Prepare a NEW append-only trust JSON (schema enforced by code),
   with exact issuer/public key, candidate id+family/source/model hashes and
   shapes, immutable algorithm commit and resource/negative-result policy.
4. REVIEW a *code change* pinning the NEW lockfile's exact Git blob SHA and
   separately validated external review SHA in the three literal
   'PINNED_...' constants. Absent these pins, the gate always returns
   'WAITING_FOR_OUTSIDE_ADMIN_APPROVAL_AND_CODE_PINNED_LOCKFILE'.
   CLI cannot select a different trust policy or override the pin.
5. Only then reveal unchanged original CNF/model and signed receipt and
   perform original-CNF SAT-model replay plus proof/rank diagnostics. Record
   every 0-rank, timeout, malformed case and abstention without exclusion.

Current external approved custodians: **0**.
Current signed independent source-model commitments: **0**.
Current external laboratory validations: **0**.
004C independent UNSAT proof verifier: **OPEN**. The source-SAT model gate
does not verify UNSAT conclusions.

Manual fail-closed preflight (never spends credits):

    python experiments/time_sat_004_external/time_sat_004d9b_trust_gate.py --preflight --out /tmp/trust-preflight.json

## Paired end-to-end baseline experiment (synthetic development ONLY)

The immutable *development* protocol is
'experiments/time_sat_004_external/TIME_SAT_004D9B_DEVELOPMENT_BENCHMARK_PROTOCOL.json',
pinned in the benchmark script by Git blob SHA. All precommitted toy cases,
3 paired repeats, fixed shuffle seed, 12-second child wall timeout, 8-second
child CPU budget, 2 GiB memory ceiling; no cherry-picking.

Arms (each in a **fresh Python process**):

- JANUS exact bounded-resolution proof/rank + source-XOR extraction + CryptoMiniSat native-XOR using entailed derived parity, full cold overhead included.
- CryptoMiniSat on the original CNF.
- CryptoMiniSat native-XOR with only the **explicit** original-CNF XOR sign-mask blocks, retaining the residual original clauses.
- CaDiCaL 1.9.5 on the original CNF.

Dependencies: Python 3.12, 'pycryptosat==5.15.0', 'python-sat==1.9.dev17'.
All SAT models MUST be replayed against every original CNF clause. No UNSAT
outcome counts as verified without a portable independently checked proof.
Unknown, timeout, memory, import failure or missing baseline is **censored**,
not counted as a JANUS speedup. Record per-attempt full cold wall time,
child peak RSS, returned SAT-model SHA, runtime statuses and baseline completeness.

    python -m pip install 'pycryptosat==5.15.0' 'python-sat==1.9.dev17'
    python experiments/time_sat_004_external/time_sat_004d9b_benchmark.py --out /tmp/janus-004d9b-cold.json

The median speed ratio must use the *fastest completed* non-JANUS baseline,
and a result is eligible for an all-arm comparison only if all baselines have
3/3 independently replayed SAT witnesses. Its tiny toy timings cannot support
a general speedup claim. A real scientific result needs a **new pre-registered
blind protocol, new external CNF sources, independent custodian, fair hardware
controls, and unrelated implementer**. The R6 mixed width4 ~31–33% loss and
'R6_FROZEN_SCIENCE_GATE_NOT_PASSED' stay in the official record unmodified.

## Reviewer request

Please inspect the exact short positive/null/negative cases, check that all
DAG steps are standard resolution, rerun the separate truth-table oracle and
compare the cold paired solver receipts. We ask for a scientific critique or
referral, **not an endorsement** or an assertion of P=NP.

No email has been sent by this supplement. No permission to use SAT Competition
organizers' name, materials or affiliation is implied.
