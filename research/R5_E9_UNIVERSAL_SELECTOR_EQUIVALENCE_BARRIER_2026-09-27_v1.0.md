# R5 E9 — Universal SAT Selector Equivalence Barrier and Oracle-Free Attack Frontier

Date: 2026-09-27

Status:
`BARRIER_THEOREM_CANDIDATE__ATTACK_FRONTIER__NOT_E8_D1_CANDIDATE`

Binds:
- `R5_B1B1C5B2B2_E8_DIRECT_ALGORITHM_CONTRACT_PREREG_2026-09-21_v1.0`
- `experiments/r5_e9_universal_selector_frontier.py`

Global boundary:
`P_VS_NP = OPEN`

## 1. Why this note exists

The next desired object was a "universal selector": a polynomial-time rule that
chooses a next SAT branch or reduction while guaranteeing that satisfiability
is not lost.

There is a critical firewall: a fully general selector of the relevant strength
is not merely a preprocessing lemma. It is already equivalent to a
polynomial-time SAT decision algorithm.

Therefore JANUS must not write

```
there exists a good child
```

and silently replace it by

```
we can compute a good child in polynomial time.
```

That replacement is exactly the missing algorithmic content.

The existing E8 contract already forbids SAT/UNSAT oracles, free semantic
merging, unbudgeted certificate discovery, and similar shortcuts. This note
makes the selector form of the same barrier explicit.

## 2. Total safe branch selector

Let F be a CNF formula and x an unassigned variable of F.

A total safe branch selector is an algorithm

```
B(F,x) in {0,1}
```

such that for every satisfiable F,

```
F is SAT
=>
F[x := B(F,x)] is SAT.
```

No promise is required on the returned bit when F is unsatisfiable, but B must
still halt on every input.

### Theorem A

The following are equivalent:

1. SAT is decidable in deterministic polynomial time.
2. There exists a deterministic polynomial-time total safe branch selector B.

### Proof: 2 => 1

Given F with variables x1,...,xn, compute successively

```
b1 = B(F,x1)
F1 = F[x1:=b1]

b2 = B(F1,x2)
F2 = F1[x2:=b2]

...

bn = B(F_{n-1},xn).
```

If the original F is satisfiable, the selector invariant guarantees every
residual Fi is satisfiable. The final complete assignment therefore satisfies
F.

If the original F is unsatisfiable, no complete assignment satisfies F.

Evaluate the final assignment directly on the original formula. Accept iff it
satisfies F.

There are at most n selector calls and polynomial-time simplifications, so the
entire decision procedure is polynomial.

### Proof: 1 => 2

Assume a polynomial SAT decider D.

On input (F,x), run D on F[x:=0].

If that branch is satisfiable, return 0. Otherwise return 1.

When F is satisfiable, at least one branch is satisfiable, so the returned bit
is safe. When F is unsatisfiable the selector may return either bit.

Thus a polynomial SAT decider gives a polynomial safe selector.

Therefore

```
POLYTIME_UNIVERSAL_SAFE_BRANCH_SELECTOR
iff
SAT in P.
```

Since SAT is NP-complete,

```
such a selector
=>
P=NP.
```

This theorem does not establish either side unconditionally.

## 3. General bounded-progress selector

Branching is not essential to the barrier.

Suppose there are polynomial-time computable objects

```
Sel(F)
mu(F)
Terminal(F)
```

with the following properties.

1. Exact satisfiability preservation:

```
SAT(F) iff SAT(Sel(F)).
```

2. Whenever F is nonterminal,

```
mu(Sel(F)) <= mu(F)-1.
```

3. The initial potential and every intermediate representation satisfy a
polynomial bound in the original input length L:

```
0 <= mu(F) <= poly(L),
|F_i| <= poly(L).
```

4. Terminal instances are recognized and decided in polynomial time.
5. Selector construction, potential updates, terminal tests, and witness
reconstruction are all charged polynomial work.

### Theorem B

