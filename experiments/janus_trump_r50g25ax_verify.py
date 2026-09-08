from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import janus_trump_r50g25ax_within_component_separator_affine_quotient as ax

ALLOWED={ax.SEP_PASS,ax.QUOT_PASS,ax.OBSTRUCTION,ax.REL_FAIL}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--result',type=Path,required=True); args=ap.parse_args()
    raw=args.result.read_bytes(); got=json.loads(raw); replay=ax.run()
    assert got['preregistration_commit']==ax.PREREG
    assert got['parent_governed_AW_head']==ax.PARENT
    assert got['residual_hash']==ax.TARGET_HASH
    assert got['verdict'] in ALLOWED
    assert got['truth_oracle']=={'generation':False,'selection':False,'verdict':False}
    assert got['firewall']=={'P_VS_NP':'OPEN','SAT_IN_P':'NOT_PROVED','TRUMP_finished':False}
    for k in ['verdict','residual_hash','residual_CLV','L','L4_budget','target_component','separator','quotient_fallback','proof_carrying_relation','relation_pass']:
        assert got[k]==replay[k], (k,got[k],replay[k])
    sep=got['separator']; assert sep['state_bound_2_pow_w']==2**sep['induced_width']
    assert sep['budget_slack']==got['L4_budget']-sep['state_bound_2_pow_w']
    if got['verdict']==ax.SEP_PASS:
        assert got['relation_pass'] is True
        assert sep['state_bound_2_pow_w']<=got['L4_budget']
        assert not sep['verification_failures']
    if got['verdict']==ax.QUOT_PASS:
        q=got['quotient_fallback']; assert q and q['relation_pass'] and q['state_bound']<=got['L4_budget']
    if got['verdict']==ax.OBSTRUCTION:
        assert sep['state_bound_2_pow_w']>got['L4_budget']
        q=got['quotient_fallback']; assert q is not None and not q['relation_pass']
    print('AX_RESULT_SHA256='+hashlib.sha256(raw).hexdigest())
    print(json.dumps({'verdict':got['verdict'],'induced_width':sep['induced_width'],'state_bound':sep['state_bound_2_pow_w'],'L4_budget':got['L4_budget'],'relation_pass':got['relation_pass']},sort_keys=True))

if __name__=='__main__': main()
