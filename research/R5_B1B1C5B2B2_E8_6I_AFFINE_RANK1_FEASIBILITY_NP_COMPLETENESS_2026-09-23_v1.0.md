# R5 E8 6I — Affine Rank-One Feasibility NP-Completeness

Date: 2026-09-23

Authority: DERIVED_COMPLEXITY_CLASSIFICATION__NO_P_NE_NP_CLAIM__NO_D1_PROMOTION

Parent: R5_E8_6I_SPARSE_BOOLEAN_RANK1_COMPLETION_GATE_V1

## Problem

Input: an affine subspace L of symmetric matrices over F2, specified by linear equations, together with the constraint Z_00=1.

Question: does L contain a matrix of rank exactly one?

Call this problem AFFINE-SYMMETRIC-RANK1-F2.

## Membership in NP

A witness is a Boolean vector w with w_0=1. Construct Z=ww^T and verify all input linear equations in polynomial time.

Equivalently, a candidate matrix Z can be checked for symmetry, the affine equations, Z_00=1, and rank one by Gaussian elimination.

Hence AFFINE-SYMMETRIC-RANK1-F2 is in NP.

## NP-hardness

The proved JANUS three-sheet quadratic/rank-one normal form gives a polynomial reduction from arbitrary signed 3CNF F to an affine matrix system L_F such that

    F is satisfiable
    iff
    L_F contains a symmetric rank-one Z with Z_00=1.

The construction has polynomial size (O(N^2) under full moment materialization) and witness reconstruction is polynomial.

Since 3SAT is NP-complete, AFFINE-SYMMETRIC-RANK1-F2 is NP-hard.

Therefore:

    AFFINE-SYMMETRIC-RANK1-F2 is NP-complete.

## Consequence for the current search

The target rank being the fixed constant one is not, by itself, a tractability condition for affine matrix-space intersection over F2.

Any polynomial solver for the unrestricted problem would immediately give a polynomial algorithm for 3SAT.

This does not show that no such solver exists; it shows only that it would already resolve P versus NP.

Hence a donor theorem is useful to JANUS only if it exploits a further structural property proved for every generated L_F.

## Ceiling

    GENERIC FIXED-RANK-ONE AFFINE FEASIBILITY = NP-COMPLETE
    JANUS-SPECIFIC STRICT SUBSTRUCTURE = OPEN
    D1 = EMPTY
    P_VS_NP = OPEN
