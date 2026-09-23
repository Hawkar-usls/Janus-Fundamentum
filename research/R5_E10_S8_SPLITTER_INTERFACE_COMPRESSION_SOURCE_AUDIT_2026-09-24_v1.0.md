# R5 E10 — S8 Splitter-Interface Compression Source Audit

Date: 2026-09-24

Authority: `SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED`

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

Strategic role:
this audit serves the Fundamentum-wide universal algorithm synthesis. It does not
open a parallel carrier program. It asks whether the new parity/matroid
representation exposes a genuinely unclosed contraction obligation after all known
matroid algorithms are reused.

## G0 — exact frozen object

Start from a cubic positive exact-one instance with square incidence matrix `A`.
Every row and every column has weight three. A polynomial 1-factorization of its
3-regular bipartite incidence graph gives, after relabeling one matching,

```
A = I + P + Q.
```

Let

```
H = A (mod 2).
```

For a Boolean vector `x`, if `Hx=1` over `GF(2)`, every row contains either
one or three selected columns. If `t` rows contain three selected columns, double
counting selected incidences gives

```
3|x| = n + 2t.
```

Therefore

```
|x| >= n/3,
```

with equality if and only if every row contains exactly one selected column.
Hence

```
Ax = 1 over the integers
iff
Hx = 1 over GF(2) and |x| = n/3.
```

Adjoin the distinguished column

```
f = 1
```

and form the binary matroid

```
M = M([H | f]).
```

With unit element lengths, a minimum-weight solution of `Hx=f` is equivalent to
a shortest circuit of `M` containing `f`, with the distinguished element
contributing one additional unit. The exact SAT target is therefore

```
shortest_f(M) = n/3 + 1.
```

The gate is NOT general shortest-f-circuit optimization. It is the lower-bound-tight
decision/search problem inherited from the cubic exact-one origin.

## G1 — internal anti-duplication

Repo-wide search at the pre-audit HEAD covered:

- `S8`, `S8 minor`, `shortest f-circuit`, `shortest circuit basis`;
- `syndrome decoding`, `coset leader`, `I+P+Q syndrome`;
- `binary matroid`, `regular matroid`, `splitter`;
- existing E8/E9 Fano, syndrome and delta-matroid artifacts.

Materially close internal objects:

1. `R5_E9_MANDATORY_PIVOT_CONDITIONING_AND_PAIR_DEFECT_SYNDROME` and
   `R5_E9_PAIR_DEFECT_SYNDROME_IMAGE_COUNTERCONTROL`.
   These concern the image of an easy NAE model set under a pair-defect map.
   They are not the present parity-check/coset-leader matroid problem.

2. `R5_B1B1C5B2B2_E8_6I_BOOLEAN_MULTISORTED_FANO_BLOCKER`.
   Its Fano plane is a Boolean multi-sorted polymorphism obstruction, not the
   binary-matroid `F7/F7*` / `S8` excluded-minor line.

3. Existing delta-matroid matching barriers.
   These concern local relation realization/exchange axioms, not shortest
   distinguished circuits in binary matroids.

Internal conclusion:

```
NO PRIOR JANUS S8 / SHORTEST-f / COSET-LEADER
UNIVERSAL CONTRACTION PROGRAM LOCATED.
```

This is a new synthesis of an existing JANUS hard core with established matroid and
coding-theory machinery, subject to the external collisions below.

## G2 — canonical external names

Primary external objects:

- syndrome decoding / minimum-weight coset representative / coset leader;
- shortest circuit containing a distinguished element `f` in a binary matroid;
- shortest circuit basis;
- binary-matroid 1/2/3-sum decomposition;
- `S8`-minor-free binary matroids;
- Splitter / Strong Splitter extension-coextension sequences;
- regular LDPC minimum-distance problems as a nearby hardness control.

The JANUS-specific residual is more precise:

```
LOWER-BOUND-TIGHT
DISTINGUISHED-f CIRCUIT
ON A BINARY MATROID ORIGINATING AS
[I+P+Q | 1],

AFTER ALL KNOWN no-S8 SUM COMPONENTS
HAVE BEEN ABSORBED.
```

## G3 — public source exhaustion

### S1 — Chapter 9, “Shortest bases of circuits in binary matroids”

CWI public source:
`https://ir.cwi.nl/pub/25496/25496.pdf`.

Source-bound facts used here:

