# GitHub-native checkpoint provenance

`Checkpoint Provenance` runs on relevant main pushes, completion of R5 Frontier
Verification, manual dispatch and an hourly recovery schedule. No external API
key, ChatGPT session or personal computer is required. GitHub scheduling may be
delayed. The built-in token only needs contents write and Actions read.

Reports live on the separate `checkpoint-reports` branch: one JSON and Markdown
record per source commit plus README and manifest. Scientific files on main are
never changed. The activation baseline is
`a4d881d272a1f67705af0bd81b1f6e9013023ba2`; older history is not advertised as new.
Every first-parent commit after the cursor is examined, including intermediate
commits. Merge commits are compared to their first parent. Only main is scientific
publication scope; unmerged experiments and meta-registry mirrors are not treated
as new canonical checkpoints. The canonical TRUMP anchor is
`registry/TRUMP_CURRENT_STATE.json` in this repository.

This is a deterministic evidence index, **not an autonomous mathematician**.
It attributes selected source lines with before/after links and SHA-256, and
records R5 runs only on the exact source SHA. Source gate/proof/counterexample
language remains SOURCE_REPORTED_ONLY. Scientific delta and next gate transition
require review. It never concludes P=NP, UNSAT, completeness or polynomial runtime
from text, hashes, CI or finite tests. P vs NP remains OPEN in these reports.

Every later run refreshes indexed reports for delayed CI. Report changes remain
in branch history. API failure aborts publication and does not advance the cursor;
non-ancestor history stops processing instead of silently skipping evidence.
Concurrency serializes publication; pushes are fast-forward only. No issue or
email messages are sent. No R5 scientific computation is launched by this observer.

Read the Actions job summary for report links. Reports are persistent Git history,
not expiring Actions artifacts. A checkpoint report can contain several source
files; excerpts are intentionally labelled incomplete. Full semantic summaries
still require scientific reading (for example, the existing ChatGPT observer).

Validation: `python -m unittest discover -s tools/checkpoint_observer -p 'test_*.py'`.
Tests cover scope, no proof promotion, deletion semantics, catch-up, deduplication,
API failure and delayed CI reconciliation.
