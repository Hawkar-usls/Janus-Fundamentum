# R5 E8 6I — Uniform pp-Lift Siggers / Edge Barrier

Date: 2026-09-22

Authority: PROVED_SOURCE_BOUND_STRUCTURAL_BARRIER__NO_D1_PROMOTION__NO_SUCCESSOR_AUTHORIZATION

## 1. Purpose

The active 6I target asks for a lifted tractable carrier whose visible decoder image covers ordinary signed OR3.

A natural old mechanism is stronger than the current A3 construction:

    choose one fixed finite tractable carrier C;
    choose one fixed pp-definable lifted domain / decoder kernel;
    pp-interpret the full Boolean 3-SAT template inside C.

This artifact proves that this entire uniform pp-interpretation route is unavailable whenever the carrier polymorphisms satisfy a nontrivial Siggers or edge identity.

The result is algebraic. It does not assume P != NP.

## 2. Source facts

### S1 — full Boolean 3-SAT has only projection polymorphisms

Barto, Krokhin, Willard, Polymorphisms, and How to Use Them, Dagstuhl Follow-Ups 7 (2017), Example 33.

Open source:
https://drops.dagstuhl.de/storage/02dagstuhl-follow-ups/dfu-vol007/DFU.Vol7.15301/DFU.Vol7.15301.pdf

The source states that the Boolean 3-SAT language has no polymorphisms except projections.

Therefore:

    Pol(Gamma_3SAT) = Proj_2.

### S2 — finite pp-interpretation iff clone homomorphism

Manuel Bodirsky, Graph Homomorphisms and Universal Algebra, arXiv:2602.14243, Corollary 8.45.

Open source:
https://arxiv.org/abs/2602.14243

For finite relational structures A,B:

    A pp-interpretable in B
    iff
    there exists a clone homomorphism Pol(B) -> Pol(A).

### S3 — few subpowers iff edge polymorphism

Bulín and Kompatscher, Polynomial definability in constraint languages with few subpowers, arXiv:2305.01984v3, Theorem 8.

Open source:
https://arxiv.org/abs/2305.01984

The source states:

    few subpowers
    iff
    some k-edge polymorphism exists.

### S4 — Siggers positive control

The finite-domain CSP dichotomy can be stated via a Siggers polymorphism on the tractable side; see Bulatov/Zhuk as summarized in Three Fundamental Questions in Modern Infinite-Domain Constraint Satisfaction, MFCS 2025, Theorem 1.

Open source:
https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.MFCS.2025.83

This source is used only as a positive control for the Siggers identity. The barrier below applies whenever the candidate carrier is independently known to possess such a Siggers polymorphism.

## 3. Lemma — projection clone has no edge operation

Let p_i^(k+1) be any projection of arity k+1, with k>=2.

A k-edge operation must satisfy identities including:

    e(y,y,x,x,...,x)=x
    e(y,x,y,x,...,x)=x

and the corresponding positions with the single y.

For every projection coordinate i, at least one edge identity places y in coordinate i while requiring output x.

Therefore:

    Proj_2 contains no k-edge operation for any k>=2.

## 4. Lemma — projection clone has no Siggers operation

Use the six-ary Siggers identity:

    s(x,y,z,x,y,z) = s(y,z,x,z,x,y).

For the six projections:

    coord 1: x != y
    coord 2: y != z
    coord 3: z != x
    coord 4: x != z
    coord 5: y != x
    coord 6: z != y.

Hence no projection satisfies the identity.

Therefore:

    Proj_2 contains no Siggers operation.

## 5. Barrier theorem

### R5_E8_6I_UNIFORM_PP_LIFT_SIGGERS_EDGE_BARRIER_V1

Let C be a finite relational structure.

If Pol(C) contains either:

    A. a k-edge polymorphism for some k>=2, or
    B. a Siggers polymorphism,

then the full signed Boolean 3-SAT template Gamma_3SAT has no primitive-positive interpretation in C.

### Proof

Assume for contradiction that Gamma_3SAT is pp-interpretable in C.

By source fact S2 there exists a clone homomorphism:

    xi: Pol(C) -> Pol(Gamma_3SAT).

By S1:

    Pol(Gamma_3SAT) = Proj_2.

A clone homomorphism preserves arities, projections, composition, and therefore all equational identities satisfied by operations.

If Pol(C) contains an edge operation, its image under xi must be an edge operation in Proj_2, contradicting Section 3.

If Pol(C) contains a Siggers operation, its image must be a Siggers operation in Proj_2, contradicting Section 4.

Therefore no such pp-interpretation exists.

QED.

## 6. Few-subpowers corollary

By S3:

    FEW SUBPOWERS => EDGE POLYMORPHISM.

Therefore:

    NO FIXED FINITE
    FEW-SUBPOWERS / EDGE CARRIER
    CAN PP-INTERPRET
    THE FULL 3-SAT TEMPLATE.

This closes the uniform route consisting of one fixed edge algebra, one fixed pp-definable domain, one fixed pp-definable decoder kernel, and exact pp-definitions of every signed OR3 relation.

## 7. What this does NOT rule out

The theorem does not apply merely because a Boolean relation is the set-theoretic decoder image of a subalgebra.

A JANUS decoder may fail to be an algebra homomorphism, a congruence quotient, or a pp-definable interpretation map with pp-definable kernel.

Therefore the theorem does not falsify:

    A. variable-specific decoder selection;
    B. instance-specific induced-algebra prototypes;
    C. local exact decoder images whose decoder kernels are not pp-definable;
    D. representation-changing preprocessing before the lifted stage;
    E. a non-pp compositional interface with an independently proved polynomial lifecycle;
    F. finite families in which the selected visible algebra/decoder depends on a polynomially discoverable certificate.

The A3 SBM positive control belongs to this broader, non-uniform interface setting.

## 8. Consequence for the active 6I search

The old target wording

    FIND A FIXED TRACTABLE VISIBLE LIFTED CARRIER THAT DIRECTLY REALIZES OR3

is too broad.

The remaining admissible form is narrower:

    INSTANCE-SPECIFIC VISIBLE INTERFACE CERTIFICATE

whose discovery is polynomial, whose local exact lifts cover every clause, whose selected lifted relations are solved polynomially, but whose decoder layer is NOT a fixed pp-interpretation of full 3-SAT into one Taylor/edge carrier.

Thus the next bridge must exploit the distinction between uniform pp interpretation and polynomially discoverable instance-specific decoder/lift structure.

## 9. Claim ceiling

    UNIFORM FIXED PP-LIFT INTO EDGE/FEW-SUBPOWERS CARRIER
    = THEOREM-LEVEL BLOCKED

    UNIFORM FIXED PP-LIFT INTO A CARRIER WITH SIGGERS POLYMORPHISM
    = THEOREM-LEVEL BLOCKED

    INSTANCE-SPECIFIC NON-PP INTERFACE
    = OPEN

    A3 SBM DIRECT DECODER-IMAGE ARCHITECTURE
    = STRICT-SUBCLASS POSITIVE CONTROL

    UNIVERSAL 3-SAT COVERAGE
    = OPEN

    SUCCESSOR_ALGORITHM
    = LOCKED

    D1
    = EMPTY

    P_VS_NP
    = OPEN
