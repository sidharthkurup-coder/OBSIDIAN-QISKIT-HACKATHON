# Demo Video Storyboard — 60–90 seconds

Record one continuous screen capture (OBS, Clipchamp, or even PowerPoint presenter view).
Evidence-focused: show the problem, the comparison, the data, the finding. No animations,
no marketing. Narrate using the script below.

---

## Shot 1 — The problem (0:00–0:15)

**Screen:** `results/coupling_maps.png` (the three topologies), then zoom on Processor A.

**Narration:**
> "Near-term quantum computers are limited not only by noise, but by how qubits are connected.
> When an algorithm needs two qubits to interact but the chip has no edge between them, the
> compiler inserts SWAP gates — three extra CNOTs each — deepening the circuit and adding noise.
> We study this with VQE on a four-site Transverse-Field Ising Model."

## Shot 2 — The topology comparison (0:15–0:35)

**Screen:** `index.html` → click through the **Live topology explorer**: Chain-compatible, then
Edge-deficient. Point at the metrics table changing (6 CX → 22 CX).

**Narration:**
> "Here's the same logical circuit — six two-qubit gates — on two topologies. Chain-compatible:
> 6 CX, depth 13, zero SWAPs. Remove one edge but keep the graph connected: 22 CX, depth 49,
> six SWAPs. Same algorithm, same physics, 3.7× the hardware cost."

## Shot 3 — The measured evidence (0:35–1:05)

**Screen:** `results/ablation.png` (the three-panel figure), then the **Experiment explorer**
on the website showing a noisy-energy card comparison at g=1.0.

**Narration:**
> "We then ran noisy, shot-based energy estimation — 8192 shots, three seeds, identical noise
> model — across five transverse-field values. At every g, the edge-deficient topology's energy
> error was 0.33 to 0.59 Ha higher, with error bars that don't overlap. In the main benchmark,
> Processor A's routing overhead costs 0.255 Ha versus 0.152 for B. That's measured evidence
> that connectivity costs accuracy — not an assumption."

## Shot 4 — Processor C + finding (1:05–1:25)

**Screen:** `results/RESULTS.md` Processor C section, then the closing line of `index.html`.

**Narration:**
> "Finally, we propose Processor C: a simulated six-qubit path matching the best topology's cost
> with fewer qubits — four run the VQE, two reserved. Our finding is simple: architecture should
> be designed around the workload. Every number you saw regenerates from `python experiment.py`
> in twenty seconds."

---

## Recording checklist
- [ ] Resolution 1080p, one take or clean cuts
- [ ] Show actual live website interactions (not screenshots) for shots 2–3
- [ ] Include the reproduce command visibly on screen at the end
- [ ] Upload as `demo.mp4` to the repo root (or unlisted YouTube link in README)
- [ ] Keep total runtime ≤ 90 seconds
