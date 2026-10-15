#!/usr/bin/env python3
"""Freeze the E4.5 mathematical instance into compact self-contained JSON.

This exporter MAY import JANUS research modules, but E4.6 clean-room
verifier MUST NOT import it or any other research modules. A separately
versioned fixture is generated from this exporter, and CI checks it
matches the frozen canonical data exactly. If source shifts, DO NOT
silently regenerate old proof certificate.
"""
import json
from r5_cycle_parity_certificate_20261015 import context
from r5_cooperative_scl_coverage_20261015 import fingerprint

def fixture():
    base,meta,frame,signs,sigma0,y,witness,cover,z,kercoord=context()
    return {
        "version":"R5_E46_FROZEN_CLEAN_ROOM_1",
        "source_sha256":fingerprint(base),
        "base_rows":[list(row) for row in base],
        "sat_voltage_bits_decimal":str(sigma0),
        "quotient_generator_bits_decimal":[str(v) for v in frame["non_gauge_basis"]],
        "z_star_bits_decimal":str(z),
        "ternary_y":list(y),
        "sat_witness_decimal":str(witness),
        "expected":{"base_n":36,"base_unsat":True,"base_nullity":6,
                    "base_rank":30,"phi_rank":26,
                    "gauge_rank":71,"quotient_dimension":11,
                    "two_lift_rank":65,"two_lift_nullity":7,
                    "z_weight":20,"G_z_components":1,
                    "G_z_cycles":11,"Psi_rank":5,
                    "SAT_classes":64,"UNSAT_classes":1984,
                    "SAT_solution_count_per_class":2,
                    "Y_z_count":1}
    }

if __name__=="__main__":
    print(json.dumps(fixture(),sort_keys=True,separators=(",",":")))
