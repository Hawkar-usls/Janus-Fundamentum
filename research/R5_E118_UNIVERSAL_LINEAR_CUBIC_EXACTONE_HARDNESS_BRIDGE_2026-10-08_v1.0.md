# R5 E118 — Universal Linear-Cubic ExactOne Hardness Bridge

Date: 2026-10-08

Status:
`POSITIVE_SQUARE_CUBIC_C4FREE_EXACTONE_IS_NP_COMPLETE_VIA_EQUAL3_PORT_SPLITTING`

Scientific ceiling:

```text
E118 CLOSES THE UNIVERSALITY / HARDNESS BRIDGE ONLY.

IT DOES NOT CONSTRUCT A POLYNOMIAL SOLVER.
IT DOES NOT PROVE P=NP.

AFTER E118, A POLYNOMIAL ALGORITHM FOR ALL POSITIVE SQUARE CUBIC C4-FREE
EXACTONE INSTANCES WOULD BE SUFFICIENT TO IMPLY P=NP.
```

## 1. Target class

The target formulas are positive ExactOne formulas satisfying all four structural
conditions used throughout R5:

```text
every clause has exactly 3 distinct variables;
every variable occurs in exactly 3 clauses;
two distinct clauses share at most one variable;
therefore the variable-clause incidence graph is C4-free.
```

Because total literal incidences are both (3|V|) and (3|C|),

[
|V|=|C|.
]

So the target is the square+cubic+C4-free positive ExactOne class.

## 2. NP-hard source

Moore and Robson prove NP-completeness of Cubic Planar Monotone (positive)
1-in-3 SAT: every clause has three positive variables and every variable occurs
exactly three times.  See:

Cristopher Moore and John Michael Robson,
"Hard Tiling Problems with Simple Tiles",
Discrete & Computational Geometry 26 (2001), 573-590;
arXiv:math/0003039.

Their source formula need not be linear for the present reduction.  We remove all
shared-variable clause intersections by occurrence splitting.

## 3. The EQUAL3 gadget

Ports are (x,y,z).  Internal variables are (a,b,c,d,e,f,g).

Add the nine ExactOne clauses

[
egin{array}{lll}
(d,f,g), & (z,c,e), & (y,e,f),\
(x,b,f), & (z,a,b), & (a,e,g),\
(x,a,d), & (y,c,d), & (b,c,g).
end{array}
]

Each clause means that the ordinary integer sum of its three Boolean variables is
exactly one.

The nine linear equations have the complete rational solution family

[
oxed{
x=y=z=g,qquad
a=c=f=t,qquad
b=d=e=1-t-z.
}
]

Hence every Boolean solution satisfies

[
oxed{x=y=z}.
]

Conversely both port values extend:

```text
x=y=z=1:
  t=0,  a=c=f=0, b=d=e=0, g=1.

x=y=z=0:
  t=0 gives a=c=f=0, b=d=e=1, g=0;
  t=1 gives a=c=f=1, b=d=e=0, g=0.
```

Therefore the gadget realizes the exact ternary equality relation on its ports.

## 4. Degree and linearity of the gadget

Inside the gadget:

```text
deg(x)=deg(y)=deg(z)=2;
deg(a)=deg(b)=deg(c)=deg(d)=deg(e)=deg(f)=deg(g)=3.
```

Every gadget clause has size three, and every pair of distinct gadget clauses
intersects in at most one variable.

Thus each port has exactly one free occurrence slot.

## 5. Polynomial reduction

Let the source formula have (n) variables.  Since it is cubic and every source
clause has size three, it also has (n) clauses.

For every source variable (v), create three fresh occurrence variables

[
v_1,v_2,v_3,
]

one for each source occurrence.  Replace the three occurrences of (v) by
these three distinct ports.  Then attach one fresh EQUAL3 gadget whose ports are
(v_1,v_2,v_3).

Properties of the transformed formula:

1. **Positive.**  No negated literal is introduced.
2. **3-uniform.**  Every source clause and every gadget clause has size three.
3. **3-regular.**  Every occurrence port appears once in a source clause and
   twice in its EQUAL3 gadget; every internal gadget variable has degree three.
4. **Linear / C4-free.**
   * distinct transformed source clauses share no variable at all, because every
     occurrence got its own port;
   * distinct gadgets are variable-disjoint;
   * a source clause and a gadget clause can meet only in one port;
   * two clauses in one gadget meet in at most one variable.
5. **Square.**  There are (3n+7n=10n) variables and (n+9n=10n) clauses.

Correctness is exact:

* from any satisfying source assignment, assign all three ports of (v) the
  source value and choose a Boolean gadget extension above;
* from any satisfying transformed assignment, every EQUAL3 gadget forces the
  three ports of each source variable equal, so contracting the ports gives a
  satisfying source assignment.

Therefore the reduction is polynomial and preserves satisfiability.

## 6. Complexity consequence

Membership in NP is immediate.  The reduction above gives

[
oxed{
	ext{Positive Square Cubic C4-Free ExactOne is NP-complete.}
}
]

This is the exact universality bridge required by the JANUS program:

[
oxed{
	ext{SolveLinearCubicXSAT in polynomial time on all inputs}
Longrightarrow P=NP.
}
]

No additional SAT gadget reduction would be needed after such a solver theorem.

## 7. Why this changes the R5 frontier

E105-E117 remain potentially useful only as internal lemmas of a complete solver.
They are not themselves a universality proof.

The next accepted progress gate is therefore not another isolated obstruction
classification.  It is a theorem that plugs into a total algorithm

```text
SolveLinearCubicXSAT(F):
    return SAT + assignment
    or UNSAT
```

for every positive square cubic C4-free input, with:

```text
soundness;
completeness;
polynomially constructible decomposition/terminal choice;
no hidden exponential branching;
an explicit n^O(1) runtime bound.
```

Any future E119+ lemma must state exactly where it enters that total algorithm.

## 8. Checker

The companion checker exhausts all (2^{10}=1024) Boolean assignments of the
gadget and verifies:

```text
exactly 3 satisfying assignments;
port projections are only 000 and 111;
000 has exactly 2 internal extensions;
111 has exactly 1 internal extension;
all three ports have internal degree 2;
all seven internal variables have degree 3;
every pair of gadget clauses intersects in at most one variable.
```

It also constructs a small occurrence-splitting reduction and checks the global
3-uniform / 3-regular / linear / square invariants.

Scientific status:

```text
E118 = UNIVERSAL NP-HARDNESS BRIDGE FOR THE EXACT R5 TARGET CLASS.
UNIVERSAL POLYNOMIAL SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
```
