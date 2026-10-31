# R5 E9 — Z3 Phase Coboundary Island and Higher-Representation Alphabet Firewall

Date: 2026-09-24

Authority: JANUS_DERIVED_EXACT_POLY_YES_ISLAND + REPRESENTATION_FIREWALL__NO_D1_PROMOTION

Parent: R5_E9_NONCOMMUTING_TWO_PERMUTATION_KERNEL_WORD_GATE_V1

Checker: experiments/r5_e9_z3_phase_coboundary_island_checker.py

## 1. Setting

Take a connected normalized cubic component

(I+P+Q)z=0,
z in {-1,2}^n,

where P,Q are permutations of the coordinate set Omega.

No commutativity assumption is made.

Let G=<P,Q> act transitively on Omega.

## 2. Z3 phase / coboundary condition

Orient the labelled Schreier edges by

i -> P(i) with increment +1 mod 3,
i -> Q(i) with increment -1 mod 3.

Seek

phi: Omega -> Z3

such that

phi(P(i))=phi(i)+1,
phi(Q(i))=phi(i)-1

for every coordinate i.

This is a finite difference-potential problem.

Algorithm:

- fix phi(root)=0;
- propagate through P,Q,P^{-1},Q^{-1};
- reject on the first inconsistent already-labelled vertex.

Each directed generator/inverse edge is processed O(1) times.

Hence the test and certificate construction take O(n) time.

Equivalently, every labelled closed walk must have total increment 0 mod 3.

## 3. Phase implies an exact 1-in-3 witness

Suppose phi exists.

For any r in Z3 set

x_i^(r)=1 iff phi(i)=r.

For every row triple

{i,P(i),Q(i)},

the phases are

phi(i), phi(i)+1, phi(i)-1,

which are exactly the three distinct residues 0,1,2.

Therefore exactly one member of every row lies in each chosen phase class.

Hence

A x^(r)=1

for r=0,1,2.

So phase consistency is an exact polynomial YES certificate and yields three canonical witnesses.

Important:

these need not be all witnesses.

## 4. Phase is exactly the one-dimensional zero-mode sector

Let omega be a primitive cube root of unity and define

f_i=omega^{phi(i)}.

Then

f_{P(i)}=omega f_i,
f_{Q(i)}=omega^2 f_i.

Under the permutation-operator convention

(Pf)_i=f_{P(i)},
(Qf)_i=f_{Q(i)},

we get

Pf=omega f,
Qf=omega^2 f,

and therefore

(I+P+Q)f=(1+omega+omega^2)f=0.

So span(f) is a one-dimensional G-subrepresentation contained in the linear kernel.

Conversely, suppose a one-dimensional G-subrepresentation W=span(f) contributes to the kernel.

Then

Pf=u f,
Qf=v f

for roots of unity u,v, because P,Q have finite order.

Kernel membership gives

1+u+v=0.

Since |u|=|v|=1, necessarily

{u,v}={omega,omega^2}.

Transitivity implies every coordinate of a nonzero f is nonzero: if one coordinate vanished, the G-orbit would force all coordinates to vanish.

Normalize one root coordinate to 1.

Because every coordinate is reached by a word in P,Q, all coordinate ratios lie in {1,omega,omega^2}.

Writing f_i=omega^{phi(i)} recovers a phase potential.

If the scalar orientation is (u,v)=(omega^2,omega), replace phi by -phi; the fixed convention (+1,-1) is recovered.

Therefore:

phase exists
iff
a one-dimensional G-subrepresentation contributes a zero-mode of I+P+Q.

## 5. Exact abelianization formulation

Fix a root coordinate o with stabilizer H<=G, so Omega is the transitive G-set G/H.

A phase exists iff there is a homomorphism

chi:G -> Z3

with

chi(P)=1,
chi(Q)=-1,
H subset ker(chi).

Then

phi(g o)=chi(g)

is well defined, and every phase arises this way up to an additive global constant.

Every one-dimensional complex representation is trivial on the commutator subgroup [G,G], hence factors through the abelianization G/[G,G].

Thus the phase test exhausts the complete one-dimensional / abelian-character zero-mode sector relevant to the operator I+P+Q.

Consequently:

phase FAIL
=>
no one-dimensional representation contributes to the kernel.

## 6. Noncommuting large-nullity easy family

For every m>=2 define

Omega=Z3 x Z_m.

Set

P(r,a)=(r+1,a),

and

Q(0,a)=(2,a+1),
Q(1,a)=(0,a),
Q(2,a)=(1,a),

with the second coordinate modulo m.

The action is connected.

P and Q do not commute:

PQ(0,a)=(0,a+1),
QP(0,a)=(0,a).

