# JANUS-DEUTSCH-001 — universal quantum computation research control

**Research status:** finite classical quantum-state simulator. **No physical quantum machine, production SAT/Exact-One replacement, or P=NP claim.** This extension lives only in the unmerged UFR-001 draft PR.

## Scientific origins

- David Deutsch (1985), *Quantum theory, the Church–Turing principle and the universal quantum computer*, DOI 10.1098/rspa.1985.0070. Foundational universal quantum computation model.
- David Deutsch and Richard Jozsa (1992), *Rapid solution of problems by quantum computation*. Our constant/balanced promise-control uses the Deutsch–Jozsa interference principle, not a general SAT speedup.
- Lov K. Grover (1996): search amplitude amplification; **Grover's algorithm was not invented by Deutsch**. Ideal query savings do not imply end-to-end classical simulation speedup or exponential-time general SAT solution.

## Actual implementation

experiments/direct/janus_deutsch_001.py builds a fully specified **truth-table-to-ANF reversible circuit**. The Boolean oracle is an XOR of positive-control multi-controlled-X gates:

    U_F |x>|b> = |x>|b XOR F(x)>

The algebraic normal form is synthesized by a Boolean Möbius transform on ALL 2^n assignments; therefore its construction may be exponential. Each gate is an *ideal* multi-controlled X without physical gate decomposition or error correction. The phase kickback on an ancilla |-> gives (-1)^F(x) on the input basis. The statevector is simulated on a classical CPU.

- Exhaustive tests check all x, both b values, involution U_F^2=I and SAT/Exact-One truth tables (including repeated literals and empty constraints).
- UFR covariance is checked by an **independently verified bijection** of active variable labels, then by all 2^n phase labels. A structural signature alone is never accepted.
- Deutsch–Jozsa tests constant-0, constant-1 and balanced functions with expected P(measure 0...0) equal to 1, 1 and 0 respectively.
- Grover tests compare ideal success probabilities with the analytical formula sin^2((2t+1)asin(sqrt(M/N))) and independently check any proposed SAT candidate.
- A complete classical scan is required to establish M, and is explicitly counted. Every Grover phase oracle step evaluates a gate-network action per simulated basis state, and statevector memory is recorded. No sampled measurement is mistaken for a deterministic SAT certificate. UNSAT is not certified by Grover alone.
- n is capped at **8 input qubits**. Formula/ancilla adds at least one qubit. This is intentional, not a size capable of comparison to MAJ3-K4 n=18.

## Benchmark and interpretation

python -m unittest discover -s tests -p 'test_deutsch_001.py' -v

python experiments/direct/janus_deutsch_001_benchmark.py --out evidence/deutsch-001.json

The benchmark runs **the same six tiny SAT/Exact-One formulas** through: (1) classical enumeration, (2) classically simulated reversible oracle + Grover, (3) unchanged C023, (4) existing opt-in UFR-C023. It reports logical agreement; baseline classical evaluation counts; simulator wall time, Python memory peak, ANF synthesis gate count, phase-oracle gate applications and statevector size; C023/UFR answer status and proof replay status.

The historical MAJ3-K4 UFR comparison is separate. UFR produced 165 iso-hits and 2354 states vs C023 2427; last pinned two independent-runner performance gate was NOT_READY. It is **not valid to compare these MAJ3-K4 timings directly with tiny n<=8 quantum controls**, because workloads differ.

## Falsification gates

1. Any oracle table error, unitarity/bijection failure, phase sign error, wrong exact-one multiplicity, or improperly accepted witness means FAIL.
2. Classical simulator wall/RSS cannot be represented as real quantum hardware runtime or speedup.
3. The Grover search estimate must account for full M enumeration and ANF synthesis; do not quote O(sqrt(N)) outside the ideal query-oracle model.
4. Any future test on an actual quantum device needs separately audited gate compilation, ancilla clean-up, shot count, error model, UNSAT handling, independent witness checks, and same-instance C023 comparison.
5. Existing MAJ3-K4 production promotion criteria remain binding; this research cannot waive them.

No automatic merge or switching of the current C023 is authorized by any result of this module.