- general shortest-`f`-circuit in a binary matroid is NP-complete;
- the shortest circuit basis problem is polynomially solvable for binary matroids
  with no `S8` minor;
- a shortest circuit basis contains, for every fixed `f`, a shortest circuit
  containing `f`;
- shortest circuit basis, shortest odd circuit and shortest-`f`-circuit are
  polynomially related in the stated no-`S8` setting;
- the no-`S8` algorithm uses binary-matroid 1/2/3-sum decomposition and
  3-connected pieces; the relevant no-`S8` pieces reduce to regular pieces and
  the exceptional finite matroids `F7`, `F7*`, and `AG(3,2)`;
- the source states that whether a binary matroid contains an `S8` minor can be
  tested in polynomial time using the decomposition/classification machinery.

JANUS consequence:

```
REGULAR MATROID
IS NOT THE SHARP KNOWN POLYNOMIAL FRONTIER.

NO-S8 BINARY MATROID
=
STRICTLY STRONGER KNOWN POLYNOMIAL LANE.
```

Therefore `F7/F7*` elimination is not the next JANUS target.

### S2 — Kingan and Lemos, Strong Splitter Theorem

S. R. Kingan; Manoel Lemos,
*Strong Splitter Theorem*,
Annals of Combinatorics 18 (2014);
arXiv:1201.4427.

For a suitable 3-connected proper minor `N` of a 3-connected matroid `M`,
Splitter theory supplies a sequence from `N` to `M` by 3-connected
single-element extensions/coextensions. The Strong Splitter theorem further
constrains the sequence: at most two consecutive extensions occur before a
coextension, except once the rank involved has reached `r(M)`; and two extensions
followed by a coextension create a triad among the new elements.

JANUS consequence:

```
S8 -> M EXTENSION/COEXTENSION SEQUENCE
=
KNOWN STRUCTURAL DONOR.

POLYNOMIAL NUMBER OF SHORTEST-f
INTERFACE STATES ALONG THAT SEQUENCE
=
NOT SUPPLIED BY THE THEOREM.
```

The rank-saturated extension-tail exception is therefore a mandatory killer
control. Strong Splitter alone does not imply constant-width state.

### S3 — Truemper, Matroid Decomposition

K. Truemper,
*Matroid Decomposition*, revised edition.

Theorem 6.4.7 gives a polynomial algorithm which, from a connected binary matroid
`M` and a 3-connected proper minor `N` on at least six elements, outputs either
a 2-separation or a 3-connected 1- or 2-element extension of an `N`-minor
(with one addition and one expansion in the 2-element case).

JANUS consequence:

there is constructive polynomial support for navigating extension structure.
However, this does NOT by itself construct the exact Strong-Splitter sequence
needed by a future shortest-`f` DP, and it supplies no polynomial signature
bound. Any JANUS algorithm must either construct the required sequence
polynomially or provide an independently certified substitute.

### S4 — Jia et al. 2026 regular-LDPC hardness control

Chenyuan Jia; Qingqing Peng; Ke Liu; Guanghui Wang; Guiying Yan,
*On the Intractability of the Minimum Distance Problem for Regular LDPC Codes*,
arXiv:2606.23161 (2026).

The source proves NP-completeness of the minimum-distance problem for regular
Tanner graphs, including the `(3,3)`-regular setting.

JANUS consequence:

```
3-REGULAR TANNER GEOMETRY ALONE
IS NOT A TRACTABILITY MECHANISM.
```

But this is a scoped barrier only. Minimum distance is the homogeneous problem

```
Hx=0, x != 0,
```

whereas the JANUS core is the affine all-ones coset

```
Hx=1
```

together with the extremal equality target `|x|=n/3`.
No exact collision with the present residual was located.

### S5 — exact lower-bound-tight / all-ones-coset searches

Searches included combinations of:

- all-ones syndrome + 3-regular / (3,3)-regular LDPC;
- coset leader + (3,3)-regular LDPC;
- `I+P+Q` + syndrome decoding;
- shortest-`f` circuit + splitter extension/coextension;
- `S8`-minor + shortest-`f` circuit + interface/dynamic programming.

No located source closed the exact lower-bound-tight problem or provided a
polynomial splitter-state propagation theorem for the present residual.

This is a research source audit, not a legal or absolute novelty certification.

## G4 — collision matrix

