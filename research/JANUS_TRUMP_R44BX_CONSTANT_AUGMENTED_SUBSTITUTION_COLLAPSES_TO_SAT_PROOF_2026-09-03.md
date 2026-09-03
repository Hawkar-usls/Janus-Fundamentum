# R44BX — adding Boolean constants to literal substitution collapses discovery to SAT

## Relation

Extend R44BS signed-literal substitution so that each target variable may map to:

- a signed source literal; or
- Boolean constant `0` or `1`.

Negation complements the image. A target clause is certified when its image:

1. evaluates `TRUE` because some literal maps to true;
2. is tautological; or
3. contains a source clause as a subset.

A supplied map and witnesses remain polynomially checkable.

## Exact theorem

Fix any satisfiable source CNF `B` and arbitrary target CNF `A`.

Then

`there exists a constant-augmented transport B -> A`

iff

`A is SAT`.

### SAT implies transport

Let `alpha` be a satisfying assignment of `A`.

Define

`phi(v)=alpha(v)`

as a Boolean constant for every target variable.

Because `alpha` satisfies every target clause, every clause image evaluates to `TRUE`.

Thus `phi` is a valid transport certificate. The source formula is not even consulted.

### Transport plus SAT source implies SAT target

Suppose a valid transport `phi` exists and `B` is satisfiable.

Take any satisfying assignment of `B`. Evaluate every signed-source-literal image under that assignment and use the literal/constant transport map to obtain values for target variables.

For each target clause, the certificate guarantees that its image is true either directly, tautologically, or because it contains a source clause that is true under the source model.

Hence every target clause is true. Therefore `A` is satisfiable.

Combining the two directions gives

`SAT(A) iff EXISTS_CONSTANT_AUGMENTED_TRANSPORT(B -> A)`

for every fixed satisfiable source `B`.

## Complexity boundary

The certificate language is strictly broader than R44BS and can defeat a no-literal-substitution finite obstruction such as R44BW whenever the target sibling is SAT.

However unrestricted discovery has not become easier. The all-constant subcase is exactly ordinary SAT witness search.

Thus deciding existence of such a transport is NP-hard, and membership in NP follows from polynomial certificate verification.

So the natural `allow constants` extension merely moves the original SAT problem into certificate discovery.

`MORE_EXPRESSIVE_CERTIFICATE_CLASS != EASIER_DISCOVERY`

`POLY_VERIFY != POLY_DISCOVER`

This theorem does not prove `P!=NP` and does not block more structured safe-deletion relations whose certificate language does not contain arbitrary satisfying assignments as a trivial subcase.

`TRUMP_finished=false`  
`SAT_IN_P=NOT_PROVED`  
`P_VS_NP=OPEN`
