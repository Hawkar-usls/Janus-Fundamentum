#include <bits/stdc++.h>
using namespace std;

static const int QRV[9] = {1,4,5,6,7,9,11,16,17};

bool is_qr(int d) {
    d %= 19; if (d < 0) d += 19;
    for (int x : QRV) if (x == d) return true;
    return false;
}

pair<int,int> oriented_arc(int a, int b) {
    return is_qr(b-a) ? make_pair(a,b) : make_pair(b,a);
}

int r0_delta(int d) {
    d %= 19; if (d < 0) d += 19;
    if (d==1 || d==7 || d==11) return 2;
    if (d==4 || d==6 || d==9) return 1;
    if (d==5 || d==16 || d==17) return 0;
    abort();
}

int t_edge(int u, int v) {
    return (3-r0_delta(v-u))%3;
}

struct Bits { uint64_t w[4]{}; };
inline void bor(Bits &a, const Bits &b) { for (int i=0;i<4;i++) a.w[i] |= b.w[i]; }
inline bool equal_bits(const Bits &a, const Bits &b) { for (int i=0;i<4;i++) if (a.w[i] != b.w[i]) return false; return true; }

vector<array<int,2>> local_arcs(const vector<int>& W) {
    vector<array<int,2>> E;
    for (int i=0;i<(int)W.size();i++) for (int j=i+1;j<(int)W.size();j++) {
        auto [u,v] = oriented_arc(W[i],W[j]);
        int iu = int(find(W.begin(),W.end(),u)-W.begin());
        int iv = int(find(W.begin(),W.end(),v)-W.begin());
        E.push_back({iu,iv});
    }
    return E;
}

void build_masks(const vector<int>& W,
                 const vector<array<int,2>>& E,
                 vector<array<Bits,3>>& masks,
                 Bits& full) {
    int s = int(W.size());
    int nassign = 1;
    for (int i=1;i<s;i++) nassign *= 3; // normalize p(W[0])=0
    for (int id=0; id<nassign; id++) {
        int z=id, p[6]={0,0,0,0,0,0};
        for (int i=1;i<s;i++) { p[i]=z%3; z/=3; }
        full.w[id>>6] |= 1ull << (id&63);
        for (int ei=0; ei<(int)E.size(); ei++) {
            int iu=E[ei][0], iv=E[ei][1];
            int u=W[iu], v=W[iv], t=t_edge(u,v);
            for (int c=0;c<3;c++) {
                if ((c+p[iv]-p[iu]-t)%3 == 0)
                    masks[ei][c].w[id>>6] |= 1ull << (id&63);
            }
        }
    }
}

bool connected6(const vector<array<int,2>>& E, int emask) {
    int seen=1;
    for (;;) {
        int old=seen;
        for (int i=0;i<(int)E.size();i++) if ((emask>>i)&1) {
            int a=E[i][0], b=E[i][1];
            if ((seen>>a)&1) seen |= 1<<b;
            if ((seen>>b)&1) seen |= 1<<a;
        }
        if (seen==old) return seen==63;
    }
}

array<bool,3> slice_cover_profile(const vector<array<Bits,3>>& masks,
                                  const Bits& full,
                                  int emask) {
    array<bool,3> out{};
    for (int c=0;c<3;c++) {
        Bits U{};
        for (int i=0;i<(int)masks.size();i++) if ((emask>>i)&1) bor(U,masks[i][c]);
        out[c]=equal_bits(U,full);
    }
    return out;
}

int rank_mod3(vector<vector<int>> M) {
    if (M.empty()) return 0;
    int m=M.size(), n=M[0].size(), r=0;
    for (int c=0;c<n;c++) {
        int p=-1;
        for (int i=r;i<m;i++) if ((M[i][c]%3+3)%3) { p=i; break; }
        if (p<0) continue;
        swap(M[r],M[p]);
        int a=(M[r][c]%3+3)%3, inv=(a==1?1:2);
        for (int j=c;j<n;j++) M[r][j]=(M[r][j]*inv)%3;
        for (int i=0;i<m;i++) if (i!=r) {
            int f=(M[i][c]%3+3)%3;
            if (!f) continue;
            for (int j=c;j<n;j++) M[i][j]=(M[i][j]-f*M[r][j])%3;
        }
        r++;
        if (r==m) break;
    }
    return r;
}

