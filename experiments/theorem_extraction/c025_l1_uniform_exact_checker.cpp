// C025 independent exact finite checker for the frozen 39100 selector-product.
//
// This checker is NOT a heuristic screen.  On the frozen uniform product family
// it implements the exact frozen v2 macro clause set and the exact raw-unit
// elimination cap semantics using compact positive/negative bitmasks.
//
// Uniform-family macro exactness argument:
//   - untouched product clauses are width 8 and contain no fresh e;
//   - replaced clauses are width 7 and contain -e;
//   - definition clauses have width 2,2,3;
//   - e is fresh, and because the source product is tautology-free a definition
//     clause cannot subsume a replaced clause; width/e separation prevents the
//     other cross-class subsumptions.  Therefore canon_cnf is exactly set-dedupe
//     on these rows, which this checker performs.
//
// Elimination exactness:
//   retained rows enter the raw set once; every positive x negative parent pair
//   is resolved; tautologies are discarded; non-tautological resolvents are
//   charged only on first set insertion by 1+width, exactly matching
//   eliminate_var_capped before optional subsumption.  Crossing cap proves that
//   pivot cannot fit.  No ML/ranking/pruning is used.
//
// P_VS_NP remains OPEN.
#include <bits/stdc++.h>
#include <omp.h>
using namespace std;

struct Clause { uint32_t pos=0, neg=0; };
struct Probe { bool fit=false; long long raw_units=0, pairs=0, tautologies=0; };

static inline uint64_t key_clause(uint32_t pos, uint32_t neg) {
    return (uint64_t(neg) << 32) | uint64_t(pos);
}
static inline int clause_width(const Clause& c) {
    return __builtin_popcount(c.pos | c.neg);
}
static inline bool has_lit(const Clause& c, int lit) {
    uint32_t b = 1u << (abs(lit)-1);
    return lit > 0 ? bool(c.pos & b) : bool(c.neg & b);
}
static inline void add_lit(Clause& c, int lit) {
    uint32_t b = 1u << (abs(lit)-1);
    if (lit > 0) c.pos |= b; else c.neg |= b;
}
static inline void del_lit(Clause& c, int lit) {
    uint32_t b = 1u << (abs(lit)-1);
    if (lit > 0) c.pos &= ~b; else c.neg &= ~b;
}
static inline pair<int,bool> lit_key(int z) { return {abs(z), z < 0}; }

struct PairCmp {
    bool operator()(const pair<int,int>& x, const pair<int,int>& y) const {
        if (lit_key(x.first) != lit_key(y.first)) return lit_key(x.first) < lit_key(y.first);
        return lit_key(x.second) < lit_key(y.second);
    }
};

static Probe raw_probe(const vector<Clause>& cnf, int var, long long cap) {
    const uint32_t bit = 1u << (var-1);
    vector<Clause> pos, neg;
    pos.reserve(4096); neg.reserve(4096);
    unordered_set<uint64_t> raw;
    raw.reserve(350000);
    long long units = 1; // frozen state_units leading 1

    for (const auto& c : cnf) {
        if (c.pos & bit) pos.push_back(c);
        else if (c.neg & bit) neg.push_back(c);
        else {
            uint64_t k = key_clause(c.pos, c.neg);
            if (raw.insert(k).second) units += 1 + clause_width(c);
        }
    }
    if (units > cap) return {false, units, 0, 0};

    long long pair_work = 0, taut = 0;
    for (const auto& p : pos) {
        uint32_t ppos = p.pos & ~bit;
        for (const auto& n : neg) {
            ++pair_work;
            uint32_t rpos = ppos | n.pos;
            uint32_t rneg = p.neg | (n.neg & ~bit);
            if (rpos & rneg) { ++taut; continue; }
            uint64_t k = key_clause(rpos, rneg);
            if (raw.insert(k).second) {
                units += 1 + __builtin_popcount(rpos | rneg);
                if (units > cap) return {false, units, pair_work, taut};
            }
        }
    }
    return {true, units, pair_work, taut};
}

