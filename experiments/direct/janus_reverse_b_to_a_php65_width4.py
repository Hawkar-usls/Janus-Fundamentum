#!/usr/bin/env python3
"""Run the exact PHP_6_5 global B->A disambiguator at width 4.

This is not a hand-supplied block identity. Width 4 is tested because the
width-3 exact search leaves six outsiders and every one of its 14,464 maximum
systems fails full-residual S_k symmetry. The same global exact gates decide
whether width 4 is admissible; failure remains a valid result.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_reverse_b_to_a_global_disambiguation as probe

probe.WIDTH = 4
probe.main()
