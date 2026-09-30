#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

struct Edge { int a,p,b,q; };
struct Bits1296 { std::array<std::uint64_t,21> w{}; };

static const int PORT_CODE[6]={0,2,3,10,12,13}; // L0,L2,L3,R0,R2,R3
static const char* WNAME[5]={"A","B","C","D","E"};
static const char* PNAME[6]={"L0","L2","L3","R0","R2","R3"};
static std::vector<Edge> edges;
static std::vector<std::array<Bits1296,32>> edge_mask;

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
void setbit(Bits1296& x,int bit){ x.w[bit>>6] |= std::uint64_t(1) << (bit&63); }
bool any(const Bits1296& x){ for(auto z:x.w) if(z) return true; return false; }
std::uint64_t popcount(const Bits1296& x){
    std::uint64_t s=0; for(auto z:x.w) s += __builtin_popcountll(z); return s;
}
Bits1296 fullbits(){
    Bits1296 x;
    for(int i=0;i<20;i++) x.w[i]=~std::uint64_t(0);
    x.w[20]=(std::uint64_t(1)<<16)-1; // 20*64 + 16 = 1296
    return x;
}
int qvalue(int qi,int w){ return ((qi>>(4-w))&1) ? 2 : 1; }
void decode_frame(int f,int C[5],int S[5]){
    C[0]=0; S[0]=1;
    for(int w=4; w>=1; --w){
        int choice=f%6; f/=6;
        C[w]=choice/2;
        S[w]=(choice%2)?2:1;
    }
}
void build_edges(){
    for(int a=0;a<5;a++) for(int b=a+1;b<5;b++)
        for(int p=0;p<6;p++) for(int q=0;q<6;q++)
            edges.push_back({a,p,b,q});
    assert(edges.size()==360);
}
void build_masks(){
    edge_mask.resize(edges.size());
    for(int ei=0;ei<(int)edges.size();++ei){
        const auto e=edges[ei];
        for(int qi=0; qi<32; ++qi){
            Bits1296 bits;
            for(int f=0; f<1296; ++f){
                int C[5],S[5]; decode_frame(f,C,S);
                const int x=colour(PORT_CODE[e.p],C[e.a],S[e.a],qvalue(qi,e.a));
                const int y=colour(PORT_CODE[e.q],C[e.b],S[e.b],qvalue(qi,e.b));
                if(x!=y) setbit(bits,f);
            }
            edge_mask[ei][qi]=bits;
        }
    }
}
int named_relation_full(){
    int rel=0;
    for(int qi=0; qi<32; ++qi){
        const int a=(qi>>4)&1,b=(qi>>3)&1,c=(qi>>2)&1;
        rel |= 1 << (4*a+2*b+c);
    }
    return rel;
}
bool required_alive_full(const std::array<Bits1296,32>& state){
    bool plus=false,minus=false;
    for(int qi=0; qi<32; ++qi){
        const int a=(qi>>4)&1,b=(qi>>3)&1,c=(qi>>2)&1;
        if(a==0&&b==0&&c==0&&any(state[qi])) plus=true;
        if(a==1&&b==1&&c==1&&any(state[qi])) minus=true;
    }
    return plus&&minus;
}
int main(){
    build_edges();
    build_masks();

    std::array<Bits1296,32> full;
    for(auto& x:full) x=fullbits();

    assert(named_relation_full()==255);
    assert(required_alive_full(full));
    assert(popcount(full[0])==1296);

    std::uint64_t min_count=1296, max_count=0, total_count=0;
    for(int ei=0; ei<(int)edges.size(); ++ei){
        for(int qi=0; qi<32; ++qi){
            const auto pc=popcount(edge_mask[ei][qi]);
            assert(pc>0 && pc<1296);
            min_count = std::min(min_count, pc);
            max_count = std::max(max_count, pc);
            total_count += pc;
        }
    }

    std::cout << "PASS: v8.5 edge universe has C(5,2)*6*6 = 360 cross-wire splice candidates\n";
    std::cout << "PASS: v8.5 q universe has 2^5 = 32 branches\n";
    std::cout << "PASS: global S3 quotient fixes A and leaves 6^4 = 1296 affine frames per q branch\n";
    std::cout << "PASS: 1296-bit masks use 21 uint64 words with 48 unused high bits masked away\n";
    std::cout << "PASS: initial named projection is all 8 triples and mandatory +++/--- branches are alive\n";
    std::cout << "EDGE_MASK_POPCOUNT_RANGE=" << min_count << ".." << max_count << "\n";
    std::cout << "EDGE_MASK_TOTAL_POPCOUNT=" << total_count << "\n";
    std::cout << "VERDICT: V8_5_TWO_HIDDEN_STATE_CODEC_FROZEN_NO_SEARCH_VERDICT\n";
    std::cout << "P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY\n";
}
