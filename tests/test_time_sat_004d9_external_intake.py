#!/usr/bin/env python3
"""004D9: synthetic signature fixtures DO NOT equal external independent witness."""
from __future__ import annotations
import base64
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d9_external_intake import (
    canonical_receipt_bytes,check_external_evidence,policy_pending,digest_file
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

EXAMPLE=b"p cnf 2 2\n1 2 0\n-1 -2 0\n"
GOOD_MODEL=json.dumps({"signed_model":[1,-2]},sort_keys=True).encode()
BAD_MODEL=json.dumps({"signed_model":[-1,-2]},sort_keys=True).encode()

class SignedModelIntake(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        self.cnf=root/"orig.cnf";self.cnf.write_bytes(EXAMPLE)
        self.model=root/"model.json";self.model.write_bytes(GOOD_MODEL)
        self.key=Ed25519PrivateKey.generate()
        pub=self.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        self.issuer="TEST_OUTSIDE_ADMIN_EPHEMERAL_NOT_REAL"
        self.case={
            "candidate_id":"fixture-unique-1",
            "external_issuer_id":self.issuer,
            "source_sha256":sha256(EXAMPLE).hexdigest(),
            "model_sha256":sha256(GOOD_MODEL).hexdigest(),
            "n_variables":2,"n_clauses":2,"n_literal_occurrences":4}
        self.policy={
            "custodian":{
              "trusted_ed25519_public_keys_base64":{self.issuer:base64.b64encode(pub).decode()},
              "authorized_external_custodians":[self.issuer]},
            "locked_candidate_cohort":[self.case],
            "input_limits":{
                "max_source_bytes":134217728,
                "max_source_variables":5000,
                "max_source_clauses":30000,
                "max_source_literals":120000,
                "max_model_bytes":200000
            }
        }
        self.receipt={
            "schema":"JANUS-TIME-SAT-004D9-INDEPENDENT-SAT-CUSTODIAN-RECEIPT-V1",
            **self.case}
        self.sign()

    def sign(self):
        data=canonical_receipt_bytes({**self.receipt,"signature_base64":""})
        self.receipt["signature_base64"]=base64.b64encode(self.key.sign(data)).decode()

    def attempt(self):
        return check_external_evidence(self.policy,self.case,self.receipt,self.cnf,self.model)

    def test_fixture_signed_source_model_then_rank(self):
        a=self.attempt()
        self.assertEqual(a["status"],
            "SIGNED_PRECOMMITTED_EXTERNAL_SOURCE_SAT_MODEL_AND_SOURCE_PROOF_VERIFIED")
        self.assertEqual(a["original_verified_SAT_model"]["verified_original_clause_count"],2)
        self.assertEqual(a["new_source_XOR_forms"],0)
        self.assertEqual(a["incremental_augmented_rank"],0)
        self.assertEqual(a["real_world_external_Witness"],
            "OPEN_PENDING_INDEPENDENT_ADMINISTRATIVE_AUDIT")
        self.assertEqual(a["performance_claim"],"NONE")

    def test_no_live_key_or_candidate_fail_closed_before_any_source(self):
        p=json.loads(json.dumps(self.policy))
        p["custodian"]["trusted_ed25519_public_keys_base64"]={}
        self.assertEqual(policy_pending(p)["status"],"WAITING_FOR_EXTERNAL_WITNESS")
        with self.assertRaises(ValueError):check_external_evidence(
            p,self.case,self.receipt,self.cnf,self.model)

    def test_unsigned_or_tampered_signature_rejected(self):
        self.receipt["signature_base64"]="AAAA"
        with self.assertRaises(ValueError):self.attempt()
        self.sign()
        self.receipt["n_clauses"]=3
        with self.assertRaises(ValueError):self.attempt()

    def test_receipt_self_supplied_public_key_is_not_trusted(self):
        self.receipt["public_key"]=self.policy["custodian"]["trusted_ed25519_public_keys_base64"][self.issuer]
        with self.assertRaises(ValueError):self.attempt()

    def test_unapproved_actor_rejected(self):
        self.receipt["external_issuer_id"]="Hawkar-usls"
        self.sign()
        with self.assertRaises(ValueError):self.attempt()

    def test_precommit_source_hash_mismatch_does_not_trigger_rank(self):
        self.cnf.write_bytes(EXAMPLE+b"c altered after original freeze\n")
        with self.assertRaises(ValueError):self.attempt()

    def test_false_sat_model_rejected_even_if_cryptographically_signed(self):
        self.model.write_bytes(BAD_MODEL)
        self.case["model_sha256"]=sha256(BAD_MODEL).hexdigest()
        self.receipt["model_sha256"]=self.case["model_sha256"]
        self.sign()
        with self.assertRaisesRegex(ValueError,"Original complete SAT model failed"):
            self.attempt()

    def test_model_byte_signature_hash_mismatch_rejected(self):
        self.model.write_bytes(BAD_MODEL)
        with self.assertRaisesRegex(ValueError,"model SHA"):
            self.attempt()

    def test_larger_source_than_frozen_limit_rejected(self):
        self.policy["input_limits"]["max_source_bytes"]=4
        with self.assertRaises(ValueError):self.attempt()

    def test_duplicate_source_identity_rejected_by_issuer(self):
        self.case["candidate_id"]="other"
        with self.assertRaises(ValueError):self.attempt()

    def test_only_source_signature_no_inferred_admin_independence(self):
        a=self.attempt()
        self.assertTrue(a["cryptographic_signature_matches_separately_approved_policy_key"])
        self.assertEqual(a["trusted_key_external_administrative_independence"],
                         "REQUIRES_SEPARATE_REAL_WORLD_AUDIT")

if __name__=="__main__":unittest.main()
