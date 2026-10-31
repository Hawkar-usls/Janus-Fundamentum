# R5 E9 — WDR Core Census v0.1 and Resolution-Expansion Charge

**Date:** 2026-09-23  
**Status:** partial executable census + exact derived theorem.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Scope of this receipt

This is **not yet** the full frozen WDR scheduler.

Implemented in the v0.1 diagnostic prototype:

- R0 unit propagation / tautology / duplicate cleanup;
- pure-literal autarky;
- R1 exact binary equivalence substitution;
- R3 blocked-clause elimination;
- R4 exact Davis-Putnam variable elimination whenever the number of distinct non-tautological resolvents does not exceed the number of removed x-clauses;
- R7 extraction/solution of variable-disjoint Horn, dual-Horn and Krom components.

Not yet implemented in this diagnostic:

- full matching-autarky kernel;
- full linear-autarky LP engine;
- signed structural-dominance synthesis;
- ranked/SR macro synthesis.

Therefore the authoritative gate
`R5_E9_WDR_NORMAL_FORM_SURVIVOR_MOTIF_GATE_V1`
remains OPEN.

## 2. First survivor census

Representative deterministic runs produced:

| family | input (vars, clauses, lits) | v0.1 outcome | residual |
|---|---:|---|---:|
| equality channels, 20 independent pairs | (40,40,80) | SAT via 20 equivalence contractions | empty |
| PHP(4,3) | (12,22,48) | 5 VE steps then survivor | (7,18,54) |
| PHP(5,4) | (20,45,100) | 5 VE steps then survivor | (15,40,120) |
| PHP(6,5) | (30,81,180) | 6 VE steps then survivor | (24,75,240) |
| linear 4-partition NAE, n=15..30 | (n,8n/3,8n) | **zero reductions in all tested samples** | unchanged |
| random 3SAT near 4.26n, n=20..50 | mostly zero or a few VE/BCE steps | survivor | almost unchanged |
| small/random cubic Tseitin | mixed: some small graphs collapse by VE; other samples survive | survivor samples connected and dense |

The exact numeric census is diagnostic only. It is not an asymptotic lower bound.

## 3. Shared motif visible already in v0.1 survivors

Every observed nontrivial survivor after this partial closure had:

- one variable-connected component;
- no unit clause;
- no pure variable;
- no detected binary equivalence;
- no blocked clause;
- no no-growth VE candidate;
- every live variable occurring in both polarities;
- positive clause/variable excess.

This motivates a local invariant measuring how strongly each variable resists exact CNF projection.

## 4. Resolution-expansion charge

For CNF F and variable x, write

[
P_x={Cin F:xin C},qquad
N_x={Cin F:
eg xin C}.
]

Let

[
mathcal R_x
]

be the set of **distinct non-tautological** resolvents obtained by resolving a clause of (P_x) with a clause of (N_x) on x.

Define the clause expansion charge

[
chi_F(x)
:=
|mathcal R_x|-|P_x|-|N_x|.
]

Exact Davis-Putnam elimination of x changes the number of clauses by at most this amount after duplicate/tautology deletion.

In particular:

[
chi_F(x)le0
]

is exactly the local admission test used by WDR-core R4.

Hence every R4-closed survivor satisfies

[
chi_F(x)>0
]

for every live x.

## 5. Exact theorem for linear regular NAE3

Let H be a **linear** 3-uniform hypergraph and encode every hyperedge
({x,a,b}) by the standard positive NAE pair

[
(xee aee b)
wedge
(
eg xee
eg aee
eg b).
]

Assume variable x belongs to exactly d hyperedges.

### Theorem NAE-CHARGE

[
oxed{chi_F(x)=d(d-3).}
]

### Proof

There are exactly d positive-x clauses and d negative-x clauses.

Resolve a positive clause from edge (E_i) against a negative clause from edge (E_j).

