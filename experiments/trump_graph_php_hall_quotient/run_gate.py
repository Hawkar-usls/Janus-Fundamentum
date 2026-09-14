from __future__ import annotations
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import solver


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pop = json.loads((ROOT / 'population.json').read_text(encoding='utf-8'))
    rows = []
    for case in pop['cases']:
        z = solver.solve(case['cnf'])
        rows.append({
            'id': case['id'], 'lane': case['lane'], 'truth': case['truth'],
            'admitted': z.get('admitted'), 'decision': z.get('decision'),
            'reason': z.get('reason'), 'certificate': z.get('certificate'),
            'assignment': z.get('assignment'), 'counting_baseline': z.get('counting_baseline'),
            'timing_ms': z.get('timing_ms')
        })
    result = {
        'artifact': 'GRAPH_PHP_CARDINALITY_HALL_QUOTIENT_RUN_V1',
        'population_sha256': pop['population_sha256'],
        'source_hashes': {
            'solver.py': file_sha(ROOT / 'solver.py'),
            'make_population.py': file_sha(ROOT / 'make_population.py'),
            'independent_checker.py': file_sha(ROOT / 'independent_checker.py'),
            'run_gate.py': file_sha(ROOT / 'run_gate.py')
        },
        'cases': rows
    }
    (ROOT / 'run_raw.json').write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
    summary = {}
    for r in rows:
        key = r['lane']; summary.setdefault(key, {'exact': 0, 'total': 0})
        summary[key]['total'] += 1
        summary[key]['exact'] += int(r['admitted'] and r['decision'] == r['truth'])
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
