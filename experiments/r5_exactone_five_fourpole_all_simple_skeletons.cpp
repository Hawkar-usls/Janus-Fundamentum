// R5: exact all-size SEMANTIC grammar for 5 cubic fourpoles joined by
// seven ordinary edges along a SIMPLE connected five-block skeleton.
// There are exactly FOUR connected unlabelled simple 5-vertex graphs
// with 7 edges. Every colourable connected cubic fourpole has one of
// the proven 11 ordered physical S3-invariant fourport signatures.
// Enumerate 11^5 choices and all 15 perfect logical pairings.
//
// Per skeleton, classes 161051, GOOD-only paired cases by truth bitmask:
// skeleton0: 1:3290 2:3038 3:24 4:3542 5:0 6:12 7:0
// skeleton1: 1:1614 2:807  3:0  4:5220 5:0 6:0  7:0
// skeleton2: 1:1033 2:2582 3:25 4:3572 5:13 6:4 7:0
// skeleton3: 1:1353 2:1084 3:22 4:2582 5:4 6:8 7:0
// Thus ZERO full three-bit 108-state Exact-One relations across all
// four simple five-block 7-join grammars and all internal block sizes.
// This is NOT a no-go for arbitrary single irreducible sixpoles,
// non-simple block skeletons, or any larger skeleton.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <utility>
using namespace std;

static int deg[5], extnum[5], incident[5][4], inputKey[2187][5];
static int classes[11], p3[5]={1,3,9,27,81};
static uint16_t support[5][11][81],allowed[729];
static uint8_t bitat[729][15];
static int matching[15][3][2];

void setup_common(){
 int j=0;
 for(int k=2;k<=4;k++)for(int m=1;m<16;m++)
  if(__builtin_popcount(unsigned(m))==k)classes[j++]=m;
 if(j!=11)exit(2);
 int m=0;
 for(int i=1;i<6;i++){
  int other[4],z=0;
  for(int t=1;t<6;t++)if(t!=i)other[z++]=t;
  for(int j=1;j<4;j++){
   int last[2],z=0;
   for(int t=1;t<4;t++)if(t!=j)last[z++]=other[t];
   matching[m][0][0]=0;matching[m][0][1]=i;
   matching[m][1][0]=other[0];matching[m][1][1]=other[j];
   matching[m][2][0]=last[0];matching[m][2][1]=last[1];
   m++;
  }
 }
 if(m!=15)exit(3);
 for(int q=0;q<729;q++){
  int port[6],v=q;
  for(int k=5;k>=0;k--){port[k]=v%3;v/=3;}
  for(int m=0;m<15;m++){
   int onehot=0,count=0;
   for(int k=0;k<3;k++)
    if(port[matching[m][k][0]]==port[matching[m][k][1]])
     {onehot=1<<k;count++;}
   if(count==1){allowed[q]|=uint16_t(1<<m);bitat[q][m]=onehot;}
  }
 }
}

