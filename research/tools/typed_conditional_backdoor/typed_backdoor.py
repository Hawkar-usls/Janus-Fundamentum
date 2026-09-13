from collections import Counter

from research.tools.typed_interface_basis_fixpoint.portfolio import solve_component
from research.tools.typed_interface_basis_fixpoint.c0372_protocol import reverse_horn_to_affine_inclusion


def row_vars(row):
    mask,_=row; out=set(); v=1
    while mask:
        if mask & 1: out.add(v)
        mask >>= 1; v += 1
    return out


def simplify_affine(rows, assignment):
    work=[]
    for mask,rhs in rows:
        m=mask; b=rhs
        for v,val in assignment.items():
            bit=1 << (v-1)
            if m & bit:
                m ^= bit; b ^= int(bool(val))
        work.append([m,b])
    pivots={}
    for m,b in work:
        while m:
            p=(m & -m).bit_length()-1
            if p not in pivots: break
            pm,pb=pivots[p]; m ^= pm; b ^= pb
        if not m:
            if b: return None
            continue
        p=(m & -m).bit_length()-1
        pivots[p]=(m,b)
        for q,(qm,qb) in list(pivots.items()):
            if q!=p and (qm & (1<<p)):
                pivots[q]=(qm^m,qb^b)
    return tuple(sorted(set(pivots.values())))


def simplify_horn(clauses, assignment):
    out=[]
    for clause in clauses:
        rem=[]; sat=False
        for lit in clause:
            v=abs(lit)
            if v in assignment:
                if bool(assignment[v]) == (lit>0): sat=True; break
            else: rem.append(lit)
        if sat: continue
        if not rem: return None
        out.append(tuple(rem))
    return tuple(sorted(set(out)))


def constraint_vars(item):
    kind,obj=item
    return {abs(x) for x in obj} if kind=='H' else row_vars(obj)


def split_components(horn, affine):
    items=[('H',c) for c in horn]+[('A',r) for r in affine]
    supports=[constraint_vars(x) for x in items]
    unseen=set(range(len(items))); comps=[]
    while unseen:
        seed=unseen.pop(); ids={seed}; support=set(supports[seed]); changed=True
        while changed:
            changed=False
            for j in list(unseen):
                if support & supports[j]:
                    unseen.remove(j); ids.add(j); support |= supports[j]; changed=True
        h=tuple(items[i][1] for i in sorted(ids) if items[i][0]=='H')
        a=tuple(items[i][1] for i in sorted(ids) if items[i][0]=='A')
        comps.append((h,a))
    return comps


def localize(horn, affine):
    vars_=sorted({abs(l) for c in horn for l in c} | set().union(*(row_vars(r) for r in affine)) if (horn or affine) else set())
    loc={v:i+1 for i,v in enumerate(vars_)}
    lh=tuple(tuple(loc[abs(l)] if l>0 else -loc[abs(l)] for l in c) for c in horn)
    la=[]
    for mask,rhs in affine:
        nm=0
        for v in row_vars((mask,rhs)): nm |= 1 << (loc[v]-1)
        la.append((nm,rhs))
    return lh,tuple(la),len(vars_)


def classify_component(horn, affine):
    if horn and not affine:
        rec=solve_component([{'kind':'HORN','clauses':horn}])
        if rec['terminal']=='CERTIFIED_CONFLICT': return 'CERTIFIED_CONFLICT',False
        return ('2CNF_ONLY' if all(len(c)<=2 for c in horn) else 'HORN_ONLY'),True
    if affine and not horn: return 'AFFINE_ONLY',True
    if not horn and not affine: return 'EMPTY_SAT',True
    lh,la,n=localize(horn,affine)
    inc=reverse_horn_to_affine_inclusion(lh,la,n,2_000_000)
    t=inc['terminal']['status']
    if t in {'HORN_EMPTY_SUBSET'}: return 'CERTIFIED_CONFLICT',False
    if t=='DIRECTED_INCLUSION': return 'HORN_SUBSET_AFFINE',True
    rec=solve_component([{'kind':'HORN','clauses':horn},{'kind':'AFFINE','rows':affine}],2_000_000)
    if rec['terminal']=='CERTIFIED_CONFLICT': return 'CERTIFIED_CONFLICT',False
    return 'MIXED_OPEN',None


def analyze(horn, affine, assignment):
    h=simplify_horn(horn,assignment)
    if h is None: return {'terminal':True,'sat':False,'classes':['CNF_CONFLICT'],'mixed':[],'horn':(), 'affine':()}
    a=simplify_affine(affine,assignment)
    if a is None: return {'terminal':True,'sat':False,'classes':['AFFINE_CONFLICT'],'mixed':[],'horn':h,'affine':()}
    mixed=[]; classes=[]; all_sat=True
    for ch,ca in split_components(h,a):
        cls,sat=classify_component(ch,ca); classes.append(cls)
        if cls=='MIXED_OPEN': mixed.append((ch,ca)); all_sat=None
        elif sat is False: return {'terminal':True,'sat':False,'classes':classes,'mixed':[],'horn':h,'affine':a}
    return {'terminal':not mixed,'sat':all_sat if not mixed else None,'classes':classes,'mixed':mixed,'horn':h,'affine':a}


