# R5 E9 — Improving-Mapping / Persistency Source Audit

Date: 2026-09-24

Authority: SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

Strategic parent:
- `R5_E9_WITNESS_DOMINANCE_QUOTIENT_CONTRACTION_2026-09-23_v1.0`
- `R5_E9_WITNESS_DOMINANCE_EXISTENCE_COLLAPSE_AND_STRUCTURAL_TRANSFORMER_GATE_2026-09-23_v1.0`
- `R5_E9_NONLOCAL_RANK1_JOINT_CONTRACTION_PIVOT_GATE_V1`

This audit does not open a parallel carrier program. It source-binds a known persistency mechanism as a certifier inside the existing JANUS universal nonlocal-contraction engine.

## G0 — Exact frozen object

For a CNF F on Boolean variables, define the clause-violation energy

```
E_F(x) = number of clauses of F falsified by x.
```

Thus

```
SAT(F) iff min_x E_F(x) = 0.
```

A map p is improving when

```
E_F(p(x)) <= E_F(x) for every Boolean assignment x.
```

If p maps every assignment into a proper fixed subspace, for example fixes a nonempty block B to alpha,

```
p(x)_B = alpha,
```

then every zero-energy witness maps to a zero-energy witness in that subspace. Hence

```
SAT(F) iff SAT(F[B=alpha]).
```

The JANUS interest is not this implication itself. The algorithmic obligation is deterministic polynomial synthesis and certification of a nonidentity contraction map, or an exact strict contraction derived from the failure certificate, on the residual rigid core.

## G1 — Internal anti-duplication

Reviewed materially close Fundamentum artifacts:

- `R5_E9_WITNESS_DOMINANCE_QUOTIENT_CONTRACTION`;
- `R5_E9_WITNESS_DOMINANCE_EXISTENCE_COLLAPSE_AND_STRUCTURAL_TRANSFORMER_GATE`;
- `R5_E9_AUTARKY_AS_WITNESS_DOMINANCE_DONOR`;
- `R5_E9_RESOLUTION_CERTIFIED_WITNESS_DOMINANCE_BARRIER`;
- `R5_E9_ADHESION2_SPQR_EXACT_CONTRACTION_META_THEOREM`;
- `R5_B1B1C5B2B2_E8_6I_RAIL_RECURSIVE_AFFINE_INTERFACE_LIFTING_META_THEOREM`;
- `R5_E10_GLOBAL_REPLAY_STATIC_COVER_FIREWALL_AND_CANCELLATIVE_GAUGE_FRONTIER`.

Internal conclusion:

JANUS already had the exact contraction abstraction and several structural repair donors. It did not have an explicit source-bound improving-mapping / maximum-persistency / reparameterization layer. Therefore that layer is not new JANUS mathematics; it is a missing external donor for the existing witness-transformer engine.

## G2 — Canonical external names

Primary external vocabulary:

- improving mapping;
- relaxed-improving mapping;
- persistency / partial optimality;
- maximum persistency;
- pseudo-Boolean / weighted-CSP energy minimization;
- LP reparameterization / dual certificate;
- roof duality / generalized roof duality.

Important scope firewall:

The Shekhovtsov framework considered here uses node-wise label maps and their linear extensions over a chosen polyhedral relaxation. A general JANUS nonlocal repair map may depend on several coordinates jointly. Such a map is not automatically represented by a polynomial-size factor-local linear extension.

Therefore:

```
KNOWN NODE-WISE IMPROVING-MAP THEORY
!=
A UNIVERSAL CERTIFIER FOR ARBITRARY JANUS NONLOCAL MAPS.
```

## G3 — Public sources

### S1 — Shekhovtsov, CVPR 2014

Alexander Shekhovtsov,
*Maximum Persistency in Energy Minimization*,
CVPR 2014,
DOI 10.1109/CVPR.2014.152,
arXiv:1404.3653.

Source facts:

- Definition 2.1 defines p as improving iff E(p(x)) <= E(x) for all x.
- The paper explicitly states that improving mappings generalize autarkies and reduce the search space to p(X).
- It restricts the main framework to node-wise mappings and uses idempotent mappings.
- Verifying the exact improving property of a given discrete map is NP-hard in general; the paper constructs tractable relaxation-based sufficient conditions.

