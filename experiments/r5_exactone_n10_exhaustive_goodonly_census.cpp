// R5: exhaustive ALL labelled n=10 simple connected cubic sixpoles.
// Vertices 0..5: distinct semiedge roots, ordinary degree 2.
// Vertices 6..9: ordinary degree 3. Twelve ordinary edges.
// Logical physical port pairs: (0,1),(2,3),(4,5).
//
// Generate EACH simple labelled degree-sequence realization exactly
// once by completing edges from vertex u to larger-numbered vertices.
// Connectedness and bridges are checked on the REAL ordinary graph.
// Every proper edge-3-colouring is recursively checked; recursion
// may stop EARLY only after a FORBIDDEN truth bit is found.
// GOOD-only outcomes are therefore EXACT full signature decisions.
// Bitmask result: 1=100, 2=010, 4=001, 8=forbidden seen.
//
// Exhaustive verdict:
// 888292 all simple labelled graphs, 866520 connected,
// 657720 connected bridgeless, 208800 connected with bridge;
// exactly 144 GOOD-only graphs, 48 each mask 3/5/6,
// all 144 WITH bridges; 0 bridgeless GOOD-only graphs, 0 full
// three-bit Exact-One. NO universal statement about n>=12.
//
// Independently check 888292 via memoized combinatorial recurrence
// in the accompanying Python verifier; the orbit of the previously
// verified 10-vertex two-bit physical graph has exactly 144 distinct
// labelled members under root-pair symmetries x four inner permutations.

#include <array>
#include <cstdint>
#include <iostream>
#include <utility>
using namespace std;

struct Census {
    array<int,10> rem{};
    uint16_t adj[10]{};
    pair<int,int> edges[12]{};
    uint64_t all=0, connected=0, bridgeless=0, bridgeful=0;
    uint64_t no_colour=0, good=0, good_bridgeless=0;
    uint64_t pairgood=0, pairgood_bridgeless=0, fullgood=0;
    uint64_t hist[16][2]{}; // sig, has_bridge

    Census() { for(int i=0;i<10;i++) rem[i]= i<6 ? 2:3; }

    bool connected_now() const {
        uint16_t reached=1,previous=0;
        while(reached!=previous) {
            previous=reached;
            for(int v=0;v<10;v++)
                if(reached & (1u<<v)) reached |= adj[v];
        }
        return reached==1023;
    }

    bool bridgeless_now() {
        for(int k=0;k<12;k++) {
            auto [a,b]=edges[k];
            adj[a]^=uint16_t(1u<<b);
            adj[b]^=uint16_t(1u<<a);
            bool remains_connected=connected_now();
            adj[a]^=uint16_t(1u<<b);
            adj[b]^=uint16_t(1u<<a);
            if(!remains_connected) return false;
        }
        return true;
    }

    int exact_truth_mask() const {
        uint8_t used[10]{};
        int signature=0;
        auto visit=[&](auto&& self,int done)->void {
            if(signature & 8) return;
            if(done==4095) {
                int port[6];
                for(int i=0;i<6;i++) {
                    int missing=7^used[i];
                    port[i]=missing==1?0:missing==2?1:missing==4?2:-1;
                    if(port[i]<0) {cerr<<"Improper complete colouring\n";exit(2);}
                }
                int truth=int(port[0]==port[1])
                         +2*int(port[2]==port[3])
                         +4*int(port[4]==port[5]);
                signature |= (truth==1?1:truth==2?2:truth==4?4:8);
                return;
            }
            int chosen=-1,options=0,min_count=4;
            for(int k=0;k<12;k++) if(!(done&(1<<k))) {
                auto [a,b]=edges[k];
                int avail=7&~(used[a]|used[b]);
                int count=__builtin_popcount(unsigned(avail));
                if(count==0) return;
                if(count<min_count) {
                    chosen=k;options=avail;min_count=count;
                    if(count==1) break;
                }
            }
            if(chosen<0) {cerr<<"Unassigned edge missing\n";exit(2);}
            auto [u,v]=edges[chosen];
            while(options) {
                int c=options&-options; options-=c;
                used[u]^=uint8_t(c);used[v]^=uint8_t(c);
                self(self,done|(1<<chosen));
                used[u]^=uint8_t(c);used[v]^=uint8_t(c);
                if(signature&8) break;
            }
        };
        visit(visit,0);
        return signature;
    }

