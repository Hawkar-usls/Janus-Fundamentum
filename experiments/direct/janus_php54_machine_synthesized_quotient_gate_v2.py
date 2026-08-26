#!/usr/bin/env python3
"""Compatibility-corrected runner for the exact machine-synthesized quotient gate.

v1 completed the mathematical assertions and failed only while formatting the
final report because it referenced progress_phi as a module function rather
than the EngineState method.  Keep v1 immutable as the failed audit witness and
bind the exact state method here before replaying the same gate.
"""
from experiments.direct import janus_php54_machine_synthesized_quotient_gate as q


def _progress_phi(state):
    return state.progress_phi()


q.base.progress_phi = _progress_phi

if __name__ == "__main__":
    q.main()
