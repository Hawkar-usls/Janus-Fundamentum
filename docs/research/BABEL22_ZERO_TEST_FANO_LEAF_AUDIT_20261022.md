# BABEL-22 / universal SAT route audit: exact zero-test hardness and a false-hardness family

**22 October 2026. Research-only diagnostic, stacked on BABEL-21 (#545).**

## Frozen authority / context recovery
- Canonical main entry: `START_HERE_TRUMP_CONTEXT.md`; current TRUMP v3.23 state blob `70e8b78fedd05bedb2e2324846d83c6fceea434d`.
- This note is **not** a new TRUMP carrier, not an authorization to re-enter a closed route, and changes no scientific authority.
- BABEL-21 independent source syzygy facts: seed20 exact Q response rank 9/9, seed37 five independent new exact syzygies closing 11/11 ([Actions run 39748679961](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39748679961)). Those are frozen finite-cover claims only.

## 1. Exact special-circuit identity testing: a reduction, not a polynomial algorithm

Let `F` be ANY legal square 3-uniform 3-regular linear Exact-One instance with incidence matrix `A` and `n` variables/rows. Put `v = 1+x` and `K=ker_GF(2)(A)`. Each row of `A` has size 3, so `A 1 = 1`, and the parity consequence of Exact-One is `A v=0`. Conversely, on `K`, a row has 0 or 2 one-bits. It satisfies Exact-One in `x` if and only if it has exactly 2 one-bits in `v`.

For any `v in K` let `b_r(v)=1` if `v` vanishes on the three variables of row `r`, and `0` otherwise, and `D(v)=sum_r b_r(v)`. Then

```
F is SAT iff there exists v in K with D(v)=0.
3*weight(v) = 2*(n-D(v))  for every v in K.
```

Take any prime `p>n`, for example the first prime >n, which can be constructed in polynomial time in the explicit input size. Work over `F_p` and use the formal character functions `chi_j(v)=(-1)^{v_j}`; on `K`,

```
b_r = (1 + chi_a + chi_b + chi_c)/4
C_F = D^(p-1) - 1.
```

The special arithmetic circuit `C_F` has polynomial size (`D` is a sum of `n` four-term expressions; the power uses repeated squaring). **Theorem for ALL legal SCL inputs**:

```
F is UNSAT  <=>  C_F(v)=0 for EVERY v in K.
```

Proof: all `D(v)` are integers from 0 to `n<p`. Fermat gives `D^(p-1)=1` exactly when `D!=0`. A witness to failure of identity is any `v in K` with `D(v)=0`, i.e. an Exact-One solution.

**Complexity boundary.** This particular promised quotient-algebra ZERO-TEST is the complement of SCL-SAT under a deterministic polynomial-time many-one mapping. Under the previously established SCL hardness reduction (see `experiments/r5_e118_universal_linear_cubic_exactone_hardness_bridge.py` and predecessors), a polynomial-time complete ZERO-TEST would imply `P=NP`. It is *not* ordinary formal polynomial identity testing and cannot be promoted from the compact circuit alone. This is a formal reduction of the missing obligation, not a solver.

The same observation applies to the compact rational product `Q_n(D)`: compact construction and polynomial-time point evaluation do not imply polynomial-time identity testing over `K`.

## 2. NEW DIAGNOSTIC: Fano leaf makes large-nullity controls locally trivial

Seven Fano rows on seven variables form the 3-regular linear incidence of the Fano plane. Delete one of its rows `L={a,b,c}` and require Exact-One on the remaining six rows. Let `s=x_a+x_b+x_c`. Summing the six satisfied row equations gives `6=3*sum(x_i)-s`, so `s` is a multiple of 3: either 0 or 3. If `s=0`, every pair of the four variables outside `L` must sum to 1 (the six remaining lines realize all six pairs): impossible on a triangle. Hence `s=3` and **a=b=c=1**.

If one variable of the missing row is replaced by *any* external Boolean variable `y`, that row contains the other two original variables, both 1. It cannot satisfy Exact-One, irrespective of `y`.

**All-n theorem (local, not complexity breakthrough):** every legal SCL containing such a terminal Fano attachment is UNSAT by a constant-local-size proof. In particular, connecting any number of Fano blocks as a chain by single swaps creates seemingly difficult connected inputs whose terminal block immediately refutes them. This disqualifies this synthetic family as evidence for or against universal degree-2 Fourier completeness.

## 3. Finite independent controls and replay scope

The independent dependency-free verifier `experiments/babel22/fano_leaf_audit.py` replays:
- all seven six-line Fano deletions over all `2^7` assignments, checking the forced 111 boundary;
- Fano7 `d=3`, exact SAT count 0;
- affine-plane SCL9 `d=2`, exact SAT count 3;
- deterministic connected, 3-regular, linear Fano-chain SCL21/42/63: `d=7/13/19`, exact SAT count 0 by Gray-code enumeration of `2^d` parity words;
- all-state finite-field defect identity for Fano7, affine9, SCL21 and SCL42. The SCL63 run checks all parity weights but *does not* replay `D` on all states; this distinction is explicit.

These are control observations; the all-n Fano lemma is proved symbolically above. The numerical least-squares Fourier scans run locally are **NOT** exact rational certificate evidence and are excluded from the scientific ledger.

## 4. Next admissible path to the user's actual target

1. Search for legal connected UNSAT SCL cases that pass **all local obstruction filters**, have growing kernel dimension and fail fixed-degree Fourier surjectivity. For a negative Fourier claim require a rational witness `h^T M_2=0, h(e0)!=0` against **all** legal columns, not a modular residual or incomplete search.
2. If no negative is found, seek a full **all-n proof** of degree-2 completeness with exact semantics, coefficient-bit bounds, and a polynomial-time rank decision. Finite passes are not this theorem.
3. A different compressed representation needs a polynomial-time full zero-test, explicit `T_construct+T_solve+T_reconstruct+T_verify`, and a universally sound SAT witness reconstruction. Do not relabel NP-hard ZERO-TEST as an algorithm.

```
BABEL22_FANO_LEAF_LOCAL_THEOREM = PROVED
BABEL22_ZERO_TEST_EQUIVALENCE = PROVED (under standard SCL hardness bridge for complexity corollary)
UNIVERSAL_DEGREE2_COMPLETENESS = OPEN
POLYNOMIAL_ZERO_TEST = OPEN
UNIVERSAL_SolveLinearCubicXSAT = NOT_PROVED
P_VS_NP = OPEN
```