void setup_skeleton(array<pair<int,int>,7> edges){
 for(int v=0;v<5;v++){
  deg[v]=0;
  for(int i=0;i<4;i++)incident[v][i]=-1;
  for(int c=0;c<11;c++)for(int x=0;x<81;x++)
   support[v][c][x]=0;
 }
 for(int k=0;k<7;k++){
  auto [a,b]=edges[k];
  incident[a][deg[a]++]=k;
  incident[b][deg[b]++]=k;
 }
 int outer=0;
 for(int v=0;v<5;v++){
  if(deg[v]<1||deg[v]>4)exit(4);
  extnum[v]=4-deg[v];outer+=extnum[v];
 }
 if(outer!=6)exit(5);
 static const int reps[4][4]={
  {0,0,0,0},{0,0,1,1},{0,1,0,1},{0,1,1,0}};
 static const int colourPerm[6][3]={
  {0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
 for(int v=0;v<5;v++)for(int cls=0;cls<11;cls++)
  for(int orb=0;orb<4;orb++)if(classes[cls]&(1<<orb))
   for(int perm=0;perm<6;perm++){
    int colours[4];
    for(int j=0;j<4;j++)
     colours[j]=colourPerm[perm][reps[orb][j]];
    int outside=0,inside=0;
    for(int j=0;j<extnum[v];j++)
     outside=outside*3+colours[j];
    for(int j=extnum[v];j<4;j++)
     inside=inside*3+colours[j];
    support[v][cls][inside] |= uint16_t(1<<outside);
   }
 for(int idx=0;idx<2187;idx++){
  int c[7],r=idx;
  for(int j=6;j>=0;j--){c[j]=r%3;r/=3;}
  for(int v=0;v<5;v++){
   int key=0;
   for(int j=0;j<deg[v];j++)
    key=key*3+c[incident[v][j]];
   inputKey[idx][v]=key;
  }
 }
}

struct Relation {
 uint16_t viable=32767;
 bool nonempty=false;
 int count=0;
 array<int,15> bitmask{};
};

Relation exact_relation(array<int,5> ids,bool full){
 Relation r;
 bool seen[729]{};
 for(int config=0;config<2187;config++){
  uint16_t choices[5];bool failed=false;
  for(int v=0;v<5;v++){
   choices[v]=support[v][ids[v]][inputKey[config][v]];
   if(!choices[v]){failed=true;break;}
  }
  if(failed)continue;
  auto emit=[&](auto&& self,int v,int code)->void {
   if(!full&&r.viable==0)return;
   if(v==5){
    r.nonempty=true;
    if(full){if(!seen[code]){seen[code]=true;r.count++;}}
    else r.viable &= allowed[code];
    return;
   }
   for(int x=0;x<p3[extnum[v]];x++)
    if(choices[v]&(1<<x)){
     self(self,v+1,code*p3[extnum[v]]+x);
     if(!full&&r.viable==0)return;
    }
  };
  emit(emit,0,0);
  if(!full&&r.viable==0)return r;
 }
 if(full)for(int q=0;q<729;q++)if(seen[q]){
  r.viable &= allowed[q];
  for(int m=0;m<15;m++)r.bitmask[m] |= bitat[q][m];
 }
 return r;
}

void audit(array<pair<int,int>,7> skeleton,int index,
           long long emptyExpected,const array<long long,8>& expected){
 setup_skeleton(skeleton);
 long long empty=0,nonempty=0,counts[8]{};
 for(int a=0;a<11;a++)for(int b=0;b<11;b++)
  for(int c=0;c<11;c++)for(int d=0;d<11;d++)
   for(int e=0;e<11;e++){
    array<int,5> cls={a,b,c,d,e};
    Relation fast=exact_relation(cls,false);
    if(!fast.nonempty){empty++;continue;}
    nonempty++;
    if(!fast.viable)continue;
    Relation all=exact_relation(cls,true);
    if(fast.viable!=all.viable)exit(6);
    for(int p=0;p<15;p++)if(all.viable&(1<<p)){
     int bit=all.bitmask[p];
     if(bit<1||bit>7)exit(7);
     counts[bit]++;
     if(bit==7)std::cout<<"UNEXPECTED THREEBIT CLASS "<<index
       <<" "<<a<<" "<<b<<" "<<c<<" "<<d<<" "<<e<<"\n";
    }
   }
 if(empty!=emptyExpected||nonempty!=161051-empty)exit(8);
 for(int j=0;j<8;j++)if(counts[j]!=expected[j])exit(9);
 cout<<"FIVE_4POLE_GRAMMAR_SKELETON_"<<index
     <<" CLASS_ASSIGNMENTS 161051"
     <<" EMPTY "<<empty<<" GOOD_BIT_MASK_COUNTS";
 for(int j=1;j<8;j++)cout<<" "<<j<<":"<<counts[j];
 cout<<" PASS\n";
}

int main(){
 setup_common();
 audit({{{0,1},{0,2},{0,3},{0,4},{1,2},{1,3},{1,4}}},
       0,1545,{{0,3290,3038,24,3542,0,12,0}});
 audit({{{0,1},{0,2},{0,3},{0,4},{1,2},{1,3},{2,3}}},
       1,1584,{{0,1614,807,0,5220,0,0,0}});
 audit({{{0,1},{0,2},{0,3},{0,4},{1,2},{1,3},{2,4}}},
       2,1213,{{0,1033,2582,25,3572,13,4,0}});
 audit({{{0,1},{0,2},{0,3},{1,2},{1,3},{2,4},{3,4}}},
       3,868,{{0,1353,1084,22,2582,4,8,0}});
 cout<<"FOUR_CONNECTED_SIMPLE_5BLOCK_7EDGE_SKELETONS"
       <<" ZERO_FULL_GOOD_THREEBIT_108_RELATIONS PASS\n";
 cout<<"IRREDUCIBLE_CORES_AND_LARGER_OR_MULTIEDGE_BLOCK_SKELETONS_OPEN\n";
}
