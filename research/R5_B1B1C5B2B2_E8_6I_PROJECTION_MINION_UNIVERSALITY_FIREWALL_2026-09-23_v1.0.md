# R5 E8 6I — Projection-Minion Universality Firewall

Date: 2026-09-23

Authority: `PROVED_META_FIREWALL_FOR_DIRECT_MINION_RELAXATIONS__NO_D1_PROMOTION`

## 1. Source order

For every finite relational template T, every coordinate projection preserves every
relation of T. Hence there is a canonical minion homomorphism

```text
Proj -> Pol(T).
```

For the full signed Boolean 3SAT template:

```text
Pol(Gamma_3SAT) = Proj.
```

Therefore `Proj` is the strongest direct target in the minion-homomorphism order
relevant to finite CSP solvability.

## 2. Universality transfer

Let R be any algorithmic relaxation characterized by

```text
R solves CSP(T)
iff
R -> Pol(T).
```

If R directly solves full signed 3SAT, then

```text
R -> Proj.
```

For every finite template T,

```text
R -> Proj -> Pol(T).
```

Therefore R would solve every finite-template CSP.

Contrapositive:

```text
ONE FINITE TEMPLATE
FOOLED BY R

=>

R -/-> Proj

=>

R CANNOT DIRECTLY SOLVE
FULL SIGNED 3SAT.
```

No P!=NP assumption is involved.

## 3. Consequence for JANUS search discipline

Once a direct minion-based relaxation R has one source-exact finite-template
counterexample, testing increasingly complicated signed-3SAT instances against R
is an anti-loop.

The only admissible reuse of R is after a genuine polynomial representation
change that maps the SAT instance into a different template / promise structure.

## 4. Instantiated direct barriers

Already source-bound:

```text
fixed-k Z_p / affine hierarchy
=
BLOCKED DIRECTLY
by Lichter-Pago finite-template counterexample

CLAP
=
BLOCKED DIRECTLY
by Lichter-Pago finite-template counterexample

fixed-k cohomological consistency
=
BLOCKED DIRECTLY
by Lichter-Pago finite-template counterexample
```

### Singleton BLP+AIP

Zhuk, *Singleton algorithms for the Constraint Satisfaction Problem*
(arXiv:2509.18434), Corollary 5.10:

```text
singleton BLP+AIP solves PCSP(A,B)
iff
M_S(BLP+AIP) -> Pol(A,B).
```

Barto--Hadek--Zhuk,
*Toward a Uniform Algorithm and Uniform Reduction for Constraint Problems*
(arXiv:2604.06335), identify the CSP of the dihedral group D4 as a fixed CSP that
fools singleton BLP+AIP, while their vector relaxation solves it.

Therefore:

```text
M_S(BLP+AIP) -/-> Pol(D4).
```

If singleton BLP+AIP solved full signed 3SAT directly, then

```text
M_S(BLP+AIP) -> Proj -> Pol(D4),
```

contradiction.

Hence:

```text
DIRECT SINGLETON BLP+AIP
ON VISIBLE FULL SIGNED 3SAT
=
BLOCKED.
```

Again, this does not block a representation-changing compiler followed by
singleton BLP+AIP on a different target structure.

## 5. Search consequence

The active problem is no longer:

```text
find a stronger fixed relaxation and run it directly on three-sheet / OR3.
```

It is:

```text
find an exact polynomial representation change
whose output no longer presents the projection minion
to the downstream solver.
```

The representation change itself must carry the missing compression currency.

## 6. Donor status

### Published/formal donors

- higher-level / vector minions: formal, but every fixed direct affine level is blocked;
- singleton algorithms: formal, but direct singleton BLP+AIP is blocked;
- delta-matroid edge-CSP: formal, but direct occurrence-split model misses its hypotheses.

### Source-reported future donor

Barto--Hadek--Zhuk state that they found a recursive enhancement of AIP that is
genuinely different from singleton and higher-level approaches and that early
results are promising. They explicitly say the ideas will appear in a separate
paper.

As of the 2026-09-23 source sweep, no separate arXiv paper was located.

Therefore:

```text
RECURSIVE AIP
=
WATCHLIST / SOURCE-REPORTED
NOT A FORMAL JANUS MECHANISM
NOT ADMISSIBLE IN A PROOF CHAIN YET.
```

## 7. Next exact gate

```text
R5_E8_6I
REPRESENTATION_CHANGE_COMPRESSION_CURRENCY_GATE_V1
```

Required output of the representation change:

1. polynomially constructible from the original formula;
2. exact SAT preservation;
3. polynomial-size state;
4. no explicit SAT-equivalent selector;
5. no hidden exponential search;
6. one Boolean witness reconstructible in polynomial time;
7. downstream template/relaxation has a source-proved polynomial solver;
8. total lifecycle polynomial in original input length.

## 8. Ceiling

```text
DIRECT FIXED MINION RELAXATION HUNT
=
ANTI-LOOP ONCE A FINITE COUNTEREXAMPLE IS KNOWN

REPRESENTATION CHANGE
=
FIRST REAL GAP

D1
=
EMPTY

P_VS_NP
=
OPEN
```
