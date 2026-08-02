#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sqlite3
import tempfile
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping

CAPABILITY_SCHEMA = "janus.c038.capability.v1"
OPEN_TRACE_SCHEMA = "janus.c038.open-trace.v1"
CAPABILITY_DOMAIN = b"JANUS-C038-CAPABILITY-V1\0"
CORE_DOMAIN = b"JANUS-C038-CORE-V1\0"


class C038Error(RuntimeError):
    pass


class ImmutableEvaluationError(C038Error):
    pass


class LookupResult(str, Enum):
    MISS = "MISS"
    HIT_VERIFIED_OPEN = "HIT_VERIFIED_OPEN"
    HIT_STALE = "HIT_STALE"
    HIT_CORRUPT = "HIT_CORRUPT"


class StoreResult(str, Enum):
    STORED = "STORED"
    IDEMPOTENT = "IDEMPOTENT"


@dataclass(frozen=True)
class CanonicalCore:
    canonical_payload: bytes
    canonicalizer_id: str
    atom_count: int
    variable_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.canonical_payload, bytes):
            raise TypeError("canonical_payload must be bytes")
        if not self.canonicalizer_id:
            raise ValueError("canonicalizer_id must be non-empty")
        if self.atom_count < 0 or self.variable_count < 0:
            raise ValueError("counts must be non-negative")

    @property
    def digest(self) -> bytes:
        return hashlib.sha256(CORE_DOMAIN + self.canonical_payload).digest()


@dataclass(frozen=True)
class CapabilityManifest:
    value: Mapping[str, Any]

    @property
    def canonical_bytes(self) -> bytes:
        _validate_json_value(self.value)
        return canonical_json(self.value)

    @property
    def digest(self) -> bytes:
        return hashlib.sha256(CAPABILITY_DOMAIN + self.canonical_bytes).digest()


@dataclass(frozen=True)
class OpenTrace:
    value: Mapping[str, Any]


ReplayOpenTrace = Callable[[Mapping[str, Any], bytes, bytes], bool]


