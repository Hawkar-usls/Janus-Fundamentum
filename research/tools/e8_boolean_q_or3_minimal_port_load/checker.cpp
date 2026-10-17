#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <vector>

struct Edge { int a,p,b,q; };
static const int PORT_CODE[6]={0,2,3,10,12,13};
static std::vector<Edge> EDGES;
static std::uint64_t EDGE_MASK[8][108];
static int path_partner[18];
static int loadv[3];
static long long source_open_k5=0;
static std::map<std::array<int,3>,long long> or_loads;

int mod3(int x){x%=3;if(x<0)x+=3;return x;}
int colour(int P,int c,int s,int q){
    int side=P/10,p=P%10;
    if(!side){if(p==0)return mod3(c+s);if(p==2)return mod3(c+s*q);return c;}
    if(p==0)return mod3(c+s*q);
    if(p==2)return mod3(c-s*(1+q));
    return mod3(c+s*(q-1));
}

void dfs(int start,int depth,const std::array<std::uint64_t,8>& masks){
    if(depth==5){
        ++source_open_k5;
        int relation=0;
        for(int i=0;i<8;i++) if(masks[i]) relation|=1<<i;
        if(relation==254) ++or_loads[{loadv[0],loadv[1],loadv[2]}];
        return;
    }
    for(int ei=start;ei<108;ei++){
        auto e=EDGES[ei];
        int a=6*e.a+e.p,b=6*e.b+e.q;
        if(path_partner[a]<0||path_partner[b]<0||path_partner[a]==b) continue;
        auto next=masks;
        for(int q=0;q<8;q++) next[q]&=EDGE_MASK[q][ei];
        int pa=path_partner[a],pb=path_partner[b];
        path_partner[a]=path_partner[b]=-1;
        path_partner[pa]=pb; path_partner[pb]=pa;
        ++loadv[e.a]; ++loadv[e.b];
        dfs(ei+1,depth+1,next);
        --loadv[e.a]; --loadv[e.b];
        path_partner[a]=pa; path_partner[b]=pb;
        path_partner[pa]=a; path_partner[pb]=b;
    }
}

int main(){
    std::vector<std::array<int,3>> Q;
    for(int a:{1,2})for(int b:{1,2})for(int c:{1,2})Q.push_back({a,b,c});
    for(int a=0;a<3;a++)for(int b=a+1;b<3;b++)
        for(int p=0;p<6;p++)for(int q=0;q<6;q++)EDGES.push_back({a,p,b,q});
    assert(EDGES.size()==108);

    for(int qi=0;qi<8;qi++)for(int ei=0;ei<108;ei++){
        auto e=EDGES[ei]; std::uint64_t bits=0; int bit=0;
        // Fix wire A's global affine colour frame to c=0,s=+1.
        for(int c1=0;c1<3;c1++)for(int s1:{1,2})
        for(int c2=0;c2<3;c2++)for(int s2:{1,2}){
            int C[3]={0,c1,c2},S[3]={1,s1,s2};
            if(colour(PORT_CODE[e.p],C[e.a],S[e.a],Q[qi][e.a]) !=
               colour(PORT_CODE[e.q],C[e.b],S[e.b],Q[qi][e.b])) bits|=std::uint64_t(1)<<bit;
            ++bit;
        }
        assert(bit==36); EDGE_MASK[qi][ei]=bits;
    }

    for(int &x:path_partner)x=-1;
    for(int w=0;w<3;w++){
        int x=6*w;
        path_partner[x+0]=x+5; path_partner[x+5]=x+0;
        path_partner[x+1]=x+3; path_partner[x+3]=x+1;
        path_partner[x+2]=x+4; path_partner[x+4]=x+2;
    }
    std::array<std::uint64_t,8> full{};
    for(auto &x:full)x=(std::uint64_t(1)<<36)-1;
    dfs(0,0,full);

    assert(source_open_k5==6476544);
    assert(or_loads.size()==3);
    assert(or_loads[std::array<int,3>{3,3,4}]==9056);
    assert(or_loads[std::array<int,3>{3,4,3}]==9056);
    assert(or_loads[std::array<int,3>{4,3,3}]==9056);
    long long total=0;for(auto const& kv:or_loads)total+=kv.second;
    assert(total==27168);

    std::cout<<"PASS: source-open five-splice matchings = 6476544\n";
    std::cout<<"PASS: exact OR3 five-splice gadgets = 27168\n";
    std::cout<<"PASS: OR3 load vectors are only (3,3,4),(3,4,3),(4,3,3), each count 9056\n";
    std::cout<<"VERDICT: MINIMUM_OR3_NEEDS_AT_LEAST_THREE_DANGLING_PORTS_PER_LITERAL_OCCURRENCE\n";
    std::cout<<"P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY\n";
}
