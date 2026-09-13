import itertools, json, math, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.min_typed_dnf_c0372.check_exact_minimum import (
    hard_core, bits_from_index, enumerate_terminal_terms, maximal_terms,
    serialize_term,
)
from research.tools.typed_conditional_backdoor.typed_backdoor import analyze


def affine_accepts(affine, bits):
    for mask, rhs in affine:
        p = 0
        for v in range(1, 7):
            if mask & (1 << (v - 1)):
                p ^= bits[v - 1]
        if p != rhs:
            return False
    return True


def affine_domain_mask(affine):
    m = 0
    for idx in range(64):
        if affine_accepts(affine, bits_from_index(idx)):
            m |= 1 << idx
    return m

def restricted_terms(all_terms, domain):
    by_mask = {}
    for t in all_terms:
        m = t['mask'] & domain
        if not m:
            continue
        rec = dict(t)
        rec['domain_mask'] = m
        rec['domain_coverage'] = m.bit_count()
        old = by_mask.get(m)
        if old is None or rec['width'] < old['width']:
            by_mask[m] = rec
    return list(by_mask.values())


def exact_cover_domain(terms, domain, slots):
    masks = [t['domain_mask'] for t in terms]
    points = [p for p in range(64) if (domain >> p) & 1]
    by_point = {p: [i for i,m in enumerate(masks) if (m >> p) & 1] for p in points}
    memo = set(); stats = {'nodes':0,'memo_hits':0,'bound_prunes':0}
    def rec(covered, left, chosen):
        stats['nodes'] += 1
        if (covered & domain) == domain:
            return tuple(chosen)
        if left == 0:
            return None
        key = (covered & domain, left)
        if key in memo:
            stats['memo_hits'] += 1; return None
        uncovered = domain & ~covered
        max_gain = max((m & uncovered).bit_count() for m in masks)
        if max_gain == 0 or math.ceil(uncovered.bit_count()/max_gain) > left:
            stats['bound_prunes'] += 1; memo.add(key); return None
        p = min((q for q in points if (uncovered >> q) & 1), key=lambda q: len(by_point[q]))
        cand = sorted(by_point[p], key=lambda i: (-(masks[i]&uncovered).bit_count(), i))
        for i in cand:
            ans = rec(covered | masks[i], left-1, chosen+[i])
            if ans is not None: return ans
        memo.add(key); return None
    ans = rec(0, slots, [])
    stats['memo_states'] = len(memo)
    return ans, stats

PAIRS = ((1,4),(2,5),(3,6))

def close_affine(partial):
    q = dict(partial)
    changed = True
    while changed:
        changed = False
        for a,b in PAIRS:
            if a in q and b in q:
                if int(q[a]) ^ int(q[b]) != 1:
                    return None
            elif a in q:
                q[b] = not q[a]; changed = True
            elif b in q:
                q[a] = not q[b]; changed = True
    return q


def minimum_literal_depth(horn, affine):
    memo = {}
    def rec(partial):
        q = close_affine(partial)
        if q is None:
            return 0, {'terminal':'AFFINE_CONFLICT'}
        key = tuple(sorted((v,int(x)) for v,x in q.items()))
        if key in memo: return memo[key]
        info = analyze(horn, affine, q)
        if info['terminal']:
            ans = (0, {'terminal':'TYPED', 'assignment':serialize_term(q)})
            memo[key] = ans; return ans
        candidates = [v for v in range(1,7) if v not in q]
        best = None
        for v in candidates:
            d0,t0 = rec({**q, v:False})
            d1,t1 = rec({**q, v:True})
            cand = (1+max(d0,d1), {'split':v,'zero':t0,'one':t1})
            if best is None or cand[0] < best[0]: best = cand
        memo[key] = best
        return best
    depth, tree = rec({})
    return {'depth':depth,'tree':tree,'memo_states':len(memo)}

def main():
    horn, affine = hard_core()
    t0 = time.perf_counter()
    domain = affine_domain_mask(affine)
    all_terms = enumerate_terminal_terms(horn, affine)
    terms = restricted_terms(all_terms, domain)
    max_cov = max(t['domain_coverage'] for t in terms)
    lower = math.ceil(domain.bit_count()/max_cov)
    searches = {}; cover = None; minimum = None
    for k in range(1,7):
        ans, stats = exact_cover_domain(terms, domain, k)
        searches[str(k)] = {'found': ans is not None, 'stats':stats}
        if ans is not None:
            cover = [terms[i] for i in ans]; minimum = k; break
    rev = list(reversed(terms))
    replay, replay_stats = exact_cover_domain(rev, domain, minimum)
    replay_cover = [rev[i] for i in replay] if replay is not None else []
    chosen_mask = 0
    for t in cover: chosen_mask |= t['domain_mask']
    terminals = [analyze(horn, affine, t['term'])['terminal'] for t in cover]
    depth = minimum_literal_depth(horn, affine)
    expected_domain = 1 << 3
    ok = (domain.bit_count()==expected_domain and chosen_mask==domain and all(terminals)
          and replay is not None and minimum>=lower and depth['depth'] is not None)
    verdict = ('PASS_EXACT_REACHABLE_DOMAIN_TYPED_COVER_AND_DEPTH' if ok
               else 'FALSIFIED_DOMAIN_OR_TERMINALITY')
    out = {
      'schema':'JANUS_TRUMP_EXACT_REACHABLE_DOMAIN_TYPED_GUARD_C0372_GATE_V1',
      'verdict':verdict,
      'domain':{'authority':'three frozen GF(2) XOR rows only','size':domain.bit_count(),
                'mask_hex':f'{domain:016x}','rank_expected':3},
      'terminal_universe':{'all_terminal_terms':len(all_terms),'restricted_distinct_masks':len(terms),
                           'max_reachable_coverage':max_cov,'coverage_lower_bound':lower},
      'exact_minimum':minimum,
      'cover':[{'term':serialize_term(t['term']),'reachable_coverage':t['domain_coverage']} for t in cover],
      'searches':searches,
      'independent_replay':{'found':replay is not None,'stats':replay_stats,
                            'cover':[serialize_term(t['term']) for t in replay_cover]},
      'literal_decision_routing':depth,
      'full_cube_minimum_inherited':6,
      'captain_obvious':'states already refuted by the exact affine module are not routing obligations',
      'runtime_ms':round(1000*(time.perf_counter()-t0),3),
      'scientific_status':{'SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0}
    }
    print(json.dumps(out,sort_keys=True))

if __name__ == '__main__':
    main()
