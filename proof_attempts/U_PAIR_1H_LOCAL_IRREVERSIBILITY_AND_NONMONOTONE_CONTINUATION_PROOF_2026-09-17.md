# U-PAIR-1H — local irreversibility certificate and continuation-count monotonicity killer

Date: 2026-09-17

Status:
`PASS_LOCAL_NONINJECTIVE_SEMANTIC_COLLISION_CERTIFICATE__FAIL_CONTINUATION_CLASS_COUNT_AS_MONOTONE_TERMINATION_POTENTIAL`

## 1. Frozen setting

Let a symbolic state represent a Boolean relation `R(B,W)`, where:

- `B` is the live semantic boundary/interface;
- `W` is a protected continuation/witness side.

Let an exact transition use a polynomial-size boundary map `q:B->B'` and existentially merge all old boundary states inside each fibre of `q`.

Reversible definitional re-encodings are quotient-normalization steps and are not allowed to claim progress.

## 2. Polynomial local irreversibility certificate

A certificate of a genuine semantic collision is the tuple

`C=(b0,b1,w)`

such that

1. `b0 != b1`;
2. `q(b0)=q(b1)`;
3. `R(b0,w) != R(b1,w)`.

The verifier evaluates the frozen circuit/RREF representation of `q` and `R` on the explicit assignments. This is polynomial in representation size and assignment length.

The third condition proves that `b0` and `b1` induce distinct residual continuation relations on `W`; the second proves that the transition identifies them.

Therefore `C` is a polynomially checkable witness that the transition is not merely a bijective alias/reparameterization.

For a bijective `q`, conditions (1) and (2) cannot simultaneously hold, so all reversible negative controls fail closed.

### Claim ceiling

This certificate proves only **one semantic collision**. It does not prove that any proposed global complexity measure decreases, nor that the projected state has a polynomial-size exact representation.

## 3. A genuine projection can increase continuation-class count

The previous checker reference used

`N_R(B|W) = number of distinct residual relations R_b(W)`

and

`mu_R = ceil(log2 N_R)`.

These quantities are invariant under bijective reparameterization of `B`, but invariance is not enough: a termination potential must also be monotone under the allowed irreversible transitions.

We now give a constant-size counterexample.

Let

`B=(u1,u2,x)` and `W={w}`.

Define `R` by the following four cases on `u=(u1,u2)`:

- `u=00`: require `w=0`, independently of `x`;
- `u=01`: require `w=1`, independently of `x`;
- `u=10`: require `w=x`;
- `u=11`: require `w=0`, independently of `x`.

Before eliminating `x`, every boundary assignment `(u1,u2,x)` has residual set either `{0}` or `{1}`. Hence

`N_before=2`, `mu_before=1`.

Now existentially eliminate `x` and retain only `u`.

The projected residuals are:

- `u=00 -> {0}`;
- `u=01 -> {1}`;
- `u=10 -> {0,1}`;
- `u=11 -> {0}`.

Therefore

`N_after=3`, `mu_after=2`.

So a genuine many-to-one existential projection has increased both `N_R` and `ceil(log2 N_R)`.

### Why this happens

Projection does not merely delete rows. Inside each `q`-fibre it takes the Boolean union/OR of old residual continuation relations. Different fibres can therefore create new residual relations that did not occur before projection.

Consequently:

`genuine semantic collision` does **not** imply `N_after < N_before`.

## 4. Frozen verdict

The local anti-alias obligation is partially solved:

`PASS_POLYNOMIAL_LOCAL_COLLISION_CERTIFICATE`.

But the proposed semantic gold standard cannot be promoted into a descent measure:

`FAIL_N_R_AND_CEIL_LOG2_N_R_AS_MONOTONE_PROGRESS_POTENTIAL`.

Thus irreversibility and terminal progress must be carried by separate ledgers.

## 5. Successor gate

`U-PAIR-1I__PROJECTED_STATE_COMPILATION_WITH_SEPARATE_IRREVERSIBILITY_AND_EXISTENTIAL_DEBT_LEDGERS`

The next candidate must separately certify:

1. **Irreversibility ledger** — a transition is not a reversible alias, using collision/quotient certificates.
2. **Exact projection ledger** — the next symbolic state is exactly the existential projection of the previous one.
3. **Existential-debt ledger** — hidden/fresh existential information cannot be renamed indefinitely while pretending to approach terminal TRUE/FALSE.
4. **Complexity ledger** — projected-state representation size, transition time, witness reconstruction and exact replay remain polynomial.
5. **Terminalization** — debt reaches zero and the process reaches TRUE/FALSE in polynomially many certified transitions.

The next attack should not search for another invariant by name. It should freeze a concrete debt/accounting rule and attack whether it can simultaneously be anti-alias, polynomially checkable, and strictly terminalizing.

Firewall:

`GENERAL_SAT_IN_P = NOT_PROVED`

`P_VS_NP = OPEN`