int main(int argc, char** argv) {
    string input = argc > 1 ? argv[1] : "c025-product.txt";
    ifstream in(input);
    if (!in) { cerr << "cannot open input\n"; return 2; }

    vector<Clause> product;
    string line;
    while (getline(in, line)) {
        stringstream ss(line);
        Clause c; int lit;
        while (ss >> lit) add_lit(c, lit);
        if ((c.pos & c.neg) != 0) { cerr << "tautological product row\n"; return 3; }
        if (clause_width(c) != 8) { cerr << "non-width8 product row\n"; return 4; }
        product.push_back(c);
    }
    if (product.size() != 8100) { cerr << "unexpected product clause count\n"; return 5; }

    set<pair<int,int>, PairCmp> pair_set;
    for (const auto& c : product) {
        vector<int> lits;
        for (int v=2; v<=21; ++v) {
            uint32_t b=1u<<(v-1);
            if (c.pos & b) lits.push_back(v);
            if (c.neg & b) lits.push_back(-v);
        }
        sort(lits.begin(), lits.end(), [](int a,int b){return lit_key(a)<lit_key(b);});
        for (int i=0;i<(int)lits.size();++i) for (int j=i+1;j<(int)lits.size();++j) {
            if (abs(lits[i]) != abs(lits[j])) pair_set.insert({lits[i],lits[j]});
        }
    }
    vector<pair<int,int>> pairs(pair_set.begin(), pair_set.end());
    if (pairs.size() != 744) { cerr << "unexpected v2 pair count=" << pairs.size() << "\n"; return 6; }

    const long long cap = 1214404;
    const int fresh = 22;
    atomic<int> rescue_index(INT_MAX);
    mutex rescue_mu;
    string rescue_json;
    atomic<long long> global_min_margin(LLONG_MAX);
    mutex min_mu;
    int min_pair=-1, min_pivot=-1;
    long long min_raw=-1, min_macro=-1;

    #pragma omp parallel for schedule(dynamic,1)
    for (int idx=0; idx<(int)pairs.size(); ++idx) {
        if (idx >= rescue_index.load()) continue;
        auto [a,b] = pairs[idx];
        unordered_set<uint64_t> seen;
        seen.reserve(10000);
        vector<Clause> macro;
        macro.reserve(8200);
        int replaced=0;

        for (auto c : product) {
            if (has_lit(c,a) && has_lit(c,b)) {
                del_lit(c,a); del_lit(c,b); add_lit(c,-fresh); ++replaced;
            }
            if (seen.insert(key_clause(c.pos,c.neg)).second) macro.push_back(c);
        }
        Clause d1,d2,d3;
        add_lit(d1,-fresh); add_lit(d1,-a);
        add_lit(d2,-fresh); add_lit(d2,-b);
        add_lit(d3, fresh); add_lit(d3,a); add_lit(d3,b);
        for (Clause d : {d1,d2,d3}) if (seen.insert(key_clause(d.pos,d.neg)).second) macro.push_back(d);

        long long macro_units = 1 + (long long)macro.size();
        for (const auto& c : macro) macro_units += clause_width(c);
        if (macro_units > cap) continue;

        for (int pivot=2; pivot<=21; ++pivot) {
            Probe r = raw_probe(macro,pivot,cap);
            long long margin = r.raw_units - cap;
            long long old = global_min_margin.load();
            while (margin < old && !global_min_margin.compare_exchange_weak(old, margin)) {}
            if (margin == global_min_margin.load()) {
                lock_guard<mutex> g(min_mu);
                if (min_pair < 0 || margin < min_raw-cap || (margin == min_raw-cap && make_pair(idx,pivot) < make_pair(min_pair,min_pivot))) {
                    min_pair=idx; min_pivot=pivot; min_raw=r.raw_units; min_macro=macro_units;
                }
            }
            if (r.fit) {
                int cur=rescue_index.load();
                while (idx < cur && !rescue_index.compare_exchange_weak(cur,idx)) {}
                if (idx <= rescue_index.load()) {
                    lock_guard<mutex> g(rescue_mu);
                    ostringstream o;
                    o << "{\"pair_index\":"<<idx<<",\"pair\":["<<a<<","<<b<<"],\"pivot\":"<<pivot
                      <<",\"macro_units\":"<<macro_units<<",\"raw_units\":"<<r.raw_units
                      <<",\"replaced_occurrences\":"<<replaced<<"}";
                    rescue_json=o.str();
                }
                break;
            }
        }
    }

    cout << "{\n";
    cout << "  \"schema\": \"JANUS/C025/L1-UNIFORM-INDEPENDENT-EXACT-CHECKER/v1\",\n";
    cout << "  \"status\": \"" << (rescue_index.load()==INT_MAX ? "COMPLETE_NO_V2_RESCUE" : "EXACT_V2_RESCUE_FOUND") << "\",\n";
    cout << "  \"candidate_pair_count\": 744,\n";
    cout << "  \"root_pivot_count_per_pair\": 20,\n";
    cout << "  \"checked_pair_pivot_scope\": " << (rescue_index.load()==INT_MAX ? 744*20 : -1) << ",\n";
    cout << "  \"cap\": 1214404,\n";
    cout << "  \"minimum_observed_cap_margin\": " << global_min_margin.load() << ",\n";
    cout << "  \"minimum_margin_pair_index\": " << min_pair << ",\n";
    cout << "  \"minimum_margin_pivot\": " << min_pivot << ",\n";
    cout << "  \"minimum_margin_raw_units\": " << min_raw << ",\n";
    cout << "  \"minimum_margin_macro_units\": " << min_macro << ",\n";
    cout << "  \"rescue\": " << (rescue_json.empty()?"null":rescue_json) << ",\n";
    cout << "  \"uniform_macro_exactness_preconditions\": {\"product_width\":8,\"product_clauses\":8100,\"fresh_extension\":22},\n";
    cout << "  \"P_VS_NP\": \"OPEN\"\n";
    cout << "}\n";
    return 0;
}