def _validate_json_value(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise TypeError("floating-point values are forbidden in canonical manifests")
    if isinstance(value, list):
        for item in value:
            _validate_json_value(item)
        return
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("JSON object keys must be strings")
        for item in value.values():
            _validate_json_value(item)
        return
    raise TypeError(f"unsupported canonical JSON value: {type(value)!r}")


def canonical_json(value: Any) -> bytes:
    _validate_json_value(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest_text(digest: bytes) -> str:
    return "sha256:" + digest.hex()


def _now_ns() -> int:
    return time.time_ns()


def _default_schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "c038-open-core-vault.sql"


def _validate_capability_manifest(manifest: CapabilityManifest) -> None:
    value = manifest.value
    if value.get("schema") != CAPABILITY_SCHEMA:
        raise ValueError(f"capability schema must be {CAPABILITY_SCHEMA}")
    for key in ("canonicalizer", "portfolio", "budgets", "protocols"):
        if key not in value:
            raise ValueError(f"capability manifest missing {key}")
    if not isinstance(value["portfolio"], list):
        raise TypeError("portfolio must be a list")


def _validate_open_trace_shape(
    trace: Mapping[str, Any],
    core_digest: bytes,
    capability_digest: bytes,
) -> None:
    if trace.get("schema") != OPEN_TRACE_SCHEMA:
        raise ValueError(f"open trace schema must be {OPEN_TRACE_SCHEMA}")
    if trace.get("core_digest") != digest_text(core_digest):
        raise ValueError("open trace core_digest mismatch")
    if trace.get("capability_digest") != digest_text(capability_digest):
        raise ValueError("open trace capability_digest mismatch")
    detectors = trace.get("detectors")
    if not isinstance(detectors, list) or not detectors:
        raise ValueError("open trace requires a non-empty detector ledger")
    seen: set[str] = set()
    for entry in detectors:
        if not isinstance(entry, dict):
            raise TypeError("detector ledger entries must be objects")
        detector_id = entry.get("id")
        terminal = entry.get("terminal")
        proof_digest = entry.get("proof_digest")
        if not isinstance(detector_id, str) or not detector_id:
            raise ValueError("detector id must be non-empty")
        if detector_id in seen:
            raise ValueError("duplicate detector id in open trace")
        seen.add(detector_id)
        if not isinstance(terminal, str) or not terminal.startswith("OPEN_"):
            raise ValueError("every refusal terminal must start with OPEN_")
        if not isinstance(proof_digest, str) or not proof_digest.startswith("sha256:"):
            raise ValueError("every detector entry requires a proof digest")
    if trace.get("terminal") != "OPEN_PORTFOLIO_EXHAUSTED":
        raise ValueError("open trace terminal must be OPEN_PORTFOLIO_EXHAUSTED")


class C038OpenCoreVault:
    def __init__(
        self,
        db_path: str = "janus.db",
        *,
        vault_dir: str | None = None,
        schema_path: str | None = None,
        replay_open_trace: ReplayOpenTrace | None = None,
    ):
        self.db_path = Path(db_path)
        self.vault_dir = Path(vault_dir) if vault_dir else self.db_path.parent / "vault"
        self.schema_path = Path(schema_path) if schema_path else _default_schema_path()
        self.replay_open_trace = replay_open_trace

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.db_path, timeout=30.0)
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("PRAGMA busy_timeout = 30000")
        db.execute("PRAGMA journal_mode = WAL")
        return db

    async def init_schema(self) -> None:
        await asyncio.to_thread(self._init_schema_sync)

    def _init_schema_sync(self) -> None:
        sql = self.schema_path.read_text(encoding="utf-8")
        with self._connect() as db:
            db.executescript(sql)

    async def register_capability(self, manifest: dict) -> bytes:
        item = CapabilityManifest(manifest)
        _validate_capability_manifest(item)
        payload = item.canonical_bytes
        capability_digest = item.digest
        manifest_digest, manifest_ref = await asyncio.to_thread(
            self._store_blob_sync, payload, "capability.json"
        )
        await asyncio.to_thread(
            self._register_capability_sync,
            capability_digest,
            manifest_digest,
            manifest_ref,
        )
        return capability_digest

    def _register_capability_sync(
        self,
        capability_digest: bytes,
        manifest_digest: bytes,
        manifest_ref: str,
    ) -> None:
        with self._connect() as db:
            row = db.execute(
                """
                SELECT manifest_digest, manifest_ref
                FROM c038_capability
                WHERE capability_digest = ?
                """,
                (capability_digest,),
            ).fetchone()
            if row is not None:
                if row != (manifest_digest, manifest_ref):
                    raise C038Error("capability digest collision or inconsistent manifest")
                return
            db.execute(
                """
                INSERT INTO c038_capability(
                    capability_digest, manifest_digest, manifest_ref, created_at_ns
                ) VALUES (?, ?, ?, ?)
                """,
                (capability_digest, manifest_digest, manifest_ref, _now_ns()),
            )

    async def set_current_capability(self, capability_digest: bytes) -> None:
        await asyncio.to_thread(self._set_current_capability_sync, capability_digest)

    def _set_current_capability_sync(self, capability_digest: bytes) -> None:
        with self._connect() as db:
            exists = db.execute(
                "SELECT 1 FROM c038_capability WHERE capability_digest = ?",
                (capability_digest,),
            ).fetchone()
            if exists is None:
                raise KeyError("capability must be registered before activation")
            db.execute(
                """
                INSERT INTO c038_current_capability(singleton_id, capability_digest)
                VALUES (1, ?)
                ON CONFLICT(singleton_id)
                DO UPDATE SET capability_digest = excluded.capability_digest
                """,
                (capability_digest,),
            )

    async def get_current_capability(self) -> bytes:
        return await asyncio.to_thread(self._get_current_capability_sync)

    def _get_current_capability_sync(self) -> bytes:
        with self._connect() as db:
            row = db.execute(
                """
                SELECT capability_digest
                FROM c038_current_capability
                WHERE singleton_id = 1
                """
            ).fetchone()
            if row is None:
                raise LookupError("current capability is not configured")
            return bytes(row[0])

    async def lookup_exact(
        self,
        core_digest: bytes,
        capability_digest: bytes,
    ) -> LookupResult:
        return await asyncio.to_thread(
            self._lookup_exact_sync, core_digest, capability_digest
        )

    def _lookup_exact_sync(
        self,
        core_digest: bytes,
        capability_digest: bytes,
    ) -> LookupResult:
        with self._connect() as db:
            current = db.execute(
                """
                SELECT capability_digest
                FROM c038_current_capability
                WHERE singleton_id = 1
                """
            ).fetchone()
            if current is None:
                return LookupResult.MISS
            current_digest = bytes(current[0])

            row = db.execute(
                """
                SELECT result_code, trace_digest, trace_ref
                FROM c038_evaluation
                WHERE core_digest = ? AND capability_digest = ?
                """,
                (core_digest, capability_digest),
            ).fetchone()

            if capability_digest != current_digest:
                return LookupResult.HIT_STALE if row is not None else LookupResult.MISS

            if row is None:
                stale = db.execute(
                    """
                    SELECT 1
                    FROM c038_evaluation
                    WHERE core_digest = ?
                      AND capability_digest != ?
                      AND result_code = 'OPEN_PORTFOLIO_EXHAUSTED'
                    LIMIT 1
                    """,
                    (core_digest, capability_digest),
                ).fetchone()
                return LookupResult.HIT_STALE if stale else LookupResult.MISS

            result_code, trace_digest, trace_ref = row
            if result_code != "OPEN_PORTFOLIO_EXHAUSTED":
                return LookupResult.MISS

            core_row = db.execute(
                """
                SELECT payload_digest, payload_ref
                FROM c038_core
                WHERE core_digest = ?
                """,
                (core_digest,),
            ).fetchone()
            if core_row is None:
                return LookupResult.HIT_CORRUPT

            payload_digest, payload_ref = bytes(core_row[0]), core_row[1]
            if self._read_verified_sync(payload_ref, payload_digest) is None:
                return LookupResult.HIT_CORRUPT

            trace_payload = self._read_verified_sync(trace_ref, bytes(trace_digest))
            if trace_payload is None:
                return LookupResult.HIT_CORRUPT
            try:
                trace = json.loads(trace_payload)
                _validate_open_trace_shape(trace, core_digest, capability_digest)
            except (ValueError, TypeError, json.JSONDecodeError):
                return LookupResult.HIT_CORRUPT

            if self.replay_open_trace is None:
                return LookupResult.HIT_CORRUPT
            try:
                replay_ok = bool(
                    self.replay_open_trace(trace, core_digest, capability_digest)
                )
            except Exception:
                replay_ok = False
            if not replay_ok:
                return LookupResult.HIT_CORRUPT

            db.execute(
                """
                UPDATE c038_core
                SET hit_count = hit_count + 1, last_seen_ns = ?
                WHERE core_digest = ?
                """,
                (_now_ns(), core_digest),
            )
            return LookupResult.HIT_VERIFIED_OPEN

    async def record_open(
        self,
        core: CanonicalCore,
        capability: CapabilityManifest,
        open_trace: OpenTrace,
    ) -> StoreResult:
        _validate_capability_manifest(capability)
        _validate_open_trace_shape(open_trace.value, core.digest, capability.digest)
        core_payload_digest, core_ref = await asyncio.to_thread(
            self._store_blob_sync, core.canonical_payload, "core.bin"
        )
        trace_payload = canonical_json(open_trace.value)
        trace_digest, trace_ref = await asyncio.to_thread(
            self._store_blob_sync, trace_payload, "open-trace.json"
        )
        return await asyncio.to_thread(
            self._record_open_sync,
            core,
            capability.digest,
            core_payload_digest,
            core_ref,
            trace_digest,
            trace_ref,
        )

    def _record_open_sync(
        self,
        core: CanonicalCore,
        capability_digest: bytes,
        core_payload_digest: bytes,
        core_ref: str,
        trace_digest: bytes,
        trace_ref: str,
    ) -> StoreResult:
        now = _now_ns()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute(
                "SELECT 1 FROM c038_capability WHERE capability_digest = ?",
                (capability_digest,),
            ).fetchone() is None:
                raise KeyError("capability is not registered")

            core_row = db.execute(
                """
                SELECT canonicalizer_id, atom_count, variable_count,
                       payload_digest, payload_ref
                FROM c038_core
                WHERE core_digest = ?
                """,
                (core.digest,),
            ).fetchone()
            if core_row is None:
                db.execute(
                    """
                    INSERT INTO c038_core(
                        core_digest, canonicalizer_id, atom_count, variable_count,
                        payload_digest, payload_ref,
                        first_seen_ns, last_seen_ns, hit_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (
                        core.digest,
                        core.canonicalizer_id,
                        core.atom_count,
                        core.variable_count,
                        core_payload_digest,
                        core_ref,
                        now,
                        now,
                    ),
                )
            else:
                expected = (
                    core.canonicalizer_id,
                    core.atom_count,
                    core.variable_count,
                    core_payload_digest,
                    core_ref,
                )
                if core_row != expected:
                    raise C038Error("core digest collision or inconsistent core metadata")
                db.execute(
                    "UPDATE c038_core SET last_seen_ns = ? WHERE core_digest = ?",
                    (now, core.digest),
                )

            evaluation = db.execute(
                """
                SELECT result_code, trace_digest, trace_ref, certificate_digest
                FROM c038_evaluation
                WHERE core_digest = ? AND capability_digest = ?
                """,
                (core.digest, capability_digest),
            ).fetchone()
            expected_eval = (
                "OPEN_PORTFOLIO_EXHAUSTED",
                trace_digest,
                trace_ref,
                None,
            )
            if evaluation is not None:
                if evaluation != expected_eval:
                    raise ImmutableEvaluationError("existing evaluation cannot be mutated")
                return StoreResult.IDEMPOTENT

            db.execute(
                """
                INSERT INTO c038_evaluation(
                    core_digest, capability_digest, result_code,
                    trace_digest, trace_ref, certificate_digest, created_at_ns
                ) VALUES (?, ?, 'OPEN_PORTFOLIO_EXHAUSTED', ?, ?, NULL, ?)
                """,
                (core.digest, capability_digest, trace_digest, trace_ref, now),
            )
            return StoreResult.STORED

    async def record_poly(
        self,
        core_digest: bytes,
        capability: CapabilityManifest,
        certificate_digest: bytes,
    ) -> StoreResult:
        _validate_capability_manifest(capability)
        receipt = {
            "schema": "janus.c038.poly-receipt.v1",
            "core_digest": digest_text(core_digest),
            "capability_digest": digest_text(capability.digest),
            "certificate_digest": digest_text(certificate_digest),
            "terminal": "CLOSED_POLY",
        }
        trace_digest, trace_ref = await asyncio.to_thread(
            self._store_blob_sync,
            canonical_json(receipt),
            "poly-receipt.json",
        )
        return await asyncio.to_thread(
            self._record_poly_sync,
            core_digest,
            capability.digest,
            certificate_digest,
            trace_digest,
            trace_ref,
        )

    def _record_poly_sync(
        self,
        core_digest: bytes,
        capability_digest: bytes,
        certificate_digest: bytes,
        trace_digest: bytes,
        trace_ref: str,
    ) -> StoreResult:
        now = _now_ns()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute(
                "SELECT 1 FROM c038_core WHERE core_digest = ?",
                (core_digest,),
            ).fetchone() is None:
                raise KeyError("core must exist before recording CLOSED_POLY")
            if db.execute(
                "SELECT 1 FROM c038_capability WHERE capability_digest = ?",
                (capability_digest,),
            ).fetchone() is None:
                raise KeyError("capability is not registered")

            evaluation = db.execute(
                """
                SELECT result_code, trace_digest, trace_ref, certificate_digest
                FROM c038_evaluation
                WHERE core_digest = ? AND capability_digest = ?
                """,
                (core_digest, capability_digest),
            ).fetchone()
            expected = (
                "CLOSED_POLY",
                trace_digest,
                trace_ref,
                certificate_digest,
            )
            if evaluation is not None:
                if evaluation != expected:
                    raise ImmutableEvaluationError("existing evaluation cannot be mutated")
                return StoreResult.IDEMPOTENT

            db.execute(
                """
                INSERT INTO c038_evaluation(
                    core_digest, capability_digest, result_code,
                    trace_digest, trace_ref, certificate_digest, created_at_ns
                ) VALUES (?, ?, 'CLOSED_POLY', ?, ?, ?, ?)
                """,
                (
                    core_digest,
                    capability_digest,
                    trace_digest,
                    trace_ref,
                    certificate_digest,
                    now,
                ),
            )
            return StoreResult.STORED

    def _store_blob_sync(self, payload: bytes, suffix: str) -> tuple[bytes, str]:
        digest = hashlib.sha256(payload).digest()
        hex_digest = digest.hex()
        target = (
            self.vault_dir
            / "sha256"
            / hex_digest[:2]
            / hex_digest[2:4]
            / f"{hex_digest}.{suffix}"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            existing = target.read_bytes()
            if hashlib.sha256(existing).digest() != digest:
                raise C038Error("content-addressed path contains corrupt data")
            return digest, str(target)

        temp = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        with temp.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.replace(temp, target)
        finally:
            if temp.exists():
                temp.unlink()
        return digest, str(target)

    @staticmethod
    def _read_verified_sync(ref: str, expected_digest: bytes) -> bytes | None:
        try:
            payload = Path(ref).read_bytes()
        except OSError:
            return None
        if hashlib.sha256(payload).digest() != expected_digest:
            return None
        return payload


def _manifest(
    *,
    solver_digest: str = "sha256:solver",
    verifier_digest: str = "sha256:verifier",
    work_budget: int = 200000,
    canonicalizer_version: int = 1,
) -> dict:
    return {
        "schema": CAPABILITY_SCHEMA,
        "canonicalizer": {
            "id": "janus.cnf.canon",
            "version": canonicalizer_version,
            "code_digest": "sha256:canon",
        },
        "portfolio": [
            {
                "id": "C037",
                "solver_digest": solver_digest,
                "verifier_digest": verifier_digest,
                "policy_digest": "sha256:policy",
            }
        ],
        "budgets": {
            "total_work_units": work_budget,
            "certificate_bytes": 1048576,
            "payload_bytes": 4194304,
        },
        "protocols": {
            "negotiation": "janus.cross_language_negotiation.v1",
            "open_core": "janus.c038.core.v1",
        },
    }


def _trace(core: CanonicalCore, capability: CapabilityManifest) -> OpenTrace:
    return OpenTrace(
        {
            "schema": OPEN_TRACE_SCHEMA,
            "core_digest": digest_text(core.digest),
            "capability_digest": digest_text(capability.digest),
            "detectors": [
                {
                    "id": "C035",
                    "terminal": "OPEN_LANGUAGE",
                    "proof_digest": "sha256:01",
                },
                {
                    "id": "C036",
                    "terminal": "OPEN_NO_SEPARATOR",
                    "proof_digest": "sha256:02",
                },
                {
                    "id": "C037",
                    "terminal": "OPEN_FIXPOINT",
                    "proof_digest": "sha256:03",
                },
            ],
            "terminal": "OPEN_PORTFOLIO_EXHAUSTED",
        }
    )


def _replay(
    trace: Mapping[str, Any],
    core_digest: bytes,
    capability_digest: bytes,
) -> bool:
    try:
        _validate_open_trace_shape(trace, core_digest, capability_digest)
    except (ValueError, TypeError):
        return False
    return [entry["id"] for entry in trace["detectors"]] == [
        "C035",
        "C036",
        "C037",
    ]


async def _self_test() -> dict:
    manifest_a = _manifest()
    manifest_b = {
        "protocols": manifest_a["protocols"],
        "budgets": manifest_a["budgets"],
        "portfolio": manifest_a["portfolio"],
        "canonicalizer": manifest_a["canonicalizer"],
        "schema": manifest_a["schema"],
    }
    cap_a = CapabilityManifest(manifest_a)
    cap_b = CapabilityManifest(manifest_b)
    assert cap_a.digest == cap_b.digest

    changed = [
        CapabilityManifest(_manifest(solver_digest="sha256:solver2")).digest,
        CapabilityManifest(_manifest(verifier_digest="sha256:verifier2")).digest,
        CapabilityManifest(_manifest(work_budget=200001)).digest,
        CapabilityManifest(_manifest(canonicalizer_version=2)).digest,
    ]
    assert all(item != cap_a.digest for item in changed)
    assert len(set(changed)) == len(changed)

    with tempfile.TemporaryDirectory(prefix="janus-c038-") as temp_dir:
        root = Path(temp_dir)
        schema_copy = root / "c038.sql"
        schema_copy.write_text(
            _default_schema_path().read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        db_path = root / "janus.db"
        vault = C038OpenCoreVault(
            str(db_path),
            vault_dir=str(root / "vault"),
            schema_path=str(schema_copy),
            replay_open_trace=_replay,
        )
        await vault.init_schema()
        digest_a = await vault.register_capability(manifest_a)
        await vault.set_current_capability(digest_a)
        assert await vault.get_current_capability() == digest_a

        core = CanonicalCore(
            b'{"clauses":[[-1,2],[1,-2]],"n":2}',
            "janus.cnf.canon.v1",
            2,
            2,
        )
        trace = _trace(core, cap_a)
        assert await vault.record_open(core, cap_a, trace) == StoreResult.STORED
        assert await vault.record_open(core, cap_a, trace) == StoreResult.IDEMPOTENT
        assert (
            await vault.lookup_exact(core.digest, digest_a)
            == LookupResult.HIT_VERIFIED_OPEN
        )

        before = sqlite3.connect(db_path).execute(
            """
            SELECT core_digest, capability_digest, result_code,
                   trace_digest, trace_ref, certificate_digest
            FROM c038_evaluation
            ORDER BY capability_digest
            """
        ).fetchall()

        manifest_c = _manifest(work_budget=300000)
        cap_c = CapabilityManifest(manifest_c)
        digest_c = await vault.register_capability(manifest_c)
        await vault.set_current_capability(digest_c)

        after = sqlite3.connect(db_path).execute(
            """
            SELECT core_digest, capability_digest, result_code,
                   trace_digest, trace_ref, certificate_digest
            FROM c038_evaluation
            ORDER BY capability_digest
            """
        ).fetchall()
        assert before == after
        assert await vault.lookup_exact(core.digest, digest_a) == LookupResult.HIT_STALE
        assert await vault.lookup_exact(core.digest, digest_c) == LookupResult.HIT_STALE

        cert_digest = hashlib.sha256(b"poly-certificate").digest()
        assert (
            await vault.record_poly(core.digest, cap_c, cert_digest)
            == StoreResult.STORED
        )
        rows = sqlite3.connect(db_path).execute(
            """
            SELECT result_code
            FROM c038_evaluation
            WHERE core_digest = ?
            ORDER BY result_code
            """,
            (core.digest,),
        ).fetchall()
        assert rows == [
            ("CLOSED_POLY",),
            ("OPEN_PORTFOLIO_EXHAUSTED",),
        ]

        core2 = CanonicalCore(
            b'{"clauses":[[1]],"n":1}',
            "janus.cnf.canon.v1",
            1,
            1,
        )
        trace2 = _trace(core2, cap_c)
        writer1 = C038OpenCoreVault(
            str(db_path),
            vault_dir=str(root / "vault"),
            schema_path=str(schema_copy),
            replay_open_trace=_replay,
        )
        writer2 = C038OpenCoreVault(
            str(db_path),
            vault_dir=str(root / "vault"),
            schema_path=str(schema_copy),
            replay_open_trace=_replay,
        )
        results = await asyncio.gather(
            writer1.record_open(core2, cap_c, trace2),
            writer2.record_open(core2, cap_c, trace2),
        )
        assert set(results) <= {StoreResult.STORED, StoreResult.IDEMPOTENT}
        count = sqlite3.connect(db_path).execute(
            """
            SELECT COUNT(*)
            FROM c038_evaluation
            WHERE core_digest = ? AND capability_digest = ?
            """,
            (core2.digest, digest_c),
        ).fetchone()[0]
        assert count == 1

        trace_ref = sqlite3.connect(db_path).execute(
            """
            SELECT trace_ref
            FROM c038_evaluation
            WHERE core_digest = ? AND capability_digest = ?
            """,
            (core2.digest, digest_c),
        ).fetchone()[0]
        Path(trace_ref).write_bytes(b"corrupt")
        assert (
            await vault.lookup_exact(core2.digest, digest_c)
            == LookupResult.HIT_CORRUPT
        )

        no_replay = C038OpenCoreVault(
            str(db_path),
            vault_dir=str(root / "vault"),
            schema_path=str(schema_copy),
            replay_open_trace=None,
        )
        await vault.set_current_capability(digest_a)
        assert (
            await no_replay.lookup_exact(core.digest, digest_a)
            == LookupResult.HIT_CORRUPT
        )

        sql_text = schema_copy.read_text(encoding="utf-8").lower()
        for forbidden in (
            "structural_fp",
            "fingerprint",
            "similarity",
            "equivalence_mapping",
        ):
            assert forbidden not in sql_text

    return {
        "status": "PASS",
        "acceptance_checks": 10,
        "capability_digest_deterministic": True,
        "capability_changes_invalidate": True,
        "verified_exact_hit": True,
        "logical_staleness_without_mass_update": True,
        "corruption_forces_miss_path": True,
        "idempotent_reinsertion": True,
        "concurrent_writers_single_row": True,
        "historical_open_preserved_after_closed_poly": True,
        "structural_matching_absent": True,
        "p_vs_np": "OPEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test")
    print(
        json.dumps(
            asyncio.run(_self_test()),
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
