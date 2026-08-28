#!/usr/bin/env python3
"""JANUS PIPPI PIT-STOP LADDER — adaptive d:d learning race.

The race starts at 1:1 and grows one d:d level at a time.  Every stage is
scored on fresh formula fingerprints BEFORE those exact receipts are allowed
into memory.  After scoring, the system enters a PIPPI pit-stop:

  exact receipts -> PIPPI journal -> M2R-PM -> JGPT teacher update
  -> Pivot-Slime update/distillation -> Spider relation ecology
  -> TOPA-Detective exact calibration gate -> Keymaster fusion calibration
  -> PIPPI Mirror -> next fresh stage.

If the current racing score falls below the previous accepted racing score,
the controller rolls difficulty down.  Let drop = previous_score-failed_score.
Recovery is accepted only when a fresh lower-difficulty stage reaches
previous_score + 3.0 points, i.e. the rebound exceeds the loss by at least
three percentage points.  Then the failed level is retried on fresh formulas.
If recovery cannot be demonstrated down to the racing floor (3:3), the run
stops and reports the frontier.

1:1 and 2:2 are formation laps because their exact root landscapes are
symmetric in the frozen track generator.  They are journaled and learned from,
but do not arm the adaptive regression controller.

Important scope boundary: the track formulas are exact UNSAT 2-CNFs.  The
canonical exact 2-SAT solver independently verifies UNSAT, but that shortcut
is deliberately NOT used as the race runtime.  The race benchmarks capped
exact-elimination navigation, not general SAT hardness.

Models and graph attention can only rank candidates.  Every accepted state
transition is exact-verified.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import adaptive_xor_track_probe as track
from experiments.mad_lab import juxtapose_50x50_multiformula_corpus as j50
from experiments.mad_lab import keymaster_50x50_cycle1_teacher_slime as c1

P_VS_NP = "OPEN"
SCHEMA = "JANUS/PIPPI/ADAPTIVE-PITSTOP-LADDER/v1.0.0"
UNBOUNDED_CAP = 10**12
FEATURE_DIM = 7
SEQ_LEN = 7
BOOTSTRAP_50_SEEDS = [1,2,4,5,7,8,11,13,18,21,25,27,28,30,31,32,33,34,37,38,39,40,41,42]


def stable_hash(obj: object) -> str:
    s=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(s.encode()).hexdigest()


def normalize(v: list[float]) -> list[float]:
    if not v: return []
    lo,hi=min(v),max(v)
    if hi-lo < 1e-12: return [0.5]*len(v)
    return [(x-lo)/(hi-lo) for x in v]


def avg_rows(rows: list[list[float]]) -> list[float]:
    if not rows: return [0.0]*FEATURE_DIM
    return [sum(r[j] for r in rows)/len(rows) for j in range(FEATURE_DIM)]


def candidate_tokens(cnf: base.CNF, pivot: int) -> list[list[float]]:
    """Variable-count invariant 7x7 cheap structural tokenization.

    No exact resolvents, raw units, safe labels, oracle routes, or numeric pivot
    IDs are model inputs.  Other-variable rows are sorted by structure and
    pooled into six quantile bins.  The seventh token is a global summary.
    """
    pos=[c for c in cnf if pivot in c]
    neg=[c for c in cnf if -pivot in c]
    retained=[c for c in cnf if pivot not in c and -pivot not in c]
    others=[v for v in base.vars_of(cnf) if v!=pivot]
    pairs=max(1,len(pos)*len(neg))
    rows=[]; conflicts=[]; aligned=[]; overlaps=[]
    for v in others:
        pp=sum(v in c for c in pos); pm=sum(-v in c for c in pos)
        np=sum(v in c for c in neg); nm=sum(-v in c for c in neg)
        conf=pp*nm+pm*np; same=pp*np+pm*nm; ov=(pp+pm)*(np+nm)
        conflicts.append(conf/pairs); aligned.append(same/pairs); overlaps.append(ov/pairs)
        rows.append([
            pp/max(1,len(pos)),pm/max(1,len(pos)),np/max(1,len(neg)),nm/max(1,len(neg)),
            conf/pairs,same/pairs,ov/pairs,
        ])
    rows.sort(key=lambda r: tuple(round(x,12) for x in r))
    pooled=[]
    if rows:
        n=len(rows)
        for b in range(6):
            a=(b*n)//6; z=((b+1)*n)//6
            pooled.append(avg_rows(rows[a:z]))
    else:
        pooled=[[0.0]*FEATURE_DIM for _ in range(6)]
    while len(pooled)<6: pooled.append([0.0]*FEATURE_DIM)
    summary=[
        sum(conflicts)/max(1,len(conflicts)),
        sum(aligned)/max(1,len(aligned)),
        sum(overlaps)/max(1,len(overlaps)),
        max(conflicts,default=0.0),
        max(conflicts,default=0.0)-min(conflicts,default=0.0),
        len(retained)/max(1,len(cnf)),
        math.log1p(len(cnf))/10.0,
    ]
    return pooled[:6]+[summary]


def pattern_key(tokens: list[list[float]]) -> str:
    s=tokens[-1]
    # Deliberately coarse buckets: attention is for discovery, not a proof key.
    q=(round(s[0]*12),round(s[1]*12),round(s[2]*12),round(s[5]*12),round(s[6]*20))
    return "pattern:"+"-".join(map(str,q))


def exact_root_episode(cnf: base.CNF, d: int, seed: int, source: str, stage_serial: int) -> dict[str,Any]:
    fp=base.fingerprint(cnf); vs=list(base.vars_of(cnf)); root_units=base.state_units(cnf)
    sat2=base.solve_2sat_exact(cnf)
    assert sat2 is not None and sat2[0] is False
    tokens=[]; raw=[]; pairs=[]; after=[]
    for p in vs:
        tokens.append(candidate_tokens(cnf,p))
        out,st=base.eliminate_var_capped(cnf,p,UNBOUNDED_CAP)
        assert out is not None and base.verify_elimination_transition(cnf,p,out,UNBOUNDED_CAP)
        raw.append(int(st['raw_units'])); pairs.append(int(st.get('pairs',0))); after.append(base.state_units(out))
    order=sorted(range(len(vs)),key=lambda i:(raw[i],stable_hash(tokens[i])))
    qidx=max(0,min(len(vs)-1,int(0.30*(len(vs)-1))))
    cap=max(root_units,sorted(raw)[qidx])
    mn,mx=min(raw),max(raw)
    rel=[0.0 if mx==mn else (x-mn)/(mx-mn) for x in raw]
    best={i for i,x in enumerate(raw) if x==mn}
    safe={i for i,x in enumerate(raw) if x<=cap}
    return {
        'd':d,'seed':seed,'source':source,'stage_serial':stage_serial,'fingerprint':fp,'cnf':cnf,
        'vars':vs,'tokens':tokens,'raw':raw,'pair_labels':pairs,'after_units':after,'raw_relative':rel,
        'best_indices':sorted(best),'safe_indices':sorted(safe),'local_stress_cap':cap,'root_units':root_units,
        'raw_span':mx-mn,'oracle_root_order':order,
    }


def split_name(fp: str) -> str:
    return 'CALIBRATION' if int(fp[:8],16)%5==0 else 'TRAIN'


def serializable_episode(e: dict[str,Any], include_tokens: bool=False) -> dict[str,Any]:
    out={k:v for k,v in e.items() if k not in {'cnf','tokens'}}
    if include_tokens: out['tokens']=e['tokens']
    return out


def ranking_order(scores: list[float], e: dict[str,Any]) -> list[int]:
    return sorted(range(len(scores)),key=lambda i:(float(scores[i]),stable_hash(e['tokens'][i])))


def best_rank(order: list[int], e: dict[str,Any]) -> int:
    b=set(e['best_indices'])
    return min(order.index(i)+1 for i in b)


def exact_runtime(e: dict[str,Any], root_order: list[int]) -> dict[str,Any]:
    root=e['cnf']; cap=e['local_stress_cap']; checks=0; pair_work=0; raw_sum=0; peak=e['root_units']
    attempts=[]; chosen=None; state=None
    for idx in root_order:
        p=e['vars'][idx]
        checks+=1
        out,st=base.eliminate_var_capped(root,p,cap)
        r=int(st['raw_units']); pr=int(st.get('pairs',0)); pair_work+=pr; raw_sum+=r; peak=max(peak,r)
        attempts.append({'pivot_local_for_audit':p,'raw_units':r,'pair_work':pr,'fit':out is not None})
        if out is not None:
            assert base.verify_elimination_transition(root,p,out,cap)
            chosen=p; state=out; break
    assert state is not None
    if state != ((),):
        for p in sorted(base.vars_of(state)):
            if state==((),): break
            if p not in set(base.vars_of(state)): continue
            checks+=1
            out,st=base.eliminate_var_capped(state,p,UNBOUNDED_CAP)
            assert out is not None and base.verify_elimination_transition(state,p,out,UNBOUNDED_CAP)
            r=int(st['raw_units']); pr=int(st.get('pairs',0)); pair_work+=pr; raw_sum+=r; peak=max(peak,r)
            state=out
    assert state==((),)
    return {'terminal_unsat':True,'exact_checks':checks,'pair_work':pair_work,'raw_units_sum':raw_sum,'peak_raw_units':peak,'chosen_first_pivot_local_for_audit':chosen,'root_attempts':attempts}


def m2r_scores(train: list[dict[str,Any]], target: dict[str,Any], k: int=9) -> list[float]:
    mem=[]
    for e in train:
        for i,tok in enumerate(e['tokens']): mem.append(([x for r in tok for x in r],float(e['raw_relative'][i])))
    if not mem: return [0.5]*len(target['tokens'])
    out=[]
    for tok in target['tokens']:
        v=[x for r in tok for x in r]; near=[]
        for u,y in mem:
            dist=math.sqrt(sum((a-b)**2 for a,b in zip(v,u)))
            near.append((dist,y))
        near=sorted(near,key=lambda z:z[0])[:min(k,len(near))]
        num=sum(y/max(1e-6,d) for d,y in near); den=sum(1/max(1e-6,d) for d,_ in near)
        out.append(num/den)
    return out


def spider_prior_map(attention_path: Path|None, rejected: set[str]) -> dict[str,dict[str,float]]:
    out:dict[str,dict[str,float]]={}
    if attention_path is None or not attention_path.exists(): return out
    for line in attention_path.read_text().splitlines():
        if not line.strip(): continue
        r=json.loads(line)
        if r.get('kind')!='EDGE_ATTENTION': continue
        src=r.get('source'); tgt=r.get('target')
        if not src or src in rejected or not tgt: continue
        out.setdefault(src,{})[tgt]=float(r.get('attention_weight',0.0))
    return out


def spider_scores(e: dict[str,Any], prior: dict[str,dict[str,float]]) -> list[float]:
    vals=[]
    for tok in e['tokens']:
        q=prior.get(pattern_key(tok),{})
        safe=q.get('outcome:SAFE_ROOT',0.0); over=q.get('outcome:OVERFLOW_ROOT',0.0)
        vals.append(0.5+over-safe)
    return normalize(vals)


def model_scores(model: torch.nn.Module, e: dict[str,Any]) -> list[float]:
    x=torch.tensor([e['tokens']],dtype=torch.float32)
    model.eval()
    with torch.no_grad(): return list(map(float,model(x)[0].tolist()))


def adviser_scores(teacher,student,train,e,prior):
    return {
        'JGPT':normalize(model_scores(teacher,e)),
        'SLIME':normalize(model_scores(student,e)),
        'M2R':normalize(m2r_scores(train,e)),
        'SPIDER':spider_scores(e,prior),
    }


def fuse(comp: dict[str,list[float]], w: dict[str,float]) -> list[float]:
    n=len(next(iter(comp.values())))
    return [sum(w[k]*comp[k][i] for k in w) for i in range(n)]


def grid_weights() -> list[dict[str,float]]:
    names=('JGPT','SLIME','M2R','SPIDER'); out=[]
    for a in range(5):
      for b in range(5-a):
       for c in range(5-a-b):
        d=4-a-b-c
        out.append(dict(zip(names,(a/4,b/4,c/4,d/4))))
    return out


def choose_fusion(teacher,student,train,calib,prior) -> tuple[dict[str,float],dict[str,Any]]:
    default={'JGPT':0.5,'SLIME':0.25,'M2R':0.25,'SPIDER':0.0}
    diverse=[e for e in calib if e['raw_span']>0]
    if len(diverse)<3: return default,{'status':'DEFAULT_INSUFFICIENT_CALIBRATION','diverse_calibration':len(diverse)}
    comps=[adviser_scores(teacher,student,train,e,prior) for e in diverse]
    def obj(w):
        ranks=[]; regrets=[]; hits=0
        for e,c in zip(diverse,comps):
            o=ranking_order(fuse(c,w),e); r=best_rank(o,e); ranks.append(r); hits+=int(r==1)
            regrets.append(e['raw'][o[0]]-min(e['raw']))
        return (sum(ranks)/len(ranks),-hits/len(ranks),sum(regrets)/len(regrets),tuple(w[k] for k in ('JGPT','SLIME','M2R','SPIDER')))
    cand=grid_weights(); best=min(cand,key=obj); q=obj(best)
    return best,{'status':'CALIBRATION_ONLY_GRID','mean_best_rank':q[0],'top1_recall':-q[1],'mean_raw_regret':q[2],'candidates':len(cand),'diverse_calibration':len(diverse)}


def target_distribution(e: dict[str,Any]) -> torch.Tensor:
    p=torch.zeros(len(e['vars']),dtype=torch.float32)
    for i in e['best_indices']: p[i]=1/len(e['best_indices'])
    return p


def train_models(teacher,teacher_opt,student,train_pool:list[dict[str,Any]],focus_patterns:set[str],max_eps:int=48) -> dict[str,Any]:
    # Recent experience + older episodes matching current Spider focus.
    recent=train_pool[-max_eps:]
    focused=[e for e in train_pool if any(pattern_key(t) in focus_patterns for t in e['tokens'])]
    seen=set(); work=[]
    for e in list(reversed(focused))+list(reversed(recent)):
        if e['fingerprint'] in seen: continue
        seen.add(e['fingerprint']); work.append(e)
        if len(work)>=max_eps: break
    work=list(reversed(work))
    if not work: return {'episodes':0,'teacher_steps':0,'slime_steps':0}
    teacher.train(); t_losses=[]
    for e in work:
        x=torch.tensor([e['tokens']],dtype=torch.float32); y=torch.tensor([e['raw_relative']],dtype=torch.float32)
        pred=teacher(x)
        mse=F.mse_loss(pred,y)
        if e['raw_span']>0:
            td=target_distribution(e).unsqueeze(0)
            rankloss=-(td*F.log_softmax(-pred/0.12,dim=1)).sum()
            loss=mse+0.25*rankloss
        else: loss=mse
        teacher_opt.zero_grad(set_to_none=True); loss.backward(); torch.nn.utils.clip_grad_norm_(teacher.parameters(),1.0); teacher_opt.step()
        t_losses.append(float(loss.item()))
    teacher.eval(); s_losses=[]; bonds=[]
    for e in work:
        x=torch.tensor([e['tokens']],dtype=torch.float32); y=torch.tensor([e['raw_relative']],dtype=torch.float32)
        with torch.no_grad(): tp=teacher(x)
        sp=student(x); exact=F.mse_loss(sp,y); dist=F.mse_loss(sp,tp)
        if e['raw_span']>0:
            td=target_distribution(e).unsqueeze(0); rankloss=-(td*F.log_softmax(-sp/0.12,dim=1)).sum()
        else: rankloss=torch.tensor(0.0)
        loss=0.55*exact+0.30*dist+0.15*rankloss
        audit=student.slime_step(loss,lr=0.010)
        s_losses.append(float(loss.item())); bonds.append(audit['mean_oxytocin_bond'])
    return {'episodes':len(work),'teacher_steps':len(work),'slime_steps':len(work),'teacher_mean_loss':sum(t_losses)/len(t_losses),'slime_mean_loss':sum(s_losses)/len(s_losses),'mean_oxytocin_bond':sum(bonds)/len(bonds),'mean_slime_trace':sum(student.slime_trace.values())/max(1,len(student.slime_trace))}


def build_relation_edges(train_pool:list[dict[str,Any]],new_fps:set[str],path:Path) -> dict[str,Any]:
    buckets=defaultdict(lambda:{'safe':0,'over':0,'fps':set(),'new':False})
    for e in train_pool:
        safe=set(e['safe_indices'])
        for i,tok in enumerate(e['tokens']):
            pat=pattern_key(tok); outcome='SAFE_ROOT' if i in safe else 'OVERFLOW_ROOT'
            b=buckets[(pat,outcome)]; b['safe']+=int(i in safe); b['over']+=int(i not in safe); b['fps'].add(e['fingerprint']); b['new']|=e['fingerprint'] in new_fps
    rows=[]
    for (pat,outcome),b in sorted(buckets.items()):
        total=b['safe']+b['over']; rate=b['safe']/max(1,total)
        tgt='outcome:'+outcome
        rows.append({
            'edge_key':f'{pat}|{tgt}|EXACT_HISTORY_ASSOCIATION|','source':pat,'target':tgt,'relation':'EXACT_HISTORY_ASSOCIATION',
            'weight':round(0.18+0.34*abs(rate-0.5),6),'observed_this_pass':True,'fresh_evidence_signature':bool(b['new']),
            'evidence_count':total,'independence_count':len(b['fps']),'contradiction_count':min(b['safe'],b['over']),
            'status':'EXACT_HISTORY_DISCOVERY_ASSOCIATION','claim_authority':'DISCOVERY_PRIORITY_ONLY__NOT_CAUSATION_OR_PROOF'
        })
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in rows))
    return {'edges':len(rows),'fresh_edges':sum(r['fresh_evidence_signature'] for r in rows)}


def run_spider(topa_dir:Path,edge_state:Path,prev:Path|None,outdir:Path,pit:int) -> tuple[Path,dict[str,Any]]:
    tool=topa_dir/'tools/topa_spider_attention_ecosystem.py'; assert tool.exists(),tool
    p1=outdir/f'attention-pit{pit}-p1.jsonl'; p2=outdir/f'attention-pit{pit}-p2.jsonl'
    hist=outdir/'attention-history.jsonl'; r1=outdir/f'attention-pit{pit}-p1-receipt.json'; r2=outdir/f'attention-pit{pit}-p2-receipt.json'
    cmd=['python',str(tool),'calibrate','--edge-state',str(edge_state)]
    if prev is not None and prev.exists(): cmd += ['--previous-attention',str(prev)]
    cmd += ['--state',str(p1),'--history',str(hist),'--receipt',str(r1),'--pass-id',f'PIT-{pit}-FRESH','--spiral-rings','3']
    subprocess.run(cmd,check=True)
    # Immediate replay: same relations, no new evidence signature.
    replay=outdir/f'edge-state-pit{pit}-replay.jsonl'; rr=[]
    for line in edge_state.read_text().splitlines():
        if line.strip():
            x=json.loads(line); x['fresh_evidence_signature']=False; rr.append(x)
    replay.write_text(''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in rr))
    subprocess.run(['python',str(tool),'calibrate','--edge-state',str(replay),'--previous-attention',str(p1),'--state',str(p2),'--history',str(hist),'--receipt',str(r2),'--pass-id',f'PIT-{pit}-REPLAY','--spiral-rings','3'],check=True)
    receipt=json.loads(r2.read_text()); assert receipt['status']=='PASS'
    focus=[]
    for line in p2.read_text().splitlines():
        if not line.strip(): continue
        x=json.loads(line)
        if x.get('kind')=='NODE_ATTENTION' and x.get('focus_state') in {'PRIMARY_FOCUS','ACTIVE_FOCUS'}:
            focus.append({'node_id':x.get('node_id'),'focus_state':x.get('focus_state'),'rank':x.get('focus_rank'),'score':x.get('attention_score'),'delta':x.get('attention_delta')})
    return p2,{'receipt':receipt,'focus':sorted(focus,key=lambda x:x.get('rank') or 999)}


def detective_calibration_gate(train_pool:list[dict[str,Any]],calib_pool:list[dict[str,Any]]) -> dict[str,Any]:
    def rates(pool):
        q=defaultdict(lambda:[0,0])
        for e in pool:
            safe=set(e['safe_indices'])
            for i,tok in enumerate(e['tokens']):
                p=pattern_key(tok); q[p][0]+=int(i in safe); q[p][1]+=1
        return {p:(a/n,n) for p,(a,n) in q.items()}
    tr=rates(train_pool); ca=rates(calib_pool); rejected=[]; survived=[]
    for p,(r,n) in tr.items():
        if p not in ca: continue
        cr,cn=ca[p]; diff=abs(r-cr)
        rec={'pattern':p,'train_safe_rate':r,'calibration_safe_rate':cr,'calibration_n':cn,'absolute_gap':diff}
        if cn>=2 and diff>0.45: rejected.append(rec)
        else: survived.append(rec)
    return {'mode':'TOPA_DETECTIVE_EXACT_CALIBRATION_GATE__NUMERIC_HARNESS_SUBSET','rejected':rejected,'survived':survived,'rejected_patterns':[x['pattern'] for x in rejected],'GRAPH_EDGE_IS_NOT_CAUSATION':True}


def efficiency_score(static:dict[str,Any],learned:dict[str,Any]) -> float:
    # 100 = static parity.  >100 = better search efficiency.  This score is
    # intentionally dimensionless; wall time is reported separately.
    ratios=[]
    for key,w in [('pair_work',0.55),('exact_checks',0.25),('raw_units_sum',0.20)]:
        ratios.append((max(1e-12,static[key]/max(1e-12,learned[key])),w))
    # geometric blend penalizes a severe regression in any major component.
    return 100.0*math.exp(sum(w*math.log(r) for r,w in ratios)/sum(w for _,w in ratios))


def stage_score(stage_eps:list[dict[str,Any]],teacher,student,train_pool,prior,weights) -> dict[str,Any]:
    totals=defaultdict(lambda:defaultdict(float)); top1=0; ranks=[]; regrets=[]; per=[]
    for e in stage_eps:
        comp=adviser_scores(teacher,student,train_pool,e,prior)
        learned_order=ranking_order(fuse(comp,weights),e)
        static_order=sorted(range(len(e['vars'])),key=lambda i:e['vars'][i])
        oracle_order=e['oracle_root_order']
        policies={'STATIC':static_order,'KEYMASTER':learned_order,'ORACLE':oracle_order}
        rt={name:exact_runtime(e,o) for name,o in policies.items()}
        br=best_rank(learned_order,e); ranks.append(br); top1+=int(br==1); regrets.append(e['raw'][learned_order[0]]-min(e['raw']))
        for name,r in rt.items():
            for k in ('exact_checks','pair_work','raw_units_sum'): totals[name][k]+=r[k]
            totals[name]['peak_raw_units']=max(totals[name]['peak_raw_units'],r['peak_raw_units'])
        per.append({'fingerprint':e['fingerprint'],'seed':e['seed'],'raw_span':e['raw_span'],'cap':e['local_stress_cap'],'best_rank':br,'static':rt['STATIC'],'keymaster':rt['KEYMASTER'],'oracle':rt['ORACLE'],'adviser_top1':{k:ranking_order(v,e)[0] for k,v in comp.items()}})
    agg={k:dict(v) for k,v in totals.items()}
    score=efficiency_score(agg['STATIC'],agg['KEYMASTER'])
    return {'performance_index':score,'aggregate':agg,'top1_best_recall':top1/len(stage_eps),'mean_best_rank':sum(ranks)/len(ranks),'mean_top1_raw_regret':sum(regrets)/len(regrets),'per_formula':per}


def make_track_stage(d:int,stage_serial:int,count:int,used:set[str]) -> list[dict[str,Any]]:
    out=[]; j=0
    while len(out)<count:
        seed=900_000_000+stage_serial*100_003+d*1009+j*37
        cnf,_=track.construct(d,seed); e=exact_root_episode(cnf,d,seed,'ADAPTIVE_XOR_TRACK',stage_serial); j+=1
        if e['fingerprint'] in used: continue
        used.add(e['fingerprint']); out.append(e)
    return out


def bootstrap_50(used:set[str]) -> tuple[list[dict[str,Any]],dict[str,Any]]:
    eps=[]; checks=0; pairs=0
    for s in BOOTSTRAP_50_SEEDS:
        cnf=j50.construct(s); e=exact_root_episode(cnf,50,s,'FROZEN_50x50_BOOTSTRAP',-1)
        used.add(e['fingerprint']); eps.append(e); checks+=len(e['vars']); pairs+=sum(e['pair_labels'])
    return eps,{'formulas':len(eps),'root_exact_transition_checks':checks,'root_pair_label_work':pairs,'source':'PIPPI_50x50_CYCLE1 historical train fingerprints only','route_exhaustive_replay_performed':False}


def append_jsonl(path:Path,row:dict[str,Any]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,sort_keys=True,separators=(',',':'))+'\n')


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--topa-dir',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--max-d',type=int,default=32)
    ap.add_argument('--formulas-per-stage',type=int,default=6)
    ap.add_argument('--max-stages',type=int,default=64)
    ap.add_argument('--time-budget-seconds',type=float,default=720.0)
    ap.add_argument('--recovery-margin',type=float,default=3.0)
    args=ap.parse_args()
    random.seed(20260828); torch.manual_seed(20260828); torch.set_num_threads(2)
    out=args.out_dir; out.mkdir(parents=True,exist_ok=True); journal=out/'pippi-journal.jsonl'
    start=time.perf_counter(); used:set[str]=set()

    memory,boot=bootstrap_50(used)
    teacher=c1.JGPTPivotTeacher(); teacher_opt=torch.optim.AdamW(teacher.parameters(),lr=0.004,weight_decay=0.002)
    student=c1.PivotSlimeStudent()
    attention_state:Path|None=None; rejected:set[str]=set(); focus_patterns:set[str]=set(); fusion={'JGPT':0.5,'SLIME':0.25,'M2R':0.25,'SPIDER':0.0}
    train_pool=[e for e in memory if split_name(e['fingerprint'])=='TRAIN']; calib_pool=[e for e in memory if split_name(e['fingerprint'])=='CALIBRATION']
    initial_train=train_models(teacher,teacher_opt,student,train_pool,set())
    # Initial pre-race Spider/PIPPI pit-stop built only from historical exact receipts.
    edge=out/'edge-state-pit0.jsonl'; er=build_relation_edges(train_pool,{e['fingerprint'] for e in memory},edge)
    attention_state,spider=run_spider(args.topa_dir,edge,None,out,0)
    detective=detective_calibration_gate(train_pool,calib_pool); rejected=set(detective['rejected_patterns'])
    prior=spider_prior_map(attention_state,rejected); fusion,fcal=choose_fusion(teacher,student,train_pool,calib_pool,prior)
    focus_patterns={x['node_id'] for x in spider['focus'] if str(x.get('node_id','')).startswith('pattern:')}
    append_jsonl(journal,{'kind':'PITSTOP','pit':0,'phase':'PRE_RACE_BOOTSTRAP','bootstrap':boot,'train':initial_train,'spider':spider,'detective':detective,'fusion_weights':fusion,'fusion_calibration':fcal,'P_VS_NP':P_VS_NP})

    history=[]; pit=0; stage_serial=0; current_d=1; highest_accepted=0; prev_accepted_score=None
    rollback=None; stop_reason=None
    while stage_serial<args.max_stages and current_d<=args.max_d:
        if time.perf_counter()-start > args.time_budget_seconds:
            stop_reason='TIME_BUDGET'; break
        stage_serial+=1
        stage_eps=make_track_stage(current_d,stage_serial,args.formulas_per_stage,used)
        prior=spider_prior_map(attention_state,rejected)
        # Quantized student copy is used at inference, while full student remains trainable.
        qstudent=copy.deepcopy(student); qaudit=c1.quantize_int8_inplace(qstudent)
        scored=stage_score(stage_eps,teacher,qstudent,train_pool,prior,fusion)
        score=float(scored['performance_index'])
        state='FORMATION' if current_d<3 else ('ROLLBACK' if rollback else 'RACING')
        event={'kind':'STAGE','stage_serial':stage_serial,'difficulty':f'{current_d}:{current_d}','d':current_d,'state':state,'score_before_learning_from_this_stage':score,'metrics':scored,'fusion_weights_used':fusion,'int8_tensor_count':qaudit['tensor_count'],'fresh_fingerprints':[e['fingerprint'] for e in stage_eps],'elapsed_seconds':time.perf_counter()-start,'P_VS_NP':P_VS_NP}
        append_jsonl(journal,event); history.append(event)

        # Adaptive controller decision uses ONLY the pre-pit-stop fresh score.
        decision={'action':'CONTINUE'}
        if current_d>=3:
            if rollback is None:
                if prev_accepted_score is None:
                    prev_accepted_score=score; highest_accepted=max(highest_accepted,current_d); decision={'action':'ACCEPT_FIRST_RACING_REFERENCE'}
                elif score >= prev_accepted_score:
                    prev_accepted_score=score; highest_accepted=max(highest_accepted,current_d); decision={'action':'ACCEPT_AND_INCREASE'}
                else:
                    drop=prev_accepted_score-score; target=prev_accepted_score+args.recovery_margin
                    rollback={'failed_d':current_d,'failed_score':score,'previous_accepted_score':prev_accepted_score,'drop':drop,'recovery_target':target,'rollback_from':current_d}
                    decision={'action':'REGRESSION_ROLLBACK','drop':drop,'recovery_target':target}
            else:
                if score >= rollback['recovery_target']:
                    decision={'action':'RECOVERY_CONFIRMED_RETRY_FAILED','recovery_target':rollback['recovery_target'],'rebound_from_failed':score-rollback['failed_score']}
                elif current_d<=3:
                    decision={'action':'STOP_RECOVERY_NOT_REACHED_AT_RACING_FLOOR','recovery_target':rollback['recovery_target']}
                else:
                    decision={'action':'ROLL_BACK_ONE_MORE_LEVEL','recovery_target':rollback['recovery_target']}
        event['controller_decision']=decision
        # Rewrite is avoided: emit explicit controller event for append-only provenance.
        append_jsonl(journal,{'kind':'CONTROLLER','stage_serial':stage_serial,'d':current_d,**decision,'P_VS_NP':P_VS_NP})

        # PIPPI pit-stop: only now do fresh exact receipts become training/memory data.
        memory.extend(stage_eps)
        new_fps={e['fingerprint'] for e in stage_eps}
        train_pool=[e for e in memory if split_name(e['fingerprint'])=='TRAIN']
        calib_pool=[e for e in memory if split_name(e['fingerprint'])=='CALIBRATION']
        pit+=1
        train_audit=train_models(teacher,teacher_opt,student,train_pool,focus_patterns)
        edge=out/f'edge-state-pit{pit}.jsonl'; edge_audit=build_relation_edges(train_pool,new_fps,edge)
        attention_state,spider=run_spider(args.topa_dir,edge,attention_state,out,pit)
        detective=detective_calibration_gate(train_pool,calib_pool); rejected=set(detective['rejected_patterns'])
        prior=spider_prior_map(attention_state,rejected)
        fusion,fcal=choose_fusion(teacher,student,train_pool,calib_pool,prior)
        focus_patterns={x['node_id'] for x in spider['focus'] if str(x.get('node_id','')).startswith('pattern:')}
        mirror={'kind':'PITSTOP','pit':pit,'after_stage':stage_serial,'d':current_d,'new_exact_receipts':len(stage_eps),'memory_formulas':len(memory),'train_formulas':len(train_pool),'calibration_formulas':len(calib_pool),'training':train_audit,'relation_edges':edge_audit,'spider_focus':spider['focus'],'detective':detective,'next_fusion_weights':fusion,'fusion_calibration':fcal,'controller_decision':decision,'performance_history':[{'stage':h['stage_serial'],'d':h['d'],'score':h['score_before_learning_from_this_stage'],'state':h['state']} for h in history],'P_VS_NP':P_VS_NP}
        append_jsonl(journal,mirror)
        (out/f'pippi-mirror-pit{pit}.json').write_text(json.dumps(mirror,indent=2,sort_keys=True)+'\n')

        # Execute controller after pit-stop.
        act=decision['action']
        if act in {'CONTINUE','ACCEPT_FIRST_RACING_REFERENCE','ACCEPT_AND_INCREASE'}:
            current_d+=1
        elif act=='REGRESSION_ROLLBACK':
            current_d=max(3,current_d-1)
        elif act=='ROLL_BACK_ONE_MORE_LEVEL':
            current_d=max(3,current_d-1)
        elif act=='RECOVERY_CONFIRMED_RETRY_FAILED':
            current_d=int(rollback['failed_d']); rollback=None
        elif act=='STOP_RECOVERY_NOT_REACHED_AT_RACING_FLOOR':
            stop_reason='RECOVERY_NOT_REACHED_AT_3x3_FLOOR'; break
        else:
            current_d+=1

    if stop_reason is None:
        if current_d>args.max_d: stop_reason='MAX_D_REACHED'
        elif stage_serial>=args.max_stages: stop_reason='MAX_STAGES_REACHED'
        else: stop_reason='ENDED'
    racing=[h for h in history if h['d']>=3]
    best=max(racing,key=lambda h:h['score_before_learning_from_this_stage']) if racing else None
    result={
        'schema':SCHEMA,'status':'ADAPTIVE_RACE_COMPLETE__EXACT_TRANSITIONS_VERIFIED','P_VS_NP':P_VS_NP,
        'rules':{'start':'1:1','formation_laps':['1:1','2:2'],'difficulty_step':1,'pitstop_before_every_next_stage':True,'regression_trigger':'score < previous accepted racing score','recovery_rule':'fresh rollback score >= previous accepted score + 3.0 points','recovery_margin_points':args.recovery_margin,'rollback_floor':'3:3'},
        'scope':{'formula_family':'balanced inconsistent XOR 2-CNF','exact_2sat_shortcut_available':True,'exact_2sat_shortcut_used_for_race_runtime':False,'race_runtime':'capped exact elimination navigation','general_sat_hardness_claim':False},
        'bootstrap':boot,'stages_completed':len(history),'pitstops_completed':pit,'highest_accepted_d':highest_accepted,'frontier':f'{highest_accepted}:{highest_accepted}' if highest_accepted else None,'stop_reason':stop_reason,
        'best_observed_racing_stage':None if best is None else {'stage':best['stage_serial'],'d':best['d'],'score':best['score_before_learning_from_this_stage']},
        'history':[{'stage':h['stage_serial'],'d':h['d'],'state':h['state'],'score':h['score_before_learning_from_this_stage'],'top1':h['metrics']['top1_best_recall'],'mean_rank':h['metrics']['mean_best_rank'],'static':h['metrics']['aggregate']['STATIC'],'keymaster':h['metrics']['aggregate']['KEYMASTER'],'oracle':h['metrics']['aggregate']['ORACLE']} for h in history],
        'final_fusion_weights':fusion,'final_detective_rejected_patterns':sorted(rejected),'elapsed_seconds':time.perf_counter()-start,
        'resource_accounting':{'symbolic_runtime_metrics_logged_separately':True,'model_training_walltime_not_added_to_pair_work':True,'spider_walltime_not_added_to_pair_work':True,'GLOBAL_RESOURCE_POSITIVE':'UNKNOWN'},
        'scientific_firewall':{'FRESH_STAGE_SCORED_BEFORE_LEARNING_FROM_IT':True,'ROLLBACK_USES_FRESH_FINGERPRINTS':True,'PIVOT_NUMERIC_ID_IS_NOT_MODEL_FEATURE':True,'EXACT_RAW_UNITS_ARE_LABELS_NOT_MODEL_INPUTS':True,'ATTENTION_WEIGHT_IS_NOT_EVIDENCE_WEIGHT':True,'SPIDER_EDGE_IS_NOT_CAUSATION':True,'MODEL_PREDICTION_IS_NOT_PROOF':True,'KEYMASTER_ONLY_REORDERS_EXACT_CHECKS':True,'EVERY_ACCEPTED_TRANSITION_EXACT_VERIFIED':True,'NO_SAME_RUN_THEOREM_PROMOTION':True,'P_VS_NP':P_VS_NP}
    }
    (out/'adaptive-race-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'frontier':result['frontier'],'stages':result['stages_completed'],'pitstops':result['pitstops_completed'],'stop_reason':stop_reason,'best_stage':result['best_observed_racing_stage'],'final_weights':fusion,'P_VS_NP':P_VS_NP},indent=2,sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
