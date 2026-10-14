// R5 seven-fourpole / eleven-join LOOPLESS multigraph COMPLETE labelled census.
//
// Select 11 undirected interblock edges from the 21 unordered distinct
// block pairs with repetition (parallel edges ALLOWED, self-loops
// FORBIDDEN). Every block has degree <=4 (it starts as a fourpole).
// Every multiset is generated ONCE via ascending pair-type multiplicity.
//
// ALL finite counts independently computed and asserted:
// degree-feasible n7 graph edge multisets:             5,229,168
// disconnected:                                         493,458
// connected:                                          4,735,710
// edge connectivity exactly 1:                        2,532,390
// edge connectivity exactly 2:                        2,188,830
// edge connectivity exactly 3:                           14,490
// 3+3 external-port splitting bridge seen:            2,311,890
// bridge graph without any 3+3 bridge:                  220,500
// edgeconn2 with SOME external-port 2+4 cut:          2,188,830
// edgeconn2 ALSO with non-2+4 cuts:                      289,590
// edgeconn2 with zero degree-two constituent blocks:     54,810
// edgeconn2 with one degree-two block:                   740,670
// edgeconn2 with >=two degree-two blocks:              1,393,350
//
// These are labelled counts, NOT graph isomorphism types. The
// 3-edge-connected category has one four-interface hub and exactly
// the seven unlabelled skeletons proved UNSAT in the separate R5
// exact 3-good-witness theorem. This census itself does NOT assert
// any no-go for edgeconn1/edgeconn2 remaining architectures.
//
// Every cut: one representative of each complementary pair of
// nonempty vertex subsets is inspected. External-port count on a
// side is sum(4-degree(v)), and total is exactly SIX.
//
// Scope: exact graph combinatorics only; no colourability claim.
// P vs NP and full native SolveLinearCubicXSAT both remain OPEN.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
using namespace std;

struct Edge { int u,v; };
array<Edge,21> edge_types{};
array<Edge,11> chosen{};
array<int,7> degree{};
uint64_t all=0;
array<uint64_t,4> connectivity{};
uint64_t bridges_33=0,bridges_other=0;
uint64_t cut2_has_24=0,cut2_has_other=0;
array<uint64_t,3> cut2_degree2_count{};

void check_one_multigraph() {
    ++all;
    int mincut=11;
    bool bridge33=false,has24=false,hasOther=false;
    // Only 63 nonempty proper subsets of seven vertices containing
    // fixed vertex zero need examination; complements are redundant.
    for(int mask=1;mask<127;mask+=2) {
        int boundary=0;
        for(const auto& e:chosen)
            boundary+=(((mask>>e.u)&1)!=((mask>>e.v)&1));
        mincut=min(mincut,boundary);
        if(boundary==1 || boundary==2) {
            int exposed=0;
            for(int v=0;v<7;v++)
                if(mask>>v&1)exposed+=4-degree[v];
            if(boundary==1 && exposed==3)bridge33=true;
            if(boundary==2) {
                if(exposed==2 || exposed==4)has24=true;
                else hasOther=true;
            }
        }
    }
    if(mincut<0 || mincut>3) {
        fprintf(stderr,"Unexpected cut %d\n",mincut);
        __builtin_trap();
    }
    ++connectivity[mincut];
    if(mincut==1) {
        if(bridge33)++bridges_33;
        else ++bridges_other;
    }
    if(mincut==2) {
        cut2_has_24+=has24;
        cut2_has_other+=hasOther;
        int n2=0;
        for(int d:degree)n2+=(d==2);
        ++cut2_degree2_count[n2==0?0:n2==1?1:2];
    }
}

void enumerate(int type,int remaining) {
    if(remaining==0) {
        check_one_multigraph();
        return;
    }
    if(type==21)return;
    auto [u,v]=edge_types[type];
    enumerate(type+1,remaining); // zero copies of this block pair
    const int maximum=min({remaining,4-degree[u],4-degree[v]});
    for(int copies=1;copies<=maximum;copies++) {
        degree[u]+=copies;
        degree[v]+=copies;
        for(int j=0;j<copies;j++)
            chosen[11-remaining+j]={u,v};
        enumerate(type+1,remaining-copies);
        degree[u]-=copies;
        degree[v]-=copies;
    }
}

int main() {
    int k=0;
    for(int u=0;u<7;u++)
        for(int v=u+1;v<7;v++)
            edge_types[k++]={u,v};
    enumerate(0,11);
    const uint64_t connected=connectivity[1]+connectivity[2]+connectivity[3];
    printf("SEVENBLOCK_LOOPLESS_DEGREEFEASIBLE_ALL %llu\n",(unsigned long long)all);
    printf("SEVENBLOCK_LOOPLESS_DISCONNECTED %llu\n",(unsigned long long)connectivity[0]);
    printf("SEVENBLOCK_LOOPLESS_CONNECTED %llu\n",(unsigned long long)connected);
    printf("SEVENBLOCK_LOOPLESS_CUT1 %llu CUT2 %llu CUT3 %llu\n",
        (unsigned long long)connectivity[1],
        (unsigned long long)connectivity[2],
        (unsigned long long)connectivity[3]);
    printf("SEVENBLOCK_LOOPLESS_BRIDGE_3PLUS3 %llu OTHER_BRIDGES %llu\n",
        (unsigned long long)bridges_33,(unsigned long long)bridges_other);
    printf("SEVENBLOCK_LOOPLESS_CUT2_HAS_2PLUS4 %llu ALSO_OTHER %llu\n",
        (unsigned long long)cut2_has_24,(unsigned long long)cut2_has_other);
    printf("SEVENBLOCK_LOOPLESS_CUT2_DEG2_NONE %llu ONE %llu MULTIPLE %llu\n",
        (unsigned long long)cut2_degree2_count[0],
        (unsigned long long)cut2_degree2_count[1],
        (unsigned long long)cut2_degree2_count[2]);
    bool ok=all==5229168 && connectivity==array<uint64_t,4>{
         493458,2532390,2188830,14490}
         && bridges_33==2311890 && bridges_other==220500
         && cut2_has_24==2188830 && cut2_has_other==289590
         && cut2_degree2_count==array<uint64_t,3>{54810,740670,1393350};
    if(!ok) {
        fprintf(stderr,"Exact sevenblock loopless census regression FAILED\n");
        return 1;
    }
    puts("EXHAUSTIVE_LOOPLESS_7FOURPOLE_11JOIN_LABELLED_CENSUS_PASS");
    puts("NO_108_STATE_ASSERTION_FOR_LOW_EDGE_CONNECTIVITY");
    puts("P_VS_NP_OPEN");
    return 0;
}
