# R5 E68 — Open-Literature Hierarchy Anti-Loop Addendum

Date: 2026-10-04

Scientific ceiling:

```text
P_VS_NP = OPEN.

THIS ADDENDUM RECORDS EXTERNAL HIERARCHY LOWER-BOUND CONTEXT SO THAT THE
FUNDAMENTUM SEARCH DOES NOT REINVENT GENERIC LP/SDP/SOS CLAIMS OR MISTAKE A
LOW-LEVEL SUCCESS ON ONE INCIDENCE FAMILY FOR A UNIVERSAL THEOREM.
```

## 1. Complete Delsarte-type hierarchies do not imply low exact level

Coregliano, Jeronimo and Jones give a complete LP hierarchy for linear codes,
with the true optimum recoverable at level `O(n^2)` in the general theorem.
This proves completeness, but does not provide the constant-level or compressed
log-level exactness required by the JANUS universal polynomial target.

Reference:

* Leonardo Nagami Coregliano, Fernando Granha Jeronimo, Chris Jones,
  "A Complete Linear Programming Hierarchy for Linear Codes",
  ITCS 2022, DOI `10.4230/LIPIcs.ITCS.2022.51`.

## 2. Fixed-stage coding SDPs are polynomial, but stage growth matters

Laurent gives a hierarchy of semidefinite bounds for binary codes.  At every
fixed stage the bound is polynomial-time computable in `n`, but the size grows
strongly with the stage.  The paper places Schrijver's Terwilliger-algebra SDP
between the first and second levels and notes that the second full level has
`O(n^7)` variables, while Schrijver's symmetry-reduced SDP has size `O(n^3)`.

References:

* Alexander Schrijver, "New Code Upper Bounds from the Terwilliger Algebra and
  Semidefinite Programming", IEEE Trans. Inf. Theory 51 (2005),
  DOI `10.1109/TIT.2005.851748`.
* Monique Laurent, "Strengthened semidefinite programming bounds for codes",
  Mathematical Programming 109 (2007), DOI `10.1007/s10107-006-0030-3`.
* Pin-Chieh Tseng, Ching-Yi Lai, Wei-Hsuan Yu,
  "Semidefinite programming bounds for binary codes from a split Terwilliger
  algebra", Designs, Codes and Cryptography (2023), arXiv `2203.06568`.

## 3. Generic hypergraph-matching LP hierarchies can remain weak for many rounds

Chan and Lau show that for general `k`-uniform hypergraph matching, an
integrality gap can survive a linear number of Sherali-Adams rounds.

Reference:

* Yuk Hei Chan, Lap Chi Lau,
  "On linear and semidefinite programming relaxations for hypergraph matching",
  Mathematical Programming 135 (2012), DOI `10.1007/s10107-011-0451-5`.

This is **not** claimed to apply directly to the JANUS square-cubic-linear
3-regular subfamily.  It is an anti-loop warning against assuming that generic
local LP constraints collapse at `O(log n)` level.

## 4. Generic CSP Lasserre/SoS can require linear level

Schoenebeck proved linear-level Lasserre lower bounds for random `k`-CSPs for
`k >= 3`, including `k`-XOR and predicates implied by XOR such as `k`-SAT.
Tulsiani then developed CSP integrality gaps and reductions in the Lasserre
hierarchy, obtaining `Omega(n)`-round gaps for broad binary `k`-CSP families.

References:

* Grant Schoenebeck,
  "Linear Level Lasserre Lower Bounds for Certain k-CSPs",
  FOCS 2008, DOI `10.1109/FOCS.2008.74`.
* Madhur Tulsiani,
  "CSP Gaps and Reductions in the Lasserre Hierarchy",
  STOC 2009, DOI `10.1145/1536414.1536457`.

These results are again **not** a lower bound for positive Exact-One on our
square-cubic-linear carrier.  No such transfer is asserted here.  Their role is
to freeze the generic shortcut

```text
"a standard SoS/Lasserre hierarchy should become exact after a few or
logarithmically many rounds on any bounded-arity CSP"
```

as unjustified.

## 5. Consequence for the JANUS search

For the universal P=NP target, a hierarchy route must contain genuinely new
structure specific to our carrier.  At minimum it must establish one of:

```text
* a universal constant exact level;
* a compressed polynomial-time evaluation of a provably exact growing level;
* a special block diagonalization / recursion caused by square cubic linearity;
* a different proof system whose certificate size and verification time are
  polynomial on the entire hard family.
```

A result that only gives `t=O(log n)` inside an `n^{O(t)}` implementation is
quasi-polynomial and is not sufficient for P=NP.
