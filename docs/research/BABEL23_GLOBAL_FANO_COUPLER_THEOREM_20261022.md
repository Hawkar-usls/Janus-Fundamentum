# BABEL-23C — connected cubic-linear Fano coupler: a GLOBAL all-n UNSAT control

**2026-10-22. Research diagnostic, stacked on BABEL-22/23.** This note introduces a deterministic infinite family with no one-block Fano-leaf obstruction, where UNSAT follows from a new *global counting identity*, not a generic SAT complexity theorem.

## Construction for every integer m>=3

Let G_m be the 3-regular, connected, bipartite, properly 3-edge-colored graph on 2m block vertices: left i in {0,...,m-1}, right m+(i+s mod m), for each s in {0,1,2}; the edge has color s. Distinct colors are disjoint incident edges and for m>=3 all edges are distinct.

At each block put an independent Fano7 incidence gadget with indexed rows

    r0=(0,1,3)
    r1=(1,2,4)
    r2=(2,3,5)
    r3=(3,4,6)
    r4=(0,4,5)
    r5=(1,5,6)
    r6=(0,2,6).

For edge color c, use (row,removed variable) pairs

    c0 -> (r0, local 0)
    c1 -> (r1, local 2)
    c2 -> (r5, local 5).

On each edge (u,v,c), swap the selected variable in these two rows. All remaining Fano row slots are unchanged. There are n=14m Boolean variables and n=14m rows. All variables have degree3, all rows size3, distinct rows intersect in at most one variable, and the incidence graph is connected. Formal verification for each frozen m is in the exact independent script; the all-n property follows from the perfect color matchings, absence of repeated edges, distinct exchanged variables in each block, and the Fano incidence relations.

## All-n theorem: the resulting SCL input is UNSAT

Suppose there were a Boolean Exact-One solution. For each block B, write its local variables x0,...,x6. The four untouched rows are r2,r3,r4,r6:

    x2+x3+x5 =1
    x3+x4+x6 =1
    x0+x4+x5 =1
    x0+x2+x6 =1.

Summing gives 2(x0+x2+x3+x4+x5+x6)=4, hence the six selected locals sum2. The second equation gives

    x3+x4+x6=1, and consequently x0+x2+x5=1.            (A)

The three edited rows at this block take the form

    x1+x3+y0=1
    x1+x4+y1=1
    x1+x6+y2=1,

where each y_c is a Boolean variable imported along the unique color-c edge from another block's exported variable {x0,x2,x5}. Sum these rows and use (A) to obtain

    3*x1 + (y0+y1+y2)=2.                                  (B)

With Boolean variables the second term is a nonnegative integer, and x1 is 0 or1, so (B) forces x1=0 and **y0+y1+y2=2** in EVERY block.

Across all 2m blocks, the total number of imported 1-bits is exactly the total number of exported 1-bits, because every edge only exchanges one variable at each end. By (A), each block exports EXACTLY ONE 1-bit, yielding total 2m. By (B), each block imports EXACTLY TWO 1-bits, yielding 4m. This is impossible for m>0.

Thus the constructed F is UNSAT for **every m>=3**, with a proof of constant local reasoning plus one globally summed invariant. No enumeration of its 2^d parity words is required.

### Why this is not BABEL-22's trivial leaf family

No block retains six unchanged Fano rows; only **four** of seven are untouched. The block admits a fully local Exact-One completion when imported values are considered as *independent* ports: choose x0=x3=1, all other local variables0 and (y0,y1,y2)=(0,1,1). All seven local modified+unmodified row equations then hold. The obstruction appears only when the ports are cross-coupled globally with literal preservation.

Hence this supplies a legitimate **global obstruction** control instead of the terminal one- or two-row-edited Fano artefact. It remains a **simple global counting contradiction** and must not be described as an asymptotically hard SAT family.

For the connected frozen instances m=3,6,9 the GF2 nullities observed by exact row-reduction are d=10,19,28, respectively (not claimed as a proved all-n formula). Thus m=9 has 2^28 parity states, but the algebraic counting proof remains O(m).

## Compatibility with BABEL-22G

Exploratory iterative double-precision least-squares diagnostics on m=3,...,7 gave small numerical degree-1 Fourier residuals. They are **NOT exact certificates** and make no scientific claim of universal degree1 sufficiency. Establishing an *exact symbolic, uniform degree1 Fourier identity* for this family is an admissible separate target. A finite floating point residual is never a substitute.

The all-n counting obstruction of THIS family does not establish an all-n degree bound for arbitrary UNSAT SCL. The new family cannot be promoted to a general P-time SCL algorithm.

### Programmatic replay
\`experiments/babel23/global_fano_coupler.py\`: independent standard-library constructor/validator, exact local-port control and exact GF2 parity rank; full exhaustive parity-state SAT count on m=3 and m=6 (m=9 is intentionally NOT enumerated; UNSAT there is symbolic). No random or modular-only evidence.

\`\`\`
BABEL23C_INFINITE_FAMILY_LEGAL = PROVED
BABEL23C_ALL_N_GLOBAL_UNSAT = PROVED
BABEL23C_LOCAL_PORT_FEASIBILITY = PROVED
BABEL23C_UNIFORM_DEGREE1_FOURIER_TRANSFER = OPEN
UNIVERSAL_DEGREE2_COMPLETENESS = OPEN
P_VS_NP = OPEN
\`\`\`
