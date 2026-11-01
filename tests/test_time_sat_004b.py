#!/usr/bin/env python3
"""Adversarial no-network 004B resource/syntax/source-identity controls."""
import gzip
import lzma
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004b_acquire import (
    trusted_uri, unpack_bounded, scan_dimacs, BoundedFailure,
)


class ExternalDimacs004BTests(unittest.TestCase):
    def test_exact_source_host_and_gbd_hash_pinned(self):
        x={"hash":"01d6fa8efd18ebfecd06af408958477b",
           "official_uri":"http://benchmark-database.de/file/01d6fa8efd18ebfecd06af408958477b"}
        self.assertEqual(trusted_uri(x),
                         "https://benchmark-database.de/file/01d6fa8efd18ebfecd06af408958477b")
        for y in [
            dict(x,official_uri="http://127.0.0.1/file/"+x["hash"]),
            dict(x,official_uri="https://example.org/file/"+x["hash"]),
            dict(x,official_uri=x["official_uri"]+"?untrusted=1"),
            dict(x,hash="../fake"),
            dict(x,official_uri="file:///etc/passwd"),
        ]:
            with self.assertRaises(BoundedFailure):trusted_uri(y)

    def test_valid_large_dimension_is_not_capped_at_old_240(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"good.cnf"
            f.write_text("c a\np cnf 24001 3\n24001 -4\n 0\nc comment\n1 0\n0\n",encoding="ascii")
            j=scan_dimacs(f)
            self.assertEqual((j["n_variables"],j["n_clauses"]),(24001,3))
            self.assertEqual(j["max_observed_variable"],24001)
            self.assertTrue(j["suitable_for_bounded_solver"])

    def test_invalid_header_range_termination_and_count_are_rejected(self):
        bad=[
            "1 0\np cnf 2 1\n",
            "p cnf 2 1\n3 0\n",
            "p cnf 2 1\n1 2\n",
            "p cnf 2 1\n0\n0\n",
            "p cnf 2 1\n",
            "p cnf 2 1\np cnf 2 1\n0\n",
            "p cnf 2 1\n1 nope 0\n",
            "p cnf 99999999 1\n1 0\n",
            "p cnf 2 1\n\xff 0\n",
        ]
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"invalid.cnf"
            for source in bad:
                with self.subTest(source=source[:40]):
                    f.write_bytes(source.encode("latin1"))
                    with self.assertRaises(BoundedFailure):scan_dimacs(f)

    def test_original_compressed_bytes_and_bomb_stop(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d)
            plain=b"p cnf 3 2\n1 -2 0\n3 0\n"
            for name,pack in [("xz",lzma.compress),("gzip",gzip.compress)]:
                x=d/("raw_"+name+".dat");y=d/("expanded_"+name+".cnf")
                x.write_bytes(pack(plain))
                j=unpack_bounded(x,y)
                self.assertEqual(y.read_bytes(),plain)
                self.assertEqual(j["decoded_format"],name)
                self.assertEqual(scan_dimacs(y)["n_clauses"],2)
                with self.assertRaises(BoundedFailure):
                    unpack_bounded(x,y,limit=3)
                self.assertFalse(y.exists())

    def test_raw_empty_clause_and_negative_literals(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"test.cnf"
            f.write_text("p cnf 500 2\n-1 500 0\n0\n")
            j=scan_dimacs(f)
            self.assertEqual(j["n_variables"],500)
            self.assertEqual(j["n_literal_occurrences"],2)
            self.assertEqual(j["max_clause_width"],2)


if __name__=="__main__": unittest.main()
