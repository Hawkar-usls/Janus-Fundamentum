# R5 E97 — Opposite-Pair Exchange-Graph and Support-Spectrum Firewall

Date: 2026-10-06

Status:
`E96_SIGNATURES_GAIN_EXCHANGE_GRAPH_MEANING__E92_SUPPORT_SPECTRUM_FORCES_STATE8_GLOBALLY`

Scientific ceiling:

```text
E97 DOES NOT YET PROVE THAT TARGET6 ALWAYS IMPLIES RAW STATE 8.

IT PROVES A UNIVERSAL EXCHANGE-GRAPH INTERPRETATION OF EVERY E96 DEFECT
SIGNATURE, ADDS A GLOBAL MOD-3 COUNTING INVARIANT FOR EACH OPPOSITE TARGET
PAIR, AND STRICTLY EXTENDS THE E94 E92-NEAR-MISS FIREWALL FROM ONE 64-STATE
LOCAL SWITCH COMPONENT TO EVERY GEOMETRY WITH THE SAME SIX-WITNESS SUPPORT
SPECTRUM.

P_VS_NP = OPEN.
```

## 1. Opposite target pairs

Use the E96 labels

```text
0 = X_A
1 = X_B
2 = X_C
3 = Q_AB
4 = Q_AC
5 = Q_BC.
```

The three opposite pairs are

```text
O0 = {X_A,Q_BC} = {0,5}
O1 = {X_B,Q_AC} = {1,4}
O2 = {X_C,Q_AB} = {2,3}.
```

Each pair has the same boundary XOR syndrome.  In particular, on every
ordinary ExactOne check both members of an opposite pair require internal
coverage.

Fix one internal witness for each of the six TARGET6 states.

At an ordinary check the supports of its three incident variables form a
partition of the six target labels.

For an opposite pair O_i there are exactly two possibilities:

```text
unsplit:
  both labels of O_i lie in the same support block;
  the two opposite covers select the same incident variable;

split:
  the labels lie in different support blocks;
  the two covers select different incident variables.
```

This simple observation converts E96's finite support algebra into geometry.

## 2. Opposite-pair exchange graphs

For each O_i take the symmetric difference of the two corresponding exact
covers.

Whenever an ordinary check is split, the two covers select two different
incident variables there.  Join those two difference variables by an edge
labelled by that check.

At A,B,C the coverage demand differs between the two opposite states, so those
checks become terminal half-edges.  The variable-side survivor V supplies the
fourth terminal.

Counting the V terminal, every difference variable has degree three.

Hence each O_i gives a cubic exchange graph with four degree-one terminals

```text
A, B, C, V.
```

Because the source is linear/C4-free, the same two Tanner variables cannot
share two checks.  Therefore the ordinary exchange graph is simple.

An ordinary check is an edge of exchange graph G_i **iff O_i is split there**.

## 3. Exact geometric dictionary for E96

E96 classified the 31 all-even support partitions at an E95 defect.

E97 checks the additional split data and obtains an exact dictionary.

### Rigid defects

The five E96 partitions repaired by no target-derived kernel correction are
exactly the coarsenings of

```text
{0,5}, {1,4}, {2,3}.
```

Every opposite pair is unsplit.  Thus

```text
boxed:
rigid defect
<=> no opposite-pair exchange graph traverses the check.
```

### Proper conflict defects

The 18 proper conflict partitions split into three classes of six.

Each class has exactly two split opposite pairs and one unsplit pair.

Thus

```text
boxed:
proper conflict signature
<=> exactly two of G0,G1,G2 traverse the check,
with the missing exchange graph determining the signature.
```

### All-repair defects

The remaining eight partitions split all three opposite pairs:

```text
boxed:
all-repair defect
<=> all three exchange graphs traverse the check.
```

Therefore E96's abstract signature system is now a three-graph overlay problem.

## 4. Global mod-3 invariant

Fix one opposite pair O_i.

Call a cubic internal variable **common** if it is selected in both opposite
covers.

