# R5 E9 — Heterogeneous Interaction Source Audit

## Result

The literature supplies an exact **composition law**, but not yet a universal compiler.

### 1. Joinwidth gives the execution skeleton

Ganian–Ordyniak–Szeider formalize CSP solving by repeatedly applying exact relational **join, projection, and pruning** operations along a join decomposition. The width is controlled by the number of tuples in intermediate relations. If a bounded-width join decomposition is given, CSP is polynomial-time solvable.

This tells us what an exact universal composition engine has to do operationally. Its weakness for our purpose is representational: an intermediate boundary relation may have exponentially many tuples even when it has a compact algebraic/circuit description.

### 2. Algebraic-circuit compatibility gives a genuine polynomial interaction law

Wang–Mauá–Van den Broeck–Choi work over arbitrary commutative semirings. On the Boolean semiring:

- product = conjunction;
- aggregation = existential quantification / projection.

For smooth decomposable circuits, aggregation is linear-time. Products are polynomial when circuits are compatible, and **X-support-compatible** circuits admit a linear-time product in the maximum input size. The relevant compatibility properties are preserved by the appropriate operations.

This is almost exactly the kind of interaction theorem E9 asks for.

### 3. Why one circuit language is not enough

There are monotone read-3 2-CNF formulas for which every DNNF has exponential size. Therefore even Krom — one of our easiest SAT carriers — cannot be forced into polynomial-size DNNF uniformly.

So the global invariant cannot be:

> compile every tractable island into one DNNF-like common currency.

The common object must instead be a **typed calculus of native summaries and certified bridges**.

### 4. q-Horn is the positive heterogeneous control

q-Horn properly contains Horn and Krom and is recognizable/solvable in linear time. It demonstrates that heterogeneous clause behavior can remain tractable when there is a compact global compatibility certificate.

The important contrast is that an unrestricted mixture of a Horn part and a 2-CNF part is NP-complete.

Hence:

> local tractability + local tractability does not imply tractable mixture;
> local tractability + a special cross-carrier certificate sometimes does.

That is precisely the E9 target shape.

## New object: Typed Native Summary Join Calculus

At each node of a join tree store the exact extendability relation on the live boundary, but do **not** prescribe one representation language.

Store instead:

```
SUMMARY_NODE =
{
  boundary variables X,
  native representation tag T,
  exact native summary S_T(X),
  proof/certificate of supported operations
}
```

At an internal join:

```
(T1,S1)  ×  (T2,S2)
      ↓
BRIDGE_CERT(T1,T2,X)
      ↓
(T3,S3)
      ↓
project forgotten variables
```

A bridge is admissible only if its construction, exactness, output size, projection, and witness reconstruction are polynomial in the original input length.

Known bridge donors now include:

- same-carrier closure;
- q-Horn certified Horn/Krom interaction;
- X-support-compatible circuit product;
- independent/factorized product;
- common-edge-polymorphism compact join/projection.

## New killer gate

`R5_E9_TYPED_NATIVE_SUMMARY_JOIN_DECOMPOSITION_UNIVERSALITY_GATE_V1`

Ask only:

> Does every 3CNF have a polynomially constructible join decomposition whose every intermediate relation remains polynomially representable in some admitted native format, with a polynomial exact bridge at every format change/join?

This is strictly stronger and more concrete than “find a polynomial interaction invariant.”

A PASS would directly assemble a universal polynomial SAT algorithm.

A FAIL should identify a frozen family for which every admissible typed decomposition is forced either to:
- produce an exponential native summary;
- cross a known NP-hard mixed interaction;
- enumerate an unbounded interface/backdoor;
- or use an inadmissible semantic oracle.

## Scientific status

No PASS is claimed.

D1 = EMPTY.  
P_VS_NP = OPEN.
