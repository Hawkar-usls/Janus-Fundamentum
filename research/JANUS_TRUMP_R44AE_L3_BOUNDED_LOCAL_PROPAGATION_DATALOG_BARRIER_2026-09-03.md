# JANUS TRUMP R44AE — bounded-local propagation barrier

## Fixed model

R44AE does **not** claim that every polynomial-time transition law is local. It fixes one exact route:

`BOUNDED_LOCAL_CONSTRAINT_PROPAGATION_DATALOG`.

The candidate machine derives progress/negative information only through one fixed Datalog-expressible bounded-local propagation regime.

## Published theorem

Albert Atserias, *On Sufficient Conditions for Unsatisfiability of Random Formulas*, Journal of the ACM 51(2):281–311, 2004, DOI `10.1145/972639.972645`.

The theorem is quantified per fixed Datalog mechanism: for every fixed Datalog-expressible sufficient condition/program of the kind considered, that fixed program fails to certify unsatisfiability on almost all relevant random 3-CNF instances in the studied regime. The paper states the corresponding consequence that constraint-propagation algorithms working with small constraints fail to certify unsatisfiability almost always.

R44AE does **not** claim a single common formula that simultaneously defeats all possible Datalog programs.

The proof proceeds through existential pebble games and extension properties, and connects the pebble requirement to Resolution width.

## TRUMP consequence

For any one fixed candidate route,

`NO_LOCAL_CONTRADICTION_FOUND != SAT`.

Fix the Datalog/bounded-local mechanism first. The theorem then supplies many globally unsatisfiable 3-CNF instances that this fixed mechanism fails to certify. Therefore a TRUMP machine whose universal decision/progress authority is exhausted by that fixed bounded-local propagation model cannot discharge `L1` universal exact exit.

This is also an `L3` architectural barrier: every individual local propagation operation can be cheap while the information available to that fixed transition law is still insufficient for total exact decision.

The obstruction is not cost per local step. It is missing global information for the fixed mechanism.

## Dead-Zone law

`LOCALLY_CONSISTENT != GLOBALLY_SATISFIABLE`.

A saturated fixed local observer may have a genuine information dead zone. Its failure to observe a contradiction must remain typed as `NO_LOCAL_CONTRADICTION_FOUND`, never promoted to `SAT`.

## Scope

R44AE does not prove a barrier for arbitrary global algorithms. It does not show `P != NP`. It does not forbid local propagation as preprocessing. It blocks only the use of one fixed Datalog/bounded-local propagation architecture as complete universal decision authority.

Hence the next admissible route must be genuinely global in a formally specified sense, and must receive either:

- a direct proof of total charged polynomial runtime and exactness, or
- a theorem-level barrier for that precisely fixed global transition model.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
