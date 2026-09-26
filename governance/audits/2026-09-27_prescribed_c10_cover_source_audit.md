# Source audit — prescribed C10 polynomial 2-group cover

Date: 2026-09-27
Decision: `PASS_SCOPED_GAP_CONFIRMED`
New math authorized: `true`
Scope: `R5_E9_PRESCRIBED_C10_POLYSIZE_2GROUP_COVER_GATE_V1`

## Internal anti-loop sweep

Checked the existing fixed-girth 2-group cover theorem, phase-cover preservation theorem, high-nullity explicit family, high-girth odd-hole control, and selector-conservation control. Those donors do not themselves preserve a designated base C10 while excluding every shorter lifted cycle.

## External names / queries

Searched voltage graph lifts, prescribed-cycle voltage constraints, one-relator group systole, Magnus Freiheitssatz, residual finite-p groups, finite 2-group separation of free words, and conditional-expectation derandomization.

## Sources checked

- Classical Magnus Freiheitssatz; modern formulation in Collins, *Intersections of Magnus subgroups*: a Magnus subset omitting a generator occurring in a cyclically reduced one-relator relator freely generates its subgroup.
- I. Emmanouil, *Residually nilpotent groups of homological dimension 1*, Bulletin of the London Mathematical Society 57 (2025), DOI `10.1112/blms.70140`; explicitly recalls that free groups are residually finite p-groups for every prime p.
- Existing JANUS source-bound voltage-cover machinery and fixed-girth theorem.

## Collision result

The classical donor facts are source-bound. In the checked sources no exact off-the-shelf statement was found combining all JANUS requirements: a designated simple C10 forced to close, no shorter lifted cycle, deterministic polynomial construction, connected extracted component, and polynomial 2-power cover degree. This is only a scoped-gap statement, not a novelty or P=NP claim.

## Authorized work

Authorize proof/checker work only for the prescribed-C10 cover construction on the already frozen nonabelian phase-inconsistent perfect-kernel route. Any semantic-route change requires a new audit.

`P_VS_NP = OPEN`.
