#!/usr/bin/env python3
import argparse,itertools,json,pathlib
COL={1,2,3,4}
def ce(a,b):return tuple(sorted((str(a),str(b))))
def E(P):return {ce(a,b) for a,b in P['edges']}
def h(P,a,b):return ce(a,b) in E(P)
def n(P,v):return {u for u in P['vertices'] if u!=v and h(P,u,v)}
def ip(P,s):
 return len(set(s))==len(s) and all(h(P,s[i],s[j])==(j==i+1) for i in range(len(s)) for j in range(i+1,len(s)))
def p7(P):
 if len(P['vertices'])<7:return None
 for c in itertools.combinations(P['vertices'],7):
  for p in itertools.permutations(c):
   if ip(P,p):return list(p)
 return None
def L(P,v):
 if v in P['S'] or v in P['X0']:return {P['f'][v]}
 return COL-{P['f'][s] for s in n(P,v)&set(P['S'])}
def proper(P,c):return all(c[a]!=c[b] for a,b in E(P))
def conn(P,A):
 A=set(A)
 if not A:return False
 st=[next(iter(A))];seen=set()
 while st:
  v=st.pop()
  if v in seen:continue
  seen.add(v);st.extend((n(P,v)&A)-seen)
 return seen==A
def main():
 ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('out');a=ap.parse_args();root=pathlib.Path(a.run)
 cand=json.load(open(root/'candidate_result.json'));summ=json.load(open(root/'summary.json'));q=json.load(open(root/'001_quarantine.json'));controls=json.load(open(root/'controls.json'))
 w=cand['reachable_escape_receipt'];P=w['P'];Pp=w['post_Lemma10_P_prime'];Q=w['Qhat_ancestor'];c=w['extension_c']
 checks={}
 checks['candidate_reports_C11_escape']=cand['verdict']=='FAIL_P7_ACCEPTABILITY_ESCAPE' and cand['E6']['cell']=='C11' and cand['E6']['classification']=='CELL_REACHABLE_ESCAPE'
 checks['P7_free_exhaustive']=p7(P) is None
 checks['target_P6_induced']=ip(P,['z','y','s1','p','m','n'])
 checks['extension_proper']=proper(P,c)
 checks['old_seed_extended']=all(c[v]==P['f'][v] for v in P['S'])
 checks['raw_Q_modes_only_111']=all(s['mode']=='111' for s in Q['local_states'])
 checks['post_seed_exact']=set(Pp['S'])=={'s1','s2','p','m','n'}
 checks['post_Y0_exact']=set(Pp['Y0'])=={'z'}
 checks['post_Y_exact']=set(Pp['Y'])=={'y','y_prime'}
 checks['post_seed_connected']=conn(Pp,Pp['S'])
 Ly=L(Pp,'y');Lyp=L(Pp,'y_prime');inter=Ly&Lyp
 checks['acceptability_premise']=(not h(Pp,'y','y_prime') and Ly!=Lyp and c['y'] in inter and c['y_prime'] in inter and h(Pp,'y','z') and h(Pp,'y_prime','z'))
 checks['old_new_lists_equal']=L(P,'y')==Ly and L(P,'y_prime')==Lyp
 T=tuple(sorted(n(P,'y')&set(P['S'])));Tp=tuple(sorted(n(P,'y_prime')&set(P['S'])))
 checks['types_exact']=T==('s1',) and Tp==('s2',) and not(set(T)&set(Tp))
 target=next(s for s in Q['local_states'] if tuple(s['T'])==T and tuple(s['T_prime'])==Tp)
 checks['E5_cardinality']=target['mode']=='111' and len(target['P'])+len(target['M'])+len(target['N'])==3
 checks['z_anti_support']=all(not h(Pp,'z',v) for v in ['p','m','n'])
 checks['stable_y_yp_p_n']=all(not h(Pp,a,b) for a,b in itertools.combinations(['y','y_prime','p','n'],2))
 checks['m_color_in_y_list']=Pp['f']['m'] in Ly and not h(Pp,'y','m')
 checks['terminal_first_unsupported_exact']=('induced P6' in w['first_unsupported_inference'] and 'P7-free' in w['first_unsupported_inference'] and 'no contradiction' in w['first_unsupported_inference'])
 checks['matrix_stop']=summ['matrix']['C11']['classification']=='CELL_REACHABLE_ESCAPE' and all(summ['matrix'][x]['analysis_status']=='NOT_REACHED_DUE_TO_STOP' for x in ['C1S','CS1','CSS'])
 checks['no_repair']=summ['repair_attempted'] is False and summ['stop_triggered'] is True
 checks['controls_pass']=all(x['verdict']=='PASS_CONTROL' for x in controls)
 checks['001_quarantine_non_authoritative']=q['verdict']=='CELL_001_QUARANTINED' and q['affects_main_authority'] is False and q['main_C11_path_uses_001'] is False and 'formal_definition' in q and 'completeness_text' in q
 checks['minimum_role_count']=cand['minimization']['vertex_count']==cand['minimization']['role_count_lower_bound']==8 and cand['minimization']['all_roles_distinct'] is True
 ceil=summ['scientific_ceiling'];checks['ceiling_exact']=(ceil['SUBGATE_A']=='NOT_CLAIMED' and ceil['FULL_LEMMA11_P7_LIFT']=='OPEN' and ceil['P7_FREE_4_COLOR_IN_P']=='NOT_PROVED' and ceil['HARDNESS_LOCALIZED']=='NOT_CLAIMED' and ceil['P_VS_NP']=='OPEN')
 verdict='INDEPENDENT_C11_REACHABLE_ESCAPE_VERIFIED' if all(checks.values()) else 'INDEPENDENT_REPLAY_FAIL'
 out={'schema':'janus.trump.p7_split4.lemma11_acceptability_fragment.independent.v1','verdict':verdict,'checks':checks,
      'independent_escape':{'cell':'C11','P7_free':p7(P) is None,'induced_P6':['z','y','s1','p','m','n'],'T':list(T),'T_prime':list(Tp),'old_lists':{'y':sorted(L(P,'y')),'y_prime':sorted(L(P,'y_prime'))},'new_lists':{'y':sorted(Ly),'y_prime':sorted(Lyp)},'first_unsupported_inference':w['first_unsupported_inference']},
      'scientific_ceiling':ceil}
 pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'verdict':verdict,'failed':[k for k,v in checks.items() if not v]},sort_keys=True))
 if verdict!='INDEPENDENT_C11_REACHABLE_ESCAPE_VERIFIED':raise SystemExit(1)
if __name__=='__main__':main()
