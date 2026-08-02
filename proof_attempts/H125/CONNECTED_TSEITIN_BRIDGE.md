# H125 — connected neutral-bridge toroidal Tseitin twins

## Status

`FORMALIZING`, reproducibility `R3`.

This artifact strengthens H121 by connecting its two toroidal primal components.
It does not prove the global factorization conjecture H127.

## Base family

H121 supplies, for each radius `R`, two CNFs on two disjoint `m × m` toroidal
Tseitin systems, where

```text
m = 8R + 13.
```

The SAT member has charge counts `(2,0)` by component, and the UNSAT member has
charge counts `(1,1)`. Their bounded-radius signed-incidence signatures are
identical, and an original primal component has treewidth at least `m-1`.

## Neutral bridge

Choose one charge-free edge variable `x` in the first torus and the corresponding
charge-free edge variable `y` in the second. Introduce fresh variables `z,w` and
add:

```text
(x ∨ z)
(¬x ∨ z)
(y ∨ w)
(¬y ∨ w)
(z ∨ w)
```

For every assignment of `x,y`, setting

```text
z = 1
w = 1
```

satisfies all five clauses. Therefore the bridge imposes no condition on the
original variables.

Consequently:

- every satisfying assignment of the SAT base extends through the bridge;
- if the bridged UNSAT formula were satisfiable, restricting its assignment to
  the original variables would satisfy the UNSAT Tseitin base, a contradiction.

The bridge is exactly satisfiability-neutral.

## Primal connectivity

The bridge clauses create the path

```text
x — z — w — y
```

in the primal graph. The original primal graph inside each torus is connected,
so this path joins the two lobes into one connected graph.

## Local equality

The bridge is identical on both sides. Its endpoint is selected at a torus
coordinate farther than `2R+4` from every charged vertex. Thus no radius-`R`
incidence neighborhood can contain both a charge-altered Tseitin gadget and a
bridge gadget.

Every radius-`R` root therefore falls into one of three disjoint classes:

1. an ordinary uncharged torus neighborhood;
2. a neighborhood containing exactly one charged vertex gadget;
3. a neighborhood containing part of the identical bridge.

H121 gives exact equality of the first two classes, including their
multiplicities. The third class is introduced identically on both formulas.
Hence the complete connected pair retains exact radius-`R` local equality.

The executable artifact checks the required clearance and all finite semantic
conditions for radii zero through four. The universal argument is the feature
separation above.

## Treewidth

Adding bridge clauses does not delete any original primal edge. The connected
primal graph contains an original toroidal Tseitin primal component as a
subgraph. Treewidth is monotone under taking subgraphs, so

```text
tw(bridged primal) >= m - 1.
```

## Reproduction

```bash
python experiments/direct/connected_toroidal_tseitin_twins.py --self-test
```

Expected headline:

```text
JANUS_CONNECTED_TOROIDAL_TSEITIN_TWINS = PASS
PRIMAL_CONNECTED = true
BRIDGE_SAT_NEUTRAL = true
```

## Remaining wall

Connectedness removes one visible global side channel, but it does not establish
that every fixed-pass low-treewidth transduction loses the same-lobe versus
split-lobe charge bit. That is the exact content of H127.

## Claim boundary

H125 is an explicit connected target for a restricted locality lower bound. It
does not refute unrestricted SAT algorithms and does not resolve `P` versus
`NP`.
