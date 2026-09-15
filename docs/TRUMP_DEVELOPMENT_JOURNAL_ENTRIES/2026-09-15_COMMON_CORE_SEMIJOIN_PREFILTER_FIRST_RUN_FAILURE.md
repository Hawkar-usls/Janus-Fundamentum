# TRUMP common-core semijoin prefilter — immutable first-run failure

Run `34972555416`, job `104392129868`, frozen head `9f7f8adc7b3645480947d1b09c0a22a5b2f1217b`.

Verdict: `FAIL_BEFORE_SCIENTIFIC_VERDICT__POSITIVE_CONTROL_PREDECESSOR_ASSUMPTION_NOT_ESTABLISHED`.

The first run failed inside the tamper-control setup with `KeyError: 'canonical'`. The v1 helper `first_failed_original_bucket(positive_aligned_overbudget_control())` returned a non-`READY` early predecessor status, so the tamper control tried to consume a receipt that did not exist.

This does **not** falsify the common-core semijoin theorem candidate: no scientific verdict was reached. The frozen positive control's predecessor premise must be diagnosed before any repair. v1 candidate/checker are not modified.

Next allowed action: a separately frozen read-only diagnostic successor that reports the actual sealed predecessor statuses of the proposed positive and sticky controls.

Firewalls remain `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, `GENERAL_EFFECTIVE_BUCKET_COMPRESSION=NOT_PROVED`.
