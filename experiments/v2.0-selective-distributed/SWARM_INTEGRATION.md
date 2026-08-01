# JANUS P–N Junction v2.0 — Swarm Integration Plan

## Existing swarm surfaces reused

The prepared JANUS swarm already provides:

- Anchor as the stable brother;
- Gladius as the experimental method scout;
- direct Anchor↔Gladius `J/T` twin-task packets;
- common `P/N` Cortex telemetry;
- heartbeat, stale TTL, channel recovery, and direct Buzz recovery paths;
- display/observer roles in Core2, PEA4, and the user's Holocron node.

The SAT experiment must not mutate the current mining ABI:

- no changes to Buzz `J/B` jobs;
- no changes to share `S/2`;
- no changes to target or SHA semantics;
- `P/N` remains observer telemetry, not scheduler control.

## Physical role map

| device | v2.0 role | responsibility |
|---|---|---|
| Gladius | `GLADIUS_SELECTIVE` | weakened-oscillation Selective Field, persistent clause charge, tested avalanche |
| Anchor | `ANCHOR_STABLE` | stable weighted field activated only after stagnation |
| Holocron | `LEGACY_V03 + COORDINATOR` | untouched control lane, arbitration, display and final witness |
| optional Zim/other brother | `SCOUT_CHAOS` | bounded fallback only after all primary lanes stall |

## New experimental wire surface

Do not overload the existing `J/T` ABI. Add a separate versioned packet family:

```cpp
enum JanusJunctionMessageType : uint8_t {
  JP_STATUS = 1,
  JP_ELITE = 2,
  JP_MODE = 3,
  JP_RESULT = 4
};

enum JanusJunctionMode : uint8_t {
  JP_EXPLOIT = 1,
  JP_HUNT = 2,
  JP_SURVIVE = 3,
  JP_CHAOS = 4,
  JP_RECOMBINATION = 5,
  JP_PROVEN_NO_RECOMBINATION = 6,
  JP_SEARCH_EXHAUSTED_NO_PROOF = 7
};

struct __attribute__((packed)) JanusJunctionPacketV2 {
  uint8_t magic[2];          // 'J','P'
  uint8_t version;           // 2
  uint8_t message_type;
  uint8_t role;
  uint8_t mode;
  uint16_t node_id;
  uint32_t seq;
  uint32_t task_id;
  uint16_t n_vars;
  uint16_t n_clauses;
  uint32_t round_id;
  uint16_t satisfied;
  uint16_t best_satisfied;
  uint16_t depth_x1000;
  uint16_t hunger_x1000;
  uint16_t flags;
  uint8_t assignment_len;    // bytes, max 32 in v2.0
  uint8_t assignment[32];    // supports up to 256 variables
  uint16_t hottest_clause[8];
  uint32_t assignment_hash;
  uint32_t crc32;
};
```

At `n=240`, the assignment requires only 30 bytes. The packet stays below the ESP-NOW payload limit.

## Coordinator rules

1. Holocron starts its untouched v0.3 control lane and orders Gladius to start Selective Field from the same assignment.
2. Holocron compares task ID, formula hash, initial-assignment hash, and round number.
3. Gladius may report depth and tested avalanche outcomes but cannot alter the control lane.
4. Anchor remains asleep until the activation gate is met.
5. When Anchor activates, Holocron sends the best assignment and a digest of the hottest clauses.
6. The first verified satisfying assignment wins.
7. Holocron independently verifies every clause before displaying `RECOMBINATION`.
8. `PROVEN_NO_RECOMBINATION` is displayed only with a sound witness.
9. Timeout without a witness is displayed as `SEARCH EXHAUSTED — NO PROOF`.

## Holocron display

Recommended live fields:

- `TASK`: k-SAT, n, m, formula hash
- `MODE`: HUNT / SURVIVE / CHAOS
- `P-HOLES`: unsatisfied clauses
- `N-CARRIERS`: active assignment bits / flips
- `DEPTH`: normalized depletion depth
- `CHARGE`: hottest-clause pressure
- `ROUND`: coordinator latency
- `WORK`: aggregate flips and probes
- `NODES`: active roles and stale state
- `RESULT`: recombination / proof / exhausted-no-proof

## Hardware validation gate

The physical release passes only if:

- all nodes receive byte-identical formula and initial assignment hashes;
- Holocron's verified result matches the simulator;
- no `J/P` packet changes mining state;
- packet loss and stale nodes are logged;
- elapsed time and energy are reported separately from total work;
- the v0.3 control lane is never modified by experimental messages;
- all false or unverifiable victories are rejected.