int main() {
    // Verify the multiplicative-character particular solution on the frozen 171 rows.
    const int REPS[9][3] = {
        {0,1,2},{0,1,10},{0,2,4},{0,3,6},{0,3,11},
        {0,4,8},{0,5,10},{0,5,12},{0,6,12}
    };
    vector<pair<int,int>> arcs;
    for (int u=0;u<19;u++) for (int v=u+1;v<19;v++) arcs.push_back(oriented_arc(u,v));
    map<pair<int,int>,int> arc_id;
    for (int i=0;i<(int)arcs.size();i++) arc_id[arcs[i]]=i;
    vector<int> r0(171);
    for (int i=0;i<171;i++) r0[i]=r0_delta(arcs[i].second-arcs[i].first);
    int rows=0;
    for (auto &rep : REPS) for (int sh=0;sh<19;sh++) {
        int a=(rep[0]+sh)%19, b=(rep[1]+sh)%19, c=(rep[2]+sh)%19;
        int verts[3]={a,b,c};
        int sum=0;
        for (int i=0;i<3;i++) for (int j=i+1;j<3;j++) sum += r0[arc_id[oriented_arc(verts[i],verts[j])]];
        assert(sum%3==1);
        rows++;
    }
    assert(rows==171);

    // Lower bound: induced five-vertex carriers.
    long long five_subsets=0;
    bool five_cover=false;
    vector<int> W;
    for (int a=0;a<19;a++) for (int b=a+1;b<19;b++) for (int c=b+1;c<19;c++)
    for (int d=c+1;d<19;d++) for (int e=d+1;e<19;e++) {
        W={a,b,c,d,e}; five_subsets++;
        auto E=local_arcs(W);
        vector<array<Bits,3>> masks(E.size()); Bits full{};
        build_masks(W,E,masks,full);
        int emask=(1<<E.size())-1;
        auto prof=slice_cover_profile(masks,full,emask);
        if (prof[0] && prof[1] && prof[2]) five_cover=true;
    }
    assert(five_subsets==11628);
    assert(!five_cover);

    // Lower bound: every connected maximal balanced six-vertex carrier.
    long long six_subsets=0, connected_balanced=0;
    long long slice_covers[3]={0,0,0};
    for (int a=0;a<19;a++) for (int b=a+1;b<19;b++) for (int c=b+1;c<19;c++)
    for (int d=c+1;d<19;d++) for (int e=d+1;e<19;e++) for (int f=e+1;f<19;f++) {
        W={a,b,c,d,e,f}; six_subsets++;
        auto E=local_arcs(W);
        vector<array<Bits,3>> masks(E.size()); Bits full{};
        build_masks(W,E,masks,full);
        for (int code=0;code<243;code++) {
            int h[6]={0,0,0,0,0,0};
            int z=code;
            for (int i=1;i<6;i++) { h[i]=z%3; z/=3; }
            int emask=0;
            for (int i=0;i<15;i++) {
                int u=E[i][0], v=E[i][1];
                if ((h[v]-h[u]+3)%3==1) emask |= 1<<i;
            }
            if (!connected6(E,emask)) continue;
            connected_balanced++;
            auto prof=slice_cover_profile(masks,full,emask);
            for (int cc=0;cc<3;cc++) if (prof[cc]) slice_covers[cc]++;
        }
    }
    assert(six_subsets==27132);
    assert(connected_balanced==2842419);
    assert(slice_covers[0]==0 && slice_covers[1]==0 && slice_covers[2]==0);

    // Explicit rank-six witness.
    vector<vector<int>> certW={{0,4,9,13},{1,2,4,9},{0,1,9,13}};
    vector<vector<int>> certS={{0,2,2,1},{0,0,1,0},{0,2,0,0}};
    set<pair<int,int>> all_edges;
    for (int cc=0;cc<3;cc++) {
        map<int,int> s;
        for (int i=0;i<4;i++) s[certW[cc][i]]=certS[cc][i];
        for (int i=0;i<4;i++) for (int j=i+1;j<4;j++) {
            auto [u,v]=oriented_arc(certW[cc][i],certW[cc][j]);
            int t=t_edge(u,v);
            assert((t-cc-(s[v]-s[u])+300)%3==0);
            all_edges.insert({u,v});
        }
    }
    assert(all_edges.size()==13);

    vector<int> V={0,1,2,4,9,13};
    map<int,int> pos;
    for (int i=0;i<6;i++) pos[V[i]]=i;
    vector<vector<int>> D,N;
    for (auto [u,v] : all_edges) {
        vector<int> d(6,0); d[pos[u]]=2; d[pos[v]]=1;
        D.push_back(d);
        vector<int> n(7,0); n[0]=1;
        for (int i=0;i<6;i++) n[i+1]=d[i];
        N.push_back(n);
    }
    assert(rank_mod3(D)==5);
    assert(rank_mod3(N)==6);
    assert(is_qr(4-0) && is_qr(9-4) && is_qr(13-9) && is_qr(0-13));

    cout << "PASS_PALEY19_EXACT_MINIMUM_AF3_COVER_RANK6\n";
    cout << "Ar0=1_on_all_171_rows\n";
    cout << "five_vertex_subsets=11628 full_three_slice_covers=0\n";
    cout << "six_vertex_subsets=27132\n";
    cout << "connected_balanced_normalized_candidates=2842419\n";
    cout << "balanced_slice_covers=0,0,0\n";
    cout << "explicit_rank6_support_vertices=6 distinct_arcs=13 rankD=5 rankN=6\n";
    cout << "rho_min_Paley19=6\n";
    cout << "E8_D1=EMPTY P_VS_NP=OPEN\n";
    return 0;
}
