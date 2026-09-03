# JANUS TRUMP R44AE — bounded-local propagation barrier

## Fixed model

R44AE does **not** claim that every polynomial-time transition law is local. It fixes one exact route:

`BOUNDED_LOCAL_CONSTRAINT_PROPAGATION_DATALOG`.

The candidate machine derives progress/negative information only through one fixed Datalog-expressible bounded-local propagation regime.

## Published theorem

Albert Atserias, *On Sufficient Conditions for Unsatisfiability of Random Formulas*, Journal of the ACM 51(2):281–311, 2004, DOI `10.1145/972639.972645`.

The theorem shows that unsatisfiability of any significant fraction of random 3-CNF formulas cannot be certified by any Datalog-expressible property. The paper explicitly states the consequence that constraint-propagation algorithms working with small constraints fail to certify unsatisfiability almost always in the random 3-CNF regime studied.

The proof proceeds through existential pebble games and extension properties, and connects the pebble requirement to Resolution width.

## TRUMP consequence

For the fixed route,

`NO_LOCAL_CONTRADICTION_FOUND != SAT`.

There are globally unsatisfiable 3-CNF instances whose bounded-local view remains consistent for the fixed mechanism. Therefore a TRUMP machine whose universal decision/progress authority is exhausted by this bounded-local propagation model cannot discharge `L1` universal exact exit.

This is also an `L3` architectural barrier: every individual local propagation operation can be cheap while the information available to the transition law is still insufficient for total exact decision.

The obstruction is not cost per local step. It is missing global information.

## Dead-Zone law

`LOCALLY_CONSISTENT != GLOBALLY_SATISFIABLE`.

A saturated local observer may have a genuine information dead zone. Its failure to observe a contradiction must remain typed as `NO_LOCAL_CONTRADICTION_FOUND`, never promoted to `SAT`.

## Scope

R44AE does not prove a barrier for arbitrary global algorithms. It does not show `P != NP`. It does not forbid local propagation as preprocessing. It blocks only the use of one fixed Datalog/bounded-local propagation architecture as complete universal decision authority.

Hence the next admissible route must be genuinely global in a formally specified sense, and must receive either:

- a direct proof of total charged polynomial runtime and exactness, or
- a theorem-level barrier for that precisely fixed global transition model.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
