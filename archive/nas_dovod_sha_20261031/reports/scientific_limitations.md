# DOVOD-SHA scientific limitations

The preserved script is a historical SHA-256 prediction experiment, not proof
that SHA-256 is predictable. Its threshold of 4.5
is not preregistered or statistically justified; the uniform-byte null has
expected cross-entropy ln(256) = 5.545177.

At noise=0, 25 of 50 test
sequences are byte-identical to training sequences. All 50 test block IDs occur
in training. The benchmark also changes nonce noise, sequence length, and nonce
modulus together, has no untouched holdout, and persists neither checkpoints
nor result manifests. Therefore memorization and target-prefix context can
explain apparent low loss without implying cryptographic prediction.

NAS execution policy: OFFLINE_MANUAL_ONLY on a selected workstation/GPU host.
