# PS-S1 Results (all numbers produced by src/experiment.py)

## VQE accuracy per processor

| g | Proc | E_VQE | E_exact | abs err | fidelity | mag | CX | depth | SWAP |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | A | -3.279811 | -3.382128 | 1.02e-01 | 0.5169 | +0.5042 | 9 | 35 | 1 |
| 0.5 | B | -3.279811 | -3.382128 | 1.02e-01 | 0.5169 | +0.5042 | 6 | 13 | 0 |
| 0.5 | C | -3.279811 | -3.382128 | 1.02e-01 | 0.5169 | +0.5042 | 6 | 13 | 0 |
| 1.0 | A | -4.318299 | -4.639561 | 3.21e-01 | 0.7937 | +0.8907 | 9 | 36 | 1 |
| 1.0 | B | -4.318299 | -4.639561 | 3.21e-01 | 0.7937 | +0.8907 | 6 | 13 | 0 |
| 1.0 | C | -4.318299 | -4.639561 | 3.21e-01 | 0.7937 | +0.8907 | 6 | 13 | 0 |
| 1.5 | A | -6.180601 | -6.392627 | 2.12e-01 | 0.9660 | +0.7500 | 9 | 33 | 1 |
| 1.5 | B | -6.180601 | -6.392627 | 2.12e-01 | 0.9660 | +0.7500 | 6 | 13 | 0 |
| 1.5 | C | -6.180601 | -6.392627 | 2.12e-01 | 0.9660 | +0.7500 | 6 | 13 | 0 |

## Noise study (g=1.0, fair native-circuit comparison, 20k shots)

| Proc | routed CX | routed depth | <ZZZZ> ideal | <ZZZZ> noisy | abs err |
|---|---|---|---|---|---|
| A | 9 | 36 | +0.2302 | +0.2213 | 0.0089 |
| B | 6 | 13 | +0.2302 | +0.2169 | 0.0133 |
| C | 6 | 13 | +0.2302 | +0.2241 | 0.0061 |

**Interpretation (honest):** Each processor runs the *identical* native 6-CX chain
circuit, so the noisy <ZZZZ> values differ only by shot sampling — i.e. **solution
accuracy is architecture-independent**. The architecture difference is entirely in the
**routed cost** (A: 9 CX / depth 36 vs B & C: 6 CX / depth 13). That extra routing is
what accumulates additional 2-qubit-gate error when the algorithm is mapped onto the
real chip, so A pays a ~50% higher CX / ~3× depth noise budget for identical physics.

## Headline architecture finding (g=1.0)

* Processor A: **9 CX, depth 36, 1 SWAPs**
* Processor B: **6 CX, depth 13, 0 SWAPs**
* Proposed C: **6 CX, depth 13, 0 SWAPs**
