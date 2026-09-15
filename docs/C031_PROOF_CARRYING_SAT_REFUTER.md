# C031 — Proof-Carrying SAT Refuter Bridge

**Status:** `CONSTRUCTIVE BRIDGE FORMALIZED / AMPLIFICATION OPEN / P_VS_NP=OPEN`

## Terminal target

For every fixed `k`, construct one deterministic polynomial-time algorithm
`R_k` which receives an `n`-input Boolean circuit `C` of size at most `n^k` and
returns:

```text
(F, b, pi)
```

such that:

1. `F` is a valid `n`-bit encoding of a CNF formula;
2. `b = SAT(F)`;
3. `C(F) != b`;
4. if `b=1`, `pi` is a satisfying assignment;
5. if `b=0`, `pi` is a refutation accepted by one fixed polynomial-time
   verifier;
6. generation, output, verification and encoding work are polynomial in
   `n + |C|`.

The negative certificate is required only for the particular UNSAT instances
printed by the refuter. C031 does not assume polynomial proofs for every UNSAT
formula.

## Theorem C031.1 — certified refuter lower-bound bridge

Let `s(n)` be a size bound. If a sound proof-carrying refuter exists against
every `n`-input circuit of size at most `s(n)` for every sufficiently large
`n`, then no circuit family of size `s(n)` decides SAT.

### Proof

Assume a circuit `C_n` of size at most `s(n)` decides SAT on all legal `n`-bit
encodings. Run the refuter on `C_n`. Sound certificate verification proves
`b=SAT(F)`, while the refuter contract gives `C_n(F) != b`, contradicting the
assumed correctness of `C_n`. QED.

### Corollary

If the theorem premise is established for `s(n)=n^k` for every fixed `k`, then

```text
SAT notin P/poly
```

and therefore `P != NP`.

## Theorem C031.2 — certificate-preserving embedding transfer

Let `f_m` be an explicit Boolean function and suppose:

1. `Ref_f` constructively refutes every circuit in a source class `D_m`;
2. `Enc(x)` produces a legal CNF encoding with
   `SAT(Enc(x)) = f_m(x)`;
3. `Cert(x)` produces a satisfying assignment when `f_m(x)=1` and a proof
   accepted by a fixed polynomial verifier when `f_m(x)=0`;
4. for every target SAT circuit `C` in the target size class, the composition
   `x -> C(Enc(x))` belongs to `D_m` with the required size accounting.

Then `Ref_f` composed with `Enc` and `Cert` is a proof-carrying SAT refuter.

The executable artifact checks both certificate polarities and this transfer
interface on a plumbing-only XOR example. The toy embedding is intentionally
not claimed to preserve hardness.

## External theorem components

### Constructive gate elimination

Carmosino, Dang and Jackman formalize convergent circuit simplification and
extract constructive lower bounds: given an undersized circuit for an explicit
function, a refuter efficiently finds an input where the circuit errs.

Their follow-up extends constructive gate-elimination refuters from XOR and the
multiplexer to more sophisticated affine-disperser arguments.

These results supply the **error-extraction mechanism**, but only in the range
of present gate-elimination lower bounds.

### Known quantitative wall

The best general-circuit gate-elimination lower bounds remain linear. Existing
analysis places an inherent sub-`5n` ceiling on purely gate-elimination methods.
Therefore present refuters cannot directly defeat circuits of size `n^k`.

### Hardness magnification

Hardness-magnification theorems show that barely superlinear lower bounds for
some meta-complexity problems can imply superpolynomial circuit lower bounds.
This offers a possible amplifier, but existing work also identifies locality
barriers. C031 additionally requires preservation of constructive error
extraction and proof-carrying labels.

## Located bottleneck

### NO_SHARING_REFUTER_AMPLIFICATION

The next theorem must amplify a constructive linear or slightly superlinear
refuter into a refuter against polynomial-size circuits **without assuming that
costs add over copies**.

A circuit may share intermediate computation across many encoded tasks. Hence

```text
m copies * one-copy lower bound
```

is not a valid lower bound without a circuit direct-sum or magnification theorem
that explicitly controls sharing.

## Active constructive hypotheses

### H-C031-A — Certified Refuter Amplification

There is a uniform transformation taking a proof-carrying refuter with a weak
size lower bound into one against `n^k` circuits, while preserving polynomial
runtime and certificate generation.

### H-C031-B — Certificate-Rich Restriction System

There is a polynomially navigable family of legal CNF encodings such that every
local structural violation exposed by circuit simplification can be completed
to a SAT or UNSAT formula with a polynomially generated certificate.

### H-C031-C — Constructive Hardness Magnification

A magnification target admits not only a weak lower bound, but an efficient
refuter whose counterexamples carry labels transferable to SAT with complete
size and witness accounting.

## Immediate work program

1. Freeze the exact source circuit basis and known constructive refuter bound.
2. Define candidate product/composition transformations.
3. Measure every shared gate once; never multiply one-copy lower bounds for
   free.
4. Require the amplified refuter to output an explicit source counterexample.
5. Build a certificate-preserving CNF embedding and prove composition-size
   bounds.
6. Repeat for every fixed polynomial exponent `k`.

## Reproduction

```bash
python experiments/direct/janus_c031_proof_carrying_sat_refuter.py --self-test
```

## Claim boundary

C031 proves the logical refuter-to-lower-bound bridge and implements an
independent SAT/RUP error verifier. It does not prove that the required
universal refuter exists, does not amplify current linear bounds, and does not
resolve P versus NP.
