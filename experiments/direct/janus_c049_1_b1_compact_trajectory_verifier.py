from __future__ import annotations
import hashlib, json, sys

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def compact(seq):
    data = [(tuple(x['left']), tuple(x['right']), x['value']) for x in seq]
    while True:
        changed = False
        for i in range(1, len(data)):
            if data[i - 1] == data[i]:
                del data[i]; changed = True; break
        if changed:
            continue
        for i in range(len(data)):
            for j in range(i + 2, len(data)):
                if data[i][:2] != data[j][:2]:
                    continue
                values = [x[2] for x in data[i:j + 1]]
                inc = values[0] <= values[-1] and all(values[0] <= z <= values[-1] for z in values[1:-1])
                dec = values[0] >= values[-1] and all(values[0] >= z >= values[-1] for z in values[1:-1])
                if inc or dec:
                    del data[i + 1:j]; changed = True; break
            if changed:
                break
        if not changed:
            return [{'left': list(x[0]), 'right': list(x[1]), 'value': x[2]} for x in data]

def verify(obj):
    integrity = obj.pop('integrity'); assert integrity == digest(obj); obj['integrity'] = integrity
    for case in obj['cases']:
        case_digest = case.pop('digest'); assert case_digest == digest(case); case['digest'] = case_digest
        output = compact(case['input'])
        assert output == case['output']
        assert compact(output) == output
        assert case['input_width'] == case['output_width'] == max(x['value'] for x in output)
        assert len(output) <= (2 * case['theta'] + 1) * (2 * case['k'] + 1)
    assert obj['summary']['failures'] == 0

if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as handle:
        verify(json.load(handle))
    print('VERIFIED')
