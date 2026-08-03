# C044 — Proof-Carrying Local Signed-Support Vtree Composition

```text
P_VS_NP=OPEN
```

## Purpose

C043 decides affine-coordinate CNF whenever one global signed representation

```text
1_(union U_C) = sum_S c_S 1_S
```

has polynomially bounded maximum live and working support.

C044 covers a strict extension: the global representation may overflow, while
a deterministically discovered recursive coordinate decomposition has:

- fixed-size separators;
- polynomial local signed support at every leaf;
- polynomial separator branch volume;
- proof-carrying SAT witness recovery or complete UNSAT composition.

No decomposition is supplied for free.

## Input and affine inheritance

The input is an ordinary CNF `F(x)` plus affine equations `A x=b`.

C044 independently constructs and certifies

```text
x = p + B lambda
```

using provenance-carrying Gaussian elimination. Each clause-falsifying set is
translated into one affine subspace `U_C` of the coordinate space, or the empty
set.

The decomposition is built on the coordinate primal graph induced by the
supports of the canonical RREF systems for the `U_C`.

This graph depends on the canonical affine basis. C044 does not search arbitrary
basis changes.

## Deterministic discovery

For one region with active coordinate set `V` and factor set `Q`:

1. Attempt a complete local C043 signed-support compilation.
2. If it stays within the fixed local support capability, emit a `SIGNED_LEAF`.
3. Otherwise construct the coordinate primal graph.
4. Accept disconnected components immediately, or enumerate separator sets
   lexicographically up to the fixed cap `k`.
5. The first separator whose remaining components have size at most `2|V|/3`
   is selected.
6. Partition factors by the components after deleting the separator.
7. Recurse before any separator value is chosen.

Every branch therefore uses one common assignment-independent decomposition.

If local support overflows and no admitted separator exists, return:

```text
OPEN_LOCAL_SUPPORT
reason = NO_ADMITTED_SEPARATOR
```

The refusal includes the failed local-support evidence and the exact separator
capability.

## Local signed leaves

A signed leaf stores

```text
1_(union local U_C) = sum_S c_S 1_S
```

over its complete local scope, including inherited boundary coordinates.

For every factor insertion C044 records:

- the previous signed support;
- every affine intersection;
- the signed delta;
- coefficient merges;
- zero cancellation;
- live support;
- working support before cancellation.

Both live support and working support must remain inside the fixed polynomial
capability. A small final message does not excuse an exponential intermediate.

Given a boundary assignment, exact signed counting determines whether an
internal extension exists. If it does, coordinates are recovered greedily by
conditional signed counts. If the boundary fiber is fully covered, the count
trace is an exact local UNSAT proof.

## Separator composition

At a separator `S`, C044 enumerates its `2^|S|` assignments in canonical order.

For each assignment:

1. separator-local forbidden factors are evaluated;
2. every child receives the restriction to its recorded boundary;
3. children are independent after `S` is fixed;
4. a SAT branch combines compatible child witnesses;
5. an UNSAT branch records either a local forbidden factor or a child UNSAT
   proof.

A root UNSAT result contains a blocker for every separator assignment. A root
SAT result contains all rejected earlier branches and one complete accepted
branch.

## Constructive theorem

Let:

- `k` be the fixed separator cap;
- `K` bound every accepted local live and working signed support;
- all work and certificate limits be fixed polynomials in the encoded input
  length `L`.

Discovery tests at most `O(n^k)` separator candidates at each plan node. For a
balanced separator the recursive solving cost obeys

```text
T(n) <= 2^k sum_i T(n_i) + poly(L,K,n^k)
sum_i n_i <= n
max_i n_i <= 2n/3.
```

For fixed `k`:

```text
T(n) = L^O(k).
```

Thus every admitted C044 instance is decided in deterministic polynomial total
work, including decomposition discovery, all failed local probes, all
intermediate supports, witness recovery, proof construction and independent
verification.

## Independent verifier

The verifier does not import the solver.

It independently reconstructs:

- the affine basis and provenance;
- every clause-falsifying subspace;
- every failed local-support probe;
- deterministic separator selection;
- factor partitioning;
- every accepted local signed transition;
- all conditional counts;
- every separator branch;
- the SAT witness or complete UNSAT tree;
- exact work and certificate capability behavior.

The verifier reconstructs the entire expected terminal and requires exact
equality with the supplied certificate.

## Strict extension beyond global C043

### Forty independent unit factors

```text
F = x_1 AND ... AND x_40
```

The global signed-union attempt exceeds support cap 8:

```text
C043 -> OPEN_INTERSECTION_CLOSURE
```

C044 detects 40 disconnected coordinate components:

```text
41 plan nodes
40 signed leaves
maximum separator size 0
C044 -> SAT
```

### Forty-variable path

```text
F = AND_i (x_i OR x_(i+1))
```

The global signed attempt exceeds support cap 16.

C044 discovers a recursive path decomposition:

```text
23 plan nodes
12 signed leaves
11 separator nodes
maximum separator size 1
maximum depth 5
C044 -> SAT
```

This is a genuine global-to-local separation: the global signed language
overflows while every admitted local message and separator remains within the
fixed capability.

## Frozen audit

```bash
python experiments/direct/janus_c044_local_signed_support_vtree.py \
  --self-test \
  --output /tmp/c044.json
cmp /tmp/c044.json \
  experiments/direct/C044-JANUS-LOCAL-SIGNED-SUPPORT-VTREE.frozen.json
```

The deterministic audit covers:

```text
300 random CNF + affine instances on <= 7 variables
300 exact terminals
0 SAT/UNSAT mismatches
0 false witnesses
0 independent-verifier failures

40 independent units:
  global C043 OPEN / local C044 SAT

40-variable path:
  global C043 OPEN / separator-one C044 SAT

proof-carrying composed UNSAT
32-variable dense CNF with affine dimension one
hard-image pressure -> OPEN_LOCAL_SUPPORT
separator-cap zero -> OPEN_LOCAL_SUPPORT
work exhaustion -> OPEN_WORK_BUDGET
certificate exhaustion -> OPEN_CERTIFICATE_VOLUME
deterministic repeated plan
tampered witness -> REJECTED
tampered plan -> REJECTED
tampered OPEN evidence -> REJECTED
```

Frozen digest:

```text
feb7b2560d72ccb198ff67f07099b1122d2aecebc6ce81d4294b5f7f2750e0cf
```

Finite random checks validate the implementation. The theorem follows from the
signed indicator identity, exact affine counting, separator independence and
the recurrence above.

## Literature alignment

The use of assignment-independent tree structure and separator messages is
aligned with structured knowledge compilation and bounded-width dynamic
programming. C044's specific contribution inside JANUS is the charged
combination of:

- affine-subspace signed-cover leaves;
- deterministic separator discovery;
- explicit accounting before cancellation;
- proof-carrying local-to-global composition.

It is not promoted as a new general width invariant.

## Decisive boundary

The registered dense NAND3+NEQ pressure family has:

- overflowing local signed support;
- no admitted separator of size at most one.

C044 returns:

```text
OPEN_LOCAL_SUPPORT
reason = NO_ADMITTED_SEPARATOR
```

This is not a hardness theorem.

The surviving gate is:

```text
JOINT_AFFINE_BASIS_DECOMPOSITION_AND_MESSAGE_DISCOVERY
```

A next route must polynomially discover one or more of:

- a better proof-carrying affine basis;
- a richer separator message;
- a non-primal semantic decomposition;
- bounded support after symbolic projection;
- another exact local cover language.

C044 does not decide arbitrary 3-CNF, unrestricted affine-coordinate
arrangements, or P versus NP.
