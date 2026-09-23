# R5 E9 — Pair-Defect Syndrome Image Tractable-Clone Countercontrol

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_FINITE_COUNTERCONTROL__NO_D1_PROMOTION

Parent: R5_E9_PAIR_DEFECT_SYNDROME_IMAGE_GATE_V1

Checker: experiments/r5_e9_pair_defect_syndrome_image_countercontrol.py

## 1. Purpose

The activated single-pivot normal form reduces the hard question to zero-membership in the pair-defect syndrome image

E(Mod(B)),

where B is the easy fanout-2 ternary NAE base and

E_i(x)=1 XOR x_u XOR x_v

for the D1 pair {u,v}.

A natural hope is that this image is automatically affine, Horn, dual-Horn, bijunctive, or delta-matroidal even when the original activated problem is hard.

This artifact gives a small exact countercontrol.

## 2. Base instance

Use 12 variables and two ternary partitions:

D2 =
{012,345,678,9 10 11}

D3 =
{036,149,2 7 10,5 8 11}.

Every D2 edge meets every D3 edge in at most one variable, so the base is linear.

Use the D1 pairing:

{04,13,25,69,7 11,8 10}.

No D1 pair lies twice in any ternary edge, so D1 union D2 union D3 is a valid linear mixed partition instance.

The easy base B=D2 union D3 has exactly 450 NAE models.

## 3. Syndrome image

For every base model x compute the 6-bit defect vector

E(x)_i = 1 XOR x_u XOR x_v.

The exact image has

|E(Mod(B))| = 55

out of 64 possible syndromes.

Zero syndrome is present; this instance is a positive control for membership, not a hardness witness.

## 4. Schaefer closure failures

The image relation is not Horn, not dual-Horn, not affine and not bijunctive.

The checker contains explicit closure witnesses:

- Horn failure under coordinatewise AND;
- dual-Horn failure under coordinatewise OR;
- affine failure under ternary XOR x XOR y XOR z;
- bijunctive failure under majority.

Therefore the syndrome image does not automatically collapse into any of the four nontrivial Boolean Schaefer tractable classes.

## 5. Delta-matroid failure

Identify a syndrome with the subset of coordinates carrying value 1.

The image fails the symmetric-exchange axiom.

One exact witness returned by the checker is:

X={2},
Y={0,1,2,3,5},
u=3,
X symmetric-difference Y = {0,1,3,5}.

For every v in {0,1,3,5},

X symmetric-difference {u,v}

(with the usual single-toggle interpretation when v=u)

is absent from the syndrome family.

Hence the syndrome image is not a delta-matroid.

## 6. Consequence

The new syndrome-image frontier cannot be discharged by assuming that projection of an easy fanout-2 NAE base through the pair-defect map automatically yields:

- an affine relation;
- a Horn or dual-Horn relation;
- a bijunctive relation;
- a delta-matroid / matching relation.

This does not rule out richer compact representations or special subclasses.

It only closes the most immediate old currencies on the image itself.

## 7. Updated target

The active question remains:

Can E(Mod(B)) be represented by some other polynomially constructible object supporting exact zero-membership and witness reconstruction?

Promising objects must explain structure not captured by the standard Boolean clones or delta-matroid exchange.

## 8. Ceiling

PAIR-DEFECT SYNDROME NORMAL FORM = PASS
STANDARD SCHAEFER IMAGE COLLAPSE = FALSIFIED BY SMALL CONTROL
DELTA-MATROID IMAGE COLLAPSE = FALSIFIED BY SMALL CONTROL
GENERAL POLY IMAGE REPRESENTATION = OPEN
D1 = EMPTY
P_VS_NP = OPEN
