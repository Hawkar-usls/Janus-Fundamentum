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
    records = []
    for theta in range(5):
        for k in range(6):
            for index in range(4):
                source = validate_trajectory(fixture(rng, theta, k), theta)
                compact, trace = compactify(source)
                payload = {'theta': theta, 'k': k, 'index': index, 'input': encode(source), 'output': encode(compact), 'trace': trace}
                records.append({
                    'theta': theta, 'k': k, 'index': index, 'case_digest': digest(payload),
                    'input_length': len(source), 'output_length': len(compact), 'width': width(compact),
                    'trace_steps': len(trace), 'idempotent': compactify(compact)[0] == compact,
                    'length_bound': len(compact) <= (2 * theta + 1) * (2 * k + 1),
                })
    out = {'artifact': 'C049.1-PHASE-B1-COMPACT-B-TRAJECTORY',
           'source': 'arXiv:1507.02184v4 Section 3.1', 'records': records,
           'summary': {'cases': len(records), 'failures': sum(not (r['idempotent'] and r['length_bound']) for r in records)}}
    out['integrity'] = digest(out)
    return out

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True); args = parser.parse_args()
    with open(args.output, 'w', encoding='utf-8') as handle:
        json.dump(build(), handle, indent=2, sort_keys=True); handle.write('\n')
