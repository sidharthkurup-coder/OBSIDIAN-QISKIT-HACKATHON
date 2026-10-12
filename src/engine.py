"""Core physics + VQE engine for the TFIM co-design study. Verified standalone."""
import numpy as np, json, os
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp, Statevector, Operator
from qiskit_aer.primitives import EstimatorV2 as Estimator
from qiskit_aer import AerSimulator

N = 4  # spins
def load(name):
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "processors", name + ".json")) as f:
        return json.load(f)

def tfim_hamiltonian(n=N, J=1.0, g=1.0, periodic=False):
    """TFIM H = -J*sum_i Z_i Z_{i+1} - g*sum_i X_i (open chain; optional periodic bond).

    Built term-by-term as full Pauli strings so each ZZ bond acts on EXACTLY two qubits
    (verified: exact ground = -4.7588 Ha for n=4, J=g=1, open boundary).
    """
    terms = []
    bonds = [(i, i + 1) for i in range(n - 1)]
    if periodic:
        bonds.append((0, n - 1))
    for a, b in bonds:
        lab = ["I"] * n
        lab[a] = "Z"; lab[b] = "Z"
        terms.append(("".join(lab), -J))
    for i in range(n):
        lab = ["I"] * n
        lab[i] = "X"
        terms.append(("".join(lab), -g))
    return SparsePauliOp.from_list(terms)

def exact_ground(H):
    M = Operator(H).to_matrix()
    w, v = np.linalg.eigh(M)
    return float(w[0]), v[:, 0]

def ansatz(theta, n=N, reps=2):
    qc = QuantumCircuit(n)
    for r in range(reps):
        for q in range(n):
            qc.ry(theta[r * n + q], q)
        for q in range(n - 1):
            qc.cx(q, q + 1)
    return qc

def vqe_energy(theta, H):
    qc = ansatz(theta)
    est = Estimator()
    res = est.run([(qc, [H])]).result()
    return float(np.asarray(res[0].data.evs).item())

def magnetization(theta):
    qc = ansatz(theta)
    obs = SparsePauliOp.from_list([("ZIII", 0.25), ("IZII", 0.25), ("IIZI", 0.25), ("IIIZ", 0.25)])
    est = Estimator()
    res = est.run([(qc, [obs])]).result()
    return float(np.asarray(res[0].data.evs).item())

if __name__ == "__main__":
    H = tfim_hamiltonian(J=1.0, g=1.0)
    E0, psi0 = exact_ground(H)
    print("Exact ground energy:", E0)
