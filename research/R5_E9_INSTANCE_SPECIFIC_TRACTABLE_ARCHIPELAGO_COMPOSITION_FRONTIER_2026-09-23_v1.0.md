# R5 E9 — Instance-Specific Tractable Archipelago Composition

## Mission

The global objective remains an exact universal polynomial-time SAT algorithm. The residual-small cube-term effective-pp candidate is treated as one new tractable carrier/compiler, not as the endpoint of the program.

## Why the next frontier cannot be “one bigger fixed algebra”

A fixed few-subpowers language has an edge polymorphism. Primitive-positive definability preserves polymorphisms. By contrast, the standard Boolean 3SAT language has only projection polymorphisms. Therefore arbitrary 3SAT cannot be absorbed by pp/gadget compilation into one fixed edge-term language while preserving that tractable polymorphism.

This is an unconditional algebraic routing constraint, not a complexity assumption.

Hence a universal route, if it exists, must be instance-specific: different regions/states of one instance may need different tractable carriers, with an exact polynomial interaction law between them.

## What the literature already gives

### Heterogeneous backdoors

Different assignments to a backdoor may place the residual instance into different tractable classes. This is strictly more flexible than committing to one homogeneous base class. The known algorithms are parameterized: they gain tractability when the backdoor parameter is small, but the assignment dependence is still exponential in an unbounded parameter.

### Scattered classes / archipelagos

Connected components may belong to different tractable languages and can then be solved componentwise. This is the cleanest existing model of “many islands of tractability.” Again, known general algorithms require a bounded/detectable backdoor or already separated components.

### Backdoor depth

Depth can be much smaller than size and parallelizes branching across components. It is a better donor than plain backdoor size, but known guarantees are FPT/bounded-depth guarantees, not an all-instance polynomial theorem.

### Few-subpowers carrier

A fixed edge-term language has compact subpower representations and polynomial CSP algorithms. The E8-6I candidate may add a direct polynomial generators-to-short-pp compiler for the residual-small cube-term region. This expands the carrier library but does not remove the heterogeneous composition problem.

## The actual missing object

For arbitrary input F, seek an instance-specific invariant I(F) that returns

1. polynomially many tractable carrier pieces;
2. polynomial-size exact summaries of their interactions;
3. polynomial exact update under every needed projection/restriction;
4. polynomial global consistency and witness reconstruction.

The critical point is item 2. Existing backdoor machinery pays for cross-class interactions by assignments to a parameter. A universal polynomial algorithm needs an interaction certificate whose total size is polynomial even when the natural separator/backdoor is large.

## Frozen gate

R5_E9_INSTANCE_SPECIFIC_TRACTABLE_ARCHIPELAGO_POLY_INTERACTION_CERTIFICATE_V1

Do not ask “which tractable class contains arbitrary 3SAT?” That is blocked for fixed edge-term carriers.

Ask instead:

> Can arbitrary 3SAT be decomposed, in polynomial time, into heterogeneous tractable islands whose **exact interaction relation itself has a polynomial compositional representation**, so that no enumeration over an unbounded backdoor/interface is required?

## Admission requirements

Any proposed positive mechanism must simultaneously prove:

- construction/recognition poly(L);
- total carrier state poly(L);
- total interaction state poly(L);
- exact solve poly(L);
- exact projection/update poly(L);
- exact reconstruction/verification poly(L);
- no semantic/SAT oracle;
- no bounded-parameter promotion;
- no hidden exponential interface.

The existing E8-6I theorem candidate is now a carrier in this portfolio while external review proceeds in parallel.

D1 = EMPTY.  
P_VS_NP = OPEN.
