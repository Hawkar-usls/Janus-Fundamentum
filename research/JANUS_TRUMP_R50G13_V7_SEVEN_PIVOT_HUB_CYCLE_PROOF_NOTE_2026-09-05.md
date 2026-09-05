# JANUS TRUMP R50G13 — V7 seven-pivot hub-cycle normal form

## Scope

Assume a persisted source formula `F` with exactly seven variables and `W(F) <= 4` is pre-BVE clean under the frozen R33 priority. Let the first R33 proposal be BVE on `x`, and suppose that proposal leaves W4. Assume further that same-pivot R47J on `x` is nonterminal with final width > 4 and that every alternate pivot `y != x` has neither an R49H door nor an R47J_SAFE door.

This note does **not** prove that such a source exists or is reachable. It derives the exact normal form any such obstruction must satisfy.

## 1. All seven pivots are closed

For every alternate `y != x`, closure is an assumption. For the distinguished pivot `x`, immediate BVE escape means the exact DP pool on `x` contains a non-tautological resolvent of width > 4; untouched source clauses have width <= 4, so the width escape must come from an `x`-resolvent. Hence `chi_star(F,x) >= 5`, so R49H is closed on `x`. Same-pivot R47J is assumed nonterminal wide, so R47J_SAFE is also closed on `x`.

Therefore every source variable `y` is a closed pivot.

By R50G11 and W4:

`chi_star(F,y) in {5,6}`

for every source pivot `y`.

## 2. Every closed R47J final has exactly V=6 and W=5

Frozen R47J exact DP removes `y` and introduces no fresh variables. Therefore for a seven-variable source:

`V(J_y) <= 6`.

A closed R47J door means the final state is nonterminal and has width > 4. The final normalization state is R33-fixed and RUP-fixed. By the R50G12 external-support theorem, any surviving clause `C` in such a state satisfies:

`V(final) >= |C| + 1`.

Taking a widest clause gives:

`V(J_y) >= W(J_y) + 1 >= 6`.

Together with `V(J_y) <= 6`:

`V(J_y) = 6` and `W(J_y) = 5`.

Since no fresh variables are introduced and `y` is eliminated, the six final variables are exactly `Vars(F) \ {y}`.

## 3. The unique external-support hub

Choose the canonical lexicographically first widest width-5 clause `C_y` in the final state `J_y`. It uses five of the six final variables, so exactly one final variable is absent. Define that variable as:

`h(y) := the unique member of Vars(J_y) \ Vars(C_y)`.

R50G12 applies to `C_y`: every nonblocking support of every literal of `C_y` must contain a variable outside `Vars(C_y)`. There is only one such final variable. Therefore every nonblocking support of `C_y` uses `h(y)`.

Thus each closed pivot carries an exact `SINGLE_EXTERNAL_SUPPORT_HUB` certificate.

## 4. No variable-removing normalization after DP_y

The exact DP transform on `y` contains no `y` and no fresh variables. The final state still contains all six other source variables. Therefore no later normalization action can remove any variable permanently.

In particular, no BVE step can occur after DP_y, because BVE removes its pivot and frozen normalization never introduces fresh variables. Likewise, no unit or pure-literal reduction that removes a variable can occur on the path to the final six-variable state.

The remaining normalization actions may delete or strengthen clauses but do not create new width. Consequently every final width-5 clause must have ancestry in the exact DP pool produced at the first `y` elimination.

## 5. Width-5/6 DP ancestry of C_y

The source has width <= 4. Therefore the only clauses wider than four immediately after eliminating `y` are exact cross-polarity DP resolvents. Since `chi_star(F,y) in {5,6}`, every wide DP ancestor has width five or six.

Because no later BVE can create a new wide clause, the selected final `C_y` descends from some exact DP resolvent `R_y` with width 5 or 6.

Two canonical ancestry cases remain:

1. `|R_y| = 5`: a width-5 DP resolvent survives to the final width-5 clause without literal loss along its selected ancestry. Then `h(y)` is the unique surviving variable omitted by that resolvent.
2. `|R_y| = 6`: the ancestor contains all six variables other than `y`; to end at width five, a literal on exactly one variable is removed along a RUP-strengthening ancestry path. That omitted final variable is `h(y)`.

This is an ancestry classification, not an assertion that every wide DP resolvent survives.

## 6. Hub-map cycle

For every source variable `y`, `h(y)` is one of the six variables different from `y`. Hence

`h : Vars(F) -> Vars(F)`

is a total fixed-point-free function on seven vertices.

Every finite functional digraph contains a directed cycle. Because fixed points are forbidden, the cycle length is in `{2,3,4,5,6,7}`.

Therefore any V7 all-doors-closed obstruction necessarily contains a replayable seven-pivot hub map with at least one directed cycle.

## Resulting target

R50G13 reduces the V7 obstruction to:

`PRE_BVE_CLEAN W4 SOURCE + ALL SEVEN PIVOTS CLOSED + SEVEN EXACT V6/W5 R47J FINALS + FIXED-POINT-FREE HUB MAP WITH A DIRECTED CYCLE`.

The next legitimate theorem target is not merely “a hub exists.” It is:

`IMPOSSIBILITY_OF_A_SHARED_W4_PARENT_SYSTEM_REALIZING_A_CYCLIC_SEVEN_PIVOT_HUB_MAP`

or an explicit exact realization, with reachability kept as a separate firewall.

No claim about full immediate-BVE elimination, U_mu, SAT in P, or P vs NP follows from this reduction alone.
