PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS c038_capability (
    capability_digest BLOB PRIMARY KEY,
    manifest_digest   BLOB NOT NULL,
    manifest_ref      TEXT NOT NULL,
    created_at_ns     INTEGER NOT NULL CHECK (created_at_ns >= 0)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS c038_current_capability (
    singleton_id      INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    capability_digest BLOB NOT NULL,
    FOREIGN KEY (capability_digest)
        REFERENCES c038_capability(capability_digest)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS c038_core (
    core_digest       BLOB PRIMARY KEY,
    canonicalizer_id  TEXT NOT NULL,
    atom_count        INTEGER NOT NULL CHECK (atom_count >= 0),
    variable_count    INTEGER NOT NULL CHECK (variable_count >= 0),
    payload_digest    BLOB NOT NULL,
    payload_ref       TEXT NOT NULL,
    first_seen_ns     INTEGER NOT NULL CHECK (first_seen_ns >= 0),
    last_seen_ns      INTEGER NOT NULL CHECK (last_seen_ns >= first_seen_ns),
    hit_count         INTEGER NOT NULL DEFAULT 0 CHECK (hit_count >= 0)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS c038_evaluation (
    core_digest        BLOB NOT NULL,
    capability_digest  BLOB NOT NULL,
    result_code        TEXT NOT NULL CHECK (
        result_code IN ('OPEN_PORTFOLIO_EXHAUSTED', 'CLOSED_POLY')
    ),
    trace_digest       BLOB NOT NULL,
    trace_ref          TEXT NOT NULL,
    certificate_digest BLOB,
    created_at_ns      INTEGER NOT NULL CHECK (created_at_ns >= 0),

    PRIMARY KEY (core_digest, capability_digest),

    FOREIGN KEY (core_digest)
        REFERENCES c038_core(core_digest),

    FOREIGN KEY (capability_digest)
        REFERENCES c038_capability(capability_digest)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS c038_evaluation_capability_idx
ON c038_evaluation(capability_digest, result_code);

-- ACTIVE versus STALE is derived, never stored:
--
-- ACTIVE iff c038_evaluation.capability_digest equals the singleton current
-- capability. Historical evaluations are immutable. Switching the current
-- capability is one UPSERT in c038_current_capability and performs no mass
-- UPDATE over c038_evaluation.
