# R5 — Exposed Boolean Exact-One sixpole: complete small-graph boundary search, 3-wire composition saturation, and GF(3) PC decoder ledger

Date: 2026-10-13 (Europe/Kyiv).
Research PR #516 DRAFT; default branch untouched.
Starting checkpoint: `0c53bd5b246996f85650d894b5937266ed5b2f84`.
**Single ultimate goal**: a total uniform deterministic n^C bit-time solver
for EVERY original square/cubic/linear positive Exact-One (SCL) source,
with SAT original witness or UNSAT; NOT CONSTRUCTED.
P vs NP remains OPEN. A fixed GF(3) PC degree lower bound >=4 is
already source-proved (J5/SCL90 frozen dual), but any bound growing
with input size remains UNPROVED.

## 1. Exact interface definition — do not confuse bit projection with physical edge colours

A proper 3-edge-coloured cubic sixpole has six labelled open semiedges.
Partition them into three labelled disjoint two-port connectors
`(p0,p3),(p1,p4),(p2,p5)` or an arbitrary matching of the six labels.
Define `t_i=1` exactly when the two connector *edge colours* agree.
The desired exposed boolean `Exact-One` gate would realize **exactly**
`{100,010,001}` as the projection of all full proper colourings to
these three bits, with all six ports remaining AVAILABLE for wiring
to another graph. An open multipole in isolation is not a legal closed
SCL source; only a suitable closed simple cubic graph gives native
original SCL.

Even if the projected Boolean relation is correct, gluing two
multipoles is permitted only when EACH physical connecting port
has the SAME 3-edge colour on both sides. Matching Boolean equality
bits alone is insufficient for source-semantic gluing.

The classical cubic multipole parity law says that the six port
colours have even counts for each label. Thus any three paired equality
bits have support within `{000,100,010,001,111}`. The target exact-one
subset itself passes this necessary parity restriction; parity alone
does NOT rule it out.

## 2. Full finite small-graph theorem: |V_internal|>=8 necessary

For a connected simple open cubic sixpole without isolated free edges,
let n be the number of internal vertices and m the number of ordinary
internal edges. Counting incidences gives `2m+6=3n` so n is even.
For n=2, m=0, so no connected such internal graph exists.
For n=4 and n=6, **enumerate every labelled subset** of the edges
of simple K_n of size `m=(3n-6)/2`; keep precisely connected
graphs with all internal degrees 1..3. Each internal vertex has
`3-deg(v)` labelled dangling semiedges. Enumerate all proper
internal 3-edge-colourings, then every ordering of missing colours
at each dangling vertex, and all 15 pairings of the six ports.
The finite exact truth projection is compared to `{100,010,001}`.

Frozen counts (labelled graphs, not isomorphism classes):
- n=4: 16 internal graphs, 240 connector pairings, 0 exact-one.
- n=6: 2700 internal graphs, 40500 connector pairings, 0 exact-one.
- n<=6: 2716 graphs, 40740 pairings, 0 exact-one.

As this is exhaustive over the stated simple connected class,
**an exposed exact-one sixpole, if it exists there, has at least EIGHT
internal vertices**. This is a finite classification theorem, not a
universal graph-size lower bound for non-simple, disconnected, isolated
free-edge, higher-port or differently coded constructions.

## 3. Every three-edge matching cut of Petersen, all 15 pairings

The 10-vertex Petersen graph has exactly 145 distinct 3-edge subsets
with six distinct endpoints. For each, remove those three independent
edges and attach one port at each exposed endpoint. The remaining
10-vertex internal graph has 12 ordinary edges and six semiedges.
Enumerate EVERY internal proper 3-edge-colouring and every one of
the 15 unordered matchings of six port labels.

Exact results across **2175** completed pairings:
- 145 natural cut-end reconnections yield the `AtMostOne` Boolean
  relation `{000,100,010,001}` (Petersen uncolourability excludes 111).
- 2030 other pairings yield the full five allowed parity patterns
  `{000,100,010,001,111}`.
- 0 yield exactly `{100,010,001}`.

Thus no choice of a cut of 3 independent Petersen edges and a
re-pairing of its six existing ports supplies exposed Exact-One.
This finite calculation does NOT classify all 10-vertex sixpoles.

## 4. ALL pairwise 3-wire compositions of the two frozen 6-poles

