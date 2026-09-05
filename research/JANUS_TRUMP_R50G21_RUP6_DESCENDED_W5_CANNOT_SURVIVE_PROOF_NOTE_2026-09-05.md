# R50G21 — RUP6-descended width-5 cannot survive the same complete RUP pass

## 1. Setup inherited from R50G20

Let `H0` be the canonical R33-fixed state at entry to one complete frozen RUP pass. Assume exactly six variables. Let

\[
R=(\sigma z)\vee C
\]

be a width-6 clause containing all six variables, where `z` is the minimum-numbered variable among those six. By R50G20, every one-literal deletion of `R` is RUP-valid at `H0`, and when frozen RUP first selects the unchanged `R`, it removes `sigma*z` and creates

\[
C=R\setminus\{\sigma z\},\qquad |C|=5.
\]

Clause strengthenings that occurred earlier in the pass only make UP-conflict certificates stronger; they cannot destroy them.

The R50G21 question is narrower than R50G20:

> Can this newly created width-5 child `C` itself survive unchanged to the nonterminal end of the same complete RUP pass?

The answer is no.

## 2. BCE witness on the removed hub literal

Because `H0` is BCE-fixed, `R` is not blocked on `sigma*z`. Hence there exists at least one nonblocking opposite-hub witness

\[
D_z=(-\sigma z)\vee S,
\qquad S\subseteq C
\]

with the same polarities as `C`. There are two exhaustive cases.

## 3. Case A — proper support `S subset C`

Assume

\[
S\subsetneq C.
\]

Choose any literal

\[
\ell\in C\setminus S.
\]

Because `R` is also not blocked on `ell`, BCE fixedness gives a nonblocking witness

\[
E_\ell=(-\ell)\vee T,
\qquad T\subseteq R\setminus\{\ell\}
\]

with `R` polarities.

Now consider the formula immediately after `R` has been strengthened to `C`. Test the further strengthening

\[
C\to C\setminus\{\ell\}
\]

by assuming the negations of all literals in `C\setminus{ell}`.

Under these assumptions:

1. `C` becomes unit `ell`.
2. Since `ell notin S`, every literal of `S` is false, so `D_z` becomes unit `-sigma*z`.
3. In `E_ell`, every support literal from `C\setminus{ell}` is false.
   - If `sigma*z notin T`, then `E_ell` itself is falsified after `ell` becomes true, giving an immediate conflict.
   - If `sigma*z in T`, then `E_ell` becomes unit `sigma*z`, conflicting with `D_z`.

Therefore

\[
\boxed{C\setminus\{\ell\}\text{ is RUP-valid}.}
\]

Any earlier RUP strengthening of `D_z` or `E_ell` preserves this conflict by the clause-strengthening monotonicity theorem from R50G20: removing a literal can only reproduce the same unit no later or produce a conflict earlier.

So in Case A the newly created width-5 `C` cannot be a RUP fixpoint.

## 4. Case B — full opposite twin

The only remaining possibility is that every nonblocking opposite-hub witness has full support:

\[
S=C.
\]

Canonicalization then gives the opposite full twin

\[
T=(-\sigma z)\vee C.
\]

Since `T` is a clause of the same R33-fixed `H0`, `T` is itself BCE-fixed.

Fix any literal `ell in C`.

- Nonblocking of `R` on `ell` gives
  \[
  E^+_\ell=(-\ell)\vee A,
  \]
  where the hub literal, if needed after the other `C` literals are falsified, has polarity `sigma*z`.

- Nonblocking of the twin `T` on `ell` gives
  \[
  E^-_\ell=(-\ell)\vee B,
  \]
  where the corresponding hub polarity is `-sigma*z`.

The polarity statement is forced by non-tautology: a witness for `R` cannot contain the polarity opposite to the hub literal in `R`, while a witness for `T` cannot contain the polarity opposite to the hub literal in `T`.

Again assume the negations of `C\setminus{ell}` after `C` has been created. Then `C` forces `ell`.

For `E^+_ell`, after `ell=true` and all other C-support literals false:

