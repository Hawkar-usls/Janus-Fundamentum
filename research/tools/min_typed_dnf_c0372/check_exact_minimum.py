from pathlib import Path
import itertools, json, math, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.typed_conditional_backdoor.typed_backdoor import analyze

FULL = (1 << 64) - 1


def hard_core():
    horn = []
    for signs in itertools.product((False, True), repeat=3):
        ids = [(3 + i if pos else i) for i, pos in enumerate(signs, start=1)]
        horn.append(tuple(-v for v in ids))
    affine = tuple((((1 << (i-1)) | (1 << (3+i-1))), 1) for i in range(1,4))
    return tuple(horn), affine


def bits_from_index(idx):
    return tuple((idx >> i) & 1 for i in range(6))


def term_mask(term):
    mask = 0
    for idx in range(64):
        bits = bits_from_index(idx)
        if all(bits[v-1] == int(val) for v, val in term.items()):
            mask |= 1 << idx
    return mask


def enumerate_terminal_terms(horn, affine):
    out = []
    for vals in itertools.product((-1, 0, 1), repeat=6):
        term = {i+1: bool(v) for i, v in enumerate(vals) if v != -1}
        info = analyze(horn, affine, term)
        if info['terminal']:
            mask = term_mask(term)
            out.append({
                'term': term,
                'mask': mask,
                'width': len(term),
                'coverage': mask.bit_count(),
                'sat': bool(info['sat']),
            })
    return out


def maximal_terms(terms):
    keep = []
    for i, t in enumerate(terms):
        dominated = False
        for j, u in enumerate(terms):
            if i == j:
                continue
            if t['mask'] != u['mask'] and (t['mask'] | u['mask']) == u['mask']:
                dominated = True
                break
        if not dominated:
            keep.append(t)
    return keep


def exact_cover_search(terms, slots, strategy='rarest'):
    masks = [t['mask'] for t in terms]
    by_point = [[i for i, m in enumerate(masks) if (m >> p) & 1] for p in range(64)]
    memo = set()
    stats = {'nodes': 0, 'memo_hits': 0, 'bound_prunes': 0}

    def rec(covered, left, chosen):
        stats['nodes'] += 1
        if covered == FULL:
            return tuple(chosen)
        if left == 0:
            return None
        key = (covered, left)
        if key in memo:
            stats['memo_hits'] += 1
            return None
        uncovered = FULL & ~covered
        max_gain = max((m & uncovered).bit_count() for m in masks)
        if max_gain == 0 or math.ceil(uncovered.bit_count() / max_gain) > left:
            stats['bound_prunes'] += 1
            memo.add(key)
            return None
        points = [p for p in range(64) if (uncovered >> p) & 1]
        if strategy == 'rarest':
            p = min(points, key=lambda x: len(by_point[x]))
        else:
            p = points[0]
        candidates = sorted(by_point[p], key=lambda i: (-(masks[i] & uncovered).bit_count(), i))
        for i in candidates:
            new = covered | masks[i]
            ans = rec(new, left-1, chosen + [i])
            if ans is not None:
                return ans
        memo.add(key)
        return None

    answer = rec(0, slots, [])
    stats['memo_states'] = len(memo)
    return answer, stats


def serialize_term(term):
    return {str(k): int(v) for k, v in sorted(term.items())}


def count_exact_k_covers(terms, k, cap_examples=20):
    if k != 4 or len(terms) > 100:
        return {'counted': False}
    count = 0
    examples = []
    for combo in itertools.combinations(range(len(terms)), k):
        union = 0
        for i in combo:
            union |= terms[i]['mask']
        if union == FULL:
            count += 1
            if len(examples) < cap_examples:
                examples.append([serialize_term(terms[i]['term']) for i in combo])
    return {'counted': True, 'count': count, 'examples': examples}


def validate_cover(horn, affine, cover):
    taut = 0
    for idx in range(64):
        bits = bits_from_index(idx)
        if any(all(bits[v-1] == int(val) for v, val in t.items()) for t in cover):
            taut |= 1 << idx
    terminals = [analyze(horn, affine, t)['terminal'] for t in cover]
    return {'tautological': taut == FULL, 'all_terms_terminal': all(terminals), 'coverage': taut.bit_count()}


