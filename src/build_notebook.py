"""Generate main.ipynb from verified source so the notebook always matches working code."""
import json, os

NB = r"c:\Users\LENOVO\Desktop\techlab project\ising-codesign\main.ipynb"

def md(src): return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}
def code(src): return {"cell_type": "code", "execution_count": None, "metadata": {},
                       "outputs": [], "source": src.splitlines(keepends=True)}
def _ids(cells):
    import uuid
    for c in cells:
        c.setdefault("id", uuid.uuid4().hex[:8])
    return cells

cells = []
cells.append(md(
"# PS-S1 · Noise-Aware Algorithm↔Architecture Co-Design of a Variational Quantum Simulator for the TFIM\n\n"
"**Quantum Simulation Track — Phase 1 submission**\n\n"
"We run the *same* VQE algorithm on a 4-site Transverse-Field Ising Model across two fixed\n"
"architectures (**Processor A**, **Processor B**) and a **proposed Processor C**, then measure\n"
"how coupling-map topology — not the physics — drives circuit cost and noise.\n\n"
"**Headline (g=1.0):** Processor A needs **9 CX / depth 36 / 1 SWAP**; B and C need "
"**6 CX / depth 13 / 0 SWAPs**. Under 0.5% CX noise, A's observable error is **5.7×** worse "
"than B's — bought entirely by routing overhead."))

cells.append(md("## 1 · Setup"))
cells.append(code(
"import os, sys, warnings\n"
"import numpy as np\n"
"import matplotlib; matplotlib.use('Agg')\n"
"import matplotlib.pyplot as plt\n"
"warnings.filterwarnings('ignore')\n\n"
"for cand in (os.path.join(os.getcwd(), 'src'), os.path.dirname(os.getcwd())):\n"
"    if os.path.isdir(os.path.join(cand, 'engine.py')):\n"
"        sys.path.insert(0, cand); ROOT = os.path.dirname(cand); break\n"
"else:\n"
"    ROOT = os.getcwd(); sys.path.insert(0, os.path.join(ROOT, 'src'))\n"
"from qiskit.quantum_info import Statevector\n"
"from qiskit_aer import AerSimulator\n"
"from qiskit_aer.noise import NoiseModel, depolarizing_error\n"
"from engine import tfim_hamiltonian, exact_ground, ansatz, N\n"
"import experiment as E\n\n"
"procs = E.processors()\n"
"print('Loaded processors:', {k: v['n'] for k, v in procs.items()})"))

cells.append(md(
"## 2 · The two fixed architectures + our proposed C\n\n"
"Coupling maps are the **source of truth** (`processors/*.json`).\n"
"* **Processor A** (5q): `(0,1),(1,2),(1,3),(3,4)` — edge `(1,3)` is a **chord skipping qubit 2**.\n"
"* **Processor B** (9q): heavy-hex-inspired, contains a clean cycle `0-1-2-3-4-5-6`.\n"
"* **Processor C** (proposed, 6q): an open path hosting the chain with **zero SWAPs**."))
cells.append(code(
"for name, p in procs.items():\n"
"    print(f\"Processor {name}: {p['n']} qubits, edges = {p['edges']}\")"))

cells.append(md(
"## 3 · Physics: the Transverse-Field Ising Model\n\n"
"$$H = -J\\sum_i \\sigma^z_i \\sigma^z_{i+1} - g\\sum_i \\sigma^x_i$$\n\n"
"We diagonalise exactly for the ground-truth energy we must beat."))
cells.append(code(
"H = tfim_hamiltonian(J=1.0, g=1.0)\n"
"E0, psi0 = exact_ground(H)\n"
"print(f'Exact ground energy (g=1.0): {E0:.6f} Ha')\n"
"print(f'Pauli terms: {len(H.paulis)}   Qubits: {H.num_qubits}')"))

cells.append(md("## 4 · VQE: optimise once, then measure cost per architecture"))
cells.append(code(
"results_rows = []\n"
"for g in (0.5, 1.0, 1.5):\n"
"    H = tfim_hamiltonian(J=1.0, g=g)\n"
"    E0, psi0 = exact_ground(H)\n"
"    Evqe, th, _ = E.optimise(H)\n"
"    fid = float(abs(np.vdot(psi0, Statevector.from_instruction(ansatz(th)).data)) ** 2)\n"
"    mag = E.expectation(th, E.MAG_OBS)\n"
"    print(f'\\n--- g={g}  exact={E0:.6f}  VQE={Evqe:.6f}  err={abs(Evqe-E0):.2e}  fid={fid:.4f} ---')\n"
"    for pname in ('A', 'B', 'C'):\n"
"        m = E.metrics(th, procs[pname])\n"
"        results_rows.append({'g': g, 'processor': pname, 'E_vqe': Evqe, 'E_exact': E0,\n"
"                             'abs_err': abs(Evqe-E0), 'fidelity': fid, 'magnetization': mag,\n"
"                             'cx': m['cx'], 'depth': m['depth'], 'swaps': m['swaps'],\n"
"                             'single': m['single']})\n"
"        print(f\"   Proc {pname}: CX={m['cx']}  depth={m['depth']}  SWAP={m['swaps']}\")"))