Classification:

```
JANUS ENERGY-IMPROVING-MAP BRIDGE
=
EXACT_EXTERNAL_COLLISION / SOURCE_BOUND.
```

### S2 — Shekhovtsov, higher-order persistency

Alexander Shekhovtsov,
*Higher Order Maximum Persistency and Comparison Theorems*,
Computer Vision and Image Understanding 143 (2016), 54–79,
DOI 10.1016/j.cviu.2015.05.002,
arXiv:1505.00571.

Source facts:

- the framework applies to partially separable discrete energies including WCSP, pseudo-Boolean optimization and 0–1 polynomial programming;
- Definition 2.3 defines Lambda-improving linear extensions;
- if the linear extension is Lambda-improving over a tractable relaxation containing the marginal polytope, the discrete map is genuinely improving;
- verification of a fixed map reduces to an LP;
- Theorem 3.3 gives an equivalent dual/reparameterized characterization;
- tightening the relaxation can only strengthen the persistency certificate;
- crucially, Theorem 3.4 shows that for BLP, finding the maximum weak improving map over all node-wise maps is polynomial for quadratic pseudo-Boolean energies but NP-hard for higher-order Boolean energies.

JANUS consequence:

```
LP / REPARAMETERIZATION CERTIFICATION OF A GIVEN ELIGIBLE MAP
=
KNOWN POLYNOMIAL DONOR.

BLP + SEARCH THE BEST WEAK NODE-WISE MAP
ON GENERAL HIGHER-ORDER BOOLEAN ENERGY
=
KNOWN NP-HARD SYNTHESIS BARRIER.
```

This prevents treating basic-LP maximum persistency as the universal discovery engine for 3CNF energy.

### S3 — Adams, Lassiter, Sherali (1998)

Warren P. Adams, Julie Bowers Lassiter, Hanif D. Sherali,
*Persistency in 0-1 Polynomial Programming*,
Mathematics of Operations Research 23(2), 359–389,
DOI 10.1287/moor.23.2.359.

This establishes earlier persistency theory for relaxations of 0–1 polynomial programs and dual-multiplier sufficient conditions.

Classification:

```
PSEUDO-BOOLEAN PERSISTENCY
=
ESTABLISHED PRIOR ART.
```

### S4 — Kolmogorov / generalized roof-duality line

Vladimir Kolmogorov,
*Generalized roof duality and bisubmodular functions*,
Discrete Applied Mathematics 160 (2012),
DOI 10.1016/j.dam.2011.10.026,
arXiv:1005.2305.

Lu–Williams and related generalized roof-duality work also provide higher-order pseudo-Boolean persistency mechanisms.

Classification:

```
ROOF-DUAL / BISUBMODULAR PERSISTENCY
=
KNOWN SPECIALIZED DONOR.
```

### S5 — Shekhovtsov, Swoboda, Savchynskyy

*Maximum Persistency via Iterative Relaxed Inference in Graphical Models*,
IEEE TPAMI 40(7), 1668–1682,
DOI 10.1109/TPAMI.2017.2730884.

This gives a polynomial iterative procedure that marks a maximal set of labels in the specified relaxation-based sense and returns a reduced residual graphical model.

Classification:

```
ITERATIVE PERSISTENCY CLOSURE
=
KNOWN DONOR / SPECIAL SETTING,
NOT A GENERAL HIGHER-ORDER SAT SOLVER.
```

### S6 — Haller, Swoboda, Savchynskyy

*Exact MAP-Inference by Confining Combinatorial Search with LP Relaxation*,
AAAI 2018,
DOI 10.1609/aaai.v32i1.12202.

The method separates an LP-tight easy region from a difficult residual region, but still invokes a combinatorial solver on the difficult region.

Classification:

```
LP-TIGHT / HARD-CORE SEPARATION
=
KNOWN DONOR.

FRACTIONAL HARD CORE
=> POLYNOMIAL EXACT CONTRACTION
=
NOT SUPPLIED.
```

