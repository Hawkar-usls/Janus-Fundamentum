# C039 package manifest

The executable proof package consists of:

- `c039_affine_core.py`: charged vtree construction, factor placement, GF(2) row operations, projection, and provenance primitives;
- `c039_affine_compile.py`: bottom-up message compiler and top-down witness recovery;
- `c039_affine_verify.py`: independent certificate replay and affine merge/separator verification;
- `janus_c039_symbolic_affine_factor_compiler.py`: deterministic adversarial audit.

The proof note, proposal, schema, source map, workflow, and active route matrix are part of the same draft package. No file is admitted automatically.
