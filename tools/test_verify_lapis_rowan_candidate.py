import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import verify_lapis_rowan_candidate as v


def artifact():
    raw={"schema_id":v.RESEARCH,"input_sha256":"a"*64,"case_id":"SYNTHETIC",
         "event":"ROWAN_RESULT_COLLECTED_UNVERIFIED",
         "workflow_uuid":"abcdef01-1234-1234-1234-abcdef012345",
         "provider":{"name":"Rowan","workflow_type":"pka","method":"starling"},
         "result":{"strongest_acid_pka":10.17,"strongest_base_pka":None,
                   "kind":"MODEL_PREDICTION_NOT_EXPERIMENT"}}
    facts={"source_class":"ROWAN_PKA","source_input_sha256":"a"*64,
           "case_id":"SYNTHETIC","event":raw["event"],"workflow_uuid":raw["workflow_uuid"],
           "method":"starling","data_status":"MODEL_PREDICTION_UNVERIFIED",
           "values":{"strongest_acid_pka":10.17,"strongest_base_pka":None},
           "provider_reported_credits":None,"scientific_note":"model only"}
    c={"schema":v.CANDIDATE_SCHEMA,"source":{
            "repository":"Hawkar-usls/Janus","adapter":"integrations/rowan",
            "receipt_sha256":v.sha(v.canonical(raw)),"schema_id":v.RESEARCH},
       "facts":facts,"hypothesis_candidate":{
            "status":"UNTESTED","category":"EMPIRICAL_FALSIFICATION_PROPOSAL"},
       "for_fundamentum":{"proof_or_exact_sat_witness":False,"P_VS_NP":"OPEN",
           "scientific_status":"UNVERIFIED","rowan_credits_spent_by_translation":0,
           "rowan_job_created_by_translation":False,
           "independent_source_authentication":False}}
    ir={"schema":v.IR_SCHEMA,"algorithm":{"mode":"explicit_contract",
          "steps":[{"operator":"ANNOTATE"},{"operator":"ANNOTATE"}]},
        "scientific_boundary":{"P_VS_NP":"OPEN","heuristic_translation_is_proof":False}}
    ir["algorithm_sha256"]=v.sha(v.canonical(ir))
    b="rowan -> lapis -> fundamentum\n"
    m={"schema":v.MANIFEST_SCHEMA,
       "source_receipt_canonical_sha256":v.sha(v.canonical(raw)),
       "status":"OFFLINE_TRANSLATION_ONLY","rowan_api_calls":0,
       "credits_spent_by_translator":0,"proof_authority":False,
       "independent_authentication":False}
    return raw,c,ir,b,m


def verify_fixture(raw,c,ir,brief,m):
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);bundle=root/"bundle";bundle.mkdir()
        for name,x in (("candidate.json",c),("algorithm_ir.json",ir)):
            (bundle/name).write_text(json.dumps(x),encoding="utf-8")
        m["candidate_sha256"]=v.sha(v.canonical(c))
        m["algorithm_ir_sha256"]=v.sha(v.canonical(ir))
        m["brief_sha256"]=v.sha(brief.encode())
        (bundle/"manifest.json").write_text(json.dumps(m),encoding="utf-8")
        (bundle/"brief.txt").write_text(brief,encoding="utf-8")
        src=root/"receipt.json";src.write_text(json.dumps(raw),encoding="utf-8")
        return v.verify(bundle,src)


class VerificationTests(unittest.TestCase):
    def test_valid_scoped_bundle(self):
        self.assertEqual(verify_fixture(*artifact())["status"],"STRUCTURALLY_VALID_UNAUTHENTICATED")

    def test_changes_to_observation_cannot_be_rehashed_into_acceptance(self):
        raw,c,ir,b,m=artifact()
        c["facts"]["values"]["strongest_acid_pka"]=99
        self.assertIn("PKA_VALUE_OR_ID_MISMATCH",verify_fixture(raw,c,ir,b,m)["issues"])

    def test_proof_authority_not_imported(self):
        raw,c,ir,b,m=artifact()
        c["for_fundamentum"]["proof_or_exact_sat_witness"]=True
        self.assertIn("FUNDAMENTUM_AUTHORITY_DRIFT",verify_fixture(raw,c,ir,b,m)["issues"])

    def test_code_operator_rejected_even_with_valid_hashes(self):
        raw,c,ir,b,m=artifact()
        ir["algorithm"]["steps"][0]["operator"]="SET"
        ir.pop("algorithm_sha256")
        ir["algorithm_sha256"]=v.sha(v.canonical(ir))
        self.assertIn("IR_SEMANTICS_ESCALATION",verify_fixture(raw,c,ir,b,m)["issues"])

    def test_hypothesis_promotion_rejected(self):
        raw,c,ir,b,m=artifact()
        c["hypothesis_candidate"]["status"]="PROVED"
        self.assertIn("HYPOTHESIS_PROMOTION",verify_fixture(raw,c,ir,b,m)["issues"])

    def test_source_change_rejected(self):
        raw,c,ir,b,m=artifact()
        raw["result"]["strongest_acid_pka"]=11.0
        self.assertIn("SOURCE_RECEIPT_HASH_MISMATCH",verify_fixture(raw,c,ir,b,m)["issues"])

    def test_outside_schema_rejected(self):
        raw,c,ir,b,m=artifact()
        raw["schema_id"]="anything"
        self.assertEqual(verify_fixture(raw,c,ir,b,m)["status"],"BLOCKED")


if __name__=="__main__":
    unittest.main()