Let `C` be the C6 sixpole from previous research, with its six
port signatures enumerated from 66 proper internal edge-colourings.
Let `P` be the fixed Petersen sixpole from three disjoint severed
edges `(0,1),(2,3),(5,8)`, with 84 distinct port signatures
from 108 proper internal edge-colourings.

For every type `C+C`, `C+P`, `P+P`:
- select 3 of 6 ports of the left and 3 of 6 of right (20² choices);
- pair these selected ports with a bijection (3!=6 choices),
  making three real intercomponent graph edges;
- leave exactly six semiedges OPEN, three from each side;
- evaluate the exact composite set of six-port *physical colours*
  by matching the 3 glued colours and projecting the remaining six;
- test all 15 remaining connector matchings.

This gives precisely 2400 gluing choices, 36000 projected Boolean
relations **per type**, or **7200 gluings and 108000 tests total**.

The exact finite outcome is **NO exposed Exact-One** in any of these
108000 tests. In fact:
- C+P: all 36000 projections contain the complete five parity bits.
- P+P: all 36000 projections contain the complete five parity bits.
- C+C: 35712 projections have all five; the other 288 have four
  patterns, each including 000 and 111.

This is a provably **exact compositional enumerator**: two proper
internal colourings extend to a legal 3-edge colouring after gluing
iff colours agree on every glued semiedge. There is no assumption
that equality of *Boolean* encoded bits suffices.

The composition family is STRICTLY finite: it says nothing about
other gadgets, more than two component blocks, different numbers of
glued wires, or general sixpoles.

## 4-A. Stronger physically compositional C4 fourpole transfer

The previous C4 `Boolean equal-bit wire` must NOT be treated as
an unrestricted wire for ordered physical edge-colour pairs. A full
source-colouring enumeration gives EXACTLY **15 distinct** four-port
colour signatures, with multiplicities:
- TRUE left pair `AA`: right pair `BB` for ANY colour B
  (9 signatures; 3 all-equal signatures have multiplicity TWO,
  6 unequal A/B signatures multiplicity ONE).
- FALSE left pair `AB` with A!=B: right pair is necessarily
  **REVERSED** `BA` (6 signatures, each multiplicity ONE).
There are no other full boundary signatures. In particular, a
FALSE ordered pair `AB` cannot pass through C4 as `AB` without
reversing its physical endpoint order; even though the Boolean bit
is preserved. This explicitly exposes the nontrivial gauge/port
orientation that a full PC-preserving global reduction must track.

The assertion-backed exact port-colour table is part of
`experiments/r5_universal_boolean_pair_xor6_tseitin_saturation_falsifier.py`
and the combined one-HEAD workflow.

## 5. Positive algebraic result: full original-source GF(3) equality-bit decoder certificate

Let `p_c`,`q_c`, c in {0,1,2}, be original native SCL
Boolean indicators for two (closed) source edges p,q, with source
edge Exact-One generators

`E_p=p0+p1+p2-1`, `E_q=q0+q1+q2-1`,

and original Boolean generators `B_z=z²-z`. Define degree-2

`T(p,q)=p0q0+p1q1+p2q2`.

On valid 3-colour source assignments this is precisely the
Boolean equality predicate for their edge colours. More strongly,
the predicate's Booleanity has an explicit **degree <=4 original-source
polynomial ideal certificate**, not merely a truth-table check.

For each distinct colour pair i,j and remaining k,
the LITERAL degree-2 identity over GF3 is

`R_ij := (p_i+p_j-p_k) E_p - B_(p_i)-B_(p_j)+B_(p_k) = 2 p_i p_j`.

Then by exact expansion,

```
T² - T =
  sum_i [ B_(p_i) q_i² + p_i B_(q_i) ]
  + sum_(i<j) R_ij q_i q_j         over GF(3).
```

The RHS consists exclusively of original source generators with
multipliers of total degree at most two. Every term has total degree
<=4. Therefore `T²-T` belongs to the original edge-row/Boolean ideal
with certificate degree <=4. No nonlinear global graph condition
is assumed; the identity holds for *every pair of native source edges*.

This is a genuinely reusable **local proof-carrying decoder**.
It does not alone prove existence of a total exposed Exact-One
gadget, nor a low-degree simulation of arbitrary base CSP equations.

Source:
`experiments/r5_universal_boolean_pair_gf3_decoder_charge_gauge.py`.

## 6. New global negative theorem: pure signed C6 reinterpretation cannot create odd Tseitin charge

Suppose a base simple cubic graph H has C6 odd-XOR at each vertex:
`xor_(e incident to v) t_e=1`. A C4-style equality wire
physically identifies the two endpoint *equality bits* `t_e`.

