# R5 Parity — Fixed-M Hall-tight / DM trade decomposition

Date: 2026-10-09

Predecessor:
`research/R5_PARITY_FIXED_M_TRADE_SPAN_NORMAL_FORM_2026-10-09_v1.0.md`

Mainline provenance anchor:
`e7d6790d533f9acd3c4fe7f2439542dfbfa3361c`

Scientific ceiling:

```text
THIS CHECKPOINT DOES NOT PROVE THE FULL
TRADE SMOOTH-COUNT / SPAN-SEPARATOR DICHOTOMY.

IT IDENTIFIES THE EXACT HALL/DM OBJECT CARRIED BY A CONNECTED FIXED-M TRADE
AND PROVES AN EXACT PRODUCT DECOMPOSITION FOR MUTUALLY COMPATIBLE TRADES.

P_VS_NP = OPEN.
```

## 1. Fixed-M incidence graph

Use the fixed-M normal form from the predecessor checkpoint.

Let:

* L = V(R_M), the residual variables outside M;
* R = M, the matching blocks;
* K_M=(L,R;E_K), where u in L is adjacent to m in M iff u occurs in one of
  the three clauses covered by m.

Because every residual variable has degree three and linearity forbids it from
sharing two clauses with the same m,

```text
deg_K(u)=3  for every u in L.
```

Each m has six distinct residual neighbours, two from each of its three clause
pairs, so

```text
deg_K(m)=6.
```

The three residual pairs at m are exactly the three R_M edges in B_m.

## 2. Hall surplus on R_M-independent sets

For X subseteq L define

```text
h(X)=|N_K(X)|-|X|.
```

Assume X is independent in R_M.

At one block m, independence permits at most one selected endpoint from each of
the three residual pairs in B_m.  Hence m has at most three neighbours in X.

Counting K-incidences from X gives

```text
3|X|
  = number of K edges from X to N_K(X)
  <= 3|N_K(X)|.
```

Therefore

```text
boxed:
X independent in R_M  =>  h(X)>=0.
```

This is a Hall theorem internal to the exact target geometry.  No global Hall
condition on all of L is needed; globally K_M is unbalanced.

## 3. Tight independent sets are exactly fixed-M trade unions

Still assume X is R_M-independent.

If h(X)=0, then equality holds in the incidence count above.  Consequently
every touched block m in N_K(X) has exactly three neighbours in X.

Since there are three residual pairs at m and X contains at most one endpoint
of each pair, it contains exactly one endpoint from every pair.

Thus every edge of B_m crosses X.

Therefore

```text
delta_R_M(X) = union_{m in N_K(X)} B_m.
```

By the fixed-M block-cut theorem, X is a union of fixed-M trade components.

Conversely every fixed-M trade union has

```text
N_K(X)=P,
|P|=|X|,
```

so h(X)=0.

Hence:

```text
boxed:
X is an R_M-independent Hall-tight set
iff
X is a union of fixed-M trade components.
```

## 4. Connected trades are inclusion-minimal Hall-tight sets

Let T=(S,P) be a connected fixed-M trade.

The bipartite graph K_M[S,P] is 3-regular:

* each u in S has all its three K-neighbours in P;
* each m in P has exactly one selected endpoint in each of its three pairs.

Take a nonempty proper X subset S.

If |N_K(X)|=|X|, the same degree count forces every vertex in N_K(X) to have
all three of its selected-side neighbours inside X.  Therefore there is no edge
of K_M[S,P] between X union N_K(X) and its complement, contradicting
connectedness.

So:

```text
boxed:
for every nonempty proper X subset S,
|N_K(X)|>|X|.
```

Thus S is inclusion-minimal among nonempty R_M-independent Hall-tight sets.

Conversely, suppose S is a nonempty R_M-independent Hall-tight set that is
inclusion-minimal among such sets.

Section 3 says S is a union of fixed-M connected trade components.
If there were more than one component, the residual shore of one component
would be a proper nonempty independent Hall-tight subset of S.

Contradiction.

Therefore S is one connected trade.

So:

```text
boxed:
CONNECTED FIXED-M TRADE
=
INCLUSION-MINIMAL NONEMPTY R_M-INDEPENDENT HALL-TIGHT SET.
```

## 5. Dulmage-Mendelsohn interpretation

For a connected trade T=(S,P), K_M[S,P] is balanced and 3-regular, hence it
has a perfect matching.

Section 4 gives the strict Hall inequalities

```text
|N(X)|>|X|
```

for every nonempty proper X subset S.

This is exactly the irreducible balanced matching block condition behind the
Dulmage-Mendelsohn decomposition: the trade block has one DM component.

Thus every connected fixed-M trade is a balanced DM-irreducible block embedded
inside the globally unbalanced graph K_M.

External reference:
Berczi, Iwata, Kato, Yamaguchi,
"Making Bipartite Graphs DM-irreducible",
arXiv:1612.08828.

This reference supplies the standard DM language; Sections 2-4 above prove the
special JANUS characterization directly.

## 6. Compatible-trade uncrossing theorem

The neighbourhood-size function

```text
h(X)=|N_K(X)|-|X|
```

is submodular on all left-side subsets because |N_K(.)| is submodular and
cardinality is modular.

