#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

struct Edge { int a,p,b,q; };
struct Bits216 {
    std::array<std::uint64_t,4> w{};
};

static const int PORT_CODE[6]={0,2,3,10,12,13}; // L0,L2,L3,R0,R2,R3
static const char* WNAME[4]={"A","B","C","D"};
static const char* PNAME[6]={"L0","L2","L3","R0","R2","R3"};
static std::vector<Edge> EDGES;
static std::vector<std::array<Bits216,16>> EDGE_MASK;
static std::array<std::array<int,4>,16> QV{};
static int path_partner[24];
static int loadv[4]={0,0,0,0};
static std::vector<int> chosen, witness;
static std::uint64_t nodes[8]={};
static bool found=false;

int mod3(int x){x%=3;if(x<0)x+=3;return x;}
int colour(int P,int c,int s,int q){
    int side=P/10,p=P%10;
    if(!side){if(p==0)return mod3(c+s);if(p==2)return mod3(c+s*q);return c;}
    if(p==0)return mod3(c+s*q);
    if(p==2)return mod3(c-s*(1+q));
    return mod3(c+s*(q-1));
}
bool any(const Bits216& x){return x.w[0]||x.w[1]||x.w[2]||x.w[3];}
Bits216 land(const Bits216& a,const Bits216& b){
    Bits216 r; for(int i=0;i<4;i++) r.w[i]=a.w[i]&b.w[i]; return r;
}
Bits216 fullbits(){
    Bits216 x; x.w={~std::uint64_t(0),~std::uint64_t(0),~std::uint64_t(0),(std::uint64_t(1)<<24)-1}; return x;
}
void setbit(Bits216& x,int bit){x.w[bit>>6]|=std::uint64_t(1)<<(bit&63);}

