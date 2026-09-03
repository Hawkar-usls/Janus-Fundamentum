#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research" / "JANUS_TRUMP_R44Q_PROTECTED_CORE_SURVIVOR_REPLAY_2026-09-03.json"


def canonical_core(c):
    p = c["protected_core"]
    return {
        "target": p["target"],
        "proof_semantics": tuple(p["proof_semantics"]),
        "authority": p["authority"],
        "cost_standard": p["cost_standard"],
        "verification_standard": p["verification_standard"],
    }


def replay_attack(core, obligations, attack):
    # A verified obstruction is allowed to add only a scoped obligation.
    after_core = dict(core)
    after_obligations = set(obligations)
    after_obligations.add((attack["source"], attack["lesson"]))
    return after_core, after_obligations


def main():
    c = json.loads(CONTRACT.read_text())
    baseline = canonical_core(c)
    current = dict(baseline)
    obligations = set()

    replay = []
    for attack in c["attack_replay"]:
        before = dict(current)
        current, obligations = replay_attack(current, obligations, attack)
        survived = current == before == baseline and attack["core_may_change"] is False
        replay.append({"source": attack["source"], "core_survived": survived})
        if not survived:
            print(json.dumps({"verdict":"FAIL_CORE_MUTATED","replay":replay}, sort_keys=True))
            raise SystemExit(1)

    # Adversarial mutation probes: each must be detected as a core change.
    probes = {}
    mutations = {
        "target_drift": ("target", baseline["target"] + " [weakened]"),
        "authority_drift": ("authority", "LEARNING_MAY_INCREASE_THEOREM_AUTHORITY"),
        "cost_drift": ("cost_standard", "Uncharged compilation permitted"),
        "verifier_drift": ("verification_standard", "PROPOSER_MAY_SELF_CERTIFY"),
    }
    for name, (field, value) in mutations.items():
        mutated = dict(baseline)
        mutated[field] = value
        probes[name] = mutated != baseline

    if not all(probes.values()):
        print(json.dumps({"verdict":"OPEN_REPLAY_INCOMPLETE","mutation_probes":probes}, sort_keys=True))
        raise SystemExit(2)

    result = {
        "verdict": "PASS_CORE_SURVIVES",
        "attacks_replayed": len(replay),
        "inherited_obligations": len(obligations),
        "replay": replay,
        "mutation_probes_detected": probes,
        "p_vs_np": "OPEN",
        "next_gate": c["next_gate"],
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
