PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS proof_blob (
    proof_digest BLOB PRIMARY KEY,
    codec TEXT NOT NULL DEFAULT 'json',
    payload BLOB NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS negotiation_certificate (
    cert_digest BLOB PRIMARY KEY,
    pattern_digest BLOB NOT NULL UNIQUE,
    schema_version TEXT NOT NULL,
    policy TEXT NOT NULL,
    terminal_code TEXT NOT NULL,
    shared_count INTEGER NOT NULL CHECK (shared_count >= 0),
    step_count INTEGER NOT NULL CHECK (step_count >= 0),
    work_units INTEGER NOT NULL CHECK (work_units >= 0),
    certificate_bytes INTEGER NOT NULL CHECK (certificate_bytes >= 0)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS negotiation_literal_step (
    cert_digest BLOB NOT NULL,
    seq INTEGER NOT NULL,
    producer TEXT NOT NULL,
    var_id INTEGER NOT NULL CHECK (var_id > 0),
    bool_value INTEGER NOT NULL CHECK (bool_value IN (0, 1)),
    proof_digest BLOB NOT NULL,
    fact_digest BLOB NOT NULL,
    PRIMARY KEY (cert_digest, seq),
    FOREIGN KEY (cert_digest) REFERENCES negotiation_certificate(cert_digest),
    FOREIGN KEY (proof_digest) REFERENCES proof_blob(proof_digest)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS negotiation_alias_step (
    cert_digest BLOB NOT NULL,
    seq INTEGER NOT NULL,
    left_var INTEGER NOT NULL CHECK (left_var > 0),
    right_var INTEGER NOT NULL CHECK (right_var > 0),
    rhs INTEGER NOT NULL CHECK (rhs = 0),
    forward_proof_digest BLOB NOT NULL,
    reverse_proof_digest BLOB NOT NULL,
    fact_digest BLOB NOT NULL,
    PRIMARY KEY (cert_digest, seq),
    CHECK (left_var < right_var),
    FOREIGN KEY (cert_digest) REFERENCES negotiation_certificate(cert_digest),
    FOREIGN KEY (forward_proof_digest) REFERENCES proof_blob(proof_digest),
    FOREIGN KEY (reverse_proof_digest) REFERENCES proof_blob(proof_digest)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS negotiation_alias_pair_index
    ON negotiation_alias_step(left_var, right_var, rhs);
