import hashlib, json

from research.tools.apma_dense_cardinality.apma_dense_cardinality import compile_c023_dense_image

SCHEMA_ID = 'C023_C034_NAND3_NEQ_V1'


def _norm_clause(c):
    return tuple(sorted((int(x) for x in c), key=lambda x:(abs(x),x)))


def _canon_image(image):
    obj={
        'n': int(image['n']),
        'horn': sorted([list(_norm_clause(c)) for c in image['horn']]),
        'affine': sorted([[int(m),int(b)] for m,b in image['affine']]),
        'provenance': image.get('provenance',{}),
    }
    return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()


def checkpoint_hash(image):
    return hashlib.sha256(_canon_image(image)).hexdigest()


def source_hash(source):
    obj=sorted([list(_norm_clause(c)) for c in source])
    return hashlib.sha256(json.dumps(obj,separators=(',',':')).encode()).hexdigest()


def encode_c023(source,n,provenance_schema=SCHEMA_ID):
    horn=[]
    for clause in source:
        if not (1 <= len(clause) <= 3):
            raise ValueError('source clause width must be 1..3')
        falsity=[n+abs(l) if l>0 else abs(l) for l in clause]
        horn.append(_norm_clause(tuple(-v for v in falsity)))
    affine=[]
    for i in range(1,n+1):
        affine.append(((1<<(i-1)) | (1<<(n+i-1)),1))
    return {
        'n':n,
        'horn':tuple(sorted(horn)),
        'affine':tuple(sorted(affine)),
        'provenance':{
            'schema':provenance_schema,
            'source_n':n,
            'source_cnf_sha256':source_hash(source),
        },
    }


def reverse_c023(image):
    n=int(image.get('n',0)); prov=image.get('provenance',{})
    if n <= 0 or prov.get('schema') != SCHEMA_ID or int(prov.get('source_n',-1)) != n:
        return {'status':'MORPH_FAIL','reason':'PROVENANCE_SCHEMA_OR_N'}
    want_affine={((1<<(i-1)) | (1<<(n+i-1)),1) for i in range(1,n+1)}
    got_affine={(int(m),int(b)) for m,b in image.get('affine',())}
    if got_affine != want_affine or len(image.get('affine',())) != n:
        return {'status':'MORPH_FAIL','reason':'NEQ_PAIR_CERTIFICATE'}
    source=[]
    for clause in image.get('horn',()):
        if not (1 <= len(clause) <= 3) or any(int(l)>=0 for l in clause):
            return {'status':'MORPH_FAIL','reason':'HORN_IMAGE_GRAMMAR'}
        out=[]
        for lit in clause:
            v=abs(int(lit))
            if not (1 <= v <= 2*n):
                return {'status':'MORPH_FAIL','reason':'VARIABLE_RANGE'}
            out.append(-v if v<=n else v-n)
        source.append(_norm_clause(tuple(out)))
    source=tuple(sorted(source))
    if source_hash(source) != prov.get('source_cnf_sha256'):
        return {'status':'MORPH_FAIL','reason':'SOURCE_HASH_MISMATCH'}
    re=encode_c023(source,n,SCHEMA_ID)
    if tuple(re['horn']) != tuple(sorted(_norm_clause(c) for c in image['horn'])) or tuple(re['affine']) != tuple(sorted(image['affine'])):
        return {'status':'MORPH_FAIL','reason':'REENCODING_MISMATCH'}
    return {'status':'MORPH_PASS','source':source,'certificate':{'source_hash':source_hash(source),'n':n}}


def classify_source(source):
    if all(len(c)<=2 for c in source): return '2CNF'
    if all(sum(1 for l in c if l>0)<=1 for c in source): return 'HORN'
    if all(sum(1 for l in c if l<0)<=1 for c in source): return 'DUAL_HORN'
    return 'GENERAL_3CNF'


def _horn_solve(source,n):
    rules=[]; bad=[]
    for c in source:
        pos=[l for l in c if l>0]
        neg=[-l for l in c if l<0]
        if len(pos)>1: raise ValueError('not Horn')
        if pos: rules.append((set(neg),pos[0]))
        else: bad.append(set(neg))
    true=set(); changed=True
    while changed:
        changed=False
        for ant,head in rules:
            if head not in true and ant <= true:
                true.add(head); changed=True
    if any(ant <= true for ant in bad): return {'sat':False,'witness':None}
    return {'sat':True,'witness':{i:(i in true) for i in range(1,n+1)}}