| JANUS object | External object | Classification | Action |
| --- | --- | --- | --- |
| minimize `|x|` subject to `Hx=1` | syndrome decoding / coset leader | EXACT_LANGUAGE_COLLISION | source-bind coding theory |
| add `f=1` and minimize dependency containing `f` | shortest-`f` circuit | EXACT_LANGUAGE_COLLISION | source-bind matroid language |
| arbitrary binary shortest-`f` circuit | known NP-complete problem | KNOWN_BARRIER_ONLY | no tractability transfer |
| regular binary matroid | known polynomial special case | SPECIAL_CASE_COLLISION | reuse, not frontier |
| binary matroid with no `S8` minor | known broader polynomial class | STRONGER_KNOWN_RESULT | absorb completely |
| 1/2/3-sum shortest-circuit composition | known decomposition machinery | KNOWN_DONOR_ONLY | reuse |
| `S8`-minor recognition / no-`S8` testing | polynomial in cited decomposition line | KNOWN_DONOR_ONLY | preprocessing |
| Strong Splitter extension/coextension sequence | structural theorem | KNOWN_DONOR_ONLY | do not infer state bound |
| rank-saturated extension tail | explicit Strong-Splitter exception | KILLER_CONTROL | must survive/falsify |
| (3,3)-regular LDPC minimum distance | homogeneous NP-hard control | KNOWN_BARRIER_ONLY | does not close affine target |
| `shortest_f=n/3+1` for `[I+P+Q|1]` | lower-bound-tight affine coset problem | SCOPED_GAP_SURVIVES | audited target |
| exact poly splitter boundary signature on surviving 3-connected S8 torso | no located closure | SCOPED_GAP_SURVIVES | new math only here |

## Representation and decomposition firewalls

### Firewall A — the cubic origin is not hereditary

The original `H=I+P+Q` representation and the counting identity
`3|x|=n+2t` apply to the full cubic-origin instance.

After arbitrary matroid deletion/contraction and 1/2/3-sum decomposition, a torso
need not itself have literal `I+P+Q` form, row/column weight three, or its own
local `n/3` lower bound.

Therefore a future algorithm must propagate exact element weights and
separator-conditioned shortest-circuit costs. It may not reapply the global cubic
counting argument independently to each torso.

### Firewall B — the S8 seed need not contain f

An `S8` minor can occur in a component/torsion route that does not literally
contain the distinguished element `f`. Its effect on a shortest circuit containing
`f` may pass through a 2/3-sum separator.

Therefore the algorithmic state is a distinguished-`f` shortest-circuit
**interface** problem, not an eight-column local gadget replacement.

### Firewall C — splitter existence is not splitter-state compression

Strong Splitter establishes constrained structural sequences. It does not prove
that all shortest-`f` interactions with the growing matroid have polynomially
many inequivalent boundary signatures.

The long extension tail allowed after rank saturation is the first mandatory
falsifier of any constant-width-state claim.

## Scoped PASS

Audit decision:

```
PASS_SCOPED_GAP_CONFIRMED
```

New JANUS mathematics is authorized only inside:

```
R5_E10_S8_SPLITTER_INTERFACE_COMPRESSION_GATE_V1
```

with the exact scope:

```
INPUT ORIGIN
=
M([H|f]),
H=I+P+Q,
f=1,
row/column weight 3 at origin.

KNOWN PREPROCESSING
=
binary 1/2/3-sum decomposition;
all no-S8 components solved/absorbed by source-bound machinery.

SURVIVOR
=
3-connected S8-containing distinguished-f shortest-circuit interface.

TARGET
=
decide/reconstruct exactly whether
shortest_f(M)=n/3+1.

NEW OBLIGATION
=
polynomial-size exact boundary signature
and polynomial update under a constructible
splitter extension/coextension route.

MANDATORY KILLER TEST
=
rank-saturated extension tail.
```

Claim ceiling:

```
NO LOCATED PUBLIC THEOREM
CLOSES THIS PRECISE RESIDUAL CLASS.

THIS IS NOT A CLAIM THAT THE CLASS
HAS NEVER BEEN STUDIED.

THIS DOES NOT CLAIM THAT S8 ITSELF
CAUSES HARDNESS.

S8 PRESENCE ONLY MARKS SURVIVAL
BEYOND THE LOCATED no-S8 POLYNOMIAL ALGORITHM.
```

Next mathematical work, after this audit passes CI, must first formalize the
smallest exact splitter-interface signature and attack the rank-saturated-tail
killer control before attempting a universal contraction theorem.