void build_qs(){
    int i=0;
    for(int a:{1,2})for(int b:{1,2})for(int c:{1,2})for(int d:{1,2})
        QV[i++]={a,b,c,d};
    assert(i==16);
}
void build_edges(){
    // Put D-incident edges first so a positive auxiliary-wire witness is found early.
    const int pairs[6][2]={{0,3},{1,3},{2,3},{0,1},{0,2},{1,2}};
    for(auto &ab:pairs) for(int p=0;p<6;p++) for(int q=0;q<6;q++)
        EDGES.push_back({ab[0],p,ab[1],q});
    assert(EDGES.size()==216);
}
void build_masks(){
    EDGE_MASK.resize(EDGES.size());
    for(int ei=0;ei<(int)EDGES.size();ei++){
        auto e=EDGES[ei];
        for(int qi=0;qi<16;qi++){
            Bits216 bits; int bit=0;
            // Global affine S3 colour symmetry fixes A to c=0,s=+1.
            for(int c1=0;c1<3;c1++)for(int s1:{1,2})
            for(int c2=0;c2<3;c2++)for(int s2:{1,2})
            for(int c3=0;c3<3;c3++)for(int s3:{1,2}){
                int C[4]={0,c1,c2,c3}, S[4]={1,s1,s2,s3};
                int x=colour(PORT_CODE[e.p],C[e.a],S[e.a],QV[qi][e.a]);
                int y=colour(PORT_CODE[e.q],C[e.b],S[e.b],QV[qi][e.b]);
                if(x!=y)setbit(bits,bit);
                ++bit;
            }
            assert(bit==216);
            EDGE_MASK[ei][qi]=bits;
        }
    }
}
void init_paths(){
    for(int &x:path_partner)x=-1;
    for(int w=0;w<4;w++){
        int x=6*w;
        path_partner[x+0]=x+5; path_partner[x+5]=x+0; // L0--R3
        path_partner[x+1]=x+3; path_partner[x+3]=x+1; // L2--R0
        path_partner[x+2]=x+4; path_partner[x+4]=x+2; // L3--R2
    }
}
int named_relation(const std::array<Bits216,16>& masks){
    int rel=0;
    for(int qi=0;qi<16;qi++) if(any(masks[qi])){
        int a=(QV[qi][0]==2), b=(QV[qi][1]==2), c=(QV[qi][2]==2);
        rel |= 1<<(4*a+2*b+c);
    }
    return rel;
}
bool required_alive(const std::array<Bits216,16>& masks){
    bool plus=false,minus=false;
    for(int qi=0;qi<16;qi++) if(any(masks[qi])){
        if(QV[qi][0]==1&&QV[qi][1]==1&&QV[qi][2]==1) plus=true;
        if(QV[qi][0]==2&&QV[qi][1]==2&&QV[qi][2]==2) minus=true;
    }
    return plus&&minus;
}
void print_witness(){
    int wl[4]={0,0,0,0};
    std::cout<<"WITNESS_EDGES="<<witness.size()<<"\n";
    for(int ei:witness){
        auto e=EDGES[ei];
        ++wl[e.a]; ++wl[e.b];
        std::cout<<WNAME[e.a]<<"."<<PNAME[e.p]<<" -- "<<WNAME[e.b]<<"."<<PNAME[e.q]<<"\n";
    }
    std::cout<<"WITNESS_LOADS=("<<wl[0]<<","<<wl[1]<<","<<wl[2]<<","<<wl[3]<<")\n";
}
void dfs(int start,int depth,const std::array<Bits216,16>& masks){
    ++nodes[depth];
    if(depth>0 && named_relation(masks)==129){
        found=true; witness=chosen; return;
    }
    if(depth==7||found)return;

    for(int ei=start;ei<(int)EDGES.size();ei++){
        auto e=EDGES[ei];
        if(loadv[e.a] >= (e.a==3?6:3) || loadv[e.b] >= (e.b==3?6:3)) continue;
        int a=6*e.a+e.p,b=6*e.b+e.q;
        if(path_partner[a]<0||path_partner[b]<0)continue;
        if(path_partner[a]==b)continue; // would close one H path into a cycle

        std::array<Bits216,16> next;
        for(int q=0;q<16;q++) next[q]=land(masks[q],EDGE_MASK[ei][q]);
        if(!required_alive(next))continue;

        int pa=path_partner[a],pb=path_partner[b];
        path_partner[a]=path_partner[b]=-1;
        path_partner[pa]=pb; path_partner[pb]=pa;
        ++loadv[e.a]; ++loadv[e.b]; chosen.push_back(ei);

        dfs(ei+1,depth+1,next);

        chosen.pop_back(); --loadv[e.a]; --loadv[e.b];
        path_partner[a]=pa; path_partner[b]=pb;
        path_partner[pa]=a; path_partner[pb]=b;
        if(found)return;
    }
}
int main(){
    build_qs(); build_edges(); build_masks(); init_paths();
    std::array<Bits216,16> full; for(auto &x:full)x=fullbits();
    assert(named_relation(full)==255);
    dfs(0,0,full);

    std::cout<<"PASS: exact quotient uses 216 frame assignments per four-wire q tuple after global S3 fixing\n";
    std::cout<<"PASS: source-open path pairing and port loads enforced at every DFS node\n";
    std::cout<<"SEARCH_NODES_BY_DEPTH=";
    for(int d=0;d<=7;d++){if(d)std::cout<<",";std::cout<<nodes[d];}
    std::cout<<"\n";
    if(found){
        print_witness();
        std::cout<<"VERDICT: ONE_HIDDEN_WIRE_REUSABLE_Q_ALL_EQ3_FANOUT_FOUND\n";
    }else{
        std::cout<<"VERDICT: NO_ONE_HIDDEN_WIRE_Q_ALL_EQ3_FANOUT_THROUGH_SEVEN_EDGES_IN_EXACT_BOUNDED_LANGUAGE\n";
    }
    std::cout<<"P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY\n";
    return 0;
}
