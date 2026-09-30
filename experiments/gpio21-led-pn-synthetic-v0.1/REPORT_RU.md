# JANUS GPIO21 LED P–N synthetic feasibility v0.1

## Hardware correction

- Camera: absent.
- GPIO48: addressable RGB status LED.
- GPIO21: firmware-controlled activity/TX indicator. In the current Gladius firmware a very long BOOT hold toggles this LED together with full UART0 logging.
- PWR LED: hardwired supply indicator and not a controllable experiment channel.

The candidate physical junction channel is therefore the direct GPIO21 LED, not a camera path.

## Synthetic design

Seed: `440240`.

56 unseen planted SAT instances across:

- 3-SAT: n = 32, 48, 64, 96, 128;
- 5-SAT: n = 64, 96;
- eight trials per point;
- fixed budget `28n`.

Compared modes:

1. `digital` — frozen v0.4 gate algorithm with conventional PRNG;
2. `diode_clean` — synthetic biased/noisy GPIO21 junction readback;
3. `diode_dirty` — severe drift/noise stress model;
4. `stuck` — ablation with a low-entropy/frozen channel.

The diode parameters are stress assumptions, not measurements from the physical board.

## Results

| mode | solved | median steps | mean steps | mean Python ms |
|---|---:|---:|---:|---:|
| digital | 56/56 | 37.0 | 117.27 | 39.84 |
| diode_clean | 56/56 | 34.0 | 153.14 | 51.81 |
| diode_dirty | 56/56 | 31.5 | 180.43 | 64.74 |
| stuck | 56/56 | 33.5 | 92.05 | 32.61 |

## Interpretation

- Correctness survived both clean and severe synthetic junction noise: `56/56` in each mode.
- The architecture is safe enough to implement as an isolated characterization probe.
- The synthetic model does **not** show that diode physics is advantageous: mean work increased in both diode modes, while the stuck ablation remained strong.
- `PHYSICAL_PN_CAUSALITY_GATE` remains `FALSE / NOT TESTED`.
- The firmware must characterize the real GPIO21 node and log raw charge/discharge threshold timing before that signal is permitted to influence SAT decisions.

## Gate

```text
SYNTHETIC_LED_CHANNEL_CORRECTNESS = TRUE
FIRMWARE_CHARACTERIZATION_PROBE_JUSTIFIED = TRUE
PHYSICAL_PN_ADVANTAGE = FALSE
PHYSICAL_PN_CAUSALITY_PROVEN = FALSE
```