# Quantum Algorithm Benchmarking on IBM Quantum Hardware

> **Master's Thesis Project**
> Systematic benchmarking of Shor's and Grover's algorithms across ideal simulation, noisy simulation, and real IBM Quantum hardware using Qiskit.

Overleaf IEEE paper:
[https://www.overleaf.com/read/mnhqjpfqdzgs#8afe03](https://www.overleaf.com/read/mnhqjpfqdzgs#8afe03)

---

## Table of Contents

1. [Overview](#overview)
2. [Background](#background)
3. [Benchmarking Framework](#benchmarking-framework)
4. [Experiment Design](#experiment-design)
5. [Metrics](#metrics)
6. [Results Summary](#results-summary)
7. [Cross-Algorithm Comparison](#cross-algorithm-comparison)
8. [Project Structure](#project-structure)
9. [How to Run](#how-to-run)
10. [Dependencies](#dependencies)
11. [Troubleshooting](#troubleshooting)
12. [Additional Details & Deep Explanations](#additional-details--deep-explanations)

---

## Overview

This project implements **Shor's order-finding algorithm** and **Grover's search algorithm** in Qiskit, then benchmarks each by running identical circuits under three conditions:

| Condition | Purpose |
|-----------|---------|
| **Ideal simulation** | Theoretical baseline — what a perfect quantum computer produces |
| **Noisy simulation** | How device-like noise degrades results, without queue wait |
| **Real IBM hardware** | Ground truth on a NISQ-era processor |

Each algorithm is swept across **48 configurations** (compiler settings, circuit sizes, error-mitigation options), yielding **96 total experiments**. The two algorithms were chosen for their contrasting circuit structures — Shor is QFT-dominated while Grover is oracle/diffusion-dominated — enabling direct comparison of how each structure interacts with real hardware noise at similar circuit depths.

---

## Background

### Shor's Algorithm

Shor's algorithm factors integers via quantum **order finding**: given $a$ and $N$, find the smallest $r$ such that $a^r \equiv 1 \pmod{N}$, then extract factors through $\gcd(a^{r/2} \pm 1,\; N)$.

**Circuit pipeline**: Hadamard on control register &#8594; controlled modular multiplications ($a^{2^k} \bmod N$) &#8594; inverse QFT &#8594; measurement &#8594; continued-fraction post-processing.

**This implementation**: $N = 15$, $a = 2$ (true order $r = 4$). Only 4 target qubits needed; modular gates $M_2$ and $M_4$ use SWAP gates only — no Toffoli or ancilla overhead. Expected output phases: {0, 0.25, 0.5, 0.75}.

### Grover's Algorithm

Grover's algorithm searches an unstructured space of $N = 2^n$ items in $O(\sqrt{N})$ queries — a quadratic speedup over classical brute-force.

**Circuit pipeline**: Hadamard on all qubits &#8594; $k$ Grover iterations (oracle phase-flip + diffusion reflection) &#8594; measurement. Optimal iterations: $k = \lfloor \frac{\pi}{4}\sqrt{N/M} \rfloor$.

**This implementation**:

| Qubits | Search Space | Iterations | Theoretical Success | Marked State |
|--------|-------------|------------|---------------------|--------------|
| 2      | 4           | 1          | 100.00%             | \|11>        |
| 3      | 8           | 2          | 94.53%              | \|101>       |
| 4      | 16          | 3          | 96.13%              | \|1010>      |

Marked states use mixed 0/1 bit patterns to exercise the oracle's X-flipping logic across different qubits.

---

## Benchmarking Framework

Both notebooks share an identical three-tier execution framework:

| Tier | Tool | Shots | Noise | Purpose |
|------|------|-------|-------|---------|
| **A — Ideal** | `StatevectorSampler` | 100,000 | None | Theoretical baseline |
| **B — Noisy** | `AerSimulator` | 1,024 | Backend-derived or generic depolarising (0.1% 1q, 1% 2q) | Intermediate reference without queue wait |
| **C — Hardware** | IBM `SamplerV2` on `ibm_marrakesh` | 1,024 | Real device noise | NISQ ground truth with configurable resilience + dynamical decoupling |

---

## Experiment Design

Each algorithm is run through a **48-configuration factorial sweep**:

| Axis | Values | What it tests |
|------|--------|---------------|
| Transpiler optimisation level | 0, 1, 2, 3 | Compiler aggressiveness vs fidelity |
| Circuit size | **Shor**: 4, 6, 8 control qubits (8-12 total) | Precision vs depth trade-off |
|              | **Grover**: 2, 3, 4 search qubits | Search space size vs depth |
| Resilience level | 0, 1 | IBM built-in error mitigation |
| Dynamical decoupling | Off, On | Idle-qubit decoherence suppression (XpXm) |

$$4 \times 3 \times 2 \times 2 = 48 \text{ configs per algorithm} = 96 \text{ total}$$

Each configuration is executed on all three tiers.

---

## Metrics

### Total Variation Distance (TVD)

$$\text{TVD}(P, Q) = \frac{1}{2} \sum_{x} |P(x) - Q(x)|$$

Ranges from 0 (identical) to 1 (disjoint). Three variants computed per run:

| Variant | Interpretation |
|---------|---------------|
| TVD(Hardware, Ideal) | Distance from perfection |
| TVD(Noisy, Ideal) | Noise model accuracy |
| TVD(Hardware, Noisy) | How well simulation predicts hardware |

### Success Probability

| Algorithm | Definition |
|-----------|-----------|
| **Shor** | Probability mass within $\varepsilon = 1/2^{t+1}$ of expected phase peaks {0, 1/4, 1/2, 3/4}, with wrap-around handling |
| **Grover** | Probability of measuring the single marked state — a stricter metric since it depends on one bitstring |

### Amplification (Grover only)

$$\text{amplification} = \frac{P(\text{marked state})}{1/2^n}$$

Fold-improvement over random guessing. Any value > 1 confirms the search succeeded.

---

## Results Summary

### Shor's Algorithm

Expected output ($a=2$, $N=15$, $r=4$): four phase peaks at equal probability.

| Control Qubits | Total Qubits | Phase Resolution | 2q-Depth (opt=2) | 2q-Count (opt=2) |
|---------------|-------------|-----------------|-------------------|-------------------|
| 4 | 8 | 1/16 | 155 | 164 |
| 6 | 10 | 1/64 | 181 | 209 |
| 8 | 12 | 1/256 | 193 | 263 |

**Factor extraction**: Continued fractions on the best hardware run successfully recover $15 = 3 \times 5$.

### Grover's Algorithm

**Ideal simulation** (100k shots) — all match theoretical predictions within statistical noise:

| Qubits | Marked State | Theoretical | Measured | Amplification |
|--------|-------------|-------------|----------|---------------|
| 2 | \|11> | 100.00% | 100.00% | 4.00x |
| 3 | \|101> | 94.53% | 94.48% | 7.56x |
| 4 | \|1010> | 96.13% | 96.09% | 15.38x |

**Noisy simulation** (1,024 shots):

| Qubits | Success Prob | Amplification | Degradation from Ideal |
|--------|-------------|---------------|------------------------|
| 2 | 98.73% | 3.95x | -1.27% |
| 3 | 76.66% | 6.13x | -17.82% |
| 4 | 49.02% | 7.84x | -47.07% |

**Transpilation metrics** (IBM basis gates: ECR + single-qubit):

| Qubits | Opt Level | 2q-Depth | 2q-Count | Total Depth |
|--------|-----------|----------|----------|-------------|
| 2 | 0 | 2 | 2 | 36 |
| 2 | 2 | 2 | 2 | 11 |
| 3 | 0 | 54 | 54 | 268 |
| 3 | 2 | 39 | 39 | 120 |
| 4 | 0 | 219 | 231 | 827 |
| 4 | 2 | 173 | 175 | 569 |

---

## Cross-Algorithm Comparison

### Circuit Depth at Comparable Scales

| Algorithm | Config | 2q-Depth (opt=0) | 2q-Depth (opt=2) | 2q-Count (opt=2) |
|-----------|--------|-------------------|-------------------|-------------------|
| **Shor** | 4 ctrl (8 total) | 218 | 155 | 164 |
| **Shor** | 6 ctrl (10 total) | 284 | 181 | 209 |
| **Shor** | 8 ctrl (12 total) | 366 | 193 | 263 |
| **Grover** | 2 qubits | 2 | 2 | 2 |
| **Grover** | 3 qubits | 54 | 39 | 39 |
| **Grover** | 4 qubits | 219 | 173 | 175 |

The 4-qubit Grover circuit (173-231 two-qubit gates) is comparable in depth to Shor's 4-control-qubit circuit (155-249), enabling direct comparison of noise impact on QFT-dominated vs oracle/diffusion-dominated circuits.

### Noise Sensitivity

| Metric | Shor (noisy sim) | Grover (noisy sim) |
|--------|-----------------|-------------------|
| Smallest circuit success | 94.63% (4 ctrl) | 98.73% (2 qubits) |
| Largest circuit success | 85.64% (8 ctrl) | 49.02% (4 qubits) |
| Degradation range | 5-15% | 1-47% |

Grover shows **higher noise sensitivity** at equivalent depths because success depends on a single bitstring, while Shor aggregates probability mass across four phase peaks.

### Sweep Coverage Parity

| Dimension | Shor | Grover |
|-----------|------|--------|
| Experiment configs | 48 | 48 |
| Optimisation levels | [0, 1, 2, 3] | [0, 1, 2, 3] |
| Circuit size sweep | [4, 6, 8] ctrl qubits | [2, 3, 4] search qubits |
| Resilience levels | [0, 1] | [0, 1] |
| Dynamical decoupling | [Off, On] | [Off, On] |
| Shots / Backend / Tiers | 1,024 / ibm_marrakesh / all 3 | 1,024 / ibm_marrakesh / all 3 |

---

## Project Structure

```
Qiskit-v1.1c/
├── Shor-Qiskit.ipynb         # Shor benchmarking notebook (48 HW runs)
├── Grover-Qiskit.ipynb       # Grover benchmarking notebook (48 HW runs)
├── apikey.json               # IBM Quantum API token (auto-loaded)
├── README.md                 # This file
│
├── results/                  # Shor output
│   ├── results.csv
│   ├── results.json
│   ├── success_prob_and_tvd.png
│   └── success_prob_bar.png
│
└── results/grover/           # Grover output
    ├── grover_results.csv
    ├── grover_results.json
    ├── success_prob_and_tvd.png
    ├── success_prob_bar.png
    └── search_verification.png
```

CSV columns `depth_2q`, `success_prob`, and `tvd_vs_ideal` are **directly comparable** across both result files.

---

## How to Run

### Prerequisites

- Python 3.10+ (tested with 3.13)
- IBM Quantum account — free at [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com/)

### 1. Authenticate

**Option A** (recommended) — save once:
```python
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token="YOUR_TOKEN_HERE",
    overwrite=True,
)
```

**Option B** — place in `apikey.json`:
```json
{"apikey": "YOUR_TOKEN_HERE"}
```

The notebooks also prompt interactively as a final fallback.

### 2. Configure

Edit cell 3 in either notebook:

| Variable | Shor Default | Grover Default | Notes |
|----------|-------------|----------------|-------|
| `SHOTS` | 1024 | 1024 | Higher = smoother distributions |
| `BACKEND_NAME` | `"ibm_marrakesh"` | `"ibm_marrakesh"` | `None` for auto-select |
| `RUN_HARDWARE` | `True` | `True` | `False` for simulations only |
| Circuit sweep | `CONTROL_QUBIT_SWEEP=[4,6,8]` | `QUBIT_SWEEP=[2,3,4]` | Reduce for quick tests |
| `OPT_LEVEL_SWEEP` | `[0,1,2,3]` | `[0,1,2,3]` | `[1,3]` for fewer runs |

### 3. Execute

Run All cells top-to-bottom. Hardware jobs print their job ID for monitoring.

- **Simulations only**: ~2-5 min per notebook
- **With hardware**: ~30-90 min depending on queue

### 4. Analyse

Results save automatically. For cross-algorithm comparison, load both CSVs and compare the shared columns.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `qiskit` | >= 2.1.0 | Quantum circuit framework |
| `qiskit-ibm-runtime` | >= 0.40.1 | IBM Quantum cloud access (SamplerV2) |
| `qiskit-aer` | >= 0.17.0 | Local noisy simulation |
| `numpy` | any | Numerical operations |
| `pandas` | any | Results DataFrames |
| `matplotlib` | any | Plotting |
| `pylatexenc` | any | LaTeX in circuit diagrams |
| `jinja2` | any | Styled table rendering |

All installed automatically by cell 0 of each notebook.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'qiskit'` | Run cell 0 or activate the virtual environment |
| `AttributeError: '.style' accessor requires jinja2` | Run cell 0 again; summary cells have a plain fallback |
| `AccountNotFoundError` | Verify token at [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com/), re-run `save_account()` |
| Backend unavailable | Set `BACKEND_NAME = None` for auto-select |
| Hardware jobs stuck in queue | Normal. Monitor at IBM Quantum Dashboard. Use `RUN_HARDWARE = False` to iterate offline. |
| `No noise model from backend` warning | Expected with some backends; auto-falls back to generic depolarising model |
| 0 two-qubit gates in transpilation | Ensure transpilation targets realistic basis gates (`ecr`, `sx`, `rz`, `x`, `id`) with a hardware coupling map |

---

## License

This is a thesis research project. Please cite appropriately if reusing.

---

## Additional Details & Deep Explanations

<details>
<summary><strong>Click to expand full technical reference</strong></summary>

---

### A. Shor's Algorithm — Full Theory

The quantum order-finding circuit operates in five stages:

1. **Control register** in uniform superposition (Hadamard gates) encodes the phase estimation.
2. **Target register** (4 qubits, initialised to $|1\rangle$) serves as the modular arithmetic workspace.
3. **Controlled modular multiplication**: for each control qubit $k$, apply controlled-$M_{a^{2^k} \bmod N}$. For $a=2$, $N=15$, the sequence $a^{2^k} \bmod 15$ yields $[2, 4, 1, 1, \ldots]$ — only the first two control qubits carry non-identity gates.
4. **Inverse QFT** on the control register converts phase information into readable bitstrings.
5. **Measurement + continued fractions** extract $r$ from the measured phase $\theta = j/2^t \approx k/r$.

#### Expected Shor Output ($a=2$, $N=15$, $r=4$)

| Phase | Bitstring (4 ctrl) | Fraction |
|-------|-------------------|----------|
| 0.00 | 0000 | 0/4 |
| 0.25 | 0100 | 1/4 |
| 0.50 | 1000 | 2/4 |
| 0.75 | 1100 | 3/4 |

A perfect quantum computer outputs only these four bitstrings at 25% each.

#### Modular Multiplication Gates

| Gate | Operation | Implementation |
|------|-----------|---------------|
| `M2mod15()` | $\times 2 \bmod 15$ | 3 SWAPs: (2,3) &#8594; (1,2) &#8594; (0,1) |
| `M4mod15()` | $\times 4 \bmod 15$ | 2 SWAPs: (1,3) &#8594; (0,2) |
| `controlled_*` | Controlled versions | `.control()` wrapper, adding 1 control qubit |

#### Factor Extraction Procedure

From the best hardware run:
1. Filter bitstrings above half the peak count.
2. Convert to phase: $\theta = j / 2^t$.
3. Apply continued fractions: `Fraction(phase).limit_denominator(N)` &#8594; denominator is $r$.
4. Compute $\gcd(a^{r/2} \pm 1,\; N)$ to extract non-trivial factors.

---

### B. Grover's Algorithm — Full Theory

#### Oracle Implementation

The phase-flip oracle $|w\rangle \to -|w\rangle$ generalises to any marked state:
1. Apply X to qubits where the marked state has bit value 0 (maps the target to $|11\ldots1\rangle$).
2. Multi-controlled Z gate via H-MCX-H on the last qubit.
3. Undo the X gates.

#### Diffusion Operator

The reflection $2|s\rangle\langle s| - I$ is implemented as:

$$H^{\otimes n} \;\to\; X^{\otimes n} \;\to\; \text{MCZ} \;\to\; X^{\otimes n} \;\to\; H^{\otimes n}$$

#### Optimal Iterations and Success Probability

$$k = \left\lfloor \frac{\pi}{4} \sqrt{\frac{N}{M}} \right\rfloor, \qquad P_{\text{success}} = \sin^2\!\big((2k+1)\,\theta\big), \qquad \theta = \arcsin\!\sqrt{M/N}$$

| Qubits | Search Space | Iterations | Theoretical Success |
|--------|-------------|------------|---------------------|
| 2      | 4           | 1          | 100.00%             |
| 3      | 8           | 2          | 94.53%              |
| 4      | 16          | 3          | 96.13%              |
| 5      | 32          | 4          | 99.87%              |

#### Marked State Selection

| Qubits | State | Binary | Rationale |
|--------|-------|--------|-----------|
| 2 | 3 | \|11> | All-ones — simplest oracle, no X-flips |
| 3 | 5 | \|101> | Mixed bits — exercises X-flip on qubit 1 |
| 4 | 10 | \|1010> | Mixed bits — exercises X-flips on qubits 0, 2 |

#### Hardware Verification (ibm_marrakesh, 2-qubit circuit)

| Outcome | Count | Probability |
|---------|-------|-------------|
| **\|11> (marked)** | **975** | **95.22%** |
| \|10> | 24 | 2.34% |
| \|01> | 22 | 2.15% |
| \|00> | 3 | 0.29% |

**Amplification: 3.81x** (ideal: 4.00x) — search **successful** on real hardware.

---

### C. Benchmarking Tiers — Implementation Details

#### Tier A — Ideal

`run_ideal(circuit, shots=100_000, seed)` uses Qiskit's built-in `StatevectorSampler`. Returns `{bitstring: probability}`. Requires the classical register to be named `"out"`.

#### Tier B — Noisy

`run_noisy(circuit, backend, shots, seed)` attempts `NoiseModel.from_backend(backend)` first. On failure, falls back to generic depolarising noise:
- 1-qubit gates (`u1`, `u2`, `u3`, `sx`, `x`, `rz`): ~0.1% error
- 2-qubit gates (`cx`, `ecr`, `cz`): ~1% error

Transpiles internally at opt_level=0 and executes via `AerSimulator.run()`.

#### Tier C — Hardware

`run_hardware(transpiled_circuit, backend, shots, resilience_level, dd_enable)` configures `SamplerV2` with:
- `resilience_level`: 0 (none) or 1 (twirling + readout mitigation)
- `dynamical_decoupling`: XpXm sequence on idle qubits
- `twirling.enable_gates`: Pauli twirling on 2-qubit gates

Submits, waits, prints job ID. Returns `(distribution_dict, job_id)`.

---

### D. Experiment Sweep Details

#### Transpilation Optimisation Levels

| Level | Strategy | Thesis relevance |
|-------|----------|-----------------|
| 0 | Minimal topology mapping | Baseline circuit depth |
| 1 | Light optimisation | Default compiler behaviour |
| 2 | Gate cancellation, commutation | Moderate depth reduction |
| 3 | Exhaustive layout/routing search | Best depth, slowest compile |

#### Circuit Size Rationale

**Shor** — increasing control qubits improves phase resolution but deepens the circuit:

| Control Qubits | Total Qubits | Phase Resolution |
|----------------|-------------|-----------------|
| 4 | 8 | 1/16 |
| 6 | 10 | 1/64 |
| 8 | 12 | 1/256 |

At some point, added precision hurts because the circuit becomes too deep for hardware to execute reliably.

**Grover** — the 2-3-4 sweep produces 1, 2, and 3 iterations respectively, matching Shor's depth-escalation pattern while staying NISQ-feasible.

#### Resilience & Dynamical Decoupling

| Option | Level 0 | Level 1 |
|--------|---------|---------|
| Resilience | No mitigation | Twirling + readout correction |
| DD | Idle qubits accumulate decoherence | XpXm pulses refocus idle qubits |

These test whether zero-effort IBM-provided mitigations yield measurable fidelity gains.

---

### E. Metrics — Formal Definitions

#### TVD — Shor Success Probability

For each measured bitstring, convert to phase $\theta = \text{int}(\text{bitstring}) / 2^t$, check proximity to any expected peak (with wrap-around at the 0/1 boundary), and sum all mass within the $\varepsilon$-window. Default $\varepsilon = 1/2^{t+1}$ — half the spacing between adjacent bitstring phases.

Ideal success probability $\approx 1.0$. Deviation below 1.0 quantifies noise-induced smearing.

#### TVD — Grover Success Probability

$P(\text{marked state})$ — the probability of the single correct bitstring. Stricter than Shor's multi-peak aggregation, which partly explains Grover's higher apparent noise sensitivity.

#### Amplification Ratio

$\text{amplification} = P(\text{marked}) \;/\; (1/2^n)$. Ideal Grover approaches $N$; any value > 1 on hardware confirms the search worked.

---

### F. Key Functions Reference

#### Shared (identical in both notebooks)

| Function | Signature | Returns |
|----------|-----------|---------|
| `transpile_for_backend` | `(circuit, backend, opt_level, seed)` | `(transpiled_circuit, {depth_2q, count_2q, total_depth})` |
| `run_ideal` | `(circuit, shots=100k, seed)` | `{bitstring: probability}` |
| `run_noisy` | `(circuit, backend, shots, seed)` | `{bitstring: probability}` or `{}` on failure |
| `run_hardware` | `(transpiled, backend, shots, res_level, dd)` | `(distribution_dict, job_id)` |

**Constraint**: classical register must be named `"out"` — both `run_ideal` and `run_hardware` access `result.data.out.get_counts()`.

#### Shor-specific

| Function | Purpose |
|----------|---------|
| `M2mod15()` / `M4mod15()` | Modular multiplication gates (SWAP-based) |
| `controlled_M2mod15()` / `controlled_M4mod15()` | `.control()`-wrapped versions for phase estimation |
| `a2kmodN(a, k, N)` | $a^{2^k} \bmod N$ by repeated squaring |
| `build_shor_circuit(num_control, num_target=4, a=2, N=15)` | Full order-finding circuit: H &#8594; controlled-M &#8594; QFT$^{-1}$ &#8594; measure |
| `compute_metrics(dist, ideal, noisy, num_control, ...)` | TVD variants + Shor peak success probability |

#### Grover-specific

| Function | Purpose |
|----------|---------|
| `build_oracle(num_qubits, marked_state)` | Phase-flip oracle via X-flips + H-MCX-H |
| `build_diffusion(num_qubits)` | Reflection operator $2\|s\rangle\langle s\| - I$ |
| `optimal_num_iterations(num_qubits, num_marked=1)` | $\lfloor \pi/4 \cdot \sqrt{N/M} \rfloor$, minimum 1 |
| `theoretical_success_prob(num_qubits, k, num_marked=1)` | $\sin^2((2k+1)\theta)$ |
| `build_grover_circuit(num_qubits, marked_state)` | Full circuit: H &#8594; (Oracle + Diffusion) $\times k$ &#8594; measure |
| `compute_grover_metrics(dist, ideal, noisy, num_qubits, marked)` | TVD variants + success prob + amplification |

---

### G. Extended Noise Sensitivity Analysis

| Metric | Shor (noisy sim) | Grover (noisy sim) |
|--------|-----------------|-------------------|
| Smallest circuit success | 94.63% (4 ctrl) | 98.73% (2 qubits) |
| Largest circuit success | 85.64% (8 ctrl) | 49.02% (4 qubits) |
| Degradation range | 5-15% | 1-47% |

The 4-qubit Grover circuit (173-231 two-qubit gates) is comparable in depth to Shor's 4-control-qubit circuit (155-249). This overlap enables direct comparison: QFT-dominated circuits (Shor) exhibit gradual, predictable degradation, while oracle/diffusion-dominated circuits (Grover) degrade more sharply because the success criterion is a single bitstring rather than a distribution across multiple peaks.

---

### H. Notebook Cell Map

#### Shor (`Shor-Qiskit.ipynb`) — 36 cells

| Cells | Section | Content |
|-------|---------|---------|
| 0-1 | Setup | Dependencies + imports (QFTGate, Fraction, gcd, log) |
| 2-3 | Config | CONTROL_QUBIT_SWEEP, N=15, a=2, all sweep params |
| 4-5 | Auth | 3-step fallback (saved account &#8594; apikey.json &#8594; prompt) + backend selection |
| 6-17 | Circuits | M2mod15, M4mod15, controlled variants, a2kmodN, full order-finding circuit with inverse QFT, visualisations |
| 18-24 | Functions | build_shor_circuit, transpile_for_backend, run_ideal, run_noisy, run_hardware, compute_metrics |
| 25-27 | Sweep | Tier explanations + 48-config main loop |
| 28-32 | Results | DataFrame, CSV/JSON export, line plots, bar chart, summary table |
| 33-35 | Factors | Continued-fraction extraction from best hardware run |

#### Grover (`Grover-Qiskit.ipynb`) — 36 cells

| Cells | Section | Content |
|-------|---------|---------|
| 0-1 | Setup | Dependencies + imports (pi, sqrt) |
| 2-3 | Config | QUBIT_SWEEP, MARKED_STATES, all sweep params |
| 4-5 | Auth | Identical 3-step fallback + backend selection |
| 6-17 | Circuits | build_oracle, build_diffusion, optimal_num_iterations, theoretical_success_prob, visualisations, StatevectorSampler verification |
| 18-24 | Functions | build_grover_circuit, compute_grover_metrics + 4 reused from Shor |
| 25-27 | Sweep | Tier explanations + 48-config main loop |
| 28-32 | Results | DataFrame, CSV/JSON export, line plots, bar chart, summary table |
| 33-35 | Verification | Amplification analysis + marked-state histogram |

---

### I. Configuration Reference

#### Shor (`Shor-Qiskit.ipynb`, cell 3)

```python
SHOTS               = 1024
BACKEND_NAME        = "ibm_marrakesh"
RUN_HARDWARE        = True
OUTPUT_DIR          = "./results"
SEED_TRANSPILER     = 42
SEED_SIMULATOR      = 42

N                   = 15
a                   = 2
num_target          = 4

OPT_LEVEL_SWEEP        = [0, 1, 2, 3]
CONTROL_QUBIT_SWEEP    = [4, 6, 8]
RESILIENCE_LEVEL_SWEEP = [0, 1]
DD_SWEEP               = [False, True]
EPSILON                = None          # Auto: 1/2^(t+1)
```

#### Grover (`Grover-Qiskit.ipynb`, cell 3)

```python
SHOTS               = 1024
BACKEND_NAME        = "ibm_marrakesh"
RUN_HARDWARE        = True
OUTPUT_DIR          = "./results/grover"
SEED_TRANSPILER     = 42
SEED_SIMULATOR      = 42

MARKED_STATES       = {2: 3, 3: 5, 4: 10}

OPT_LEVEL_SWEEP        = [0, 1, 2, 3]
QUBIT_SWEEP            = [2, 3, 4]
RESILIENCE_LEVEL_SWEEP = [0, 1]
DD_SWEEP               = [False, True]
```

---

### J. Known Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| **venv pip target mismatch** | `.venv` created for an older directory; pip wrote to the wrong site-packages | Install with `python -m pip install --target=<correct path>` |
| **Token expiration** | IBM API tokens expire periodically | Regenerate at [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com/) and update `apikey.json` |
| **0 two-qubit gates in metrics** | `AerSimulator()` without basis gate constraints skips MCX decomposition | Transpile with `basis_gates=['id','rz','sx','x','ecr']` and a realistic coupling map |
| **`result.data.out` KeyError** | Classical register not named `"out"` | Both circuit builders use `ClassicalRegister(n, name="out")` explicitly |

</details>
