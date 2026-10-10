# Direct Universal Solver Attack: Exact Positive Coefficient / SUPPORT_c Extraction

Date: 2026-10-10

**Goal:** deterministic n^{O(1)} SolveLinearCubicXSAT for every square,
cubic, linear, positive Exact-One instance with proved correctness,
completeness, and **total bit-complexity**.

**Status:** ATTEMPTED; GLOBAL EXTRACTION LEMMA NOT PROVED.
P vs NP = OPEN. No universal polynomial algorithm is claimed.

This is a proof audit of a *universal algorithmic candidate*, not an
additional easy-instance terminal or an asymptotic benchmark family.
Predecessors: E118 NP-hardness gadget, E79 nonuniform matchgate firewall,
one-check SUPPORT_c, E123/E127, and SC23 char-2/3 cancellation controls.

## 1. A single exact expression for every instance

Let A be any n x n zero-one incidence matrix, each row and column of
weight 3 and no repeated pair of incidences. Put

    m_j(t) = product_{i:A[i,j]=1} t_i,
    P_A(t) = product_{j=1}^n (1 + m_j(t)).

The coefficient

    Z(A) = [t_1 t_2 ... t_n] P_A(t)

is precisely the **nonnegative integer number of Exact-One witnesses**.
Indeed the chosen factors correspond bijectively to subsets of columns,
and the exponent of t_i is exactly the number of chosen columns hitting
check i. The all-ones exponent exists iff every check is hit once.

For each column j incident with check c, the number of extensions
selecting that port is exactly

    N_(c,j)(A) =
      [t_1 ... t_n] m_j(t) * product_{v != j} (1 + m_v(t)).

The desired three-bit mask is therefore

    SUPPORT_c(j) = [N_(c,j)(A) > 0].

This proves soundness and completeness of the **identity** for
arbitrary n. It does NOT give a polynomial extraction algorithm.

## 2. Global candidate: coefficients modulo enough primes + exact CRT

Every coefficient N_(c,j) and Z(A) lies in [0,2^n].
Choose n+1 distinct primes (each at least 2). Their product exceeds 2^n.
If one had a deterministic algorithm computing the specified coefficient
of P_A modulo *each* such prime in polynomial bit-time, the ordinary
Chinese Remainder Theorem would reconstruct the exact nonnegative
integer coefficient in polynomial time.

Decision: Z(A)>0 iff SAT.
Witness: for each remaining variable, use a pinned version of the same
coefficient formula, choose any positive extension and continue. Pins
simply replace factors (1+m_j) with 1 or m_j; the extraction procedure
would need to handle these factor substitutions as well. It is sufficient
to reconstruct each count under polynomially many such calls.

**Missing theorem, exactly:**

    UNIVERSAL_MODULAR_COEFFICIENT_EXTRACTION

    Compute [t_1 ... t_n] of a product of factors (1+m_j)
    and pinned variants, modulo any polynomial-bit prime p,
    for every square+cubic+linear A,
    in deterministic poly(n,log p) *bit* operations.

The input is a linear-size product circuit, but extracting a multivariate
coefficient from that circuit is the difficult part. A circuit for P_A
does not imply a circuit for its target coefficient; explicitly reducing
modulo (t_1^2,...,t_n^2) can maintain 2^n independent subset monomials.
Similarly, binary mixed differentiation or a 2^n-point Fourier inversion
does not yield a polynomial algorithm. A huge one-integer Kronecker
encoding hides exponential **bit length**. We have no proved
low-rank factorization, cancellation-free determinant, or global
compression replacing these costs.

This missing theorem is at least as difficult as the NP-complete
Exact-One decision problem (by E118): computing the coefficient, even
modulo sufficiently many small primes, would give a deterministic
polynomial exact decision and witness procedure. We do NOT infer
that it is impossible; proving it would be a breakthrough.

## 3. General E118 solution-count amplification theorem

E118 splits the three occurrences of each source variable into three
ports and attaches the proven 9-clause EQUAL3 gadget. That gadget
requires port equality and has precisely

    000: two Boolean internal extensions,
    111: one Boolean internal extension.

For a cubic source with n variables and n Exact-One checks, every
source witness has precisely n/3 true variables and f=2n/3 false
variables. Gadgets are internally disjoint. Therefore **every** source
witness extends to exactly 2^f target witnesses, and conversely every
target witness projects to exactly one source witness:

    Z(target) = 2^(2n/3) * Z(source).

The target is square+cubic+linear (E118); this is a general exact
multiplicity identity, not a finite-instance extrapolation.

Now fix ANY target variable j. It belongs to one source-variable
gadget: either as a port, or as one of its seven internal variables.
For a fixed source solution, requiring target j=1 either

* excludes all extensions;
* leaves all 2^f extensions (true gadget or both choices agree); or
* selects one of the two extensions of a false gadget, leaving 2^(f-1).

Thus, for **every target port j**,

    2^(f-1) divides N_(c,j)(target).

Since any satisfiable cubic source has n>=3 and f>=2, **every
one-check extension count is even**. Consequently, a characteristic-2
nonzero-coefficient test returns an empty support mask even when
the target is SAT. This holds for an infinite family obtained from
SAT cubic sources; no linearity of the source is required.

This formalizes and generalizes the finite SC23 parity-cancellation
phenomenon. It refutes only naive fixed-characteristic, unweighted
ordinary counting as a Boolean support oracle; it does not refute
an isolation construction, CRT with an actual coefficient oracle,
or any other noncancelling representation.

## 4. Exact executable reproduction (independent target checks)

    python experiments/r5_universal_support_coefficient_extraction_attack.py

The checker imports canonical E118 gadget definitions and constructs two
SAT source cases with n=3 and n=6. It enumerates all internal
extensions, verifies the transformed 30- and 60-variable
square+cubic+linear Exact-One constraints over the integers, and checks
all one-check port counts:

    source n=3, target N=30:
      3 source witnesses, 12 target witnesses,
      exactly 4 per port at each of all 30 checks.

    source n=6, target N=60:
      9 source witnesses, 144 target witnesses,
      exactly 48 per port at each of all 60 checks.

Every target check has genuine SUPPORT=111 but mod-2 count mask=000.
The general amplification theorem is symbolic, while these two cases
are finite replay controls.

## 5. Scientific boundary / unsolved polynomial-time obligation

We did not produce a universal polynomial algorithm. This attempt
provides an **exact** global counting expression and a correct
**conditional** CRT reduction, but the polynomial-time extraction
step—the very NP-hard content of the problem—remains unproved.

Neither the number of ports (three), nor the size of the product
circuit (O(n)), nor exact CRT, nor finite successful runs proves
polynomial **total** complexity.

    COEFFICIENT_IDENTITY_FOR_ALL_INPUTS = PROVED.
    E118_MULTIPLICITY_2^(2n/3) = PROVED.
    FIXED_CHARACTERISTIC_2_ORDINARY_COUNT_SUPPORT = REFUTED.
    POLYNOMIAL_GLOBAL_MODULAR_EXTRACTION = OPEN.
    DETERMINISTIC_GLOBAL_SYMBOLIC_SUPPORT = OPEN.
    UNIVERSAL_SOLVER_SOUND_COMPLETE_POLY = NOT_CONSTRUCTED.
    P_VS_NP = OPEN.

A valid successor would supply the missing extractor with rigorous
gate/bit-size and branch accounting **for all inputs**, or an entirely
different general-purpose constructive theorem, not another finite
counterexample alone.
