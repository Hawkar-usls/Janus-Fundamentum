#include <array>
#include <cassert>
#include <iostream>
#include <set>
#include <tuple>
#include <vector>

int mod3(int x){ x%=3; if(x<0) x+=3; return x; }

using State = std::array<int,6>;
using Freq = std::array<int,6>;

State wire_state(int c,int s,int q){
    // Port order: L0,L2,L3,R0,R2,R3
    return {
        mod3(c+s),
        mod3(c+s*q),
        mod3(c),
        mod3(c+s*q),
        mod3(c-s*(1+q)),
        mod3(c+s*(q-1))
    };
}

int dot(const Freq& k,const State& x){
    int z=0; for(int i=0;i<6;++i) z+=k[i]*x[i]; return mod3(z);
}

int dotv(const Freq& k,const std::array<int,6>& v){
    int z=0; for(int i=0;i<6;++i) z+=k[i]*v[i]; return mod3(z);
}

int h(int t){ return t==0 ? 2 : -1; }

int main(){
    const std::array<int,6> vp={1,1,0,1,1,0};
    const std::array<int,6> vm={1,2,0,2,0,1};

    std::vector<State> states;
    std::set<State> unique_states;
    for(int c=0;c<3;++c){
        for(int s: {1,2}){
            for(int q: {1,2}){
                auto x=wire_state(c,s,q);
                states.push_back(x);
                unique_states.insert(x);
            }
        }
    }
    assert(states.size()==12);
    assert(unique_states.size()==12);

    std::uint64_t outside_zero=0;
    std::uint64_t amp12=0,amp3=0,ampm6=0;

    for(int code=0;code<729;++code){
        int t=code;
        Freq k{};
        for(int i=5;i>=0;--i){ k[i]=t%3; t/=3; }

        int sigma=0; for(int z:k) sigma=mod3(sigma+z);
        const int lp=dotv(k,vp);
        const int lm=dotv(k,vm);

        // Exact cyclotomic count: sum_j n_j * omega^j.
        // This vanishes iff n0=n1=n2. If n1=n2 it is the integer n0-n1.
        int n[3]={0,0,0};
        for(const auto& x:states) ++n[dot(k,x)];

        if(sigma!=0){
            assert(n[0]==4 && n[1]==4 && n[2]==4);
            ++outside_zero;
            continue;
        }

        assert(n[1]==n[2]);
        const int exact_amp=n[0]-n[1];
        const int predicted=3*(h(lp)+h(lm));
        assert(exact_amp==predicted);

        if(lp==0 && lm==0){ assert(exact_amp==12); ++amp12; }
        else if((lp==0) != (lm==0)){ assert(exact_amp==3); ++amp3; }
        else { assert(exact_amp==-6); ++ampm6; }
    }

    assert(outside_zero==486);
    assert(amp12==27);
    assert(amp3==108);
    assert(ampm6==108);

    std::cout << "PASS: 12 affine wire states are distinct\n";
    std::cout << "PASS: exact F3 Fourier identity holds on all 3^6=729 frequencies\n";
    std::cout << "PASS: support is exactly sigma(k)=0, size 243\n";
    std::cout << "SPECTRUM_COUNTS=zero_outside:486,amp12:27,amp3:108,amp-6:108\n";
    std::cout << "VERDICT: C4_WIRE_F3_FOURIER_TWO_LINEAR_FORM_IDENTITY_CONFIRMED\n";
    std::cout << "P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY\n";
}