def _dual_horn_solve(source,n):
    transformed=tuple(tuple(-l for l in c) for c in source)
    r=_horn_solve(transformed,n)
    if not r['sat']: return r
    return {'sat':True,'witness':{i:not r['witness'][i] for i in range(1,n+1)}}


def _2sat_solve(source,n):
    N=2*n; g=[[] for _ in range(N)]; gr=[[] for _ in range(N)]
    def node(l):
        v=abs(l)-1; return 2*v + (0 if l>0 else 1)
    def add(a,b):
        u=node(a); v=node(b); g[u].append(v); gr[v].append(u)
    for c in source:
        if len(c)==1: a=b=c[0]
        elif len(c)==2: a,b=c
        else: raise ValueError('not 2CNF')
        add(-a,b); add(-b,a)
    seen=[False]*N; order=[]
    def dfs(v):
        seen[v]=True
        for w in g[v]:
            if not seen[w]: dfs(w)
        order.append(v)
    for v in range(N):
        if not seen[v]: dfs(v)
    comp=[-1]*N
    def rdfs(v,cid):
        comp[v]=cid
        for w in gr[v]:
            if comp[w]<0: rdfs(w,cid)
    cid=0
    for v in reversed(order):
        if comp[v]<0: rdfs(v,cid); cid+=1
    for i in range(n):
        if comp[2*i]==comp[2*i+1]: return {'sat':False,'witness':None}
    return {'sat':True,'witness':{i+1:comp[2*i]>comp[2*i+1] for i in range(n)}}


def solve_source(source,n,kind):
    if kind=='HORN': return _horn_solve(source,n)
    if kind=='DUAL_HORN': return _dual_horn_solve(source,n)
    if kind=='2CNF': return _2sat_solve(source,n)
    return {'sat':None,'witness':None}


def direct_cardinality(image):
    n=int(image['n'])
    return compile_c023_dense_image(image['horn'],image['affine'],tuple(range(1,n+1)),tuple(range(n+1,2*n+1)))


def run_apma_ss(image):
    start_bytes=_canon_image(image); start_hash=hashlib.sha256(start_bytes).hexdigest(); ledger=[]
    rev=reverse_c023(image)
    if rev['status']=='MORPH_FAIL':
        rollback_bytes=_canon_image(image); rollback_hash=hashlib.sha256(rollback_bytes).hexdigest()
        ledger.append({'morph':'PROVENANCE_PRESERVING_REVERSE_MORPH','status':'MORPH_FAIL_ROLLED_BACK','reason':rev['reason'],'checkpoint_hash':start_hash,'rollback_hash':rollback_hash})
        carrier=direct_cardinality(image)
        if carrier is not None:
            ledger.append({'morph':'COMPLETE_NEGATIVE_3_UNIFORM_HORN_TO_AT_MOST_2','status':'MORPH_PASS'})
            return {'status':'MORPH_PASS','terminal':'CARDINALITY_CARRIER','carrier':carrier,'ledger':ledger,'checkpoint_hash':start_hash,'rollback_hash':rollback_hash}
        return {'status':'OPEN_NO_AUTHORIZED_MORPH','ledger':ledger,'checkpoint_hash':start_hash,'rollback_hash':rollback_hash}
    ledger.append({'morph':'PROVENANCE_PRESERVING_REVERSE_MORPH','status':'MORPH_PASS','source_hash':rev['certificate']['source_hash']})
    source=rev['source']; kind=classify_source(source)
    ledger.append({'morph':'TRACTABLE_SOURCE_LANGUAGE_RECOGNITION','status':'MORPH_PASS','class':kind})
    if kind=='GENERAL_3CNF':
        return {'status':'OPEN_GENERAL_SOURCE_3CNF','source_class':kind,'ledger':ledger,'checkpoint_hash':start_hash}
    sol=solve_source(source,int(image['n']),kind)
    return {'status':'CERTIFIED_SAT' if sol['sat'] else 'CERTIFIED_UNSAT','source_class':kind,'witness':sol['witness'],'ledger':ledger,'checkpoint_hash':start_hash}
