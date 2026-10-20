# JANUS Fundamentum — BABEL-16

## Exact seven-coordinate obstruction to the *canonical paired-transfer method* for SCL-252 seed 3

**Scientific verdict: EXACT NEGATIVE FOR ONE TRANSFER MECHANISM.**
The canonical BABEL-14/BABEL-15 source-coefficient lift to the connected
legal SCL-252 seed 3 instance cannot be repaired using only admissible
paired-multiplier differences plus signed row-difference corrections.
This is **not** a proof that the full degree-4 Fourier ideal identity is
impossible. Other source certificates, nullsyzygies, or correction generators
can still potentially remove the obstruction.

### Exact rank proof

1. The degree-3 canonical anti-sector has 20,464 active frequencies.
   Signed row-difference corrections reach 14,855, leaving 5,609.
2. The frozen base identity forces 483 of these 5,609 frequencies to zero.
   The projected paired-generator problem therefore has 5,126 rows.
3. Evaluate every one of the **43,485** distinct sparse nonzero paired
   signatures over the integers.
4. Modular sparse elimination modulo 65,521 establishes rank at least
   **5,119 over Q** (a nonzero modular minor lifts to nonzero determinant
   over Q).
5. Independently, an exact weighted rational union-elimination finds
   **seven** linearly independent rational left-kernel vectors; each is
   supported at a single missing frequency. Exhaustive substitution into
   all 43,485 integer signatures gives exactly zero. Consequently rank
   over Q is at most 5,126 - 7 = 5,119.

Both bounds coincide:

  `rank_Q(paired correction projection) = 5119`, `nullity_Q = 7`.

The seven isolated canonical coordinates are:

`7984, 16142, 16156, 31072, 33062, 55754, 59828`.

### Test of the frozen canonical source Krylov lift

The exact integer source Krylov recurrence of degree 556 was re-evaluated
over the integers for seed 3. The canonical lift of its coefficients was
projected onto precisely those seven coordinates, without numerical
approximations or any omission of source column products.

| Missing canonical frequency | Exact error |
|---|---|
| 7984 | zero |
| 16142 | nonzero, negative |
| 16156 | nonzero, negative |
| 31072 | nonzero, negative |
| 33062 | zero |
| 55754 | nonzero, negative |
| 59828 | nonzero, negative |

Every paired correction generator has coefficient zero on those seven
coordinates. The row-difference graph likewise does not touch them.
Thus five persistent nonzero residuals prove that this specific canonical
lifting algorithm cannot finish a degree-2 multiplier identity for seed 3.

**This does not give a rational left-null functional annihilating every
possible full degree-2 Fourier row generator.** Accordingly no degree-6
minimum or universal SOS lower bound has been proved.

### The next admissible gate

`BABEL-17`: allow arbitrary source-certificate coefficient freedom (source
nullsyzygies) and admissible unpaired lifting generators. Form the exact
seven-coordinate compatibility map. Either:

- construct a new source certificate whose projected residual annihilates
  all seven directions, and then recover complete SOS4 on seed3; or
- construct a rational full-matrix left-kernel witness whose pairing with
  the constant is nonzero, genuinely excluding degree4.

Keep the prior exact seed1 and seed2 positive gates fixed. No conclusion
about arbitrary legal SCL, polynomial-time `SolveLinearCubicXSAT`, or P vs NP.

### Machine-readable evidence

- `babel16_SEED3_EXACT_PAIRED_KERNEL.json`: exact seven sparse rational
  witnesses and matching modular rank lower bound.
- `babel16_SEED3_SOURCE_RESIDUAL.json`: all seven unrestricted integer
  errors from canonical lifted source certificate.
- `janus_babel16_seed3_exact_pair_kernel.py`: constructive exact rank solver.
- `janus_babel16_seed3_source_residual.py`: exact source Krylov recurrence
  and seven-coordinate checker.

Proof numerics are seed-local and refer to the *projected paired-transfer
subspace*, not to the global P-versus-NP proposition.
