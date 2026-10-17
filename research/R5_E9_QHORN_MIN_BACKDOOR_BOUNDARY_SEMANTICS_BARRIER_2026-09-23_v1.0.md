# R5 E9 — q-Horn Minimum-Backdoor Boundary Semantics Barrier

**Date:** 2026-09-23  
**Status:** exact derived reduction / negative control.  
**Scientific firewall:** this is not a SAT lower bound. It shows only that q-Horn backdoor minimality by itself imposes no useful restriction on the exact boundary extendability relation.

## 1. Statement

Let (G) be any 3CNF on variables

[
B={b_1,ldots,b_k}.
]

For (t=k+1), introduce fresh private variables
[
u_{i,j},v_{i,j}
qquad
(1le ile k, 1le jle t)
]
and define

[
F_G
=
G
wedge
igwedge_{i=1}^kigwedge_{j=1}^{t}
left[
(b_iee u_{i,j}ee v_{i,j})
wedge
(
eg b_iee
eg u_{i,j}ee
eg v_{i,j})
ight].
]

Then:

1. (F_G) is a 3CNF of size polynomial in (|G|+k).
2. (B) is a deletion q-Horn backdoor of (F_G).
3. (B) is the **unique deletion q-Horn backdoor of size at most (k)**, hence the unique minimum deletion q-Horn backdoor.
4. For every truth assignment (alpha:B	o{0,1}),

[
F_G[alpha]inmathrm{SAT}
iff
alphamodels G.
]

Therefore the exact boundary extendability relation

[
R_B(F_G)
=
{alphain{0,1}^{B}:F_G[alpha]	ext{ is satisfiable}}
]

is exactly

[
R_B(F_G)=operatorname{Mod}(G).
]

Since (G) is arbitrary 3CNF, the boundary semantics on a unique minimum q-Horn deletion backdoor can be an arbitrary 3SAT model relation.

## 2. Central q-Horn obstruction gadget

For variables (b,u,v), define

[
Q(b,u,v)
=
(bee uee v)
wedge
(
eg bee
eg uee
eg v).
]

This formula is not q-Horn.

Indeed, for a q-Horn certificate (eta), the positive clause requires

[
eta(b)+eta(u)+eta(v)le1,
]

while the all-negative clause requires

[
(1-eta(b))+(1-eta(u))+(1-eta(v))le1,
]

equivalently

[
eta(b)+eta(u)+eta(v)ge2,
]

a contradiction.

Deleting **any one** of (b,u,v) leaves two clauses of length at most two, hence a Krom formula and therefore q-Horn.

## 3. Why B is the unique minimum deletion backdoor

Fix (i).

There are (t=k+1) pairwise private copies (Q(b_i,u_{i,j},v_{i,j})).

Suppose a deletion q-Horn backdoor (S) does **not** contain (b_i).

Because q-Horn is clause-induced, no intact non-q-Horn subformula (Q(b_i,u_{i,j},v_{i,j})) may remain. Hence (S) must contain at least one of (u_{i,j},v_{i,j}) for every (j).

Therefore

[
|S|ge t=k+1.
]

Thus every deletion q-Horn backdoor of size at most (k) must contain every (b_i). Consequently any such backdoor equals (B).

On the other hand, deleting all variables in (B):

- turns every private obstruction into
  [
  (u_{i,j}ee v_{i,j})
  wedge
  (
eg u_{i,j}ee
eg v_{i,j}),
  ]
  which is Krom;
- turns every original clause of (G) into the empty clause, which is also syntactically Horn/Krom/q-Horn.

Hence (F_G-B) is q-Horn, so (B) is indeed the unique minimum deletion q-Horn backdoor.

## 4. Exact boundary semantics

Fix an assignment (alpha) to (B).

For a private gadget:

- if (alpha(b_i)=0), the negative clause is satisfied and the positive clause reduces to
  [
  u_{i,j}ee v_{i,j};
  ]
- if (alpha(b_i)=1), the positive clause is satisfied and the negative clause reduces to
  [
  
eg u_{i,j}ee
eg v_{i,j}.
  ]

Either residual clause is independently satisfiable.

Thus all private gadgets can always be extended, regardless of (alpha).

The only way (F_G[alpha]) is unsatisfiable is that some original clause of (G) is falsified by (alpha), producing an empty clause.

Therefore

[
F_G[alpha]inmathrm{SAT}
iff
alphamodels G.
]

## 5. Consequence for the universal route

This kills the following hoped-for intermediate claim:

> “Once a minimum q-Horn deletion backdoor is known, its assignment boundary has some generic q-Horn-derived polynomial semantic structure.”

False.

Even for a **unique minimum** backdoor, its exact extendability relation can be an arbitrary 3SAT relation.

Hence a procedure which, for every such ((F,B)), compiled the complete boundary semantics into a polynomial-size representation with polynomial-time emptiness and witness extraction would already solve arbitrary 3SAT through the reduction above.

That does **not** prove such a compiler cannot exist; constructing one would essentially be the desired P=NP breakthrough. It does prove that q-Horn backdoor structure alone is not a weaker intermediate theorem from which universal polynomial SAT follows for free.

## 6. Cut/separator currency is also insufficient as a generic summary

Two source controls reinforce the pivot:

- exact mimicking networks preserving all terminal cuts can require (2^{Omega(k)}) size;
- all-subsets important separators have bounds with a (4^k) factor and matching combinatorial dependence on terminal subsets.

These are graph-summary lower bounds only, not SAT lower bounds. They justify abandoning “store all separator choices exactly in one ordinary cut structure” as the primary universal currency.

## 7. Frontier correction

The previous gate

`R5_E9_HORN_DUALHORN_QHORN_OBSTRUCTION_COMPRESSION_GATE_V1`

is retained as a mechanism study but **demoted from universal intermediate target**.

The active universal requirement becomes:

`R5_E9_STRUCTURED_INTERFACE_DECOMPOSITION_GATE_V1`

Seek a polynomially constructible decomposition in which every live boundary relation is guaranteed **by construction** to remain in a source-backed tractable representation family, rather than taking an arbitrary backdoor boundary and hoping its semantics compresses.

Any claimed PASS must prove:
- every boundary relation has a certified tractable/native representation;
- every join/project update preserves a certified representation in polynomial total size;
- no arbitrary boundary can encode an unconstrained 3SAT model relation as above;
- no exponential branching, cut enumeration, or semantic oracle is hidden.

D1 = EMPTY.  
P_VS_NP = OPEN.
