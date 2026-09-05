# R50G22 — ALL-DIRECT5 V7 cycle: parent-omission reduction and frozen falsifier

R50G21 leaves exactly one V7 hub-cycle ancestry class:

\[
\boxed{ALL\_DIRECT5\_CYCLE.}
\]

This note records what is source-level theorem and what remains finite falsification.

## 1. DIRECT5 edge = exact parent-omission certificate

Let the seven source variables be `V`, and let an unsafe R47J pivot `v` have final canonical width-5 clause `C_v` and unique external hub `h(v)`. R50G13 gives

\[
Vars(C_v)=V\setminus\{v,h(v)\}.
\]

If the surviving ancestry label is `DIRECT5`, R50G14 says `C_v` is already an exact non-tautological cross-pivot resolvent of one positive-v and one negative-v source parent.

Because the resolvent is exactly `C_v`, neither parent may contain `h(v)`. Their pivot-deleted residual union is exactly the five variables of `C_v`.

Under source width at most four, the only possibilities are exactly the already frozen R50G14 geometries:

- `4x3_DISJOINT`: residual sizes `3+2`, overlap 0;
- `3x4_DISJOINT`: residual sizes `2+3`, overlap 0;
- `4x4_OVERLAP1`: residual sizes `3+3`, overlap exactly 1.

Thus every DIRECT5 edge

\[
v\to h(v)
\]

carries a proof object

\[
(P_v,N_v,C_v)
\]

with opposite `v` polarities, both parents omitting the hub, and residual union `V\\{v,h(v)}`.

## 2. ALL-DIRECT5 cycle = parent-omission cycle

R50G13 already proves that an all-doors-closed V7 source induces a total no-self-loop hub map and therefore a directed cycle. R50G21 proves every surviving edge on such a cycle is DIRECT5.

Hence a remaining counterexample must contain a directed cycle

\[
v_1\to v_2\to\cdots\to v_k\to v_1
\]

such that for every edge `v_i -> v_{i+1}` there is an opposite-`v_i` parent pair whose two members both omit `v_{i+1}` and whose exact DP resolvent covers the other five variables.

This is a strict source-level reduction. It is **not** yet a contradiction.

## 3. Why the frozen family is legitimate but non-authoritative

R50G22 instantiates a canonical deterministic family designed to realize the parent-omission condition directly, then subjects each source to the frozen R33/R49H/R47J machinery.

For cycle length `k=2..7`, freeze

\[
1\to2\to\cdots\to k\to1,
\]

with each non-cycle tail vertex pointing to 1. For every pivot `v`, let

\[
C_v=V\setminus\{v,h(v)\}
\]

with a global sign choice for each source variable. Build a designated opposite-v pair in one of the three exact DIRECT5 geometries. Five deterministic cyclic rotations vary which target variables occupy which parent residual positions.

The family size is

\[
6\times128\times3\times5=11520.
\]

There is no randomness and no adaptive search. Every candidate is checked for exact designated ancestry before any scientific use.

However:

\[
\boxed{NO\ FIND\ IN\ 11520\neq UNIVERSAL\ IMPOSSIBILITY.}
\]

The family exists to do one of two useful things:

1. produce an explicit local all-doors-closed DIRECT5 counterexample; or
2. expose a reproducible rejection profile telling us which source obligation most often kills parent-omission cycles, thereby selecting the next symbolic lemma.

## 4. Counterexample standard

A local counterexample requires all of the following:

- exact V7, W<=4 source;
- pre-BVE clean;
- first frozen R33 microstep = immediate BVE escape on distinguished pivot 1;
- designated DIRECT5 certificate for every pivot with the declared hub map;
- same-pivot R47J unsafe;
- every alternate pivot has R49H closed and R47J unsafe;
- all seven R47J candidates independently replay;
- total hub map has the declared DIRECT5 cycle.

This would refute a **local** ALL-DIRECT5 impossibility statement. It does not refute the reachable theorem unless a separate reachable-trajectory certificate is supplied.

## 5. No-find standard

If no local all-doors-closed candidate appears, R50G22 must not change `ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED`. It reports an exact rejection histogram, first examples of each rejection class, and the strongest deterministic partial witness found.

The next theorem gate must then attack the dominant rejection condition symbolically rather than enlarge the family without reason.
