// R5: independently enumerate all loopless SIX-fourpole / NINE-join
// multigraph block skeletons. Each of the six blocks has four total
// physical semiedges, so interface degree <=4.
// 110170 connected labelled six-block graphs, exactly 217 unlabeled
// types under ALL degree-preserving permutations of six blocks.
//
// Print ONE representative per line, each line comma-separated a-b
// edges, retaining multiplicity of parallel interblock edges.
// The catalogue feeds the exact anti-phase 87-state transfer verifier.
// Scope is sixblock LOOPLESS grammar, not arbitrary physical sixpoles.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <set>
#include <string>
#include <utility>
using namespace std;

array<pair<int,int>,15> edge_types;
array<int,15> multiplicity{};
array<int,6> degrees{};
set<string> catalog;
uint64_t connected_labelled=0;

string serialize(const array<int,15>& a) {
    string s;
    for(int x:a){assert(x>=0&&x<=4);s+=char('0'+x);}
    return s;
}

void record_graph() {
    unsigned reached=1,prev=0;
    while(reached!=prev){
        prev=reached;
        for(int v=0;v<6;v++)if(reached&(1u<<v))
            for(int k=0;k<15;k++)if(multiplicity[k]){
                const auto [a,b]=edge_types[k];
                if(a==v) reached|=1u<<b;
                if(b==v) reached|=1u<<a;
            }
    }
    if(reached!=63u)return;
    ++connected_labelled;
    array<int,6> perm={0,1,2,3,4,5};
    string minimum(15,'9');
    do{
        bool sorted_degree=true;
        for(int i=1;i<6;i++)if(degrees[perm[i]]<degrees[perm[i-1]]){
            sorted_degree=false;break;
        }
        if(!sorted_degree)continue;
        array<int,6> inverse{};
        for(int i=0;i<6;i++)inverse[perm[i]]=i;
        array<int,15> counts{};
        for(int k=0;k<15;k++)if(multiplicity[k]){
            auto [u,v]=edge_types[k];
            int a=inverse[u],b=inverse[v];
            if(a>b)swap(a,b);
            for(int j=0;j<15;j++)if(edge_types[j]==make_pair(a,b)){
                counts[j]=multiplicity[k];break;
            }
        }
        minimum=min(minimum,serialize(counts));
    }while(next_permutation(perm.begin(),perm.end()));
    assert(minimum!=string(15,'9'));
    catalog.insert(minimum);
}

void enumerate(int index,int remain){
    if(remain==0){record_graph();return;}
    if(index==15)return;
    const auto [u,v]=edge_types[index];
    enumerate(index+1,remain);
    for(int copies=1;copies<=min({remain,4-degrees[u],4-degrees[v]});copies++){
        multiplicity[index]=copies;
        degrees[u]+=copies;degrees[v]+=copies;
        enumerate(index+1,remain-copies);
        degrees[u]-=copies;degrees[v]-=copies;
    }
    multiplicity[index]=0;
}

int main(){
    int k=0;
    for(int u=0;u<6;u++)for(int v=u+1;v<6;v++)
        edge_types[k++]={u,v};
    enumerate(0,9);
    if(connected_labelled!=110170 || catalog.size()!=217){
        cerr<<"SIXBLOCK_CATALOGUE_REGRESSION_FAIL labelled="
            <<connected_labelled<<" types="<<catalog.size()<<'\n';
        return 1;
    }
    cerr<<"SIXBLOCK_CATALOGUE_LABELLED_110170_UNLABELED_217_PASS\n";
    for(const auto& s:catalog){
        bool first=true;
        for(int i=0;i<15;i++)for(int j=0;j<s[i]-'0';j++){
            if(!first)cout<<',';
            first=false;
            cout<<edge_types[i].first<<'-'<<edge_types[i].second;
        }
        cout<<'\n';
    }
}