- either the clause conflicts directly, or
- it becomes unit `sigma*z`.

For `E^-_ell`:

- either it conflicts directly, or
- it becomes unit `-sigma*z`.

Thus in every subcase unit propagation conflicts, and

\[
\boxed{C\setminus\{\ell\}\text{ is RUP-valid for every }\ell\in C.}
\]

Earlier clause strengthenings again cannot destroy this certificate.

So the opposite-full-twin case also cannot leave a newly created width-5 `C` at the complete RUP fixpoint.

## 5. Re-creation and deduplication do not rescue a novel width-5 child

There may be several width-6 clauses whose frozen minimum-variable deletion produces the same width-5 clause `C`.

If `C` was absent from `H0`, consider the **last** time during the finite RUP pass that any width-6 source creates `C`. By Sections 3–4, after that creation at least one one-literal deletion of `C` is RUP-valid. Subsequent transformations only strengthen clauses, so the deletion remains valid until `C` is touched. There is no later width-6 creator after the chosen last creation.

Therefore the complete pass cannot terminate nonterminal with this novel `C` present.

Hence:

\[
\boxed{
C\notin H_0
\land
C\text{ created only as a width6->width5 child}
\implies
C\notin H_{rup\_fix}.
}
\]

If collapse of a width-6 clause deduplicates into a `C` that was already present in `H0`, then any surviving width-5 provenance is already **pre-existing H0 provenance**, not a novel `RUP6_DROP_HUB` provenance.

## 6. Final width-5 provenance theorem

Frozen RUP never widens a clause. Therefore every width-5 clause at a nonterminal RUP fixpoint is either:

1. a width-5 clause already present at `H0`; or
2. a novel width6->width5 child.

Section 5 eliminates option 2.

Thus

\[
\boxed{
W5(H_{rup\_fix})\subseteq W5(H_0)
}
\]

at the level of surviving canonical clauses/provenance.

## 7. V7 ancestry corollary: RUP6_DROP_HUB disappears

R50G14 already proved that on a V7 unsafe trace every final V6/W5 hub edge has one of two initial-DP ancestry labels:

\[
\boxed{DIRECT5\quad\text{or}\quad RUP6\_DROP\_HUB.}
\]

It also proved that an unsafe V7 trace cannot perform a post-distinguished-DP variable elimination: losing another variable would leave at most five variables, which cannot support the required nonterminal wide fixed point.

Therefore before the first RUP pass, non-BVE normalization cannot create a new width-5 clause from the original W<=4 base clauses. Any width-5 clause already present at `H0` is an initial distinguished-DP width-5 resolvent, i.e. `DIRECT5` in the R50G14 classification.

R50G21 eliminates novel surviving RUP6-descended width-5 children. Consequently:

\[
\boxed{
RUP6\_DROP\_HUB\text{ cannot label a surviving V7 unsafe hub edge.}
}
\]

and every surviving V7 hub edge is `DIRECT5`.

Hence the R50G14 cycle bifurcation collapses from

\[
ALL\_DIRECT5\_CYCLE\quad\lor\quad RUP\_BEARING\_CYCLE
\]

to

\[
\boxed{ALL\_DIRECT5\_CYCLE.}
\]

This eliminates the **RUP-bearing ancestry branch**, not the V7 case itself.

## 8. Allowed status transition

After frozen implementation controls pass, R50G21 may set:

- `RUP6_DESCENDED_NOVEL_W5_SURVIVOR = ELIMINATED`;
- `RUP6_DROP_HUB_SURVIVING_V7_EDGE = ELIMINATED`;
- `RUP_BEARING_V7_HUB_CYCLE_ELIMINATED = true`;
- `V7_SURVIVING_HUB_CYCLE_CLASS = ALL_DIRECT5_ONLY`.

It may not set:

- `ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED = true`;
- `V7_IMMEDIATE_BVE_CASE_ELIMINATED = true`;
- `U_MU = PROVED`;
- `SAT_IN_P = PROVED`;
- `P_EQ_NP = PROVED`.

The next front becomes exactly the historical `ALL_DIRECT5_CYCLE`.
