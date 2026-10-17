# JANUS P-vs-NP Stream Resume Cache

This repository-side cache exists because a chat/UI stream can fail with
`Stream cache expired` or `resume stream unavailable` while the Git research
branch remains intact.

It does **not** prevent a UI stream failure. It makes recovery deterministic.

## Canonical files

- `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` — current resume checkpoint.
- `.janus/stream_cache_history/` — append-only archived checkpoints created by
  the utility when the current checkpoint is replaced.
- `tools/janus_stream_resume_cache.py` — verify/status/resume/write/archive tool.

## Mandatory resume sequence

```bash
python tools/janus_stream_resume_cache.py verify
python tools/janus_stream_resume_cache.py status
python tools/janus_stream_resume_cache.py resume
```

Then inspect commits newer than `source_scientific_head`.

**Never reset or rewind a live branch to the cached head.** The cached SHA binds
the scientific state being summarized. If the live branch is a descendant,
newer commits must be ingested before research continues. If it diverged, writes
stop until the states are reconciled.

## Scientific fail-closed rule

The cache is navigation state, not proof authority.

A stream checkpoint may record:

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
```

but it cannot promote those values merely because the checkpoint says so. The
utility rejects a non-`OPEN` `P_VS_NP` value unless a `promotion_receipt` field
is present. Actual promotion still remains subject to the repository's
proof/governance gates.

Finite regression, benchmark success, absence of a counterexample, or a chat
claim is never a P=NP proof.

## Updating the cache

Prepare a complete JSON state, then run:

```bash
python tools/janus_stream_resume_cache.py write \
  --from-json /path/to/new_state.json \
  --source-head <scientific-head-sha>
```

The existing checkpoint is archived byte-for-byte before replacement. The new
checkpoint is canonical-JSON hashed with SHA-256. Secret-like keys and common
credential patterns are rejected.

Commit the resulting current checkpoint and any new history file together with
the research changes they summarize, or immediately after them as a
transport-only persistence commit.

## Recovery contract for future JANUS work

After a stream failure, do not ask the user to reconstruct the research state
from memory. Read this cache, verify the live branch relation, ingest any newer
commits, and continue from `current_research_state.next_attack`.

The cache must preserve at least:

- repository / branch / source scientific HEAD;
- exact scientific ceiling;
- active frontier and carrier;
- established theorem/countercontrol facts;
- open gates and live route split;
- anti-loop exclusions;
- critical artifact paths;
- stale workflow/bootstrap hazards;
- next executable attack.

This follows JANUS's broader persistence discipline: source-head binding,
deterministic replay, append-only failed-attempt history, no silent rollback,
and no history rewrite.