- If (i=j), the resolvent contains both signs of the other two variables of the same NAE edge, hence is tautological.
- If (i
e j), linearity implies (E_icap E_j={x}). Therefore the resolvent is a non-tautological 4-clause consisting of the two positive literals from (E_i-{x}) and the two negative literals from (E_j-{x}).
- Distinct ordered pairs ((i,j)) give distinct resolvents: the positive literal pair identifies (E_i), and the negative literal pair identifies (E_j).

Thus

[
|mathcal R_x|=d(d-1).
]

Since (|P_x|+|N_x|=2d),

[
chi_F(x)=d(d-1)-2d=d(d-3).
]

∎

## 6. Exact threshold consequence

For linear d-regular positive NAE-3SAT:

[
d=3
quadLongrightarrowquad
chi(x)=0
]

for every variable initially.

But

[
d=4
quadLongrightarrowquad
chi(x)=4
]

for every variable initially.

Therefore the source-backed tractability/hardness boundary between the 3-occurrence and 4-occurrence linear NAE families has an exact local resolution-expansion signature:

[
0 longrightarrow +4.
]

This does **not** prove that charge alone characterizes tractability.

It does prove that the fourth occurrence changes every local exact CNF projection from clause-neutral to clause-expanding.

## 7. Literal charge and migration

The same elimination removes (2d) ternary clauses, hence (6d) literal occurrences, and creates (d(d-1)) 4-clauses, hence

[
4d(d-1)
]

literal occurrences.

The literal-occurrence change is therefore

[
lambda(d)
=
4d(d-1)-6d
=
2d(2d-5).
]

In particular:

- d=3: clause charge 0 but literal charge +6;
- d=4: clause charge +4 and literal charge +24.

This explains why even the d=3 family can stop being locally no-growth after several eliminations: charge is not destroyed; it can migrate into higher-arity constraints.

## 8. Pairwise grouped-elimination diagnostic

For selected v0.1 survivors, exact two-variable Davis-Putnam projection was tested in both elimination orders.

Best observed final clause growth relative to the residual before the pair elimination:

- DDD NAE4: +8;
- selected Tseitin survivor: +8;
- PHP(5,4) survivor: +12;
- random threshold 3SAT sample: +7.

No tested survivor had a pair with nonpositive final clause growth.

Interpretation:

> merely grouping two ordinary DP eliminations does not yet neutralize the survivor charge.

This is diagnostic, not an asymptotic theorem.

## 9. Structural meaning for witness-dominance

For one variable

[
F=Cwedgeigwedge_i(xee A_i)wedgeigwedge_j(
eg xee B_j),
]

exact existential elimination is

[
exists x,F
equiv
Cwedge
left[
left(igwedge_i A_iight)
ee
left(igwedge_j B_jight)
ight].
]

Expanding this disjunction back into CNF gives exactly the Cartesian family

[
igwedge_{i,j}(A_iee B_j),
]

i.e. the Davis-Putnam resolvents.

Therefore (chi_F(x)) measures a local **distributive-expansion cost** of preserving both Shannon branches explicitly in CNF.

Witness-dominance / ranked-repair aims to avoid paying this product cost by proving that one branch, or one ranked canonical region, is sufficient for satisfiability and witness reconstruction.

This tightly connects the WDR frontier to the survivor charge rather than treating them as unrelated ideas.

## 10. Updated immediate target

### R5_E9_WDR_EXPANSION_CHARGE_REPAIR_GATE_V1

On a deterministic WDR normal-form survivor:

1. compute (chi_F(x)) for every live variable;
2. identify minimal-charge variables/blocks;
3. attempt to synthesize a ranked structural repair that fixes/removes a positive-charge block **without materializing its Cartesian resolvent product**;
4. require exact reverse witness reconstruction;
5. measure progress by live Boolean dimensions plus a bounded charge budget.

The next new (mu/ho) rule should explain how to destroy or amortize this expansion charge.

D1 = EMPTY.  
P_VS_NP = OPEN.