Such a universal bounded-progress selector implies SAT in P.

### Proof

Iterate Sel until Terminal becomes true. The integer potential decreases at
least once per nonterminal step and begins polynomially bounded, so there are
only polynomially many iterations. Every iteration and every intermediate
encoding has polynomial cost/size. Terminal SAT is polynomial-time decidable.
Exact satisfiability preservation carries the answer back to the original
formula.

The E8 contract then supplies standard search-from-decision if a satisfying
assignment must be reconstructed.

### Converse

If SAT is in P, define Sel(F) to return a fixed encoded TRUE terminal when F is
satisfiable and a fixed encoded FALSE terminal otherwise. Hence the
unrestricted bounded-progress schema is also equivalent, in this broad sense,
to polynomial SAT decision.

Therefore

```
UNIVERSAL_PROGRESS_LEMMA
```

cannot be treated as a small theorem downstream of the real algorithm. Under
the stated contracts it contains the real algorithm.

## 4. Existential progress is not computable progress

The following statement is insufficient:

```
For every satisfiable F there exists a child c in Children(F)
such that c is satisfiable and mu(c)<mu(F).
```

Ordinary SAT branching already has this property: for every satisfiable F and
every variable x, at least one of F[x:=0], F[x:=1] is satisfiable.

The missing object is a polynomial procedure that identifies a safe child
without first solving SAT.

Hence all future selector claims must separately bind:

```
EXISTENCE
CONSTRUCTION
SOUNDNESS
COMPLETENESS
TOTAL_RUNTIME
```

An existential good branch is not a D1 candidate.

## 5. First oracle-free selector primitive: failed-literal unit propagation

A legitimate partial selector is:

```
try x=0 and run unit propagation;
if contradiction, choose x=1;

try x=1 and run unit propagation;
if contradiction, choose x=0;

otherwise return UNKNOWN.
```

This is polynomial and safe whenever it returns a bit.

However it is not universal.

The executable frontier checker uses

```
F =
(x v a v b)
&
(x v a v -b)
&
(x v -a v b)
&
(x v -a v -b).
```

For x=0 the residual is

```
(a v b)
(a v -b)
(-a v b)
(-a v -b),
```

which is unsatisfiable but has no unit clause, so ordinary unit propagation
does not refute it.

For x=1 the formula is satisfiable.

Therefore x is forced to 1, yet the failed-literal-UP selector returns

```
UNKNOWN.
```

The brute-force routine in the checker is explicitly marked

```
OFFLINE_FALSIFIER_ONLY
```

and is forbidden from the E8 algorithm.

This fixture rejects only the attempted `FAILED_LITERAL_UP` universalization.
It is not a SAT lower bound.

## 6. Literature anti-loop

Known preprocessing and structural shortcuts fit naturally as partial
selectors/reductions, not as universal deciders.

### Blocked clause elimination

Blocked-clause elimination is satisfiability preserving and polynomially
applicable. It can remove clauses safely but reaches a fixpoint; the known
theory does not say that every arbitrary CNF becomes polynomially decidable at
that fixpoint.

Reference:
M. Jarvisalo, A. Biere, M. Heule, "Blocked Clause Elimination", TACAS 2010.

### Autarkies and lean kernels

Autarkies give satisfiability-preserving clause deletion. Important subclasses
such as linear/matching autarkies have polynomial algorithms and lead to lean
kernels. General autarky existence is not a free universal selector.

Reference:
O. Kullmann, "Lean clause-sets: generalizations of minimally unsatisfiable
clause-sets", Discrete Applied Mathematics 130 (2003), 209-249.

A recent line of work studies stronger conditional autarkies and redundancy
reasoning, but this does not supply a general polynomial SAT decider.

Reference:
I. Bonacina, M. L. Bonet, A. Kolokolova, M. Lauria,
"Conditional Autarkies: Hard Formulas Made Easy", SAT 2026,
DOI 10.4230/LIPIcs.SAT.2026.8.

