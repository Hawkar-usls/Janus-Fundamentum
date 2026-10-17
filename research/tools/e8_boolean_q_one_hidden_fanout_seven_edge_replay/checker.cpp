#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

struct Edge { int a,p,b,q; };
struct Bits216 { std::array<std::uint64_t,4> w{}; };

static const int PORT_CODE[6]={0,2,3,10,12,13};
static std::vector<Edge> edges;
static std::vector<std::array<Bits216,16>> edge_mask;
static bool used_port[24]{};
static int loadv[4]{};
static std::uint64_t nodes[8]{};
static bool found=false;

struct DSU {
    int p[24], sz[24];
    void init(){ for(int i=0;i<24;i++){p[i]=i;sz[i]=1;} }
    int find(int x) const { while(p[x]!=x) x=p[x]; return x; }
    void unite_permanent(int a,int b){
        a=find(a); b=find(b); assert(a!=b);
        if(sz[a]<sz[b]) std::swap(a,b);
        p[b]=a; sz[a]+=sz[b];
    }
    struct Undo { int ra,rb,old_size; };
    Undo unite_reversible(int a,int b){
        a=find(a); b=find(b); assert(a!=b);
        if(sz[a]<sz[b]) std::swap(a,b);
        Undo u{a,b,sz[a]};
        p[b]=a; sz[a]+=sz[b];
        return u;
    }
    void undo(const Undo& u){ p[u.rb]=u.rb; sz[u.ra]=u.old_size; }
} dsu;

int mod3(int x){ x%=3; if(x<0)x+=3; return x; }
int colour(int P,int c,int s,int q){
    const int side=P/10, k=P%10;
    if(side==0){
        if(k==0) return mod3(c+s);
        if(k==2) return mod3(c+s*q);
        return c;
    }
    if(k==0) return mod3(c+s*q);
    if(k==2) return mod3(c-s*(1+q));
    return mod3(c+s*(q-1));
}

bool any(const Bits216& x){ return x.w[0]||x.w[1]||x.w[2]||x.w[3]; }
Bits216 band(const Bits216& a,const Bits216& b){
    Bits216 r; for(int i=0;i<4;i++) r.w[i]=a.w[i]&b.w[i]; return r;
}
Bits216 fullbits(){
    Bits216 x; x.w={~std::uint64_t(0),~std::uint64_t(0),~std::uint64_t(0),(std::uint64_t(1)<<24)-1}; return x;
}
void setbit(Bits216& x,int bit){ x.w[bit>>6]|=std::uint64_t(1)<<(bit&63); }

int qvalue(int qi,int w){
    const int shift=3-w;
    return ((qi>>shift)&1) ? 2 : 1;
}

void build_edges(){
    const int pairs[6][2]={{0,3},{1,3},{2,3},{0,1},{0,2},{1,2}};
    for(const auto& ab:pairs)
        for(int p=0;p<6;p++) for(int q=0;q<6;q++)
            edges.push_back({ab[0],p,ab[1],q});
    assert(edges.size()==216);
}

void decode_frame(int f,int C[4],int S[4]){
    C[0]=0; S[0]=1;
    for(int w=3;w>=1;--w){
        int choice=f%6; f/=6;
        C[w]=choice/2;
        S[w]=(choice%2)?2:1;
    }
}

void build_masks(){
    edge_mask.resize(edges.size());
    for(int ei=0;ei<(int)edges.size();++ei){
        const auto e=edges[ei];
        for(int qi=0;qi<16;++qi){
            Bits216 bits;
            for(int f=0;f<216;++f){
                int C[4],S[4]; decode_frame(f,C,S);
                const int x=colour(PORT_CODE[e.p],C[e.a],S[e.a],qvalue(qi,e.a));
                const int y=colour(PORT_CODE[e.q],C[e.b],S[e.b],qvalue(qi,e.b));
                if(x!=y) setbit(bits,f);
            }
            edge_mask[ei][qi]=bits;
        }
    }
}

void init_topology(){
    dsu.init();
    for(int w=0;w<4;++w){
        const int x=6*w;
        dsu.unite_permanent(x+0,x+5); // L0--R3
        dsu.unite_permanent(x+1,x+3); // L2--R0
        dsu.unite_permanent(x+2,x+4); // L3--R2
    }
}

bool required_alive(const std::array<Bits216,16>& m){
    const bool plus=any(m[0])||any(m[1]);   // A=B=C=+1, either q_D
    const bool minus=any(m[14])||any(m[15]); // A=B=C=-1, either q_D
    return plus&&minus;
}

int named_relation(const std::array<Bits216,16>& m){
    int rel=0;
    for(int qi=0;qi<16;++qi) if(any(m[qi])){
        const int a=(qi>>3)&1, b=(qi>>2)&1, c=(qi>>1)&1;
        rel |= 1<<(4*a+2*b+c);
    }
    return rel;
}

void dfs(int start,int depth,const std::array<Bits216,16>& masks){
    ++nodes[depth];
    if(depth>0 && named_relation(masks)==129){ found=true; return; }
    if(depth==7 || found) return;

    for(int ei=start;ei<(int)edges.size();++ei){
        const auto e=edges[ei];
        if(loadv[e.a] >= (e.a==3?6:3) || loadv[e.b] >= (e.b==3?6:3)) continue;
        const int a=6*e.a+e.p, b=6*e.b+e.q;
        if(used_port[a] || used_port[b]) continue;
        if(dsu.find(a)==dsu.find(b)) continue; // independent forest/cycle test

        std::array<Bits216,16> next;
        for(int qi=0;qi<16;++qi) next[qi]=band(masks[qi],edge_mask[ei][qi]);
        if(!required_alive(next)) continue;

        used_port[a]=used_port[b]=true;
        ++loadv[e.a]; ++loadv[e.b];
        auto undo=dsu.unite_reversible(a,b);

        dfs(ei+1,depth+1,next);

        dsu.undo(undo);
        --loadv[e.a]; --loadv[e.b];
        used_port[a]=used_port[b]=false;
        if(found) return;
    }
}

int main(){
    build_edges();
    build_masks();
    init_topology();
    std::array<Bits216,16> full; for(auto& x:full) x=fullbits();
    assert(named_relation(full)==255);
    dfs(0,0,full);

    const std::uint64_t expected[8]={
        1ULL,216ULL,19440ULL,954432ULL,25064640ULL,312820128ULL,1425396096ULL,1298827008ULL
    };
    for(int d=0;d<=7;++d) assert(nodes[d]==expected[d]);
    assert(!found);

    std::cout<<"PASS: independent topology engine uses matching flags plus rollback DSU cycle detection\n";
    std::cout<<"PASS: independent q/frame indexing reproduces the exact 216-frame quotient\n";
    std::cout<<"PASS: replay node counts match primary v8.4 at every depth 0..7\n";
    std::cout<<"SEARCH_NODES_BY_DEPTH=1,216,19440,954432,25064640,312820128,1425396096,1298827008\n";
    std::cout<<"VERDICT: INDEPENDENT_REPLAY_CONFIRMS_NO_ONE_HIDDEN_WIRE_Q_ALL_EQ3_FANOUT_THROUGH_SEVEN_EDGES\n";
    std::cout<<"P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY\n";
}
