# C032 — JANUS PS-width Alignment

**Status:** `CONSTRUCTIVE ALIGNMENT / SOFTWARE-ONLY / NOT CANONICAL`

```text
P_VS_NP=OPEN
```

## Why this cycle exists

The constructive chain from C023 through C029 repeatedly located the same
resource under different views:

```text
C023  instance-specific tractable regions
C024  nonlinear quotient core survives coarse fracture topology
C025  continuation-distinct residual states and merge certificates
C027  tractable projection discovery
C028  semantic support overlap across conjunctive regions
C029  definitional occurrence splitting cannot lower incidence treewidth
```

The next proposed object was a proof-carrying semantic quotient across a cut.
C032 compares that object with the primary literature before introducing a new
parameter.

## Exact identification

For a cut

```text
S = C union X
```

of a CNF formula `F`, let the JANUS left signature of an assignment to `X` be
the exact set of clauses outside `C` already satisfied by literals whose
variables lie in `X`.

The collection of all such signatures is exactly

```text
PS(F_(cla(F)\C, X)),
```

the family of precisely satisfiable clause sets used in the definition of
PS-width by Sæther, Telle and Vatshelle.

The symmetric right signature is exactly

```text
PS(F_(C, var(F)\X)).
```

Therefore:

```text
JANUS semantic cut signature count
=
the PS-value of the corresponding cut.
```

This is not a heuristic analogy. It is equality of the two definitions.

## Existing algorithmic bridge

Sæther, Telle and Vatshelle prove that, given a CNF formula of size `s` with
`n` variables and `m` clauses and a branch decomposition of PS-width `k`,
`#SAT` and weighted `MaxSAT` can be solved in

```text
O(k^3 * s * (m+n)).
```

Thus a deterministic polynomial-time procedure that, for every CNF, constructs
a decomposition of polynomial PS-width would already give a polynomial-time
algorithm for `#SAT`, and hence for SAT.

Primary source:

- Sigve Hortemo Sæther, Jan Arne Telle, Martin Vatshelle,
  *Solving MaxSAT and #SAT on structured CNF formulas*,
  arXiv:1402.6485.

## Structural/semantic gap theorem

Let `F_(n,m)` contain `m` copies of the same clause

```text
x1 OR x2 OR ... OR xn.
```

Then:

```text
inc(F_(n,m)) = K_(n,m)
tw(inc(F_(n,m))) = min(n,m)
```

and, when `m >= 2`, the C028 global overlap-defect set contains all `n`
variables.

Nevertheless every cut has PS-value at most `2`.

### Proof

Every cut-induced subformula consists only of copies of one identical projected
clause.

- If the projected clause is empty, every copy is unsatisfied and there is one
  signature.
- If it is nonempty, an assignment either satisfies every copy or satisfies no
  copy, giving at most two signatures.

Hence every branch decomposition has:

```text
PS-width <= 2.
```

So unbounded incidence treewidth and unbounded raw support overlap can coexist
with constant semantic cut width.

This proves that C029's graph-minor barrier does not block genuine semantic
compression. It blocks only definitional expansion masquerading as compression.

## Machine-checkable audit

The executable uses two independent implementations:

1. projected-subformula precisely-satisfiable sets;
2. direct JANUS boundary-satisfaction signatures.

Frozen audit:

```text
random cut identity cases:       800
signatures compared:             12055
duplicate-family cuts checked:   3844
maximum duplicate-family value:  2
largest explicit cut signatures: 65536
integrity:                       bf7866648a570d87b2a6e4d9480b6754467358ca1316454984579ccb5df75964
```

The explicit unit-clause cut realizes `2^n` signatures. This is a cut-level
explosion control, not a claim that the formula's optimal PS-width is
exponential.

Reproduce:

```bash
python experiments/direct/janus_c032_ps_width_alignment.py --self-test
```

## Important limitation: PS-width is not a complete tractability classifier

Brault-Baron, Capelli and Mengel give a polynomial-time elimination algorithm
for `#SAT` on beta-acyclic CNFs and show that such formulas may have PS-width so
large that the PS-width dynamic-programming framework does not even yield
subexponential bounds.

Primary source:

- Johann Brault-Baron, Florent Capelli, Stefan Mengel,
  *Understanding model counting for beta-acyclic CNF-formulas*,
  arXiv:1405.6043.

Therefore JANUS must not replace one coarse width parameter by PS-width and call
the search complete.

## Located bottleneck

# POLYNOMIAL_PS_DECOMPOSITION_OR_SYMBOLIC_SIGNATURE_COMPRESSION

Two constructive routes remain.

### Route A — universal polynomial PS decomposition

Construct, in polynomial time for every CNF, a branch decomposition whose
PS-width is polynomial in the input length.

This route is already strong enough to imply `P=NP` through the published
algorithmic bridge.

### Route B — symbolic signatures beyond explicit PS enumeration

Represent an exponentially large family of cut signatures by a polynomial-size
proof-carrying object supporting:

```text
construction
composition
elimination
SAT decision
witness recovery
independently checkable UNSAT handling
```

The representation portfolio must include elimination-style mechanisms that can
cover beta-acyclic formulas with large PS-width, not only branch-decomposition
dynamic programming.

## Next attack plan

C033 should compare exact semantic signatures and symbolic representations on:

```text
duplicate-clause K_(n,m)        constant PS-width / high treewidth
Horn and dual-Horn modules      closure compression
XOR and parity modules          GF(2) compression
beta-acyclic formulas           elimination beyond PS-width
Tseitin and expander CNFs       adversarial global interaction
deterministic 3-CNF embedding   arbitrary SAT preservation
```

For every representation, charge selection, construction, message volume,
composition, verification, certificate discovery and witness recovery.

## Claim boundary

C032 does not prove that every CNF has polynomial PS-width, does not produce a
universal symbolic signature language, and does not resolve P versus NP.

It prevents JANUS from reinventing a known width parameter and redirects the
constructive route toward the exact missing theorem.