Let S1,S2 be fixed-M trade unions and assume

```text
S1 union S2
```

is independent in R_M.

Then S1 intersection S2 is also independent.

By Section 2,

```text
h(S1 union S2)>=0,
h(S1 intersection S2)>=0.
```

But h(S1)=h(S2)=0 and submodularity gives

```text
h(S1 union S2)+h(S1 intersection S2)
<= h(S1)+h(S2)=0.
```

Hence both terms vanish:

```text
boxed:
h(S1 union S2)=h(S1 intersection S2)=0.
```

So union and intersection are themselves trade unions.

## 7. Distinct connected compatible trades are completely disjoint

Let S1,S2 be distinct connected trades and assume their union is
R_M-independent.

If S1 intersection S2 were nonempty, Section 6 would make it a nonempty
Hall-tight independent set properly contained in at least one of S1,S2,
contradicting the minimality theorem.

Therefore

```text
S1 intersection S2 = empty.
```

Moreover,

```text
|N(S1 union S2)|
=|S1 union S2|
=|S1|+|S2|
=|N(S1)|+|N(S2)|.
```

Since

```text
N(S1 union S2)=N(S1) union N(S2),
```

this equality forces

```text
N(S1) intersection N(S2)=empty.
```

Thus compatible connected trades are disjoint on both sides:

```text
boxed:
S1 cap S2 = empty,
P1 cap P2 = empty.
```

Their simultaneous flip is exactly the product of two independent trade flips.

For a mutually compatible family the same argument gives pairwise disjoint
residual shores and pairwise disjoint M-block shores, so every subcollection
can be flipped independently.

## 8. Product decomposition consequence

Fix a minimum matching M and a weight vector w.

Restrict to connected zero-w-circulation M-trades.

Any mutually compatible subfamily

```text
T1,...,Tk
```

is pairwise disjoint on both matching sides and therefore generates exactly

```text
2^k
```

minimum matchings by independently choosing which components to flip.

This exponential multiplicity is algorithmically benign: it is an explicit
product decomposition, not an entangled family.

If every connected trade has volume at least g, then

```text
k*g <= |M|,
```

so

```text
k <= |M|/g.
```

The genuinely hard family is therefore not "many trades"; it is many
near-minimum trades with extensive incompatibility.

## 9. Exact form of incompatibility

Let S1,S2 be distinct connected trades.

If they overlap, Section 7 says their union cannot be R_M-independent.

Because each Si is independently R_M-independent, every violating R_M edge
must have one endpoint in

```text
S1-S2
```

and the other in

```text
S2-S1.
```

If S1 and S2 are disjoint but incompatible, an R_M edge directly joins the two
sets.

Therefore every incompatibility between distinct connected trades has a
concrete witness in the residual cubic graph R_M:

```text
either overlap plus an exclusive-to-exclusive R_M edge,
or a direct cross-edge between disjoint shores.
```

This converts the unresolved smooth-count problem into a structured
intersection/incompatibility problem for DM-irreducible tight blocks.

## 10. Refined dichotomy target

The previous target

```text
many near-minimum trades
=>
low-connectivity trade-span separator
```

can now be sharpened.

For the family F of connected zero-circulation M-trades of volume at most
alpha*g, define the incompatibility graph J:

```text
V(J)=F,
T1T2 in E(J)
iff
S(T1) union S(T2) is not independent in R_M.
```

Then:

* every independent set of J is an exact product decomposition into pairwise
  disjoint trade blocks;
* every edge of J is witnessed locally by overlap / an R_M conflict edge;
* every trade vertex of J is a balanced DM-irreducible Hall-tight block.

The remaining theorem can therefore be stated as:

```text
DM-TIGHT TRADE INCOMPATIBILITY DICHOTOMY

For fixed alpha>1, either

A. F has polynomial size; or

B. J contains a polynomially discoverable product/decomposition structure
   that induces a low-order separator of the signed trade span / exact-cover
   interface compatible with E109-E111 additive DP.
```

A mere large physical separator inside one trade is neither required nor
possible in general.

## 11. What DM theory does and does not give automatically

Classical DM decomposition canonically decomposes a *fixed bipartite graph*
with respect to its maximum matchings.

Here each connected trade selects its own balanced induced left-closed block
K_M[S,N(S)] inside one larger unbalanced graph K_M.

Therefore standard DM decomposition does not automatically enumerate or
separate all such embedded trade blocks.

The new result is the identification of each connected trade with one
DM-irreducible tight block; a global theorem controlling a superpolynomial
family of overlapping such blocks is still required.

## Claim boundary

```text
INDEPENDENT_HALL_SURPLUS_NONNEGATIVE = PROVED.
HALL_TIGHT_INDEPENDENT_SET = TRADE_UNION = PROVED.
CONNECTED_TRADE = MINIMAL_HALL_TIGHT_DM_BLOCK = PROVED.
COMPATIBLE_CONNECTED_TRADES_ARE_DISJOINT_PRODUCT_FACTORS = PROVED.

SUPERPOLY_INCOMPATIBLE_DM_BLOCKS => LOW SPAN CONNECTIVITY = OPEN.
POLYNOMIAL ISOLATING FAMILY = OPEN.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT CONSTRUCTED.
P_VS_NP = OPEN.
```
