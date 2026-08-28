// General exact finite v2 checker for C025 disjoint selector products.
// Input: one canonical product clause per line. argv[2]=cap, argv[3]=first root var,
// argv[4]=last root var. Fresh extension is maxvar+1.
// Implements the exact uniform-family macro set and exact raw-unit capped
// elimination semantics. Search/discovery only until a candidate is separately
// frozen and confirmed. P_VS_NP remains OPEN.
#include <bits/stdc++.h>
#include <omp.h>
using namespace std;
struct C{uint64_t p=0,n=0;};
struct P{bool fit=false; long long u=0;};
struct Key{uint64_t p,n; bool operator==(Key const&o)const{return p==o.p&&n==o.n;}};
struct KH{size_t operator()(Key const&k)const{return hash<uint64_t>{}(k.p^(k.n*0x9e3779b97f4a7c15ULL));}};
static inline int w(C const&c){return __builtin_popcountll(c.p|c.n);} 
static inline void add(C&c,int l){uint64_t b=1ULL<<(abs(l)-1); if(l>0)c.p|=b;else c.n|=b;}
static inline bool has(C const&c,int l){uint64_t b=1ULL<<(abs(l)-1);return l>0?(c.p&b):(c.n&b);} 
static inline void del(C&c,int l){uint64_t b=1ULL<<(abs(l)-1);if(l>0)c.p&=~b;else c.n&=~b;}
static inline pair<int,bool> lk(int z){return {abs(z),z<0};}
struct PC{bool operator()(pair<int,int>const&a,pair<int,int>const&b)const{if(lk(a.first)!=lk(b.first))return lk(a.first)<lk(b.first);return lk(a.second)<lk(b.second);}};
P probe(vector<C>const&cnf,int v,long long cap){uint64_t bit=1ULL<<(v-1);vector<C>a,b;unordered_set<Key,KH>s;s.reserve(400000);long long u=1;for(auto const&c:cnf){if(c.p&bit)a.push_back(c);else if(c.n&bit)b.push_back(c);else if(s.insert({c.p,c.n}).second)u+=1+w(c);}if(u>cap)return {false,u};for(auto const&x:a){uint64_t xp=x.p&~bit;for(auto const&y:b){uint64_t rp=xp|y.p,rn=x.n|(y.n&~bit);if(rp&rn)continue;if(s.insert({rp,rn}).second){u+=1+__builtin_popcountll(rp|rn);if(u>cap)return {false,u};}}}return {true,u};}
int main(int ac,char**av){if(ac<5){cerr<<"usage product cap firstroot lastroot\n";return 2;}string f=av[1];long long cap=stoll(av[2]);int fr=stoi(av[3]),lr=stoi(av[4]);ifstream in(f);if(!in)return 3;vector<C>prod;string line;int maxv=0;while(getline(in,line)){stringstream ss(line);int l;C c;while(ss>>l){add(c,l);maxv=max(maxv,abs(l));}if(c.p&c.n)return 4;prod.push_back(c);}set<pair<int,int>,PC> ps;for(auto const&c:prod){vector<int>ls;for(int v=fr;v<=lr;v++){uint64_t bit=1ULL<<(v-1);if(c.p&bit)ls.push_back(v);if(c.n&bit)ls.push_back(-v);}sort(ls.begin(),ls.end(),[](int a,int b){return lk(a)<lk(b);});for(int i=0;i<(int)ls.size();i++)for(int j=i+1;j<(int)ls.size();j++)if(abs(ls[i])!=abs(ls[j]))ps.insert({ls[i],ls[j]});}vector<pair<int,int>>pairs(ps.begin(),ps.end());int fresh=maxv+1;atomic<int>ri(INT_MAX);mutex mu;string rj;atomic<long long>minm(LLONG_MAX);int mpi=-1,mpv=-1;long long mraw=-1,mmacro=-1;mutex mmu;
#pragma omp parallel for schedule(dynamic,1)
for(int idx=0;idx<(int)pairs.size();idx++){if(idx>=ri.load())continue;auto [a,b]=pairs[idx];unordered_set<Key,KH>seen;seen.reserve(prod.size()+8);vector<C>mac;mac.reserve(prod.size()+3);for(auto c:prod){if(has(c,a)&&has(c,b)){del(c,a);del(c,b);add(c,-fresh);}if(seen.insert({c.p,c.n}).second)mac.push_back(c);}C d1,d2,d3;add(d1,-fresh);add(d1,-a);add(d2,-fresh);add(d2,-b);add(d3,fresh);add(d3,a);add(d3,b);for(auto d:{d1,d2,d3})if(seen.insert({d.p,d.n}).second)mac.push_back(d);long long mu=1+mac.size();for(auto const&c:mac)mu+=w(c);if(mu>cap)continue;for(int v=fr;v<=lr;v++){P q=probe(mac,v,cap);long long margin=q.u-cap;long long old=minm.load();while(margin<old&&!minm.compare_exchange_weak(old,margin)){}if(margin==minm.load()){lock_guard<mutex>g(mmu);if(mpi<0||margin<mraw-cap||(margin==mraw-cap&&make_pair(idx,v)<make_pair(mpi,mpv))){mpi=idx;mpv=v;mraw=q.u;mmacro=mu;}}if(q.fit){int cur=ri.load();while(idx<cur&&!ri.compare_exchange_weak(cur,idx)){}if(idx<=ri.load()){lock_guard<mutex>g(mu);ostringstream o;o<<"{\"pair_index\":"<<idx<<",\"pair\":["<<a<<","<<b<<"],\"pivot\":"<<v<<",\"macro_units\":"<<mu<<",\"raw_units\":"<<q.u<<"}";rj=o.str();}break;}}}
cout<<"{\n\"schema\":\"JANUS/C025/GENERAL-UNIFORM-EXACT-V2-CHECKER/v1\",\n\"status\":\""<<(ri.load()==INT_MAX?"COMPLETE_NO_V2_RESCUE":"EXACT_V2_RESCUE_FOUND")<<"\",\n\"product_clauses\":"<<prod.size()<<",\n\"candidate_pair_count\":"<<pairs.size()<<",\n\"root_pivot_count\":"<<(lr-fr+1)<<",\n\"cap\":"<<cap<<",\n\"minimum_margin\":"<<minm.load()<<",\n\"minimum_pair_index\":"<<mpi<<",\n\"minimum_pivot\":"<<mpv<<",\n\"minimum_raw_units\":"<<mraw<<",\n\"minimum_macro_units\":"<<mmacro<<",\n\"rescue\":"<<(rj.empty()?"null":rj)<<",\n\"P_VS_NP\":\"OPEN\"\n}\n";}
