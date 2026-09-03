# JANUS TRUMP R47O — Universal Constant Certified Macro-Depth Target

Date: 2026-09-03

Status: **OPEN THEOREM TARGET**

Define `d(F)` for a genuine reachable residual fixpoint `F` as the least number of exact-DP layers in a proof-carrying macro that, with certified normalization closure after every layer, reaches either an independently verified semantic terminal or a final canonical state strictly below `F` in frozen CLV order.

Internal layers are allowed to be non-descending. Only the final macro state must terminate or descend relative to the macro input.

R47K/R47L give a sealed witness with `d(F)=2`: its full depth-1 scan has zero accepted pivots, while ordered pair `(11,20)` is independently replayed and ends at `[76,209,20] < [77,206,22]`.

The precise universal route is:

> There exists one fixed integer `K`, independent of input length and instance, such that every reachable genuine residual fixpoint satisfies `d(F) <= K`.

If such a fixed `K` were proved for the frozen grammar, exhaustive canonical search through all sequences of length at most `K` would remain polynomial: the sequence count is `O(V^K)`, the coarse explicit-DP representation envelope is `O(C^(2^K))`, normalization closure is polynomial per layer, and the number of certificate compositions is fixed.

This is why fixed depth is mathematically different from “keep adding layers until something works.” R47N already forbids the latter as a polynomiality argument without a stronger representation bound.

## Required proof

A valid R47O proof must establish all of the following simultaneously:

1. one fixed `K` covers **every reachable residual**, not a finite corpus;
2. reachability carries no hidden structural promise inserted by the proof;
3. every composed macro preserves exact SAT semantics and reconstructs SAT witnesses or verifies UNSAT terminals independently;
4. all intermediate construction and verification costs have one input-independent polynomial exponent determined by the fixed `K`;
5. deterministic discovery uses no oracle, advice, truth label, or unbounded search.

## Falsification route

Reachable witnesses with `d(F)>1`, `d(F)>2`, ... are valid lower bounds on any proposed constant. A finite sequence of such witnesses does not refute existence of a larger constant. An explicit family with `d(F_n)` provably unbounded would refute this constant-depth route and force the representation/compression route instead.

## Current firewall

`K=2` is not proved. Existence of any universal constant `K` is not proved. O4 remains open. `SAT_IN_P`, `P=NP`, and `P!=NP` are not proved; `P_VS_NP=OPEN`; `TRUMP_finished=false`.
