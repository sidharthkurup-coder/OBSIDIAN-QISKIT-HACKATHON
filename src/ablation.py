"""Ablation study: coupling-topology effect on routing overhead and noisy VQE accuracy.

Tests two topologies:
  1. Chain-compatible (baseline): native edges support all required NN interactions
  2. Edge-deficient: remove a required edge, keep graph connected if possible

Sweeps g ∈ {0.5, 0.75, 1.0, 1.25, 1.5} with fixed Hamiltonian, ansatz, optimizer,
shot budget, and noise assumptions.

Run: python ablation.py
Outputs: results/ablation_results.csv, results/ablation.png
"""
import os, csv, json, warnings, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

from qiskit import transpile
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit_aer.primitives import EstimatorV2 as Estimator
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.transpiler import CouplingMap
from scipy.optimize import minimize

from engine import tfim_hamiltonian, exact_ground, ansatz, N, load

ROOT = os.path.dirname(os.path.dirname(__file__))
RES = os.path.join(ROOT, "results")
REPS = 2
NPARAM = REPS * N

# Fixed noise params (from PDF spec, loaded from A.json)
NOISE_2Q = 0.005
NOISE_1Q = 0.001


def get_ablation_topologies():
    """Return dict of topologies to test."""
    return {
        # Chain-compatible baseline: full path supports 0-1-2-3
        "chain_compatible": {
            "name": "Chain-compatible",
            "description": "Path topology supporting all required NN interactions",
            "num_qubits": 6,
            "coupling_edges": [[0,1],[1,2],[2,3],[3,4],[4,5]],
        },
        # Edge-deficient: remove direct edge (1,2), force routing through longer path
        # Keep graph connected: still has 0-1 and 2-3-4-5, but qubits 1 and 2 not directly connected
        # To keep it connected, add a bridge edge (0,5) creating a cycle
        "edge_deficient": {
            "name": "Edge-deficient",
            "description": "Remove edge (1,2); add bridge (0,5) to stay connected; forces routing",
            "num_qubits": 6,
            "coupling_edges": [[0,1],[2,3],[3,4],[4,5],[0,5]],  # missing [1,2], added [0,5]
        },
    }


def build_noise_model():
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(NOISE_2Q, 2), ["cx"])
    nm.add_all_qubit_quantum_error(depolarizing_error(NOISE_1Q, 1), ["sx", "rz"])
    return nm


def transpile_metrics(theta, edges, n_qubits):
    """Transpile ansatz onto topology; report CX, depth, measured SWAPs separately."""
    base = ansatz(theta)
    logical_2q = int(base.count_ops().get("cx", 0))
    tr = transpile(base, coupling_map=CouplingMap(edges),
                   initial_layout=list(range(N)),
                   basis_gates=["rz", "sx", "x", "cx"],
                   optimization_level=3, seed_transpiler=42)
    tr_swaps = transpile(base, coupling_map=CouplingMap(edges),
                         initial_layout=list(range(N)),
                         basis_gates=None, optimization_level=3, seed_transpiler=42)
    measured_swaps = int(tr_swaps.count_ops().get("swap", 0))
    return {
        "logical_2q": logical_2q,
        "cx": int(tr.count_ops().get("cx", 0)),
        "depth": int(tr.depth()),
        "swaps": measured_swaps,
    }


def measure_group(theta, edges, n_qubits, basis, noise, shots, seed):
    """Measure in Z or X basis on noisy topology. Returns counts in logical order."""
    qc = ansatz(theta)
    if basis == "X":
        qc = qc.copy()
        qc.h(range(N))
    qc.measure_all()
    tr = transpile(qc, coupling_map=CouplingMap(edges),
                   initial_layout=list(range(N)),
                   basis_gates=["rz", "sx", "x", "cx"],
                   optimization_level=0, seed_transpiler=seed)
    sim = AerSimulator(noise_model=noise, shots=shots, seed_simulator=seed)
    return sim.run(tr, shots=shots).result().get_counts()


def parity_expect(counts, qubits):
    tot = sum(counts.values())
    s = 0
    for bs, c in counts.items():
        b = bs.replace(" ", "")[::-1]
        par = 1
        for q in qubits:
            par *= (1 if b[q] == "0" else -1)
        s += c * par
    return s / tot


def x_expect(counts, i, all_q):
    tot = sum(counts.values())
    s = 0
    for bs, c in counts.items():
        b = bs.replace(" ", "")[::-1]
        par = 1
        for j in range(all_q):
            if j != i:
                par *= (1 if b[j] == "0" else -1)
        s += c * par
    return s / (tot * all_q)