def choose_var(horn, affine):
    score=Counter()
    for c in horn:
        for l in c: score[abs(l)] += 1
    for r in affine:
        for v in row_vars(r): score[v] += 1
    return min(score, key=lambda v:(-score[v],v))


def solve_core(horn, affine, prefix=None, stats=None):
    if prefix is None: prefix={}
    if stats is None: stats=Counter()
    info=analyze(horn,affine,prefix); stats['visited_states'] += 1
    if info['terminal']:
        return {'kind':'leaf','term':dict(prefix),'sat':info['sat'],'classes':info['classes']},stats
    if len(info['mixed'])>1:
        stats['parallel_splits'] += 1
        kids=[]
        for ch,ca in info['mixed']:
            kid,_=solve_core(ch,ca,{},stats); kids.append(kid)
        return {'kind':'parallel','prefix':dict(prefix),'children':kids},stats
    ch,ca=info['mixed'][0]; v=choose_var(ch,ca); stats['split_nodes'] += 1
    children={}
    for val in (False,True):
        q=dict(prefix); q[v]=val
        children[str(int(val))],_=solve_core(horn,affine,q,stats)
    return {'kind':'split','var':v,'prefix':dict(prefix),'children':children},stats


def tree_metrics(node):
    if node['kind']=='leaf': return {'leaves':1,'depth':0,'max_term_width':len(node['term']),'sat_leaves':int(bool(node['sat']))}
    if node['kind']=='split':
        ms=[tree_metrics(x) for x in node['children'].values()]
        return {'leaves':sum(x['leaves'] for x in ms),'depth':1+max(x['depth'] for x in ms),'max_term_width':max(x['max_term_width'] for x in ms),'sat_leaves':sum(x['sat_leaves'] for x in ms)}
    ms=[tree_metrics(x) for x in node['children']]
    return {'leaves':sum(x['leaves'] for x in ms),'depth':max((x['depth'] for x in ms),default=0),'max_term_width':max((x['max_term_width'] for x in ms),default=0),'sat_leaves':sum(x['sat_leaves'] for x in ms)}


def solve_forest(horn, affine):
    base=analyze(horn,affine,{})
    if base['terminal']:
        tree,stats=solve_core(horn,affine); return {'components':1,'trees':[tree],'stats':dict(stats),'metrics':tree_metrics(tree)}
    trees=[]; stats=Counter()
    for ch,ca in base['mixed']:
        t,_=solve_core(ch,ca,{},stats); trees.append(t)
    ms=[tree_metrics(t) for t in trees]
    return {'components':len(trees),'trees':trees,'stats':dict(stats),'metrics':{'leaves':sum(x['leaves'] for x in ms),'depth':max((x['depth'] for x in ms),default=0),'max_term_width':max((x['max_term_width'] for x in ms),default=0),'sat_leaves':sum(x['sat_leaves'] for x in ms)}}

def tree_decision(node):
    if node['kind']=='leaf': return bool(node['sat'])
    if node['kind']=='split': return any(tree_decision(x) for x in node['children'].values())
    return all(tree_decision(x) for x in node['children'])


def collect_leaf_terms(node):
    if node['kind']=='leaf': return [dict(node['term'])]
    if node['kind']=='split':
        out=[]
        for x in node['children'].values(): out.extend(collect_leaf_terms(x))
        return out
    return []


def generalize_terms(horn, affine, terms):
    generalized=[]
    for term in terms:
        q=dict(term); changed=True
        while changed:
            changed=False
            for v in sorted(list(q), reverse=True):
                r=dict(q); r.pop(v)
                if analyze(horn,affine,r)['terminal']:
                    q=r; changed=True; break
        generalized.append(q)
    unique=[]
    for q in sorted(generalized,key=lambda x:(len(x),sorted(x.items()))):
        if any(all(k in q and q[k]==v for k,v in p.items()) for p in unique):
            continue
        unique.append(q)
    return unique


def solve_forest(horn, affine):
    base=analyze(horn,affine,{})
    if base['terminal']:
        tree,stats=solve_core(horn,affine)
        terms=generalize_terms(horn,affine,collect_leaf_terms(tree))
        m=tree_metrics(tree); m['component_local_term_count']=len(terms)
        return {'components':1,'trees':[tree],'generalized_terms':[terms],'stats':dict(stats),'metrics':m,'sat':tree_decision(tree)}
    trees=[]; terms_by_component=[]; stats=Counter(); decisions=[]
    for ch,ca in base['mixed']:
        t,_=solve_core(ch,ca,{},stats); trees.append(t); decisions.append(tree_decision(t))
        raw=collect_leaf_terms(t)
        terms_by_component.append(generalize_terms(ch,ca,raw) if raw else [])
    ms=[tree_metrics(t) for t in trees]
    metrics={'leaves':sum(x['leaves'] for x in ms),'depth':max((x['depth'] for x in ms),default=0),'max_term_width':max((x['max_term_width'] for x in ms),default=0),'sat_leaves':sum(x['sat_leaves'] for x in ms),'component_local_term_count':sum(len(x) for x in terms_by_component)}
    return {'components':len(trees),'trees':trees,'generalized_terms':terms_by_component,'stats':dict(stats),'metrics':metrics,'sat':all(decisions)}