    void evaluate() {
        ++all;
        if(!connected_now()) return;
        ++connected;
        bool no_bridge=bridgeless_now();
        if(no_bridge)++bridgeless;else ++bridgeful;
        int sig=exact_truth_mask();
        if(sig&8)++hist[8][!no_bridge];
        else ++hist[sig][!no_bridge];
        if(sig==0) {++no_colour;return;}
        if(sig&8) return;
        ++good;
        if(no_bridge)++good_bridgeless;
        int size=__builtin_popcount(unsigned(sig));
        if(size==2){++pairgood;if(no_bridge)++pairgood_bridgeless;}
        if(size==3)++fullgood;
    }

    void select_later(int u,int needed,int j,int placed) {
        if(needed==0) {
            // Each later vertex has at most 10-u-2 possible
            // neighbours remaining in the unprocessed vertex set.
            for(int v=u+1;v<10;v++)
                if(rem[v]>8-u) return;
            generate(u+1,placed);
            return;
        }
        if(j==10) return;
        int available=0;
        for(int v=j;v<10;v++) if(rem[v]>0)++available;
        if(available<needed) return;
        if(rem[j]>0) {
            --rem[j];--rem[u];
            adj[u] |= uint16_t(1u<<j);
            adj[j] |= uint16_t(1u<<u);
            edges[placed]={u,j};
            select_later(u,needed-1,j+1,placed+1);
            adj[u] ^= uint16_t(1u<<j);
            adj[j] ^= uint16_t(1u<<u);
            ++rem[j];++rem[u];
        }
        select_later(u,needed,j+1,placed);
    }

    void generate(int u,int placed) {
        if(u==10){if(placed==12)evaluate();return;}
        if(rem[u]==0){generate(u+1,placed);return;}
        select_later(u,rem[u],u+1,placed);
    }
};

int main() {
    Census c;c.generate(0,0);
    cout<<"N10_TOTAL_SIMPLE "<<c.all<<"\n";
    cout<<"N10_CONNECTED "<<c.connected<<"\n";
    cout<<"N10_CONNECTED_BRIDGELESS "<<c.bridgeless<<"\n";
    cout<<"N10_CONNECTED_WITH_BRIDGE "<<c.bridgeful<<"\n";
    cout<<"N10_GOODONLY_TOTAL "<<c.good<<"\n";
    cout<<"N10_GOODONLY_BRIDGELESS "<<c.good_bridgeless<<"\n";
    cout<<"N10_TWO_BITS "<<c.pairgood<<"\n";
    cout<<"N10_TWO_BITS_BRIDGELESS "<<c.pairgood_bridgeless<<"\n";
    cout<<"N10_THREE_BITS "<<c.fullgood<<"\n";
    for(int s: {3,5,6})
        cout<<"N10_GOODONLY_MASK_"<<s<<"_WITH_BRIDGE "<<c.hist[s][1]<<"\n";
    bool pass= c.all==888292 && c.connected==866520 &&
        c.bridgeless==657720 && c.bridgeful==208800 &&
        c.no_colour==0 && c.good==144 && c.good_bridgeless==0 &&
        c.pairgood==144 && c.pairgood_bridgeless==0 &&
        c.fullgood==0 && c.hist[3][1]==48 &&
        c.hist[5][1]==48 && c.hist[6][1]==48 &&
        c.hist[8][0]==657720 && c.hist[8][1]==208656;
    if(!pass){cerr<<"N10 exhaustive census failed\n";return 1;}
    cout<<"N10_EXHAUSTIVE_ALL_SIMPLE_CONNECTED_SIXPOLES_PASS\n";
    cout<<"FULL_108_EXACTONE_N10_EXCLUDED; ALL_N_OPEN\n";
    return 0;
}