def main():
    horn, affine = hard_core()
    t0 = time.perf_counter()
    all_terms = enumerate_terminal_terms(horn, affine)
    maximal = maximal_terms(all_terms)
    census = {
        'all_terminal_terms': len(all_terms),
        'maximal_nondominated_terms': len(maximal),
        'max_coverage': max(t['coverage'] for t in all_terms),
        'min_width': min(t['width'] for t in all_terms),
        'all_terminal_sat_flags_false': not any(t['sat'] for t in all_terms),
    }
    lower = math.ceil(64 / census['max_coverage'])
    searches = {}
    found = None
    found_k = None
    for k in (4, 5, 6):
        ans, stats = exact_cover_search(maximal, k, 'rarest')
        searches[str(k)] = {'found': ans is not None, 'stats': stats}
        if ans is not None:
            found = ans
            found_k = k
            break
    if found is None:
        verdict = 'OPEN_IMPLEMENTATION_OR_RESOURCE_LIMIT'
        cover = []
    else:
        cover = [maximal[i]['term'] for i in found]
        verdict = f'PASS_EXACT_MINIMUM_TYPED_TERMINAL_DNF_IS_{found_k}'

    replay = validate_cover(horn, affine, cover) if cover else {}
    independent = {}
    if found_k is not None:
        for k in range(4, found_k + 1):
            ans2, stats2 = exact_cover_search(maximal, k, 'first')
            independent[str(k)] = {'found': ans2 is not None, 'stats': stats2}
    exact4 = count_exact_k_covers(maximal, 4) if found_k == 4 else {'counted': False}

    census_ok = (
        census['all_terminal_terms'] == 594 and
        census['max_coverage'] == 16 and
        census['min_width'] == 2 and
        lower == 4
    )
    replay_ok = bool(cover) and replay.get('tautological') and replay.get('all_terms_terminal')
    minimality_ok = found_k is not None and all(not searches[str(k)]['found'] for k in range(4, found_k))
    independent_ok = found_k is not None and all(
        independent[str(k)]['found'] == (k == found_k) for k in range(4, found_k + 1)
    )
    if not census_ok or (found_k and not replay_ok):
        verdict = 'FALSIFIED_PARENT_TERMINAL_CENSUS_OR_COVER'
    elif found_k is not None and not (minimality_ok and independent_ok):
        verdict = 'OPEN_IMPLEMENTATION_OR_RESOURCE_LIMIT'

    cover_details = []
    for t in cover:
        m = term_mask(t)
        cover_details.append({
            'term': serialize_term(t),
            'width': len(t),
            'coverage': m.bit_count(),
            'mask_hex': f'{m:016x}',
        })
    overlaps = []
    for i in range(len(cover)):
        for j in range(i+1, len(cover)):
            overlaps.append({
                'i': i,
                'j': j,
                'intersection': (term_mask(cover[i]) & term_mask(cover[j])).bit_count(),
            })
    supports = [sorted(t) for t in cover]
    same_support = bool(supports) and all(s == supports[0] for s in supports)

    out = {
        'schema': 'JANUS_TRUMP_EXACT_MINIMUM_TYPED_TERMINAL_DNF_C0372_GATE_V1',
        'verdict': verdict,
        'census': census,
        'coverage_lower_bound': lower,
        'searches': searches,
        'independent_replay_searches': independent,
        'minimum': found_k,
        'minimum_cover': cover_details,
        'cover_replay': replay,
        'cover_pairwise_overlaps': overlaps,
        'all_cover_terms_share_same_support': same_support,
        'shared_support_if_any': supports[0] if same_support else None,
        'exact_four_cover_census': exact4,
        'runtime_ms': round(1000 * (time.perf_counter() - t0), 3),
        'scientific_status': {
            'SAT_IN_P': 'NOT_PROVED',
            'P_VS_NP': 'OPEN',
            'Pi_negative_evidence_weight': 0,
        },
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
