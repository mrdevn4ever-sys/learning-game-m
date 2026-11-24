"""SQLite-Schema v1. Artefaktbytes sind Teil derselben Sicherung."""

SCHEMA_VERSION = 1
SCHEMA = """
BEGIN IMMEDIATE;
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) STRICT;
CREATE TABLE imports (
    digest TEXT PRIMARY KEY, raw BLOB NOT NULL, imported_at INTEGER NOT NULL
) STRICT;
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    revision INTEGER NOT NULL CHECK(revision > 0),
    phase INTEGER NOT NULL CHECK(phase >= 0),
    title TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN
      ('planned','ready','leased','running','verifying','done',
       'retry_wait','reconciling','blocked','superseded')),
    input_digests TEXT NOT NULL,
    lease_owner TEXT,
    lease_expires INTEGER,
    fencing_token INTEGER NOT NULL DEFAULT 0 CHECK(fencing_token >= 0),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts >= 0),
    next_check_at INTEGER NOT NULL DEFAULT 0 CHECK(next_check_at >= 0),
    results TEXT NOT NULL DEFAULT '[]',
    blocked_reason TEXT,
    CHECK((lease_owner IS NULL) = (lease_expires IS NULL)),
    CHECK((state = 'blocked') = (blocked_reason IS NOT NULL)),
    CHECK(state NOT IN ('leased','running','verifying') OR lease_owner IS NOT NULL),
    CHECK(state IN ('leased','running','verifying','reconciling') OR lease_owner IS NULL)
) STRICT;
CREATE TABLE dependencies (
    job_id TEXT NOT NULL REFERENCES jobs(id),
    dependency_id TEXT NOT NULL REFERENCES jobs(id),
    position INTEGER NOT NULL,
    PRIMARY KEY(job_id, dependency_id),
    UNIQUE(job_id, position),
    CHECK(job_id != dependency_id)
) STRICT;
CREATE TABLE artifacts (
    digest TEXT PRIMARY KEY,
    data BLOB NOT NULL,
    size INTEGER NOT NULL CHECK(size >= 0),
    CHECK(length(data) = size)
) STRICT;
CREATE TABLE job_artifacts (
    job_id TEXT NOT NULL REFERENCES jobs(id),
    digest TEXT NOT NULL REFERENCES artifacts(digest),
    role TEXT NOT NULL,
    PRIMARY KEY(job_id, digest, role)
) STRICT;
CREATE TABLE effects (
    operation_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    kind TEXT NOT NULL CHECK(kind IN ('merge','upload')),
    revision INTEGER NOT NULL CHECK(revision > 0),
    state TEXT NOT NULL CHECK(state IN
        ('prepared','checking','armed','unknown','confirmed')),
    request TEXT NOT NULL,
    request_digest TEXT NOT NULL,
    target_key TEXT NOT NULL,
    candidate_digest TEXT NOT NULL,
    artifact_digest TEXT NOT NULL REFERENCES artifacts(digest),
    lease_owner TEXT,
    lease_expires INTEGER,
    job_fencing_token INTEGER NOT NULL DEFAULT 0,
    fencing_token INTEGER NOT NULL DEFAULT 0,
    attempts INTEGER NOT NULL DEFAULT 0,
    dispatch_count INTEGER NOT NULL DEFAULT 0 CHECK(dispatch_count IN (0,1)),
    uncertain INTEGER NOT NULL DEFAULT 0 CHECK(uncertain IN (0,1)),
    next_check_at INTEGER NOT NULL DEFAULT 0,
    observation TEXT,
    UNIQUE(kind, target_key),
    CHECK((lease_owner IS NULL) = (lease_expires IS NULL)),
    CHECK(state NOT IN ('checking','armed') OR lease_owner IS NOT NULL)
) STRICT;
CREATE INDEX effects_job ON effects(job_id, state);
CREATE TABLE audit (
    sequence INTEGER PRIMARY KEY,
    entity TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    revision INTEGER NOT NULL,
    action TEXT NOT NULL,
    at INTEGER NOT NULL,
    details TEXT NOT NULL
) STRICT;
CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit
    BEGIN SELECT RAISE(ABORT, 'audit is append-only'); END;
CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit
    BEGIN SELECT RAISE(ABORT, 'audit is append-only'); END;
PRAGMA user_version = 1;
COMMIT;
"""
