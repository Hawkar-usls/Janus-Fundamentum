# TRUMP SATLIB UF20 signed-automorphism admissibility — direct proof

**Authority:** diagnostic definition/proof scope only. No group search, solver, carrier, quotient, or complexity promotion.

## 1. Frozen signed action

Let `F` be a finite multiset of explicit Boolean constraints. A constraint is `(S,R)` where `S` is a finite variable scope and `R` is an explicit set of Boolean assignments on `S`.

A signed action is `g=(sigma,epsilon)` where:

- `sigma` is a permutation of the variable identities;
- `epsilon:V->{0,1}` is indexed by the **old** variable identities.

For a total assignment `a:V->{0,1}`, define

`(g.a)(sigma(v)) = a(v) XOR epsilon(v)`.

For a constraint `(S,R)`, define the transported scope `sigma(S)` and transported relation

`g.R = { r' : r in R and r'(sigma(v)) = r(v) XOR epsilon(v) for every v in S }`.

Transport every constraint by the same rule to obtain `g.F`.

A signed automorphism of `F` is a signed action satisfying `g.F = F` as the normalized explicit-relation constraint multiset. Pure variable permutations are the special case `epsilon=0`.

## 2. Assignment action is bijective

For `w=sigma(v)`, the defining equation is

`b(w)=a(v) XOR epsilon(v)`.

Hence the inverse assignment is

`a(v)=b(sigma(v)) XOR epsilon(v)`.

Thus `a -> g.a` is a bijection on the Boolean assignment cube. No assignment enumeration is needed for this statement.

## 3. Satisfaction is equivariant under transport

Fix a constraint `C=(S,R)` and assignment `a`. By definition,

`a satisfies C` iff `a|S in R`.

Let `b=g.a`. The restriction of `b` to `sigma(S)` is exactly the coordinate transport of `a|S` used in the definition of `g.R`:

`b(sigma(v)) = a(v) XOR epsilon(v)` for every `v in S`.

Therefore

`a|S in R` iff `b|sigma(S) in g.R`.

So `a satisfies C` iff `g.a satisfies g.C`. Applying this independently to every constraint gives

`a satisfies F` iff `g.a satisfies g.F`.

Consequently, if `g.F=F`, the bijection `a -> g.a` permutes the satisfying assignments of `F`. The signed action is therefore semantically admissible as an exact representation symmetry.

## 4. Primal degree under signed actions

Bit complementation changes relation rows but not scopes. Variable permutation maps every scope `S` to `sigma(S)`. Thus primal adjacency is transported solely by `sigma`:

`{u,v}` is a primal edge iff `{sigma(u),sigma(v)}` is a primal edge of `g.F`.

If `g.F=F`, `sigma` is an automorphism of the primal graph and

`deg(sigma(v)) = deg(v)`.

## 5. Single-forbidden-tuple clause relations

Now restrict to the frozen UF20 clause-relation subdomain. Each arity-3 relation is the Boolean cube minus exactly one forbidden tuple `f:S->{0,1}`.

Transporting the seven allowed rows bijectively transports the unique missing row as well. Therefore the transported relation has unique forbidden tuple `f_g` satisfying

`f_g(sigma(v)) = f(v) XOR epsilon(v)`.

For a variable `v`, let:

- `p(v)` be the number of incident constraints with forbidden bit `0` at `v`;
- `n(v)` be the number of incident constraints with forbidden bit `1` at `v`.

An exact signed automorphism induces a bijection from constraints incident to `v` to constraints incident to `sigma(v)`. For every such occurrence the forbidden bit is XORed with the **same variable-specific** `epsilon(v)`. Hence:

- if `epsilon(v)=0`, `(p(sigma(v)),n(sigma(v)))=(p(v),n(v))`;
- if `epsilon(v)=1`, `(p(sigma(v)),n(sigma(v)))=(n(v),p(v))`.

Together with degree preservation, every signed automorphism must preserve

`S1_unsigned(v) = ( deg(v), min(p(v),n(v)), max(p(v),n(v)) )`

under `sigma`.

This is a necessary invariant only. Equality of unsigned signatures does not imply the existence of a signed automorphism.

## 6. Relation to the previous pure-permutation theorem

When `epsilon(v)=0` for all variables, the ordered pair `(p,n)` is preserved, recovering the already sealed pure-permutation S1 theorem.

Allowing bit complements can merge variables whose ordered `(p,n)` counts are reversals of one another. Therefore the earlier proof of trivial pure-permutation groups on `UF20_01..05` does **not** by itself prove trivial signed-automorphism groups.

## 7. Scientific firewall

This proof establishes only:

1. the stated signed action is an exact semantics-preserving representation action;
2. signed automorphisms in the frozen single-forbidden-tuple clause domain preserve `(degree,min(p,n),max(p,n))` under their variable permutation part.

It does not search any signed group, does not prove any signed group trivial or nontrivial, does not construct a quotient, solver, or carrier, and does not change `P_VS_NP = OPEN` or `GENERAL_SAT_IN_P = NOT_PROVED`.
