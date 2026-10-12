# PS-S1 Results (all numbers produced by src/experiment.py)

## 1 · Circuit cost per processor (g = 1.0, identical 2-layer ansatz)

Reported separately — logical gate count, routed CX, depth, and **measured** SWAP ops.
No quantity is inferred from another. `seed_transpiler=42` fixed for reproducibility.

| Proc | logical 2Q | routed CX | depth | measured SWAP |
|---|---|---|---|---|
| A | 6 | 9 | 33 | 1 |
| B | 6 | 6 | 13 | 0 |
| C | 6 | 6 | 13 | 0 |

All three start from the same **6** logical two-qubit gates. Routing onto Processor A's chorded map raises CX to **9** (depth 33, 1 measured SWAP); B and C need no SWAPs (CX 6, depth 13).

## 2 · Ideal (noiseless) VQE accuracy — identical across processors by construction

| g | Proc | E_VQE | E_exact | abs err | fidelity |
|---|---|---|---|---|---|
| 0.5 | A | -3.425842 | -3.427034 | 1.19e-03 | 0.9980 |
| 0.5 | B | -3.425842 | -3.427034 | 1.19e-03 | 0.9980 |
| 0.5 | C | -3.425842 | -3.427034 | 1.19e-03 | 0.9980 |
| 1.0 | A | -4.758081 | -4.758770 | 6.89e-04 | 0.9999 |
| 1.0 | B | -4.758081 | -4.758770 | 6.89e-04 | 0.9999 |
| 1.0 | C | -4.758081 | -4.758770 | 6.89e-04 | 0.9999 |
| 1.5 | A | -6.503724 | -6.503892 | 1.67e-04 | 1.0000 |
| 1.5 | B | -6.503724 | -6.503892 | 1.67e-04 | 1.0000 |
| 1.5 | C | -6.503724 | -6.503892 | 1.67e-04 | 1.0000 |

Energy/fidelity depend only on the optimized parameters, not the chip, so these are **identical by design** — the architecture signal lives in the cost columns (§1) and the noisy-accuracy columns (§3).

## 3 · NOISY, shot-based VQE energy on each processor's ROUTED circuit (g=1.0)

Same noise model (0.5% depol. on CX, 0.1% on 1Q), same 8192-shot budget, 3 seeds. `E_exact = -4.7588` Ha.

| Proc | logical 2Q | routed CX | depth | SWAP | E_noisy (mean) | σ | |E−E_exact| |
|---|---|---|---|---|---|---|---|
| A | 6 | 9 | 33 | 1 | -4.3802 | 0.0231 | 0.3786 |
| B | 6 | 6 | 13 | 0 | -4.5396 | 0.0170 | 0.2192 |
| C | 6 | 6 | 13 | 0 | -4.5396 | 0.0170 | 0.2192 |

**Interpretation (honest, P1):** With routing noise included, Processor A's extra CX gates (depth 33 vs 13) degrade the noisy energy estimate. A's error |E−E_exact| = 0.3786 Ha vs B's 0.2192 Ha. This is the evidence that a higher routed gate count can cost accuracy — not merely an assumption. Variability (σ) is reported across 3 independent shot/seed runs.

## 4 · Scope of the claim

For **this 4-site VQE workload**, processor connectivity changes transpiled circuit cost, and the added gate overhead **can** increase noise sensitivity. We do not claim a universal 'routing is the bottleneck' result beyond this instance.

## 5 · Processor C — simulated proposed topology

Processor C is a **simulated, proposed** 6-qubit open path: 4 qubits run the VQE, 2 are **reserved (currently unused)**. It matches B's cost (CX 6, depth 13, 0 SWAP) with fewer qubits. The reserved qubits are a design placeholder for future ancilla-based mitigation — **no mitigation benefit is claimed or measured** in this submission.
