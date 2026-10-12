# Noise-Aware Algorithm↔Architecture Co-Design of a Variational Quantum Simulator for the Transverse-Field Ising Model

**PS-S1 · Quantum Simulation Track · Phase 1 submission**

We study how **processor connectivity** changes the hardware cost of running the *same*
variational algorithm. Using VQE on a 4-site Transverse-Field Ising Model (TFIM), we
benchmark on two fixed architectures (**Processor A**, **Processor B**) and a **simulated
proposed Processor C**, measuring transpiled circuit cost and noisy shot-based energy
accuracy under identical conditions.

> **Scope of the claim (intentionally narrow).** For **this 4-site VQE workload**,
> processor connectivity changes transpiled circuit cost, and the added gate overhead
> **can** increase noise sensitivity. We do **not** claim a universal "routing is the
> bottleneck" result beyond this instance.

---

## Headline results (g = 1.0)

**Circuit cost** (identical 2-layer ansatz, `seed_transpiler=42`, measured not inferred):

| Processor | logical 2Q | routed CX | depth | measured SWAP |
|---|---|---|---|---|
| A (5q, chorded) | 6 | **9** | **33** | **1** |
| B (9q, heavy-hex) | 6 | 6 | 13 | 0 |
| **C (simulated, 6q path)** | 6 | 6 | 13 | 0 |

All three start from the **same 6 logical two-qubit gates**. Routing onto A's chorded map
raises CX to 9 (depth 33, 1 measured SWAP); B and C need no SWAPs.

**Noisy, shot-based VQE energy** on each processor's **routed** circuit (same noise model —
0.5% depolarizing on CX, 0.1% on 1Q — same 8192-shot budget, 3 seeds; `E_exact = -4.7588` Ha):

| Processor | routed CX / depth | E_noisy (mean) | σ | \|E − E_exact\| |
|---|---|---|---|---|
| A | 9 / 33 | −4.3802 | 0.0231 | **0.379** |
| B | 6 / 13 | −4.5396 | 0.0170 | **0.219** |
| C | 6 / 13 | −4.5396 | 0.0170 | **0.219** |

Processor A's extra routing gates measurably degrade the noisy energy estimate (error
**0.379** vs **0.219** Ha) — this is measured evidence, not an assumption, that a higher
routed gate count can cost accuracy.

**Ideal (noiseless) VQE** is identical across processors *by construction* — energy and
fidelity depend only on the optimized parameters, not the chip. VQE converges to error
10⁻³–10⁻⁴ Ha with fidelity 0.998–1.000 against exact diagonalization.

---

## Why this matters
Variational algorithms (VQE/QAOA) are leading near-term candidates for quantum advantage,
but their success is decided by the hardware. A nearest-neighbour interaction like
`Z_i Z_{i+1}` needs a CNOT between *connected* qubits. When the chip lacks that edge, the
compiler inserts **SWAP gates** (each = 3 CNOTs), deepening the circuit and adding noise.

## The architecture finding
Processor A's coupling map is `(0,1),(1,2),(1,3),(3,4)`. The edge `(1,3)` is a **chord that
skips qubit 2** — routing the chain `0-1-2-3` forces an extra SWAP and ~2.5× depth.
Processor B contains a clean cycle `0-1-2-3-4-5-6`, so the identical chain maps with **zero
SWAPs**. We verify this by transpiling onto each real coupling map with a **fixed
`seed_transpiler`** and reporting logical count, routed CX, depth, and measured SWAP ops
separately.

## Honest methodology
- **Reproducible:** `seed_transpiler=42` fixed; identical compilation settings for A/B/C.
- **Measured, not inferred:** logical 2Q, routed CX, depth, and SWAP are each reported
  independently — SWAP count is read from the routed circuit, never back-computed.
- **Fair noise comparison:** same noise model and shot budget for all three; 3 seeds give
  reported variability (σ).
- **Correctness checked:** exact ground state (`-4.7588` Ha) verified against an independent
  term-by-term Hamiltonian construction.

## Repository layout
```
├── main.ipynb              # runnable solution notebook (deliverable)
├── main_executed.ipynb     # executed copy (proof it runs end-to-end)
├── index.html              # demo website (GitHub Pages)
├── requirements.txt        # pinned environment
├── processors/             # coupling maps (source of truth)
│   ├── A.json              # 5-qubit Phase-1 benchmark
│   ├── B.json              # 9-qubit heavy-hex Phase-1 benchmark
│   └── C.json              # simulated proposed processor
├── src/
│   ├── engine.py           # TFIM Hamiltonian, exact diagonalisation, VQE ansatz
│   └── experiment.py       # benchmark: optimise, transpile, noisy energy, plots
└── results/                # all figures + tables (generated)
```

## Reproduce (3 steps)
```bash
pip install -r requirements.txt
cd src
python experiment.py        # ~20 s; regenerates everything in ../results
```
Or execute the notebook: `jupyter nbconvert --to notebook --execute main.ipynb`

## Processor C — simulated proposed topology
Processor C is a **simulated, proposed** 6-qubit open path
`(0,1),(1,2),(2,3),(3,4),(4,5)`: **4 qubits run the VQE, 2 are reserved (currently
unused)**. It matches B's cost (6 CX / depth 13 / 0 SWAP) with fewer qubits. The reserved
qubits are a design placeholder for future ancilla-based mitigation — **no mitigation
benefit is claimed or measured** in this submission.

## What we'd do next (Phase 2 readiness)
- Scale to 6–8 spins to widen the A/B routing gap.
- Implement the reserved ancilla on Processor C and *measure* a mitigation benefit.
- Add zero-noise extrapolation and compare fidelity recovery A vs B vs C.
- Test whether A's hub topology ever wins for non-chain (e.g. all-to-all) Hamiltonians.

---
*Built for the Algorithm↔Architecture Co-Design Challenge. All numbers are reproducible from `src/experiment.py`.*