Such a variable cannot touch A,B,C: at each of those boundary checks exactly
one member of the opposite pair requires internal coverage.

It also cannot be x.  The variable-side survivor differs between the two
opposite states.

At every one of the common variable's three Tanner checks the same variable is
selected in both covers, so O_i is unsplit there.

Conversely, every ordinary unsplit check is covered in both states by one
common selected variable.

Hence there is a bijective incidence count

```text
# ordinary unsplit checks for O_i
    = 3 * # common cubic variables of O_i.
```

Therefore

```text
boxed:
N_i == 0 (mod 3)
```

for i=0,1,2.

This is a genuine global constraint on the three exchange-graph overlays that
was not visible in E96's one-check classification.

## 5. E92 support-spectrum firewall

E94 proved that a 64-member TARGET6-preserving local switch cube around the E92
near miss always retained raw state 8.

E97 identifies why a much larger class must do the same.

For one deterministic choice of the six E92 TARGET6 witnesses, the 18 variable
supports have even-cardinality members

```text
empty,
{0,4}, {0,4}, {0,4},
{4,5}, {4,5}.
```

An E95 triple-even defect at an ordinary check requires three incident support
sets which are

```text
* all even,
* pairwise disjoint,
* and whose union is all six target labels.
```

No such triple exists in the E92 support spectrum: labels 1,2,3 cannot even be
covered by the available even supports.

Consequently:

```text
boxed:
For EVERY Tanner geometry preserving this six-witness support assignment,
the E95 even-occurrence candidate has no ordinary triple-even defect.
```

The E95 boundary argument is support-only, so that candidate is automatically
an exact raw-state-8 witness.

Thus:

```text
boxed:
E92 SUPPORT SPECTRUM + TARGET6 => RAW STATE 8
```

independently of the particular local switches or Tanner embedding.

This strictly extends E94: the obstruction is not merely that one 64-state
switch component failed to remove state8; the entire fixed-support-spectrum
class cannot remove it.

## 6. Relation to Steiner-trade literature

Cavenagh and Griggs show that subcubic Steiner trades admit graph/edge-colouring
descriptions and, in the cubic Type-1 case, are equivalent to 1-factorisations
of simple cubic graphs.  Their result reinforces the usefulness of an exchange
graph language for linear triple systems.

Reference:

```text
Nicholas J. Cavenagh, Terry S. Griggs,
Subcubic trades in Steiner triple systems,
Discrete Mathematics 340 (2017), 1351-1358.
DOI 10.1016/j.disc.2016.10.021.
```

Their theorem is **not** used as a black-box proof here: our opposite-cover
differences are point-balanced exact-cover exchanges and are not automatically
Steiner 2-trades.  E97 only records the structural analogy.

## 7. Correct E98 target

If a genuine exact TARGET6 parent exists, E97 says it must escape the E92
support spectrum and satisfy E96 globally.

If a rigid defect is absent, global failure of the four E96 parity candidates
requires all three proper conflict classes.  Geometrically this means there
must be ordinary defect checks

```text
c0, c1, c2
```

such that

```text
c0 is missed only by G0,
c1 is missed only by G1,
c2 is missed only by G2.
```

At the same time each total unsplit count N_i is divisible by three.

Therefore the next killer is:

```text
E98 THREE-EXCHANGE-GRAPH TOPOLOGY KILLER

Use the common four terminals A,B,C,V, simplicity/C4-freeness, cubicity,
and N_i == 0 mod 3 to either:

1. prove a rigid defect or a rainbow triple of missing-graph conflict checks
   forces a reducible exchange component / additional raw boundary state; or
2. construct the first exact TARGET6 C4-free parent.
```

The main representation claim remains open until that step is resolved.

Scientific status:

```text
E97 = UNIVERSAL EXCHANGE-GRAPH DICTIONARY
      + GLOBAL MOD-3 UNSPLIT COUNT
      + E92 SUPPORT-SPECTRUM STATE8 FIREWALL.

GLOBAL_TARGET6_PARENT = OPEN.
P_VS_NP = OPEN.
```
