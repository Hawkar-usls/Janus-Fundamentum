PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS proof_blob (
    proof_digest BLOB PRIMARY KEY,
    codec TEXT NOT NULL,
    raw_bytes INTEGER NOT NULL CHECK (raw_bytes >= 0),
    payload BLOB NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS negotiation_certificate (
    cert_digest BLOB PRIMARY KEY,
    schema_version TEXT NOT NULL,
    pattern_digest BLOB NOT NULL UNIQUE,
    policy TEXT NOT NULL,
    terminal_code TEXT NOT NULL,
    shared_count INTEGER NOT NULL CHECK (shared_count >= 0),
    step_count INTEGER NOT NULL CHECK (step_count >= 0),
    work_units INTEGER NOT NULL CHECK (work_units >= 0),
    certificate_bytes INTEGER NOT NULL CHECK (certificate_bytes >= 0),
    trace_digest BLOB NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS negotiation_step (
    cert_digest BLOB NOT NULL,
    seq INTEGER NOT NULL CHECK (seq >= 0),
    opcode TEXT NOT NULL,
    producer TEXT,
    var_id INTEGER,
    bool_value INTEGER CHECK (bool_value IN (0, 1) OR bool_value IS NULL),
    proof_digest BLOB,
    PRIMARY KEY (cert_digest, seq),
    FOREIGN KEY (cert_digest) REFERENCES negotiation_certificate(cert_digest),
    FOREIGN KEY (proof_digest) REFERENCES proof_blob(proof_digest)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS separator_chunk (
    cert_digest BLOB NOT NULL,
    chunk_no INTEGER NOT NULL CHECK (chunk_no >= 0),
    bit_payload BLOB NOT NULL,
    PRIMARY KEY (cert_digest, chunk_no),
    FOREIGN KEY (cert_digest) REFERENCES negotiation_certificate(cert_digest)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS negotiation_terminal_idx
ON negotiation_certificate(terminal_code, policy);

-- Exact-pattern cache key:
-- SHA256(schema_version || policy || ordered module digests ||
--        ordered shared scope || initial facts)
--
-- Modules are stored elsewhere and referenced by digest. Native proof blobs are
-- content-addressed and deduplicated. No RREF matrix or Horn closure is copied
-- into every step. The canonical JSON certificate remains an interchange object,
-- while this normalized layout is the persistent janus.db representation.
