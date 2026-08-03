from __future__ import annotations
import argparse, hashlib, json, random
from janus_c049_1_b1_compact_trajectory_core import *

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def fixture(rng, theta, k):
    raw = []
    if theta == 0:
        for _ in range(rng.randrange(1, 18)):
            raw.append({'left': [], 'right': [], 'value': rng.randrange(k + 1)})
        return raw
    for t in range(theta + 1):
        left = [1 << i for i in range(t)]
        right = [1 << i for i in range(t, theta)]
        for _ in range(rng.randrange(1, 8)):
            raw.append({'left': left, 'right': right, 'value': rng.randrange(k + 1)})
    return raw

def build():
    rng = random.Random(49101)
    cases = []
    for theta in range(5):
        for k in range(6):
            for _ in range(20):
                source = validate_trajectory(fixture(rng, theta, k), theta)
                compact, trace = compactify(source)
                case = {
                    'theta': theta, 'k': k, 'input': encode(source), 'output': encode(compact),
                    'trace': trace, 'input_width': width(source), 'output_width': width(compact),
                    'idempotent': compactify(compact)[0] == compact, 'compact': is_compact(compact),
                    'length_bound': len(compact) <= (2 * theta + 1) * (2 * k + 1),
                }
                case['digest'] = digest(case)
                cases.append(case)
    out = {'artifact': 'C049.1-PHASE-B1-COMPACT-B-TRAJECTORY', 'cases': cases,
           'summary': {'cases': len(cases), 'failures': sum(not (c['idempotent'] and c['compact'] and c['length_bound'] and c['input_width'] == c['output_width']) for c in cases)}}
    out['integrity'] = digest(out)
    return out

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True); args = parser.parse_args()
    with open(args.output, 'w', encoding='utf-8') as handle:
        json.dump(build(), handle, indent=2, sort_keys=True); handle.write('\n')
