# R5 E41 — Raw Distance-to-Signed-Graph Firewall

Date: 2026-10-02

Status:
`RAW_SIGNED_GRAPH_BACKDOOR_CAN_BE_LINEAR_ON_POLYNOMIAL_ROOT_KERNEL_FAMILY__EFFECTIVE_LANGUAGE_ORDER_REQUIRED`

Scientific ceiling:

```text
R5 E39 gives an exact O(2^t poly(n)) terminal when an exposed orthogonal
representation has only t columns outside the signed-graphic two-endpoint class.

This note shows that raw t is not a hardness measure.

The R5 E31 tripartite family has n=3m^2 columns and every raw incidence column has
exactly three +1 entries, so its raw distance to the E37 signed-graphic class is
exactly n.

Nevertheless R5 E31/E32 expose a global vertex-potential/root-kernel normal form and
solve the whole family polynomially.

Therefore signed-graph backdoor size must be measured only after all stronger exact
kernel-language recognizers and quotients have run.

P_VS_NP = OPEN.
```

## 1. The E31 tripartite family

R5 E31 constructs variables

```text
X_ab, Y_bc, Z_ca
```

for `a,b,c in Z_m`, with

```text
n=3m^2.
```

Every source row contains one variable of each family, and every variable occurs in
exactly three rows. Thus the raw incidence matrix `A_m` is square+cubic+linear.

In particular every raw column has exactly

```text
3
```

nonzero entries, all equal to `+1`.

## 2. Raw E39 backdoor size

Apply the E39 definition directly to the raw representation

```text
R=A_m.
```

A good signed-graphic column must have exactly two nonzero entries, both in

```text
{+1,-1}.
```

But every column of `A_m` has support exactly three. Therefore no raw column is
signed-graphic.

Hence every column must be placed in the exceptional set:

```text
boxed:
t_raw(A_m)=n=3m^2.
```

This is maximal possible raw E39 distance.

## 3. Yet the family is polynomial

R5 E31 proves the exact rational kernel normal form

```text
U_ab = alpha_a-beta_b,
V_bc = beta_b-gamma_c,
W_ca = gamma_c-alpha_a.
```

Thus the kernel is a tripartite root/tension potential space of dimension

```text
3m-1.
```

R5 E32 supplies the corresponding root-kernel potential terminal. In particular the
family has the immediate Exact-One witness

```text
X=0,
Y=0,
Z=1.
```

So the family is exactly polynomial despite

```text
t_raw=n.
```

Therefore:

```text
boxed:
LARGE RAW DISTANCE TO SIGNED-GRAPH DOES NOT IMPLY HARDNESS.
```

## 4. Same pattern as E35

R5 E35 showed

```text
raw TU distance = Theta(n)
```

on E16 even though exact quotienting makes the effective TU defect zero.

E41 shows the analogous phenomenon for E39:

```text
raw signed-graph distance = n
```

can coexist with a different exact polynomial global kernel language.

The common lesson is:

```text
raw representation defect
!=
effective post-reduction language complexity.
```

## 5. Correct router order

The E39 backdoor should therefore be measured only after the earlier exact branches
have failed.

A safe order is

```text
1. coordinate forcing / KPROJ / equality-complement quotient;
2. local-gauge and bounded-interface quotient;
3. LOW-DEGREE-PEEL (E40);
4. commuting / potential / root-language recognizers;
5. TU / graph-factor / signed-graph exact languages;
6. simplify the residual representation;
7. only then measure an exposed distance-to-signed-graph backdoor t.
```

If a stronger global language already solves the instance, a large raw `t` is
irrelevant.

## 6. Effective signed-graphic complexity

The representation-invariant quantity one would ultimately like is conceptually

```text
t_eff(K)
=
minimum signed-graphic exceptional-column count over all exact polynomially
certifiable representations / quotients exposing the same residual kernel language.
```

This note does **not** claim that computing this global minimum is polynomial.
Indeed, requiring the router to solve a difficult representation-search problem
would merely hide the original hardness.

Instead every usable branch must provide an explicit representation together with a
verifiable upper bound on its own `t`.

Thus E39 is a certificate-driven FPT terminal:

```text
explicit small t -> exploit it;
no explicit small t -> do not assume one exists.
```

## 7. Updated hard-core requirement

A genuine post-E41 survivor must remain unresolved after all currently exposed
global languages and, on every representation actually produced by the router,
retain

```text
t = omega(log n)
```

for the E39 signed-graphic backdoor.

This must coexist with the earlier requirements:

```text
large effective kernel,
high quotient width,
integer feasibility,
no KPROJ/KLOC obstruction,
no TU/root/f-factor language,
no bounded-interface decomposition,
and no compact commuting/potential normal form.
```

The next useful progress must therefore come from a **new exact three-endpoint
global language**, not from raw support counting.

```text
P_VS_NP = OPEN.
```
