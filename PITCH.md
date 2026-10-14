# 90-Second Pitch — PS-S1 Quantum Simulation Co-Design

## Opening (the problem)

Near-term quantum computers are limited not only by noise, but also by how their qubits are
connected. When a quantum algorithm needs qubits to interact but the hardware doesn't have a
direct connection between them, the compiler has to insert SWAP gates — each costing three
extra CNOTs — which makes circuits deeper and exposes them to more noise.

## Our investigation

We investigated this problem using the Variational Quantum Eigensolver to simulate a
four-site Transverse-Field Ising Model, a standard benchmark in quantum simulation.

We compared quantum processor topologies while keeping the underlying computational task
consistent: same Hamiltonian, same ansatz, same optimized parameters, same noise model,
same shot budget, same random seeds. The only thing we changed was the coupling graph.

## What we measured

In our tested configuration:

- The **chain-compatible** topology — which supports all required nearest-neighbor
  interactions natively — required **6 CX gates** and a circuit **depth of 13**.

- The **edge-deficient** topology — which removes one critical edge and forces longer
  routing paths — required **22 CX gates** and a **depth of up to 49**, with **six routing
  SWAPs**.

That's a **3.7× increase** in two-qubit gates and nearly **4× increase** in circuit depth,
from a single missing edge.

## The accuracy question

We then examined how this cost difference relates to noisy energy-estimation accuracy
across multiple transverse-field values (g ∈ {0.5, 0.75, 1.0, 1.25, 1.5}).

At every tested value of g, the edge-deficient topology's noisy VQE results showed
**0.33–0.59 Ha higher energy error** than the chain-compatible topology's. The routing
overhead and the accuracy penalty co-occur in this configuration.

## Our contribution

Finally, we propose **Processor C**, a simulated architecture designed around the workload's
connectivity requirements. It matches the best-performing topology's cost with fewer qubits.

Our central contribution is a **reproducible algorithm–architecture co-design study**:
measuring how connectivity affects circuit cost, and investigating when that cost translates
into degraded simulation accuracy.

## Closing

Rather than assuming every quantum processor is equally suitable for every algorithm, we
show why architecture should be designed around the workload. This is the co-design
principle: the algorithm and the hardware must be engineered together.

---

## Backup slides / talking points if asked

**Q: How do you know the difference isn't just statistical noise?**
A: We ran 3 seeds per topology per g value. The error bars (σ ≈ 0.01–0.03 Ha) are much
smaller than the 0.33–0.59 Ha gap between topologies. The effect is consistent across all
five g values tested.

**Q: Is Processor C actually better, or just smaller?**
A: Processor C is a simulated proposed topology. It matches the chain-compatible baseline's
cost (6 CX / depth 13 / 0 SWAP) with 6 qubits instead of the 9-qubit heavy-hex Processor B.
We don't claim it's "better" than B — we claim it achieves the same routing efficiency with
fewer qubits for this specific workload.

**Q: Why only 3 seeds? Isn't that weak statistics?**
A: 3 seeds is preliminary evidence. We report mean and standard deviation, and the effect
size (0.33–0.59 Ha) is large relative to the variability. For publication, we'd increase to
10+ seeds and report confidence intervals.

**Q: Does this prove that more gates always cause more error?**
A: No. We show a measured association in this specific 4-site VQE workload and these two
topologies. The extra routing gates and the higher noisy error co-occur. We don't claim
universal causation — that would require testing many more workloads and noise models.

**Q: What's the phase-transition physics story here?**
A: We swept g across the expected transition region (g=1.0 is critical for TFIM). Both
topologies show increasing error with g, as expected. We don't claim to have observed the
phase transition itself — that would require measuring order parameters and finite-size
scaling. Our focus is the architecture comparison, not the condensed-matter physics.

**Q: Can you run this on real quantum hardware?**
A: The code is Qiskit-based and could run on IBM Quantum backends with minor modifications.
The topology comparison would be even more relevant on real hardware, where connectivity
constraints and calibration differences matter more.

---

## One-slide summary (for visual backup)

**Title:** Algorithm↔Architecture Co-Design for Variational Quantum Simulation

**Left panel:** Two coupling graphs
- Chain-compatible: 0-1-2-3-4-5 (green, all edges present)
- Edge-deficient: 0-1 ... 2-3-4-5 with bridge 0-5 (orange, missing edge 1-2)

**Middle panel:** Circuit cost
- Chain: 6 CX, depth 13, 0 SWAP
- Edge-deficient: 22 CX, depth 48-49, 6 SWAP
- Callout: "3.7× more two-qubit gates from one missing edge"

**Right panel:** Noisy energy error vs exact
- Plot showing edge-deficient consistently higher by 0.33-0.59 Ha across g sweep
- Callout: "Higher routing cost → higher noisy error (measured, not assumed)"

**Bottom:** "Reproducible: python src/ablation.py regenerates all results in 24 s"