Yet

phi(r,a)=r

satisfies the phase equations.

So the entire family is SAT in O(n) by the phase certificate.

## 7. Exact rational nullity of the family

Write z_{r,a} for a kernel vector.

The row equations reduce to

z_{0,a}+z_{1,a}+z_{2,a}=0

and

z_{2,a+1}=z_{2,a}.

Thus z_2 is one global constant and for each a one of z_{0,a},z_{1,a} may be chosen freely.

Therefore

dim_Q ker(I+P+Q)=m+1=n/3+1.

This is linearly large nullity despite the linear-time SAT certificate.

## 8. Exact two-letter word count in the family

If the global value z_2=2, then

z_{0,a}=z_{1,a}=-1

for all a: one exact word.

If z_2=-1, then

z_{0,a}+z_{1,a}=1,

so independently for every a the pair is

(2,-1) or (-1,2).

Hence there are

2^m+1

exact {-1,2} kernel words.

This is an explicit infinite falsifier of:

- large nullity => difficult-looking;
- noncommutativity => difficult-looking;
- few exact witnesses as the reason the phase island is easy.

## 9. Phase failure is not an UNSAT certificate

The checker contains a connected noncommuting n=6 control with:

phase = FAIL,
rational nullity = 2,
two valid {-1,2} kernel words.

So the phase test only removes the one-dimensional zero-mode sector.

It does not solve the whole small- or higher-dimensional representation sector.

## 10. Representation decomposition: valid linear algebra

Over C, finite-group permutation representations are semisimple.

Decomposing the permutation module into G-invariant irreducible submodules block-diagonalizes every group element, hence also

I+P+Q.

Thus the unrestricted linear kernel can be analyzed representation block by representation block.

After phase FAIL, every block capable of contributing a zero-mode has irreducible dimension at least 2.

## 11. Alphabet-factorization firewall

The exact JANUS problem is not unrestricted linear kernel membership.

It requires

z in {-1,2}^Omega

in the original coordinate basis.

This coordinate alphabet does not factor across an arbitrary irreducible decomposition.

Minimal example:

R^2 = span(1,1) direct-sum span(1,-1).

The exact alphabet word

(2,-1)

decomposes as

(1/2,1/2) + (3/2,-3/2).

Neither component is itself a {-1,2} word.

Therefore:

IRREP BLOCK DIAGONALIZATION = VALID LINEAR ALGEBRA.

INDEPENDENT EXACT SOLVE PER IRREP = NOT VALID WITHOUT A NEW ALPHABET-LIFT THEOREM.

Any representation-theoretic solver must prove a polynomial exact mechanism for coupling block coordinates back into the original two-letter alphabet.

Otherwise it has solved only the rational relaxation already handled by Gaussian elimination.

## 12. Refined preprocessing

For each connected cubic kernel-word component:

1. component-size / rank / low-nullity filters;
2. known balanced / matching / other proved-P lanes;
3. commuting test;
4. if noncommuting, run the O(n) Z3 phase coboundary test;
5. phase PASS -> output a canonical exact witness;
6. phase FAIL -> only then expose the component to higher-representation analysis.

## 13. New active gate

Freeze:

R5_E9_PHASE_INCONSISTENT_HIGHER_REP_KERNEL_GATE_V1

Input:

a connected cubic normalized overlay

(I+P+Q)z=0,
z in {-1,2}^n,

with:

- PQ != QP;
- Z3 phase coboundary test FAIL;
- no one-dimensional zero-mode sector;
- not in low-nullity or other known-P lanes.

Target:

a polynomial exact contraction/solver using higher-dimensional nonabelian structure while preserving the original two-letter coordinate alphabet or providing a polynomial exact lift.

Forbidden:

- solve representation blocks independently without alphabet-factorization proof;
- enumerate combinations of block solutions;
- drop the {-1,2} condition;
- branch on coordinate letters;
- hide the same coupling in fresh selectors.

## 14. Ceiling

COMMUTING OVERLAY = POLY
NONCOMMUTING Z3-PHASE-CONSISTENT OVERLAY = POLY YES ISLAND
PHASE TEST = O(n)
PHASE TEST EXHAUSTS 1D ZERO-MODE SECTOR = PASS
LARGE-NULLITY NONCOMMUTING EASY FAMILY = PASS
PHASE FAIL DOES NOT IMPLY UNSAT = PASS
IRREP LINEAR DECOMPOSITION = VALID
IRREP ALPHABET FACTORIZATION = OPEN / REQUIRED
HIGHER-DIMENSIONAL PHASE-INCONSISTENT SECTOR = OPEN
D1 = EMPTY
P_VS_NP = OPEN
