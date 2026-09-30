#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
except ImportError as exc:  # fail closed
    raise SystemExit(
        "cryptography package required; refusing to seal/unseal without an audited AEAD implementation"
    ) from exc

SCHEMA = "JANUS/SEALED-DISCOVERY/v1"
INFO = b"JANUS-SEALED-DISCOVERY-v1"
DEFAULT_KEY_ENV = "JANUS_SEAL_KEY_B64"


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"), validate=True)


def load_master_key(env_name: str = DEFAULT_KEY_ENV) -> bytes:
    raw = os.environ.get(env_name)
    if not raw:
        raise RuntimeError(f"missing {env_name}; refusing to write or decrypt sealed artifact")
    key = b64d(raw)
    if len(key) != 32:
        raise RuntimeError(f"{env_name} must decode to exactly 32 bytes")
    return key


def derive_artifact_key(master_key: bytes, salt: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=INFO,
    ).derive(master_key)


def canonical_aad(label: str, plaintext_sha256: str) -> bytes:
    aad_obj = {
        "label": label,
        "plaintext_sha256": plaintext_sha256,
        "schema": SCHEMA,
    }
    return json.dumps(aad_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def seal_bytes(plaintext: bytes, master_key: bytes, *, label: str) -> dict:
    plaintext_sha256 = hashlib.sha256(plaintext).hexdigest()
    salt = secrets.token_bytes(32)
    nonce = secrets.token_bytes(12)
    aad = canonical_aad(label, plaintext_sha256)
    artifact_key = derive_artifact_key(master_key, salt)
    ciphertext = AESGCM(artifact_key).encrypt(nonce, plaintext, aad)
    ciphertext_sha256 = hashlib.sha256(ciphertext).hexdigest()
    return {
        "schema": SCHEMA,
        "label": label,
        "cipher": "AES-256-GCM",
        "kdf": "HKDF-SHA-256",
        "kdf_info_b64": b64e(INFO),
        "salt_b64": b64e(salt),
        "nonce_b64": b64e(nonce),
        "aad_b64": b64e(aad),
        "plaintext_commitment_sha256": plaintext_sha256,
        "ciphertext_sha256": ciphertext_sha256,
        "ciphertext_b64": b64e(ciphertext),
        "key_material_in_artifact": False,
        "recipient": {
            "mode": "JANUS_LOCAL_SEALED_ONLY",
            "external_recipient": None,
            "recipient_public_key_fingerprint": None,
        },
        "scientific_boundary": {
            "P_VS_NP": "OPEN",
            "commitment_is_not_correctness_proof": True,
        },
    }


def unseal_object(obj: dict, master_key: bytes) -> bytes:
    if obj.get("schema") != SCHEMA:
        raise RuntimeError("unsupported sealed artifact schema")
    ciphertext = b64d(obj["ciphertext_b64"])
    if hashlib.sha256(ciphertext).hexdigest() != obj["ciphertext_sha256"]:
        raise RuntimeError("ciphertext SHA-256 mismatch")
    salt = b64d(obj["salt_b64"])
    nonce = b64d(obj["nonce_b64"])
    aad = b64d(obj["aad_b64"])
    expected_aad = canonical_aad(obj["label"], obj["plaintext_commitment_sha256"])
    if aad != expected_aad:
        raise RuntimeError("associated-data mismatch")
    artifact_key = derive_artifact_key(master_key, salt)
    plaintext = AESGCM(artifact_key).decrypt(nonce, ciphertext, aad)
    if hashlib.sha256(plaintext).hexdigest() != obj["plaintext_commitment_sha256"]:
        raise RuntimeError("plaintext commitment mismatch")
    return plaintext


def write_json_atomic(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def cmd_seal(args: argparse.Namespace) -> int:
    master_key = load_master_key(args.key_env)
    if args.input == "-":
        plaintext = sys.stdin.buffer.read()
    else:
        plaintext = Path(args.input).read_bytes()
    obj = seal_bytes(plaintext, master_key, label=args.label)
    write_json_atomic(Path(args.output), obj)
    print(json.dumps({
        "status": "SEALED",
        "output": args.output,
        "plaintext_commitment_sha256": obj["plaintext_commitment_sha256"],
        "ciphertext_sha256": obj["ciphertext_sha256"],
    }, sort_keys=True))
    return 0


def cmd_unseal(args: argparse.Namespace) -> int:
    master_key = load_master_key(args.key_env)
    obj = json.loads(Path(args.input).read_text(encoding="utf-8"))
    plaintext = unseal_object(obj, master_key)
    if args.output == "-":
        sys.stdout.buffer.write(plaintext)
    else:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(plaintext)
    return 0


def cmd_selftest(_: argparse.Namespace) -> int:
    key = secrets.token_bytes(32)
    payload = b"JANUS sealed-discovery selftest: no secret material."
    obj = seal_bytes(payload, key, label="SELFTEST")
    assert unseal_object(obj, key) == payload

    tampered = json.loads(json.dumps(obj))
    raw = bytearray(b64d(tampered["ciphertext_b64"]))
    raw[0] ^= 1
    tampered["ciphertext_b64"] = b64e(bytes(raw))
    tampered["ciphertext_sha256"] = hashlib.sha256(bytes(raw)).hexdigest()
    try:
        unseal_object(tampered, key)
    except Exception:
        pass
    else:
        raise AssertionError("tampered ciphertext was accepted")

    try:
        unseal_object(obj, secrets.token_bytes(32))
    except Exception:
        pass
    else:
        raise AssertionError("wrong key was accepted")

    print("PASS: JANUS sealed discovery authenticated-encryption selftest")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fail-closed JANUS sealed-discovery artifact tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("seal")
    s.add_argument("input", help="input path or '-' for stdin")
    s.add_argument("output", help="sealed JSON output path")
    s.add_argument("--label", required=True)
    s.add_argument("--key-env", default=DEFAULT_KEY_ENV)
    s.set_defaults(func=cmd_seal)

    u = sub.add_parser("unseal")
    u.add_argument("input", help="sealed JSON path")
    u.add_argument("output", help="output path or '-' for stdout")
    u.add_argument("--key-env", default=DEFAULT_KEY_ENV)
    u.set_defaults(func=cmd_unseal)

    t = sub.add_parser("selftest")
    t.set_defaults(func=cmd_selftest)
    return p


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
