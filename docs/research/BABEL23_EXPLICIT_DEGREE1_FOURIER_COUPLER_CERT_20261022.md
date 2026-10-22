# BABEL-23D — explicit all-n, degree-ONE Fourier ideal certificate for global Fano couplers

**2026-10-22.** Research-only exact theorem for the BABEL-23C deterministic infinite SCL family. This is a restricted structural theorem, **not** uniform bounded-degree completeness for arbitrary legal SCL. Stacked Draft PR #549, main untouched.

## Definitions

For each of B=2m Fano blocks, m>=3, use the 7 row indices r0..r6 and selected variables from \`BABEL23_GLOBAL_FANO_COUPLER_THEOREM_20261022.md\`; each color connects one imported Boolean literal \`y_c\` to another block's exported local literal from positions \`(x0,x2,x5)\`. The four unmodified rows are 2,3,4,6. Work on the full \`K=ker_GF2(A)\`, with \`v=1+x\` and \`chi_j(v)=(-1)^v_j=2*x_j-1\` for individual variable characters. Every row has even \`v\` parity and, therefore, \`prod_(j in r) chi_j=1\`. Define \`g_r=1+sum_(j in r)chi_j\`. Then \`g_r=2(sum_(j in r) x_j-1)\` **exactly on K**.

## The explicit identity

\`\`\`
                          1     B
  1 = ------------------------- sum [
           4B                  i=1
       g_(i,1)+g_(i,2)+g_(i,3)+g_(i,4)+g_(i,5)+g_(i,6)
       -(2+3*chi_(i,6)) * g_(i,0)
      ].
\`\`\`

Here \`chi_(i,6)\` is the single **local variable-6 character**, so the multiplier degree is at most ONE; no product of two or more variable characters is required. The certificate uses at most **8B** row-multiplier terms, coefficients in \`{1,-2,-3}/(4B)\` and a uniform algorithm to output its terms in O(B log B) bit operations. The Fourier coefficients are checked exactly at **every frequency** through a dictionary of at most \`4*(8B)\` nonzero contributions; there is no exponential 2^d loop.

### Proof: local single-character identity

For a given block abbreviate t=chi_1, a=chi_3, b=chi_4, c=chi_6. Parity of the unmodified r3=(3,4,6) gives a*b*c=1, so c*a=b. Parity of the three modified rows r0=(1,3,y0), r1=(1,4,y1), r5=(1,6,y2) gives

    g0=(1+t)(1+a)
    g1=(1+t)(1+b)
    g5=(1+t)(1+c).

Therefore, as an identity of functions on K,

    g1+g5-c*g0
      = (1+t)*[(1+b)+(1+c)-c(1+a)]
      = (1+t)*(2+b-c*a)
      = 2(1+t)
      = 4*x1.                                           (L)

This uses only parity equations and is valid for **arbitrary assignments of all other blocks**, without assuming Exact-One satisfiability.

### Proof: global coefficient cancellation

Write \`ell_r=sum_(j in r) x_j-1=g_r/2\`. Within a block write \`A=x0+x2+x5\` (export count), \`B'=x3+x4+x6\`, and \`Y=y0+y1+y2\` (import count). The four untouched rows give

    A-1 = (ell2+ell3+ell4+ell6)/2 - ell3.

The three edited rows give

    Y-2 = ell0+ell1+ell5-ell3-3*x1.

Subtracting gives

    A-Y+1
      = (ell2+ell3+ell4+ell6)/2 -(ell0+ell1+ell5)+3*x1
      = [g1+g2+g3+g4+g5+g6-(2+3*chi6)*g0]/4,

where the last step uses (L).

Summing over all B blocks, **each imported bit is exactly one exported bit under the perfect-matchings swap**, hence \`sum A = sum Y\` as a literal identity. The left-hand side sums to B, proving the exact Fourier ideal identity at the top.

This is a direct proof for every B and every admissible properly 3-edge-colored matching network of these couplers, not a limit inferred from finite numerics.

## Exact all-frequency independent replay

\`experiments/babel23/global_fano_fourier_identity.py\` reconstructs the target rows by an independent direct formula, Gaussian-eliminates their incidence matrix over GF2, computes all variable character labels, expands the 8B formal terms over the at-most-four-frequency generators, and asserts that the sparse Fourier coefficient map is EXACTLY \`{0:4B}\`. It checks sizes 42,84,126,168, whose computed kernel dimensions are 10,19,28,37. It never enumerates K. This is an exact certificate replay rather than floating-point or finite-field rank evidence.

## Scientific boundaries

- \`BABEL23D_ALL_N_COUPLER_DEGREE1_FOURIER_IDENTITY = PROVED\`
- \`BABEL23D_EXPLICIT_TERMS = 8B; COEFFICIENT_DENOMINATOR = 4B\`
- \`BABEL23D_GENERALIZE_TO_ANY_LEGAL_UNSAT_SCL = NOT_PROVED\`
- \`GENERAL_SAT_IN_P = NOT_PROVED\`
- \`P_VS_NP = OPEN\`

Other UNSAT instances can require different, potentially unbounded multiplier degrees. No generic lower or upper bound is implied by this special all-n construction.
