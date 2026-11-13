# R5 Parity — Induced C5 counterexample for fixed-M trade compatibility

Date: 2026-10-10

Status:
TRADE_COMPATIBILITY_PERFECTNESS_REFUTED

P_VS_NP = OPEN.

## Claim

There exists a positive square, cubic, linear Exact-One instance, a fixed
perfect matching M, and five connected fixed-M trades T_0,...,T_4 whose
compatibility graph is exactly the induced cycle C5.

Therefore the universal claims

* fixed-M trade compatibility graphs are chordal;
* fixed-M trade compatibility graphs are perfect;

are both false.

## 1. Block variables

Work modulo 5.

Create ten variables in the fixed perfect matching M:

* q_0,...,q_4;
* p_0,...,p_4.

They will each cover three clauses.

## 2. Residual variables

Create

* s_{i,k} for i in Z_5 and k in {0,1,2}; 15 variables;
* f_0,...,f_4; 5 filler variables.

Thus there are 20 residual variables and 30 variables total.

## 3. Residual cubic graph R_M and block partition

Every edge of R_M corresponds to one Exact-One clause; its block label is the
unique M-variable in that clause.

### Shared blocks q_i

For each i in Z_5, block q_i consists of the three matching edges

    s_{i,k} -- s_{i+2,k},  k=0,1,2.

Thus q_i is a 3-edge matching between S_i and S_{i+2}, where

    S_i={s_{i,0},s_{i,1},s_{i,2}}.

### Private blocks p_i

For each i in Z_5, block p_i consists of

    s_{i,0} -- f_i
    s_{i,1} -- f_{i+1}
    s_{i,2} -- f_{i+2}

with indices modulo 5.

Again p_i is a 3-edge matching.

Every s_{i,k} is incident with exactly the three blocks

    q_i, q_{i-2}, p_i.

Every filler f_j is incident with exactly the three private blocks

    p_j, p_{j-1}, p_{j-2}.

Hence R_M is simple and cubic, and its 30 edges are partitioned into the ten
3-edge matching blocks.

## 4. Exact-One instance

For every residual edge uv belonging to block m, create one Exact-One clause

    (m,u,v).

There are 30 clauses and 30 variables.

Every clause has size 3.
Every variable has degree 3.
Two distinct clauses share at most one variable:

* R_M is simple, so two residual variables share at most one clause;
* every block is a matching, so an M-variable and a residual variable share at
  most one clause.

Therefore the instance is square, cubic and linear.

The ten block variables q_i,p_i form a perfect matching M: select every M
variable and no residual variable.

## 5. Five connected trades

For each i define

    P_i={q_i,q_{i-2},p_i},
    S_i={s_{i,0},s_{i,1},s_{i,2}}.

Replace the three M-variables P_i by the three residual variables S_i.

Each s_{i,k} occurs once in each of the three blocks in P_i, so S_i covers
exactly the nine clauses formerly covered by P_i, exactly once.

Thus

    T_i=(S_i,P_i)

is a valid fixed-M trade of volume 3.

Its trade incidence graph is K_{3,3}, hence it is connected.

## 6. Compatibility graph

Two fixed-M trades T_i,T_j are compatible exactly when their removed
M-supports P_i,P_j are disjoint.

Here

    P_i={q_i,q_{i-2},p_i}.

Adjacent indices modulo 5 have disjoint supports:

    P_i intersect P_{i+1} = empty.

Distance-two indices share exactly one q-block:

    P_i intersect P_{i+2} = {q_i}.

Therefore

    T_i compatible with T_j
    iff
    j=i+1 or i-1 mod 5.

So the compatibility graph induced by T_0,...,T_4 is exactly

    C5.

Because C5 is an odd hole, it is not perfect.

Hence the fixed-M trade compatibility graph is not universally perfect.

## 7. Consequence

The hoped-for universal solver shortcut

    optimize compatible fixed-M trades
    by chordal/perfect-graph machinery

is invalid.

The exponential branching cannot be removed merely by proving a global
perfectness property of the compatibility graph.

Any surviving polynomial route must exploit additional structure beyond the
abstract compatibility graph itself, for example weights/zero-circulation,
near-minimum restrictions, or algebraic decomposition of the exact trade
system.

## Claim boundary

TRADE_COMPATIBILITY_CHORDALITY = REFUTED.
TRADE_COMPATIBILITY_PERFECTNESS = REFUTED.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