Try to define logical edge variable `b_e=t_e xor s_e`,
choosing a sign s_e independently for each **complete** wire.
At vertex v, the apparent signed parity charge is

`c_v = 1 xor xor_(e incident v) s_e`.

Summing/XOR over all vertices:
`xor_v c_v = (|V(H)| mod 2) xor xor_e (s_e xor s_e) = 0`,
because every finite cubic graph has EVEN number of vertices.

Thus every coherently signed interpretation produces a
Tseitin charge vector of EVEN total parity. It never creates the
required ODD-total contradiction; the physical native graph
continues to have the explicit global proper colouring
(all wire edges colour2, each internal C6 alternates 0/1).

One-sided logical negation s_(u,e)!=s_(v,e) is NOT a physical
inverter: the equality wire enforces `t_(u,e)=t_(v,e)`, so a
single global b_e cannot satisfy both opposite interpretations.
An actual native inverter with correct source semantics, or a
different interface, remains UNCONSTRUCTED.

This is a symbolic all-cubic-graphs theorem; exhaustive parity
sanity checks cover all coherent edge sign patterns on K4 (64),
K3,3 (512), and Petersen (32768).

## 7. Relation to published hardness and PC back-simulation

Holyer (SIAM J. Computing 10(4), 1981,
https://doi.org/10.1137/0210055) proves 3-edge-colouring simple
cubic graphs NP-complete. This alone does **not** establish a
polynomial-calculus degree-preserving reduction.

Hard published base systems:
- Conneryd et al., graph *vertex* 3-colouring PC degree Omega(N),
  ECCC TR25-032 (https://eccc.weizmann.ac.il/report/2025/032/).
- Classical expander Tseitin contradictions, with field and
  encoding restrictions (Buss–Grigoriev–Impagliazzo–Pitassi,
  JCSS 2001, DOI:10.1006/jcss.2000.1726).

For a valid back-simulation, require a **globally consistent,
constant-local, explicit source-variable substitution** `P_j(b)`;
every TARGET native Exact-One source row and Boolean axiom must
have bounded-degree certificates from EXACT original base
constraints, including constraints on all local Boolean patterns,
not just satisfying GLOBAL assignments. Ordinary SAT equivalence
or boundary Boolean truth relations DO NOT suffice.

If all such identities existed uniformly with target variable
degree k and maximum local source derivation degree C, an alleged
degree-d target refutation would pull back to base degree <=k*d+C,
yielding the desired lower bound. That full gadget system
has NOT been constructed.

## 8. Exact tools, provenance, gates

Check:
```
python -u experiments/r5_universal_open_sixpole_2175_108000_signature_composition.py
python -u experiments/r5_universal_boolean_pair_gf3_decoder_charge_gauge.py
```

Workflows:
`.github/workflows/r5-open-sixpole-boundary-composition.yml`,
`.github/workflows/r5-gf3-pair-decoder-charge-gauge.yml`.

Prior exact source reference:
`research/R5_BOOLEAN_PAIR_ODD_XOR_TSEITIN_SATURATION_2026-10-13.md`.

Strict statuses:
- PETERSEN_145x15 = EXHAUSTED, NO OPEN EXACT-ONE
- ALL_CONNECTED_SIMPLE_SIXPOLES_INTERNAL_N_LE_6 = EXHAUSTED, NO OPEN EXACT-ONE
- OPEN_EXACTONE_INTERNAL_N_GE_8 = PROVED WITHIN STATED CLASS
- C6_PETERSEN_PAIRWISE_3WIRE_108000 = EXHAUSTED, NO OPEN EXACT-ONE
- GF3_EQUALITY_BIT_T_BOOLEANITY_DEGREE4 = PROVED EXPLICIT POLYNOMIAL IDENTITY
- COHERENT_SIGNED_C6_CHARGE_ODD = REFUTED FOR ALL CUBIC GRAPHS
- ACTUAL_EXPOSED_EXACTONE_6POLE = NOT CONSTRUCTED, EXISTENCE OPEN
- LOCAL_GLOBAL_COLOR_COMPATIBILITY_AND_PC_BACKSIM = OPEN
- UNBOUNDED_NATIVE_GF3_PC_DEGREE = OPEN
- TOTAL_POLYNOMIAL_SCL_SOLVER = NOT CONSTRUCTED
- P_VS_NP = OPEN
