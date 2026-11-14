# JANUS PHOSPHOR-01: PLA GLOW as passive analog memory (not a SAT oracle)

Date: 2026-10-28
State: PREREGISTERED CONTROL / SIMULATION ONLY / NO HARDWARE DATA
Parent lane: FARADAY–RAMANUJAN–EXACTONE Draft PR #569.
No changes to A3/C023/R5 theorem authority.

## Verified scientific basis

Persistent photoluminescence is optical charge-carrier excitation, trapping
and delayed recombination. In SrAl2O4 doped with Eu2+ and Dy3+, the
activator and defect/trap populations are studied experimentally, but the
precise trapping mechanism is not unique or fully settled. Commercial
"glow PLA" does not necessarily contain that particular chemical formulation
unless the product manufacturer confirms the additive.

Photoluminescent charging by a UV/visible lamp is NOT Faraday induction;
Faraday's electromagnetic induction involves an emf from a changing
magnetic flux. Luminescence is not instantaneous nonlocal field optimization.
The optical readout is an emission signal, not a verified SAT witness.
A freely evolving passive material does not know arbitrary Exact-One clauses.

The Ramanujan theta/mock-theta relationship is currently ONLY a proposed
mathematical comparison. The physical crystal lattice is not the theta
series, and its excitation dynamics do not implement a modular-form
transformation without a separately specified physical/algorithmic map.

Sources:
- D. Van der Heggen et al., "Persistent Luminescence in Strontium
  Aluminate: A Roadmap to a Brighter Future" (2022):
  https://doi.org/10.1002/adfm.202208809
- P. F. Smet et al., "Persistent Luminescence in Eu2+-Doped Compounds:
  A Review" (2010): https://pmc.ncbi.nlm.nih.gov/articles/PMC5445854/
- Bambu Lab, "PLA Glow" (abrasion/nozzle/AMS compatibility):
  https://bambulab-us.myshopify.com/products/pla-glow

## A bounded, falsifiable idealized model

For local site i, with incident optical exposure u_i, represent independent
excitation traps as three fading populations with rates lambda_j > 0 and
weights w_j >= 0, sum_j w_j=1:

    N_ij(0) = w_j u_i
    N_ij(t) = N_ij(0) exp(-lambda_j t)
    I_i(t)  = sum_j lambda_j N_ij(t)

This is an illustrative *linear first-order null model*, not a physical fit,
and assumes no interactions among sites and no backreaction/optical
reabsorption. Coefficients are illustrative, not empirical estimates.

Core falsification control: n=12 circulant square-cubic-linear Exact-One
(0,1,3) is UNSAT, whereas (0,1,5) has three witnesses. Both receive the
same uniform optical pump. In this independent-trap model they produce
the exact same optical afterglow for all t. Consequently neither prompt
brightness nor the full afterglow curve implements an Exact-One verifier.

A second control illuminates the first six versus the last six sites.
A spatial camera can observe their distinct locations, so there is
spatially addressed fading *memory*. Yet an integrating single detector
produces the same curve for both because total dose is identical.

This is a negative result *only for the stated non-interacting trap model*.
It is NOT a no-go theorem for all photonic, coupled nonlinear, or quantum
computing.

## Specific hardware protocol (not yet performed)

Objective: measure repeatability, dynamic range, decay constants, spatial
cross-talk, and distinguishability of 12 optically addressed cells.

- Printer: Bambu Lab A1. Prepare a 3x4 array of 12 identical 10x10x2 mm
  cells with spacing; compare equal total volume/thickness tiles rather
  than changing the phosphor dosage unpredictably. Print matched non-glow
  PLA controls and at least three repeated tiles per print orientation.
- Material: record exact brand, color, declared additive, batch, profile,
  mass and print orientation. Confirm hardened 0.4/0.6 mm nozzle before
  extended glow printing because glow filler is abrasive. Bambu Lab's
  PLA Glow is not recommended for AMS lite and not for 0.2 mm nozzles.
- Optical pump: use a fixed-position LED light source of known wavelength,
  fixed duration and fixed distance; prefer a shielded 395 nm source
  or appropriate eye/skin protection. Never look directly into UV LEDs.
  Measure and record ambient/plate temperature, since trap release is
  temperature dependent. Do not use strong magnetic or high-voltage
  pulses, high-power lasers, or uncontrolled heating.
- Readout: fixed-position camera in a dark enclosure with locked exposure,
  ISO, focus and white balance; photograph before excitation and at
  t = 0,10,30,60,120,300 seconds following a reproducible illumination.
  Record raw images where feasible, environmental controls and lamp-off time.
- Blinded random order: all-sites, left-half, right-half and shuffled
  same-total-dose patterns; also repeat after full decay to check
  carry-over. Background subtract image intensity using non-glow control.
- Report: per-cell normalized intensity trajectories, background/noise,
  repeatability, temporal bandwidth, spatial cross-talk, memory decay,
  readout information capacity with uncertainty, power cost and time.
- Negative control: two Exact-One fixtures same n and same illumination,
  but opposite SAT status. Uncoupled glow response is expected to collide.
  Never identify glow intensity with SAT status merely because patterns
  visually differ.

Do not claim that a static printed PLA part induces strong quantum
coherence, performs P=NP computation or implements an NP-complete physical
energy function.

## Potential positive research gate

If measured materials show reproducible, task-relevant nonlinear response
and controllable coupling, test their *information processing capacity*
against standard linear-memory baselines on ordinary time-series prediction.
Only afterward investigate an explicit SAT-to-device encoding with all
resources charged: preparation, hardware, time, energy, noise, measurement
precision, readout, repetitions and independent exact witness checking.

A physical computation claim requires a polynomially uniform preparation
procedure, a sound and complete answer criterion, and polynomial total
physical costs in the input length. The existence of parallel electrons,
an afterglow or a finite experimental speedup does not establish any of this.

## Reproduction

    python experiments/direct/pla_glow_trap_memory_probe.py --self-test
    python experiments/direct/pla_glow_trap_memory_probe.py --json

    SIMULATED_PASS != HARDWARE_VALIDATED
    REAL_PLA_GLOW_MEASUREMENTS = NOT_PERFORMED
    NP_ORACLE = NOT_ESTABLISHED
    P_VS_NP = OPEN
