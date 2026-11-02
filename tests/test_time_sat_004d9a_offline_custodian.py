#!/usr/bin/env python3
"""004D9A independent-offline-custodian synthetic interoperability only.

Test keys are generated only in temporary directories; none is real
third-party witness or production trust root. Tests prove compatibility
with frozen 004D9 verifier and fail closed on source/model tampering.
"""
from __future__ import annotations
import base64
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"time_sat_004_external"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from external_custodian_offline_004d9a import (
    create_key,build_precommit,strict_dimacs,verify_complete_model,
    canonical_receipt,private_not_in_git_worktree
)
from janus_time_sat_004d9_external_intake import (
    canonical_receipt_bytes,check_external_evidence
)

CNF=b"p cnf 3 3\n1 2 0\n-1 2 0\n3 -2 0\n"
MODEL=json.dumps({"signed_model":[1,2,3]},sort_keys=True).encode()


class CustodianTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        folder=Path(self.temp.name)
        self.folder=folder
        self.key=folder/"secret.pem"
        self.ident=folder/"public.json"
        self.cnf=folder/"original.cnf"
        self.model=folder/"full-sat-model.json"
        self.cnf.write_bytes(CNF)
        self.model.write_bytes(MODEL)
        self.issuer="SYNTHETIC_TEST_NOT_INDEPENDENT"
        self.candidate="synthetic-fixture-001"
        self.identity=create_key(self.key,self.ident,self.issuer)

    def precommit(self):
        return build_precommit(self.key,self.issuer,self.candidate,self.cnf,self.model)

    def test_key_is_created_private_mode_0600_never_in_public(self):
        self.assertTrue(self.key.exists())
        self.assertEqual(stat.S_IMODE(self.key.stat().st_mode),0o600)
        self.assertNotIn("PRIVATE KEY",self.ident.read_text())
        self.assertFalse(self.identity["cryptographic_key_proves_admin_independence"])
        with self.assertRaises(ValueError):create_key(self.key,self.ident,self.issuer)

    def test_precommit_interoperates_with_004d9_intake_in_fixture(self):
        commit,receipt=self.precommit()
        self.assertEqual(commit["signed_receipt"],receipt)
        self.assertFalse(commit["original_source_and_model_bytes_included"])
        self.assertEqual(receipt["source_sha256"],sha256(CNF).hexdigest())
        self.assertEqual(receipt["model_sha256"],sha256(MODEL).hexdigest())
        self.assertTrue(commit["original_model_local_full_clause_check"]["complete_model_verified"])
        self.assertEqual(canonical_receipt(receipt),canonical_receipt_bytes(receipt))
        case={k:receipt[k] for k in (
            "candidate_id","external_issuer_id","source_sha256",
            "model_sha256","n_variables","n_clauses","n_literal_occurrences")}
        policy={
            "custodian":{"trusted_ed25519_public_keys_base64":{
                self.issuer:commit["public_identity"]["ed25519_public_key_base64"]},
                "authorized_external_custodians":[self.issuer]},
            "locked_candidate_cohort":[case],
            "input_limits":{"max_source_bytes":134217728,
                            "max_source_variables":5000,
                            "max_source_clauses":30000,
                            "max_source_literals":120000,
                            "max_model_bytes":200000}
        }
        proof=check_external_evidence(policy,case,receipt,self.cnf,self.model)
        self.assertEqual(proof["original_verified_SAT_model"]["verified_original_clause_count"],3)
        self.assertEqual(proof["status"],"SIGNED_PRECOMMITTED_EXTERNAL_SOURCE_SAT_MODEL_AND_SOURCE_PROOF_VERIFIED")
        self.assertEqual(proof["real_world_external_Witness"],"OPEN_PENDING_INDEPENDENT_ADMINISTRATIVE_AUDIT")
        self.assertEqual(proof["incremental_augmented_rank"],0)

    def test_bad_model_must_not_be_signed(self):
        self.model.write_text(json.dumps({"signed_model":[-1,-2,-3]}))
        with self.assertRaisesRegex(ValueError,"fails original source clause"):
            self.precommit()

    def test_source_missing_clause_terminator_rejected(self):
        self.cnf.write_bytes(b"p cnf 3 1\n1 2\n")
        with self.assertRaises(ValueError):self.precommit()

    def test_original_dimacs_incorrect_var_rejected(self):
        self.cnf.write_bytes(b"p cnf 3 1\n4 0\n")
        with self.assertRaises(ValueError):self.precommit()

    def test_model_incomplete_duplicate_bool_rejected(self):
        for model in ([1,2],[1,1,3],[True,2,3],[1,0,3],[1,2,4]):
            self.model.write_text(json.dumps({"signed_model":model}))
            with self.assertRaises(ValueError):self.precommit()

    def test_tamper_signed_receipt_or_public_key_fails(self):
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        commitment,receipt=self.precommit()
        pub=Ed25519PublicKey.from_public_bytes(base64.b64decode(
            commitment["public_identity"]["ed25519_public_key_base64"]))
        signature=base64.b64decode(receipt["signature_base64"])
        pub.verify(signature,canonical_receipt_bytes(receipt))
        forged=deepcopy(receipt);forged["n_clauses"]+=1
        with self.assertRaises(InvalidSignature):
            pub.verify(signature,canonical_receipt_bytes(forged))
        forged=deepcopy(receipt);forged["source_sha256"]="f"*64
        with self.assertRaises(InvalidSignature):
            pub.verify(signature,canonical_receipt_bytes(forged))

    def test_different_signers_produce_distinct_public_keys(self):
        other=self.folder/"other.pem"
        public=self.folder/"other-public.json"
        new=create_key(other,public,"SYNTHETIC_OTHER_ACTOR")
        self.assertNotEqual(new["ed25519_public_key_base64"],
                            self.identity["ed25519_public_key_base64"])

    def test_refuse_secret_inside_current_git_tree(self):
        root=Path(__file__).resolve().parents[1]
        with self.assertRaisesRegex(ValueError,"INSIDE_GIT_WORKTREE"):
            private_not_in_git_worktree(root/".github"/"sensitive-private.pem")

    def test_tautology_not_signing_invalid_model_because_true(self):
        n,m,l,rows=strict_dimacs(b"p cnf 1 1\n1 -1 0\n")
        self.assertEqual((n,m,l),(1,1,2))
        self.assertTrue(verify_complete_model(rows,n,json.dumps(
            {"signed_model":[1]}).encode())["complete_model_verified"])

if __name__=="__main__":
    unittest.main()
