# R5 — Complete nauty census of every simple connected open Exact-One sixpole with 2..12 internal vertices

Date: 2026-10-13 (Europe/Kyiv).
PR #516 remains DRAFT; main untouched.
Code: `experiments/r5_universal_exposed_exactone_nauty_n8_all_graphs.py`
Workflow: `.github/workflows/r5-exposed-exactone-nauty-n8.yml`

## Precise required gadget

An *open simple connected cubic sixpole* is a finite connected simple
interior graph G=(V,E), with 1<=deg_G(v)<=3 for every internal
vertex, plus 3-deg_G(v) attached labelled dangling semiedges at v.
There are exactly six semiedges; thus
`2|E|+6=3|V|`. In particular |V| is even, and for |V|=2,
|E|=0 so connected G does not exist.

We select any partition of six dangling semiedges into three
**ordered** pair positions (the 15 pairings suffice, because the
target relation is invariant under permutation of the three
bit positions). Their Boolean bit values are
`t_i=1 iff the two corresponding PHYSICAL edge-colours match`
for any proper 3-edge colouring of the cubic multipole.
The target EXACT exposed relation is
`R={100,010,001}`. Every one of the three one-hot states must
admit an actual physical extension; 000,111 and all other states
must be impossible. A finite partial search or one SAT witness
would not suffice.

## Exhaustive generation and independently replayable algorithm

Use canonical graph enumeration `nauty-geng -c -q -d1 -D3 n m`
with `m=(3n-6)/2` to produce one graph6 representative of EVERY
isomorphism class of simple connected graphs with n internal vertices,
exactly m ordinary edges, minimum degree>=1 and maximum degree<=3.
`nauty-geng` is the standard isomorph-free graph enumerator by
McKay et al.; see the Ubuntu 24.04 manpage:
https://manpages.ubuntu.com/manpages/noble/man1/nauty-geng.1.html

For EACH generated representative, the Python source:
1. Parses canonical graph6 using its documented upper-triangle column
   ordering (0,1),(0,2),(1,2),(0,3),...;
2. Rechecks n,m, all degrees, all six port deficit slots;
3. Performs exhaustive proper 3-edge-colouring DFS of ALL internal
   edges, never pruning a proper colouring;
4. For any degree-1 internal vertex, enumerates BOTH permutations
   of the two unoccupied 3-edge colours to its two distinct port
   slots (for degree-2 vertex, missing colour is uniquely determined);
5. Builds the **FULL SET OF SIX PHYSICAL PORT COLOUR TUPLES**;
6. For all 15 pairings of the six fixed port slots, projects every
   tuple to the three Boolean equal-colour predicates and compares
   EXACTLY to {100,010,001}.
7. Prints every candidate with its graph6 representation, full edge
   list, ordered ports, pairing, complete physical colour signature
   set for independent checking. No candidate was printed for n<=12.

Because each graph is represented up to vertex isomorphism, all
arbitrary choices of six-port pairing and of the two port orders at
a degree-1 vertex are explicitly tested; the enumeration does not
exclude asymmetric port labellings.

## Complete results from authoritative CI

| Internal n | Ordinary edges | Non-isomorphic interiors | Colourable | Uncolourable | Checked pairings | Exact-One |
|--:|--:|--:|--:|--:|--:|--:|
| 2 | 0 | 0 (connected impossible) | 0 | 0 | 0 | 0 |
| 4 | 3 | 2 | 2 | 0 | 30 | 0 |
| 6 | 6 | 9 | 9 | 0 | 135 | 0 |
| 8 | 9 | 63 | 63 | 0 | 945 | 0 |
| 10 | 12 | 551 | 545 | 6 | 8175 | 0 |
| 12 | 15 | 5741 | 5652 | 89 | 84780 | 0 |
| TOTAL | — | 6366 | 6271 | 95 | 94065 | **0** |

Source CI:
- `#38400666128` SUCCESS: full n=4,6,8 exact classification;
- `#38400836931` SUCCESS: n=4,6,8,10;
- `#38400976941` SUCCESS: n=4,6,8,10,12;
  exact head `f6488fa63d32c94f8e81ce515054580dcb1ecc3b`.
- Earlier independent full **labelled** n4/n6 enumeration:
  CI `#38398794905` SUCCESS: n4 16 labelled graphs/240
  pairings; n6 2700 labelled graphs/40500 pairings,
  also zero target.

This nauty 6366 total is a count of **non-isomorphic INTERNAL**
graphs, not a count of fully port-labelled multipoles. Every
needed 3-pairing on each graph is nevertheless explicitly checked,
so it is an exhaustive finite theorem for the specified class.

### Theorem (finite, source-independent)

For every finite *simple connected cubic sixpole without free isolated
edges* with at most 12 internal vertices, no partition of its six
distinct dangling semiedges into three pairs has EXACT three-bit
colour-equality projection {100,010,001}.