### Backdoors

If a small strong backdoor to a tractable class is known, enumerating its
assignments reduces SAT to tractable residuals. The cost is exponential in
backdoor size; finding suitable backdoors has its own complexity landscape.

Reference:
S. Gaspers, N. Misra, S. Ordyniak, S. Szeider, S. Zivny,
"Backdoors into Heterogeneous Classes of SAT and CSP", AAAI 2014 / JCSS 2017.

Thus a claimed universal backdoor route must prove both:
- polynomial-time discovery, and
- a universal O(log n) or otherwise polynomial total evaluation bound.

Neither may be assumed.

### Unique solutions are not an escape hatch

A selector that works only because a formula has a unique satisfying
assignment still has to recover the forced branch bits.

Valiant-Vazirani show that zero/one-solution SAT remains tightly connected to
general SAT under randomized reductions. This is not a deterministic P=NP
theorem, but it is a strong warning against treating uniqueness as an easy
case.

Reference:
L. G. Valiant, V. V. Vazirani,
"NP is as easy as detecting unique solutions",
Theoretical Computer Science 47 (1986), 85-93.

## 7. Oracle-free partial-selector library to attack next

The productive target is not to rename the whole P-vs-NP problem as
`UniversalSelector`.

Build a partial selector/reducer whose every successful move carries a
polynomially checkable reason.

Candidate primitive families:

1. `UNIT_OR_FAILED_LITERAL`
   - unit propagation;
   - failed-literal contradiction certificates.

2. `BLOCKED_OR_BOUNDED_ELIMINATION`
   - blocked clause elimination;
   - variable elimination only when representation growth is polynomially
     charged.

3. `AUTARKY`
   - matching/linear autarkies and other polynomially constructible autarky
     subclasses.

4. `TRACTABLE_RESIDUAL`
   - Horn / dual-Horn / 2-CNF and other explicitly recognized polynomial
     classes;
   - bounded structural parameters only when discovery and decomposition are
     polynomially charged.

5. `CERTIFIED_BRANCH_EQUIVALENCE`
   - choose either side only when a polynomially verified transformation maps
     the two branch residuals in a satisfiability-preserving way.

6. `SHORT_UNSAT_CERTIFICATE_FOR_ONE_BRANCH`
   - choose the other branch when an explicitly constructed polynomial-size
     certificate refutes one side;
   - certificate discovery cost is charged, not merely verification.

Every primitive may return

```
UNKNOWN
```

without compromising soundness.

The scientific question becomes:

```
What infinite cores remain UNKNOWN after the union of all certified primitives?
```

That is a falsifiable frontier.

## 8. Required promotion condition

A partial selector library becomes a genuine E8-D1 route only after a theorem
proves a polynomial total bound covering every valid 3-CNF:

```
for every F:
    either a certified safe move is constructed in polynomial time,
    or F is recognized as belonging to a polynomial terminal class;
and the total number/size of all moves is polynomial in the original input.
```

If this coverage theorem is proved, then by Theorem B SAT is in P and hence
P=NP.

Until then:

```
E8_D1
=
EMPTY

UNIVERSAL_SELECTOR
=
OPEN

P_VS_NP
=
OPEN
```

## 9. Next concrete attack

The next noncircular experiment is:

```
SELECTOR-COVERAGE-001
```

Input families:
- the explicit JANUS high-nullity / phase-FAIL family and its covers,
- formulas surviving the existing filtered root-preprocessor once that
  bootstrap is materially available,
- standard lean/autarky-resistant controls,
- known hard SAT benchmark families.

For each instance record:

```
which certified primitive fires,
whether it gives a branch or SAT-equivalent reduction,
potential decrease,
construction cost,
certificate size,
remaining UNKNOWN core.
```

A primitive that stalls is not evidence for P!=NP.
A primitive that works on all finite tests is not evidence for P=NP.

Only an arbitrary-input coverage proof can cross the E8-D1 gate.
