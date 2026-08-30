from mk_r2c_core import canon,restrict,compile_obdd,make_pair,make_random,orders

def support_obdd(comp,node,memo=None):
    memo={} if memo is None else memo
    if node in (0,1): return frozenset()
    if node in memo:return memo[node]
    v,lo,hi=comp['nodes'][node]
    s=frozenset({v})|support_obdd(comp,lo,memo)|support_obdd(comp,hi,memo)
    memo[node]=s;return s

def translate(comp):
    nodes={0:('CONST',False),1:('CONST',True)};uniq={('CONST',False):0,('CONST',True):1};nxt=[2]
    srcmap={0:0,1:1};litcache={};cert_fail=[];work=[0]
    smemo={}
    def mk(k):
        work[0]+=1
        if k in uniq:return uniq[k]
        i=nxt[0];nxt[0]+=1;uniq[k]=i;nodes[i]=k;return i
    def lit(v,pol):
        k=(v,pol)
        if k not in litcache:litcache[k]=mk(('LIT',v,pol))
        return litcache[k]
    def rec(i):
        if i in srcmap:return srcmap[i]
        v,lo,hi=comp['nodes'][i];sl=support_obdd(comp,lo,smemo);sh=support_obdd(comp,hi,smemo)
        if v in sl or v in sh:cert_fail.append({'source_node':i,'failure':'DECOMPOSABILITY_SUPPORT','var':v})
        l=rec(lo);h=rec(hi)
        a0=mk(('AND',lit(v,False),l));a1=mk(('AND',lit(v,True),h));o=mk(('OR',a0,a1))
        srcmap[i]=o;return o
    root=rec(comp['root'])
    return {'root':root,'nodes':nodes,'source_to_dest':srcmap,'local_cert_failures':cert_fail,'translation_work':work[0],'structural_nodes':len(nodes)}

def cond_dd(d,var,val):
    old=d['nodes'];memo={};uniq={('CONST',False):0,('CONST',True):1};nodes={0:('CONST',False),1:('CONST',True)};nxt=[2];work=[0]
    def mk(k):
        work[0]+=1
        if k in uniq:return uniq[k]
        i=nxt[0];nxt[0]+=1;uniq[k]=i;nodes[i]=k;return i
    def rec(i):
        if i in memo:return memo[i]
        k=old[i];t=k[0]
        if t=='CONST':r=1 if k[1] else 0
        elif t=='LIT':r=(1 if (val if k[2] else not val) else 0) if k[1]==var else mk(k)
        else:
            a,b=rec(k[1]),rec(k[2])
            if t=='AND':
                if a==0 or b==0:r=0
                elif a==1:r=b
                elif b==1:r=a
                elif a==b:r=a
                else:r=mk(('AND',a,b))
            else:
                if a==1 or b==1:r=1
                elif a==0:r=b
                elif b==0:r=a
                elif a==b:r=a
                else:r=mk(('OR',a,b))
        memo[i]=r;return r
    root=rec(d['root']);return {'root':root,'nodes':nodes,'condition_work':work[0]}

def var_patterns(vs):
    n=len(vs);M=(1<<(1<<n))-1;patterns={}
    for i,v in enumerate(vs):
        p=0
        for mask in range(1<<n):
            if (mask>>i)&1:p|=1<<mask
        patterns[v]=p
    return M,patterns

def cnf_bits(f,vs):
    M,p=var_patterns(vs);out=M
    if f==((),):return 0
    for c in f:
        q=0
        for lit in c:q |= p[abs(lit)] if lit>0 else (M^p[abs(lit)])
        out &= q
    return out

def dd_bits(d,vs):
    M,p=var_patterns(vs);memo={}
    def rec(i):
        if i in memo:return memo[i]
        k=d['nodes'][i]
        if k[0]=='CONST':r=M if k[1] else 0
        elif k[0]=='LIT':r=p[k[1]] if k[2] else M^p[k[1]]
        elif k[0]=='AND':r=rec(k[1])&rec(k[2])
        else:r=rec(k[1])|rec(k[2])
        memo[i]=r;return r
    return rec(d['root']),len(memo)

def project_bits(bits,vs,var,val):
    idx=vs.index(var);rem=[v for v in vs if v!=var];out=0
    for m in range(1<<len(rem)):
        full=0;j=0
        for i,v in enumerate(vs):
            b=val if v==var else ((m>>j)&1);j+=0 if v==var else 1
            full|=b<<i
        if (bits>>full)&1:out|=1<<m
    return out,rem