**Proof**: The above exhaustive isomorph-free graph generation,
per-graph degree/edge checks, complete exact colouring enumeration,
and complete boundary partition enumeration. Under the declared
nauty graph generation correctness, no unexplored graph class or
port matching remains. This is an effectively finite certified
classification, NOT a symbolic proof for arbitrary n.

Therefore **if** such an exposed Exact-One gadget exists within
this precisely defined class, it requires
`n_internal >=14`.

The observed pattern through n=12 is also compatible with a much
stronger *CONJECTURE*: any colourable ordinary cubic sixpole whose
boundary pairing realizes ALL 100,010,001 must realize at least one
of 000 or 111. This is NOT proven and MUST NOT be promoted to a
general theorem.

## Independent universal-necessary Kempe signature sanity theorem

Research file:
`experiments/r5_universal_open_sixpole_kempe_necessary_closure.py`;
CI [#38401979434](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38401979434) SUCCESS.

For a colourable proper cubic multipole M and a fixed FULL physical
six-port boundary colour state s, the two-colour subgraph for any
two labels A,B is a disjoint union of cycles and alternating paths.
The boundary semiedges coloured A or B are paired by those paths.
Any SUBSET of these disjoint paths can have A and B exchanged
independently while retaining a proper cubic 3-edge colouring.
Therefore, a necessary condition for ANY proposed boundary state
set S=Col(M) is:

For every state s in S and every pair of colours (A,B), there
exists some perfect pairing P of the A/B-coloured terminal positions
such that ALL `2^|P|` independently swapped boundary states
remain members of S.

The candidate EXACTONE projected relation has precisely **108**
FULL SIX-COLOUR boundary states consistent with the cubic colour
parity rule; its projections are exactly {100,010,001}.
A complete enumerator checked **ALL 108 * 3 = 324** such
state/colour-pair cases; every one has a matching P that satisfies
this necessary condition. It freezes explicit matching examples.

Consequently **PARITY plus EXISTENTIAL boundary Kempe-pair closure
alone CANNOT disprove the target abstract relation**. This is NOT
a graph-realization theorem: actual one fixed interior topology
must realize the path pairings consistently for all colour states.
The missing GLOBAL path-consistency theorem remains OPEN.

Literature context: Fiol--Vilaltella (2015), *Some Results on the
Structure of Multipoles in the Study of Snarks*,
https://www.combinatorics.org/ojs/index.php/eljc/article/view/v22i1p45
formalizes colour-state sets, cubic parity and Kempe state constraints.
The no-go via these necessary conditions alone is excluded by the
above constructive finite abstract relation, but other stronger
universal structural identities may still rule out ExactOne.

## Essential exclusions / non-overclaims

- Does NOT rule out n>=14 gadgets.
- Does NOT cover multigraphs, disconnected multipoles, isolated
  free semiedge-to-semiedge strands, >6 ports, higher-arity grouped
  ports, signed/twisted local colour systems or alternative semantic
  Boolean encodings.
- Open multipoles are not themselves legal closed SCL sources. A
  future gadget must be composed into a cubic CLOSED simple graph
  and verified as an original square/cubic/linear Positive Exact-One
  source, including original edge and vertex-colour one-hot clauses.
- A truth-table-compatible construction is NOT YET sufficient
  for Polynomial Calculus transfer. Must provide local polynomial
  substitutions and bounded-degree ORIGINAL source generator
  identities, including Boolean axioms, with constants k,C
  independent of hard base graph size.
- The existing original SCL90 J5 GF3 dual proves degree>=4,
  but this census does not imply unbounded SCL degree.
- `SolveLinearCubicXSAT` remains NOT CONSTRUCTED; P vs NP OPEN.

## Scientifically admissible next test

Either (1) derive a genuine universal Kempe/flow invariant that
refutes the six-port equality-code Exact-One interface for EVERY
size, OR (2) build a graph with >=14 vertices realizing the
exact full **physical colour boundary** relation and independently
test closed-source compatibility, SAT equivalence, and constant-degree
Polynomial Calculus back-simulation. A mere further finite
negative result, by itself, cannot settle all-n existence.

GATES:
- EXACT_6POLE_N_LE_12_NO_ONEHOT = PROVED_FINITE_CI_SUCCESS
- MINIMUM_INTERNAL_N_IF_EXISTS = AT_LEAST_14
- ALL_N_ONEHOT_IMPOSSIBLE = CONJECTURE_ONLY
- EXPOSED_SIXPOLE_EXACTONE = NOT_CONSTRUCTED
- GENERAL_PC_BACK_SIMULATION = NOT_CONSTRUCTED
- UNBOUNDED_ORIGINAL_SCL_PC_DEGREE = OPEN
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN
