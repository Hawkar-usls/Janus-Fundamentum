#!/usr/bin/env python3
"""R20 diagnostic mirror: same frozen R18 DAG operations, preemptible orchestration, no truth."""
from __future__ import annotations
import argparse,json,signal,time,inspect
from pathlib import Path
import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_prospective_unseen_shannon_dag_holdout as r19

TARGETS=("R19-W05","R19-W07","R19-W08","R19-W10")
PREEMPT_SECONDS=90

class DiagnosticPreempt(RuntimeError): pass

def diagnostic_firewall():
    src="\n".join(inspect.getsource(f) for f in (run_world,))
    banned=["Solver(","dpll(","independent_original_allowed","candidate_allowed(","allowed_masks","truth_table"]
    hits=[x for x in banned if x in src]; return {"pass":not hits,"forbidden_hits":hits}

def snapshot(dag,root,step,var,phase,trajectory,started):
    return {"step":step,"variable":var,"phase":phase,"elapsed_seconds":time.monotonic()-started,"active_nodes":len(dag.nodes),"maximum_nodes_seen":dag.max_nodes_seen,"nodes_created_total":dag.budget.nodes_created_total,"restrict_calls_total":dag.budget.restrict_calls,"hashcons_hits":dag.hashcons_hits,"gc_calls":dag.gc_calls,"gc_removed_total":dag.gc_removed_total,"root_support_size":dag.support[root].bit_count() if root in dag.support else None,"completed_steps":len(trajectory)}

def run_world(wid):
    if wid not in TARGETS: raise ValueError(wid)
    freeze,_=r19.load_contracts(); spec=next(w for w in freeze['worlds'] if w['id']==wid);frame,bridge,checks=r19.generate_world(spec)
    started=time.monotonic(); budget=r18.Budget(deadline=started+10_000); dag=r18.Dag(budget); root=r18.compile_cnf(dag,frame); dag.gc(root); order=r18.elimination_order(frame,bridge); trajectory=[]; current={"step":0,"variable":None,"phase":"COMPILED"}
    def handler(signum,frame_obj): raise DiagnosticPreempt("POSIX_PREEMPT_90S")
    old=signal.signal(signal.SIGALRM,handler); signal.setitimer(signal.ITIMER_REAL,PREEMPT_SECONDS)
    try:
        for step,var in enumerate(order,start=1):
            before=len(dag.nodes); calls0=budget.restrict_calls; created0=budget.nodes_created_total; reuse0=dag.hashcons_hits
            current.update(step=step,variable=int(var),phase="RESTRICT_FALSE"); a,ma=dag.restrict(root,var,False)
            after_false=len(dag.nodes)
            current["phase"]="RESTRICT_TRUE"; b,mb=dag.restrict(root,var,True)
            after_true=len(dag.nodes)
            current["phase"]="OR_MERGE"; newroot=dag.OR(a,b); after_or=len(dag.nodes)
            current["phase"]="GC"; removed=dag.gc(newroot); root=newroot; after_gc=len(dag.nodes)
            trajectory.append({"step":step,"variable":int(var),"before_nodes":before,"after_restrict_false_nodes":after_false,"after_restrict_true_nodes":after_true,"after_or_nodes":after_or,"after_gc_nodes":after_gc,"gc_removed":removed,"restrict_calls_step":budget.restrict_calls-calls0,"nodes_created_step":budget.nodes_created_total-created0,"hashcons_hits_step":dag.hashcons_hits-reuse0,"support_after":dag.support[root].bit_count()})
            current["phase"]="BETWEEN_STEPS"
        signal.setitimer(signal.ITIMER_REAL,0)
        return {"schema":"JANUS/TRUMP/R20/DAG_RESOURCE_PREEMPTIBLE_FORENSICS/WORLD_RESULT/v1.0","created_date":"2026-09-02","world_id":wid,"source":spec,"regeneration_checks":checks,"status":"FORENSIC_COMPLETE_ONLY__DO_NOT_UPGRADE_R19","checkpoint":snapshot(dag,root,len(order),order[-1] if order else None,"COMPLETE",trajectory,started),"final_support":sorted(v for v in range(1,spec['frame_variable_count']+2) if dag.support[root]&(1<<(v-1))),"trajectory":trajectory,"truth_accessed":False,"P_VS_NP":"OPEN"}
    except DiagnosticPreempt as e:
        cp=snapshot(dag,root,current['step'],current['variable'],current['phase'],trajectory,started)
        return {"schema":"JANUS/TRUMP/R20/DAG_RESOURCE_PREEMPTIBLE_FORENSICS/WORLD_RESULT/v1.0","created_date":"2026-09-02","world_id":wid,"source":spec,"regeneration_checks":checks,"status":"FORENSIC_PREEMPTED_WITH_CHECKPOINT","reason":str(e),"checkpoint":cp,"trajectory":trajectory,"truth_accessed":False,"P_VS_NP":"OPEN"}
    finally:
        signal.setitimer(signal.ITIMER_REAL,0); signal.signal(signal.SIGALRM,old)

def main():
    a=argparse.ArgumentParser();a.add_argument('--world',required=True);a.add_argument('--output',required=True);z=a.parse_args();fw=diagnostic_firewall();d=run_world(z.world);d['diagnostic_firewall']=fw;Path(z.output).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'world':d['world_id'],'status':d['status'],'checkpoint':d['checkpoint'],'firewall':fw,'P_VS_NP':'OPEN'},indent=2,sort_keys=True));return 2 if not fw['pass'] else 0
if __name__=='__main__':raise SystemExit(main())