## G4 — Collision matrix

| JANUS object | External object | Classification | Action |
| --- | --- | --- | --- |
| E_F(x)=# falsified clauses | pseudo-Boolean / WCSP energy | EXACT_LANGUAGE_COLLISION | Source-bind |
| E(p(x))<=E(x) | improving mapping | EXACT_COLLISION | Source-bind Shekhovtsov |
| fixed labels can be eliminated | persistency / partial optimality | EXACT_COLLISION | Source-bind |
| LP sufficient certificate for fixed p | relaxed improving mapping | EXACT_COLLISION | Reuse |
| dual/reparameterized local inequalities | improving-map reparameterization | EXACT_COLLISION | Reuse |
| iterative exhaustion of certifiable labels | maximum/iterative persistency | KNOWN_DONOR | Reuse where scope matches |
| BLP universal synthesis for higher-order Boolean weak persistency | max-wi over node-wise maps | KNOWN_NP_HARD_BARRIER | Do not use as free discovery oracle |
| arbitrary context-dependent JANUS nonlocal repair map | beyond node-wise map | SCOPED_GAP_SURVIVES | Requires polynomial local-extension theorem |
| LP/fractional failure -> exact strict JANUS contraction | no located closure | SCOPED_GAP_SURVIVES | New math may target only this bridge |

## Critical representation firewall

For a node-wise map p, the source constructs a local linear extension P acting on the marginal representation. This locality is essential to the polynomial LP/reparameterization certificate.

For a general nonlocal map

```
p_i(x) = function of many coordinates,
```

the induced action on a local factor may depend on variables outside that factor. A naive linear extension may therefore require enlarged scopes or an exponentially large global representation.

Accordingly, every JANUS use of the improving-map certifier must prove:

```
POLY_LOCAL_LINEAR_EXTENSION(p, Lambda)
```

or another independently polynomial certificate representation.

Without that theorem, the phrase

```
"verify the nonlocal map by the persistency LP"
```

is invalid.

A second firewall: the source's node-wise idempotent reduction does not imply that an arbitrary global JANUS map can be made idempotent with polynomial description or polynomially many compositions.

## Scoped gap that survives

The donor itself is known. The remaining JANUS mathematical obligation is:

```
R5_E9_PERSISTENCY_LEAN_DUAL_OBSTRUCTION_CONTRACTION_GATE_V1
```

Input:

- Boolean CNF zero-energy representation;
- JANUS rigid core after existing polynomial simplification, adhesion-2/SPQR, autarky and currently certified witness-dominance lanes;
- standard source-proved persistency lanes exhausted.

Allowed PASS:

1. polynomially synthesize a nonidentity structural map p with a polynomial-size local linear extension and a relaxed-improving/reparameterization certificate, such that contraction strictly lowers live Boolean dimension; or
2. from the LP/dual/fractional obstruction to such a map, polynomially derive another exact JANUS contraction or a normalization into an already proved polynomial terminal.

Required:

- no general SAT/UNSAT oracle;
- no exponential map enumeration;
- no hidden full marginal polytope;
- no unbounded hierarchy level without a total polynomial bound;
- exact SAT preservation and polynomial witness reconstruction;
- strict progress potential on every successful contraction.

This is a child of the existing universal nonlocal-contraction engine, not a new carrier program.

## Audit decision

```
IMPROVING-MAPPING THEORY
=
SOURCE_BOUND_REUSE

LP / REPARAMETERIZATION CERTIFIER
=
SOURCE_BOUND_REUSE

BASIC-LP UNIVERSAL HIGHER-ORDER MAP SYNTHESIS
=
BLOCKED BY KNOWN NP-HARDNESS

PERSISTENCY-LEAN FRACTIONAL/DUAL OBSTRUCTION
TO EXACT JANUS CONTRACTION
=
SCOPED_GAP_SURVIVES

DECISION
=
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside the frozen child gate above.

Scientific ceiling:

```
D1 = EMPTY
P_VS_NP = OPEN
P_EQ_NP = NOT_PROVED
```
