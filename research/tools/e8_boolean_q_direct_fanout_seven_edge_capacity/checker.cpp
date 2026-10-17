#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <tuple>
#include <vector>

struct Edge { int a,p,b,q; };

static const int PORT_CODE[6] = {0,2,3,10,12,13}; // L0,L2,L3,R0,R2,R3
static std::vector<Edge> EDGES;
static std::uint64_t EDGE_MASK[8][108];
static int path_partner[18];
static long long target_nodes[7];
static bool forbidden_found = false;

int mod3(int x) { x %= 3; if (x < 0) x += 3; return x; }

int colour(int port_code, int c, int s, int q) {
    const int side = port_code / 10;
    const int p = port_code % 10;
    if (side == 0) {
        if (p == 0) return mod3(c+s);
        if (p == 2) return mod3(c+s*q);
        return c;
    }
    if (p == 0) return mod3(c+s*q);
    if (p == 2) return mod3(c-s*(1+q));
    return mod3(c+s*(q-1));
}

void build_masks() {
    std::vector<std::array<int,3>> qs;
    for (int q0 : {1,2}) for (int q1 : {1,2}) for (int q2 : {1,2}) qs.push_back({q0,q1,q2});
    for (int a=0;a<3;a++) for (int b=a+1;b<3;b++)
        for (int p=0;p<6;p++) for (int q=0;q<6;q++) EDGES.push_back({a,p,b,q});
    assert(EDGES.size()==108);

    for (int qi=0;qi<8;qi++) for (int ei=0;ei<108;ei++) {
        const auto Q=qs[qi]; const auto e=EDGES[ei];
        std::uint64_t bits=0; int bit=0;
        // Global affine S3 colour symmetry fixes wire A to c=0,s=+1.
        for (int c1=0;c1<3;c1++) for (int s1 : {1,2})
        for (int c2=0;c2<3;c2++) for (int s2 : {1,2}) {
            int c[3]={0,c1,c2}; int s[3]={1,s1,s2};
            int x=colour(PORT_CODE[e.p],c[e.a],s[e.a],Q[e.a]);
            int y=colour(PORT_CODE[e.q],c[e.b],s[e.b],Q[e.b]);
            if (x!=y) bits |= (std::uint64_t(1)<<bit);
            ++bit;
        }
        assert(bit==36);
        EDGE_MASK[qi][ei]=bits;
    }
}

void init_paths() {
    for (int &x : path_partner) x=-1;
    for (int w=0;w<3;w++) {
        int x=6*w;
        path_partner[x+0]=x+5; path_partner[x+5]=x+0; // L0--R3
        path_partner[x+1]=x+3; path_partner[x+3]=x+1; // L2--R0
        path_partner[x+2]=x+4; path_partner[x+4]=x+2; // L3--R2
    }
}

void dfs_minimality(int start, int depth, const std::array<std::uint64_t,8>& masks) {
    ++target_nodes[depth];
    int relation=0;
    for (int q=0;q<8;q++) if (masks[q]) relation |= 1<<q;
    if (depth>0 && relation==129) { forbidden_found=true; return; }
    if (depth==6 || forbidden_found) return;

    for (int ei=start;ei<108;ei++) {
        const auto e=EDGES[ei];
        int va=6*e.a+e.p, vb=6*e.b+e.q;
        if (path_partner[va]<0 || path_partner[vb]<0) continue; // port already used
        if (path_partner[va]==vb) continue;                    // closes an H path into a cycle

        std::array<std::uint64_t,8> next{};
        for (int q=0;q<8;q++) next[q]=masks[q]&EDGE_MASK[q][ei];
        // Any exact ALL_EQ witness must retain both +++ and --- branches.
        if (!next[0] || !next[7]) continue;

        int pa=path_partner[va], pb=path_partner[vb];
        path_partner[va]=path_partner[vb]=-1;
        path_partner[pa]=pb; path_partner[pb]=pa;
        dfs_minimality(ei+1,depth+1,next);
        path_partner[va]=pa; path_partner[vb]=pb;
        path_partner[pa]=va; path_partner[pb]=vb;
        if (forbidden_found) return;
    }
}

int edge_id(int a,int p,int b,int q) {
    if (a>b) { std::swap(a,b); std::swap(p,q); }
    for (int i=0;i<108;i++) {
        auto e=EDGES[i]; if (e.a==a && e.p==p && e.b==b && e.q==q) return i;
    }
    return -1;
}

bool source_open(const std::vector<int>& selected) {
    int parent[18]; std::iota(parent,parent+18,0);
    auto find=[&](int x) { while(parent[x]!=x){ parent[x]=parent[parent[x]]; x=parent[x]; } return x; };
    auto unite=[&](int a,int b) { a=find(a); b=find(b); if(a==b) return false; parent[b]=a; return true; };
    for(int w=0;w<3;w++){int x=6*w; assert(unite(x+0,x+5)); assert(unite(x+1,x+3)); assert(unite(x+2,x+4));}
    for(int ei:selected){auto e=EDGES[ei]; if(!unite(6*e.a+e.p,6*e.b+e.q)) return false;}
    return true;
}

int relation_of(const std::vector<int>& selected) {
    int rel=0;
    for(int qi=0;qi<8;qi++){
        std::uint64_t bits=(std::uint64_t(1)<<36)-1;
        for(int ei:selected) bits &= EDGE_MASK[qi][ei];
        if(bits) rel |= 1<<qi;
    }
    return rel;
}

int main() {
    build_masks();
    init_paths();
    std::array<std::uint64_t,8> full{};
    for(auto &x:full) x=(std::uint64_t(1)<<36)-1;
    dfs_minimality(0,0,full);
    assert(!forbidden_found);
    const long long EXPECTED[7]={1,108,4536,95328,1073472,6405168,18706368};
    for(int d=0;d<=6;d++) assert(target_nodes[d]==EXPECTED[d]);

    // First achieved direct ALL_EQ witness at seven splice edges.
    std::vector<int> witness={
        edge_id(0,0,1,0),   // A.L0 -- B.L0
        edge_id(0,1,1,1),   // A.L2 -- B.L2
        edge_id(0,2,2,2),   // A.L3 -- C.L3
        edge_id(0,3,2,4),   // A.R0 -- C.R2
        edge_id(0,4,2,1),   // A.R2 -- C.L2
        edge_id(0,5,2,3),   // A.R3 -- C.R0
        edge_id(1,4,2,5)    // B.R2 -- C.R3
    };
    for(int x:witness) assert(x>=0);
    assert(source_open(witness));
    assert(relation_of(witness)==129); // bits 0 and 7 only: +++ and ---
    int load[3]={0,0,0};
    for(int ei:witness){auto e=EDGES[ei]; ++load[e.a]; ++load[e.b];}
    assert(load[0]==6 && load[1]==3 && load[2]==5);

    std::cout << "PASS: exact global-colour quotient leaves 36 frame assignments per q triple\n";
    std::cout << "PASS: target-preserving source-open search counts k=0..6: 1,108,4536,95328,1073472,6405168,18706368\n";
    std::cout << "PASS: no direct source-open ALL_EQ_3 gadget exists through six splice edges\n";
    std::cout << "PASS: explicit seven-edge source-open witness has exact q relation {+++ , ---}\n";
    std::cout << "PASS: witness port loads are (6,3,5); reusable >=2-free-ports-per-terminal budget permits at most six edges\n";
    std::cout << "VERDICT: DIRECT_THREE_WIRE_REUSABLE_Q_FANOUT_IS_CAPACITY_BLOCKED; AUXILIARY_WIRES_REQUIRED\n";
    std::cout << "P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY\n";
}