def noisy_energy(theta, H, edges, n_qubits, noise, shots=8192, seed=0):
    """Estimate <H> from noisy shot counts on given topology."""
    labels = H.paulis.to_labels()
    coeffs = np.real(H.coeffs)
    z_counts = measure_group(theta, edges, n_qubits, "Z", noise, shots, seed)
    x_counts = measure_group(theta, edges, n_qubits, "X", noise, shots, seed)
    energy = 0.0
    for lab, c in zip(labels, coeffs):
        z_pos = [i for i, ch in enumerate(lab) if ch == "Z"]
        x_pos = [i for i, ch in enumerate(lab) if ch == "X"]
        if lab.count("Z") == 2 and not x_pos:
            energy += c * parity_expect(z_counts, z_pos)
        elif lab.count("X") == 1 and not z_pos:
            energy += c * x_expect(x_counts, x_pos[0], N)
        elif set(lab) == {"I"}:
            energy += c
        else:
            raise ValueError(f"unsupported term {lab}")
    return float(energy)


def optimise(H):
    """Find optimal VQE parameters with fixed seeds."""
    E0 = exact_ground(H)[0]
    best, bestx = 1e9, None
    for seed in range(4):
        rng = np.random.default_rng(seed)
        x0 = rng.uniform(-np.pi, np.pi, NPARAM)
        def obj(th):
            qc = ansatz(th)
            return float(np.asarray(Estimator().run([(qc, [H])]).result()[0].data.evs).item())
        r = minimize(obj, x0, method="COBYLA", options={"maxiter": 300})
        if r.fun < best:
            best, bestx = float(r.fun), r.x
    return best, bestx, E0


def run_ablation():
    t0 = time.time()
    topologies = get_ablation_topologies()
    noise = build_noise_model()
    g_values = [0.5, 0.75, 1.0, 1.25, 1.5]
    seeds = (1, 2, 3)
    shots = 8192

    rows = []
    print("=" * 78)
    print("ABLATION STUDY: Chain-compatible vs Edge-deficient topology")
    print("=" * 78)

    for g in g_values:
        H = tfim_hamiltonian(J=1.0, g=g)
        E0, _ = exact_ground(H)
        Evqe, th, _ = optimise(H)
        print(f"\n--- g = {g}  exact E0 = {E0:.6f} Ha  ideal VQE = {Evqe:.6f} Ha ---")

        for topo_name, topo in topologies.items():
            edges = [tuple(e) for e in topo["coupling_edges"]]
            n_qubits = topo["num_qubits"]

            # 1. Routing cost
            m = transpile_metrics(th, edges, n_qubits)

            # 2. Noisy energy (fixed seeds)
            ests = [noisy_energy(th, H, edges, n_qubits, noise, shots=shots, seed=s)
                    for s in seeds]
            mean = float(np.mean(ests))
            std = float(np.std(ests))
            err = abs(mean - E0)

            row = {
                "g": g,
                "topology": topo_name,
                "logical_2q": m["logical_2q"],
                "cx": m["cx"],
                "depth": m["depth"],
                "swaps": m["swaps"],
                "E_exact": E0,
                "E_vqe_ideal": Evqe,
                "E_noisy_mean": mean,
                "E_noisy_std": std,
                "abs_err_vs_exact": err,
            }
            rows.append(row)
            print(f"  {topo_name:20s}  CX={m['cx']:2d}  depth={m['depth']:2d}  "
                  f"SWAP={m['swaps']}  noisy_err={err:.4f} ± {std:.4f}")

    # Save results
    csv_path = os.path.join(RES, "ablation_results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # CX count
    ax = axes[0]
    for topo_name in topologies:
        rs = [r for r in rows if r["topology"] == topo_name]
        ax.plot([r["g"] for r in rs], [r["cx"] for r in rs], "o-", label=topo_name)
    ax.set_xlabel("transverse field g")
    ax.set_ylabel("routed CX count")
    ax.set_title("Circuit cost vs g")
    ax.legend()
    ax.grid(alpha=0.3)

    # Noisy energy error
    ax = axes[1]
    for topo_name in topologies:
        rs = [r for r in rows if r["topology"] == topo_name]
        ax.errorbar([r["g"] for r in rs], [r["abs_err_vs_exact"] for r in rs],
                    yerr=[r["E_noisy_std"] for r in rs], fmt="o-", label=topo_name, capsize=4)
    ax.set_xlabel("transverse field g")
    ax.set_ylabel("|E_noisy - E_exact| (Ha)")
    ax.set_title("Noisy energy error vs g")
    ax.legend()
    ax.grid(alpha=0.3)

    # SWAP count
    ax = axes[2]
    for topo_name in topologies:
        rs = [r for r in rows if r["topology"] == topo_name]
        ax.plot([r["g"] for r in rs], [r["swaps"] for r in rs], "o-", label=topo_name)
    ax.set_xlabel("transverse field g")
    ax.set_ylabel("measured SWAP count")
    ax.set_title("Routing overhead vs g")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(RES, "ablation.png"), dpi=130)
    plt.close()

    print(f"\n[done in {time.time()-t0:.1f}s]")
    print(f"  Results: {csv_path}")
    print(f"  Figure:  {os.path.join(RES, 'ablation.png')}")

    return rows


if __name__ == "__main__":
    run_ablation()