cells.append(md(
"### Why Processor A costs more\n"
"A's chord `(1,3)` skips qubit 2, so chain `0-1-2-3` double-backs through the hub, forcing a "
"SWAP (3 extra CNOTs) and ~3× depth. B's clean cycle maps the chain with zero SWAPs. Identical "
"algorithm and physics on both — the difference is pure architecture."))

cells.append(md("## 5 · Noisy, shot-based VQE energy on each processor's routed circuit\n\n"
"Same noise model (0.5% depolarizing on CX, 0.1% on 1Q), same 8192-shot budget, 3 seeds. "
"`noisy_energy()` reads the full TFIM Hamiltonian from measurement counts of the **routed** "
"circuit — this is where routing overhead turns into accuracy loss."))
cells.append(code(
"from qiskit_aer.noise import NoiseModel, depolarizing_error\n"
"noise_rows = []\n"
"H = tfim_hamiltonian(J=1.0, g=1.0)\n"
"E0, _ = exact_ground(H)\n"
"_, th, _ = E.optimise(H)\n"
"nm = NoiseModel()\n"
"nm.add_all_qubit_quantum_error(depolarizing_error(0.005, 2), ['cx'])\n"
"nm.add_all_qubit_quantum_error(depolarizing_error(0.001, 1), ['sx', 'rz'])\n"
"SHOTS, SEEDS = 8192, (1, 2, 3)\n"
"for pname in ('A', 'B', 'C'):\n"
"    p = procs[pname]\n"
"    ests = [E.noisy_energy(th, H, p, nm, shots=SHOTS, seed=s) for s in SEEDS]\n"
"    mean, std = float(np.mean(ests)), float(np.std(ests))\n"
"    m = E.metrics(th, p)\n"
"    noise_rows.append({'processor': pname, 'logical_2q': m['logical_2q'], 'cx': m['cx'],\n"
"                       'depth': m['depth'], 'swaps': m['swaps'],\n"
"                       'E_noisy_mean': mean, 'E_noisy_std': std,\n"
"                       'abs_err_vs_exact': abs(mean - E0), 'E_exact': E0})\n"
"    print(f\"Proc {pname}: noisy E = {mean:+.4f} ± {std:.4f} |err|={abs(mean-E0):.4f} \"\n"
"          f\"(logical2q={m['logical_2q']} CX={m['cx']} depth={m['depth']} SWAP={m['swaps']})\")"))

cells.append(md("## 6 · Figures"))
cells.append(code(
"E.figures(results_rows, noise_rows, procs)\n"
"print('Saved to results/: coupling_maps.png, energy_error.png, architecture_cost.png, noise_impact.png')\n"
"try:\n"
"    from IPython.display import Image, display\n"
"    for f in ('coupling_maps.png', 'architecture_cost.png', 'energy_error.png', 'noise_impact.png'):\n"
"        p = os.path.join(ROOT, 'results', f)\n"
"        if os.path.exists(p): display(Image(filename=p))\n"
"except Exception as e:\n"
"    print('display skipped:', e)"))

cells.append(md(
"## 7 · Processor C — simulated proposed topology\n\n"
"A **simulated, proposed** 6-qubit open path: 4 qubits run the VQE, 2 are **reserved "
"(currently unused)**. It matches B's cost (6 CX / depth 13 / 0 SWAP) with fewer qubits. "
"The reserved qubits are a design placeholder for future ancilla-based mitigation — **no "
"mitigation benefit is claimed or measured** here."))
cells.append(code(
"C = [r for r in results_rows if r['processor']=='C' and r['g']==1.0][0]\n"
"A = [r for r in results_rows if r['processor']=='A' and r['g']==1.0][0]\n"
"print(f\"Processor A: {A['cx']} CX, depth {A['depth']}, {A['swaps']} SWAP\")\n"
"print(f\"Processor C: {C['cx']} CX, depth {C['depth']}, {C['swaps']} SWAP  (6 qubits vs B's 9)\")\n"
"print(f\"Cost reduction vs A: {100*(A['cx']-C['cx'])/A['cx']:.0f}% CX, {100*(A['depth']-C['depth'])/A['depth']:.0f}% depth\")"))

nb = {"cells": _ids(cells), "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"}},
      "nbformat": 4, "nbformat_minor": 5}

with open(NB, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
print("wrote", NB, "cells:", len(cells))

