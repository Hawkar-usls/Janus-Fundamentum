# R5 E9 — Monotone Escape-Closure Repair Calculus

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_REPAIR_CALCULUS__POLY_PROPAGATION__SYNTHESIS_OPEN__NO_D1_PROMOTION

Parent: R5_E9_SYMBOLIC_NONLOCAL_DESCENT_TRANSFORMER_GATE_V1

Checker: experiments/r5_e9_nae_monotone_escape_closure_checker.py

## 1. Local model-relative geometry

Fix a positive NAE instance F and one satisfying assignment y.
For each hyperedge e={a,b,c}, exactly one vertex is the minority value under y and the other two are majority vertices.

Write:

m_e = minority vertex
M_e = {u_e,v_e} = majority vertices.

For a flip set S, the repaired assignment is y XOR 1_S.

A direct case check gives:

the repaired edge is monochromatic iff

S intersect e = {m_e}

or

S intersect e = M_e.

These are the only two forbidden local mask patterns.

## 2. Escape selector

For each edge choose one designated escape majority

sigma(e) in M_e.

Given a pivot p, initialize

S_0={p}.

Repeatedly apply the monotone closure rules:

Rule E1:
if m_e is in S, add sigma(e) to S.

Rule E2:
if both vertices of M_e are in S, add m_e to S.

No vertex is ever removed from S.

## 3. Termination theorem

Every nontrivial closure step adds at least one previously absent variable.

Therefore the process terminates after at most |V| additions.

A simple well-founded process rank is

rho_process(S)=|V|-|S|.

This strictly decreases on every propagation step.

So the earlier two-cycle of toggle-based greedy repair is eliminated by construction.

## 4. Soundness theorem

Let S* be the fixed point of the escape closure.

For any edge e:

- if S* intersect e were {m_e}, Rule E1 would still be enabled;
- if S* intersect e were M_e, Rule E2 would still be enabled.

Hence neither forbidden mask pattern occurs.

Therefore y XOR 1_{S*} satisfies every NAE edge.

Since p belongs to S* from initialization, the endpoint flips the pivot.

Thus every supplied escape selector defines a deterministic polynomial nonlocal repair action.

## 5. Protected variables

Let A be a set of already canonicalized/protected variables that are not allowed to flip.

If the computed fixed point satisfies

S* intersect A = emptyset,

then the repair action:

- flips the pivot;
- preserves every protected variable;
- preserves every NAE constraint.

This is an exact ranked-repair certificate.

Verification is polynomial: recompute edge roles, closure, and the final NAE conditions.

## 6. Completeness of escape selectors

### Theorem MEC-1

For fixed (F,y,p,A), the following are equivalent:

(i) there exists a valid repair mask W such that p in W, W intersect A is empty, and y XOR 1_W models F;

(ii) there exists an escape selector sigma whose monotone closure S*(sigma,p) avoids A.

### Proof: (ii) => (i)

Soundness above gives that S* is a valid repair mask; it contains p and, by assumption, avoids A.

### Proof: (i) => (ii)

Let W be a valid repair mask.

For every edge with m_e in W, validity forbids W intersect e={m_e}.
Therefore at least one majority vertex in M_e also belongs to W.
Choose sigma(e) to be such a majority.

For edges with m_e not in W choose either majority arbitrarily.

Now run the closure from {p}.
Inductively S is always a subset of W:

- E1 adds sigma(e), which was chosen inside W whenever its premise m_e in S subset W holds;
- E2 can fire only when both majority vertices lie in S subset W; validity of W forbids the pattern M_e without m_e, so m_e lies in W.

Hence the fixed point S* is a subset of W.

Since W avoids A, S* avoids A.

QED.

## 7. Exact localization of the missing algorithm

The propagation problem is now solved:

- termination is linear in the number of newly added vertices;
- every endpoint is a genuine model;
- certificates are polynomial;
- the earlier local toggle cycle cannot occur.

But MEC-1 also gives a firewall:

finding an anchor-avoiding escape selector is equivalent to finding an anchor-avoiding repair mask.

Combined with the repair-mask self-similarity theorem, unrestricted selector synthesis is not a new compressed problem: it is another presentation of the remaining model-search task.

Therefore the next algorithm cannot invoke a generic search over all escape selectors.

## 8. Structural subcases

The calculus is still useful as a proof-carrying donor whenever sigma is synthesized by an independently polynomial structural theorem.

Examples of admissible future subclasses:

- acyclic/join-tree repair regions;
- deterministic implication regions where each E1 edge has a forced safe escape;
- bounded-interface components handled by an already-proved polynomial solver;
- algebraically generated selector patterns with a direct construction theorem.

Each such theorem immediately yields a terminating nonlocal repair action through MEC-1.

## 9. New active gate

Freeze:

R5_E9_ESCAPE_SELECTOR_STRUCTURAL_SYNTHESIS_GATE_V1

Input:

a translation-rigid WDR NAE survivor, canonical protected set A, and candidate pivot p.

Target:

deterministically synthesize, from structural information only, an escape selector sigma whose monotone closure avoids A, or prove that the instance belongs to an already solved terminal class.

Forbidden:

- brute-force search over 2^{|E|} selectors;
- solving the model-relative repair-mask CSP as a subroutine;
- SAT/reconfiguration oracle;
- endpoint search disguised as selector synthesis.

## 10. Ceiling

NAIVE TOGGLE PROPAGATION = CYCLES
MONOTONE ESCAPE PROPAGATION = TERMINATING
ESCAPE-CLOSURE SOUNDNESS = PASS
ESCAPE-SELECTOR COMPLETENESS = PASS
POLY VERIFICATION = PASS
UNIVERSAL POLY SELECTOR SYNTHESIS = OPEN
D1 = EMPTY
P_VS_NP = OPEN
