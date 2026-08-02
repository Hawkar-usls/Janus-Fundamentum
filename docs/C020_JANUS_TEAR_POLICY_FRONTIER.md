# C020 addendum — policy-selected JANUS Tear frontiers

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

No swarm node, device, miner, radio channel, NAS runtime, or physical P–N
junction is used by this audit.

The previous C020 attack falsified the statement that **all** residual states of
every CNF always admit a polynomial continuation-complete quotient. The
surviving route asks whether one explicit policy can visit only polynomially
many selected states.

This addendum introduces an exact resource for that question on affine Boolean
systems.

## Exact semantic frontier formula

Let

```text
A x = b  over GF(2)
```

be satisfiable. Split the variables at one policy cut into processed variables
`P` and unprocessed variables `U`:

```text
A_P x_P + A_U x_U = b.
```

After a prefix assignment `x_P=a`, the residual system is

```text
A_U x_U = b + A_P a.
```

The number of distinct **extendable** residual solution sets is exactly

```text
2^d
```

where

```text
d = dim(im A_P ∩ im A_U)
  = rank(A_P) + rank(A_U) - rank(A).
```

If some prefixes cannot be extended, all of them contribute one additional
empty residual class.

Thus:

```text
one Tear signature needs d bits
but the policy may encounter 2^d different signatures.
```

This separates two resources that the early Tear metaphor conflated:

- payload size of one Tear;
- total number of reachable Tears under the policy.

## Policy sensitivity — the equality family

For

```text
E_n(X,Y) = AND_i (x_i <-> y_i)
```

consider two variable orders.

### Bad order

```text
x1,...,xn,y1,...,yn
```

At the middle cut:

```text
d = n
extendable residual classes = 2^n.
```

Every processed `X=a` leaves the distinct requirement `Y=a`.

### Good order

```text
x1,y1,x2,y2,...,xn,yn
```

At every cut:

```text
d <= 1
all residual classes <= 3
```

The third class is the common contradiction state created by an already broken
equality.

Therefore the C020 congruence explosion does **not** refute the surviving
policy-selected route. It proves that policy choice is essential: the same
formula family has exponential and constant width under different orders.

## Separator explosion — toroidal Tseitin

Take one `m x m` toroidal grid. Every edge is a Boolean variable and every
vertex is one parity equation. Process all edges column by column.

At every internal whole-column boundary, the executable audit obtains exactly

```text
d = 2m - 1
```

and therefore

```text
extendable residual affine states = 2^(2m-1).
```

The equality is also explained directly by incidence-matrix ranks. For a cut
after `k` complete columns, `1 <= k < m`:

```text
rank(A)   = m^2 - 1
rank(A_P) = m(k+1) - 1
rank(A_U) = m^2 - 1 - m(k-1)
```

so

```text
rank(A_P)+rank(A_U)-rank(A) = 2m-1.
```

Since the encoded formula length is `Theta(m^2)`, the tested sweep policy has

```text
2^Theta(sqrt(L))
```

semantic states. This is subexponential in `L`, but not polynomial.

For the C019 torus side `m=77`, the exact formula gives

```text
frontier dimension = 153 bits
extendable frontier states = 2^153
                           = 11417981541647679048466287755595961091061972992.
```

The CI self-test executes sides `3..12`; the `m=77` value is an exact algebraic
extrapolation from the proved rank formula, not a brute-force enumeration.

## Representation sensitivity — why this is not a SAT lower bound

An odd-charge toroidal Tseitin system is still decided in polynomial time by
one global affine certificate:

```text
XOR every vertex equation.
Every edge appears twice, so the left side is 0.
An odd charge sum makes the right side 1.
Therefore 0=1.
```

The certificate references `m^2` equations and is linear in the input.

So the result is deliberately asymmetric:

```text
CNF frontier sweep     -> 2^(2m-1) possible residual states
recognized XOR system -> one linear global contradiction certificate
```

The frontier explosion attacks the chosen quotient policy, not all algorithms.
The same instance becomes easy after the correct representation change.

## New missing theorem

The surviving P=NP route can now be stated more precisely.

### Universal Tear Policy and Representation Selection Theorem

For every CNF `F` of length `L`, a deterministic polynomial-time procedure must
select:

1. a variable/state exploration policy;
2. a semantic module decomposition;
3. a proof language or representation for each module;
4. sound interface Tears between modules;
5. witness-recovery information;

such that the total number of visited states, all representation-search work,
all certificates, and all recovery work are bounded by `poly(L)`.

The theorem must handle at least three independent failure modes:

```text
bad order             -> equality family gives 2^n states
bad decomposition     -> connected C019 hides the XOR lobes
bad proof language    -> torus sweep has 2^(2m-1) states despite a linear XOR proof
```

Constructing such a universal selector would already provide a polynomial-time
SAT algorithm and prove `P=NP`.

## Reproduction

```bash
python experiments/direct/janus_tear_policy_frontier.py --self-test
python experiments/direct/janus_tear_policy_frontier.py --equality-n 12
python experiments/direct/janus_tear_policy_frontier.py --torus-side 12
python experiments/direct/janus_tear_policy_frontier.py --json
```

## Claim boundary

This addendum does not prove `P=NP` or `P!=NP`. It gives an exact state-count
formula for affine policy cuts, shows that order can change width from
exponential to constant, and shows that a proof-language switch can bypass a
large separator state space.
