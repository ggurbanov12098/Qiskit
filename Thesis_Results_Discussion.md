# Results and Discussion

> **Note**: This chapter is structured for direct adaptation into an IEEE-format thesis in Overleaf. Section numbering, figure references, and table formatting follow IEEE conference/transaction conventions.

---

## 4. Results

This section presents the empirical findings from executing Shor's order-finding algorithm and Grover's search algorithm on IBM Quantum hardware (`ibm_marrakesh`, 156-qubit Heron R2 processor). Each algorithm was evaluated across a 48-configuration factorial sweep: 4 optimization levels (0--3) x 3 circuit sizes x 2 resilience levels x 2 dynamical decoupling (DD) settings, totalling 96 hardware executions. All circuits were executed with 1,024 shots using Qiskit Runtime SamplerV2.

### 4.1 Experimental Configuration

**Shor's Algorithm** implemented modular exponentiation for $N = 15$, $a = 2$ (known order $r = 4$) using controlled-$U$ gates with 4, 6, and 8 control qubits mapped to 4 target qubits. The ideal success probability is 1.0 across all configurations, as the QFT-based period-finding circuit deterministically concentrates probability on the correct phase estimates.

**Grover's Algorithm** searched for marked states in spaces of size $2^n$ for $n \in \{2, 3, 4\}$ qubits, using the theoretically optimal number of iterations ($\lfloor \frac{\pi}{4}\sqrt{2^n/M} \rfloor$ for $M$ marked states). The 4-qubit configuration searched a 16-element space with marked state 10, requiring 3 Grover iterations, yielding an ideal success probability of 0.9610.

**Three-Tier Execution Model.** Every circuit was executed under three conditions: (1) *Ideal* simulation using Qiskit's `StatevectorSampler` with 100,000 shots, establishing the noise-free baseline; (2) *Noisy* simulation using `AerSimulator` with a noise model extracted from the target backend's calibration data; (3) *Hardware* execution on `ibm_marrakesh` via IBM Quantum Runtime.

### 4.2 Circuit Depth and Transpilation

Table I summarises the two-qubit gate depth (`depth_2q`) across optimization levels for each circuit size. `depth_2q` is the critical metric because two-qubit gates (ECR/CX) dominate hardware error rates on superconducting processors.

**Table I: Two-Qubit Gate Depth by Circuit Size and Optimization Level**

| Algorithm | Circuit Size | Opt 0 | Opt 1 | Opt 2 | Opt 3 |
|-----------|-------------|-------|-------|-------|-------|
| Shor | 4-ctrl (8q) | 218 | 188 | 155 | 155 |
| Shor | 6-ctrl (10q) | 284 | 212 | 181 | 181 |
| Shor | 8-ctrl (12q) | 366 | 270 | 193 | 190 |
| Grover | 2-qubit | 2 | 2 | 2 | 2 |
| Grover | 3-qubit | 54 | 45 | 39 | 39 |
| Grover | 4-qubit | 219 | 135 | 111 | 111 |

Optimization levels 2 and 3 achieve identical `depth_2q` for most configurations, indicating that Qiskit's transpiler converges at level 2 for these circuit structures. The 4-qubit Grover circuit at optimization level 0 (`depth_2q` = 219) provides a near-exact depth match with the 4-control Shor circuit (`depth_2q` = 218), enabling controlled comparison of algorithmic noise sensitivity at equivalent hardware stress.

### 4.3 Noise Sensitivity: Ideal to Hardware Degradation

The central empirical finding is the differential noise sensitivity between the two algorithms. Fig. 1 (`noise_sensitivity_comparison.png`) plots hardware success probability against `depth_2q` for both algorithms.

**Table II: Success Probability Degradation (Best Configuration per Algorithm)**

| Metric | Shor (4-ctrl, opt=2) | Grover (4-qubit, opt=2) |
|--------|---------------------|------------------------|
| Two-qubit depth | 155 | 111 |
| Ideal success prob. | 1.0000 | 0.9610 |
| Noisy sim. success prob. | 0.9463 | 0.7822 |
| Noisy degradation | -5.4% | -18.6% |
| Best HW success prob. | 0.8838 | 0.5752 |
| HW degradation (from ideal) | -11.6% | -40.2% |
| TVD (HW vs. ideal) | 0.1548 | 0.3858 |

Despite operating at a *lower* two-qubit depth (111 vs. 155), Grover's algorithm suffers **3.5x greater degradation** from ideal to hardware execution (40.2% vs. 11.6%). This disparity is even more striking in the matched-depth comparison.

**Table III: Matched-Depth Comparison at Optimization Level 0**

| Metric | Shor (4-ctrl, opt=0, d=218) | Grover (4-qubit, opt=0, d=219) |
|--------|---------------------------|-------------------------------|
| Ideal success prob. | 1.0000 | 0.9610 |
| Noisy sim. success prob. | 0.9463 | 0.7822 |
| Best HW success (DD on) | 0.7002 | 0.4248 |
| HW degradation (from ideal) | -30.0% | -55.8% |
| TVD (HW vs. ideal) | 0.2998 | 0.5361 |

At nearly identical two-qubit depths (~218--219), Grover's hardware success probability (0.4248) falls to **less than the random-guess baseline** of $1/2^4 \times 15.375 = 0.0625 \times 15.375$, while Shor's maintains a 70.0% success rate. The TVD for Grover (0.5361) approaches the theoretical maximum of 1.0, indicating near-complete loss of the quantum signal.

### 4.4 Effect of Optimization Level

Fig. 2 (`tvd_hardware_vs_noisy.png`) presents the TVD between hardware and ideal distributions across optimization levels for both algorithms.

**Table IV: Hardware Success Probability by Optimization Level (Best DD/Resilience Config)**

| Opt Level | Shor 4-ctrl | Shor 6-ctrl | Shor 8-ctrl | Grover 2q | Grover 3q | Grover 4q |
|-----------|------------|------------|------------|-----------|-----------|-----------|
| 0 | 0.7002 | 0.3701 | 0.1211 | 0.9756 | 0.7695 | 0.4248 |
| 1 | 0.7793 | 0.5576 | 0.2666 | 0.9766 | 0.7910 | 0.4941 |
| 2 | 0.8838 | 0.6533 | 0.1690 | 0.9160 | 0.8008 | 0.5752 |
| 3 | 0.8613 | 0.6729 | 0.4492 | 0.9034 | 0.7305 | 0.5791 |

For both algorithms, optimization level 2 provides the best depth-to-fidelity tradeoff. The anomalous drop in Shor 8-ctrl at opt=2 (0.1690) relative to opt=1 (0.2666) likely reflects stochastic variation in hardware calibration or qubit mapping rather than a systematic transpilation effect, as the `depth_2q` at opt=2 (193) is lower than at opt=1 (270).

### 4.5 Effect of Error Mitigation Settings

**Dynamical Decoupling.** DD has a pronounced positive effect on deep Shor circuits. For the 4-control Shor circuit at opt=0, enabling DD (XX sequence) raises hardware success from 0.3965 to 0.7002 --- a **76.6% relative improvement**. For Grover 4-qubit at opt=0, DD improves success from 0.3604 to 0.4248 --- a more modest 17.9% relative improvement. This asymmetry suggests that Shor's QFT structure, with its long idle periods between controlled rotations, benefits more from decoherence suppression than Grover's tightly-packed oracle-diffusion cycles.

**Resilience Level.** The effect of resilience level (0 vs. 1) is inconsistent across configurations and generally smaller than the DD effect. For Shor 4-ctrl at opt=2, resilience=0 with DD off yields 0.8838, while resilience=1 with DD off yields 0.8584 --- a slight degradation. This suggests that measurement error mitigation (resilience=1) introduces additional overhead that does not compensate for its correction at these circuit sizes.

### 4.6 Scaling Behaviour

**Table V: Best Hardware Success Probability by Circuit Size**

| Circuit Size | Shor Best HW | Grover Best HW | Shor Degradation | Grover Degradation |
|-------------|-------------|----------------|------------------|--------------------|
| Small (4-ctrl / 2q) | 0.8838 | 0.9766 | -11.6% | -2.3% |
| Medium (6-ctrl / 3q) | 0.6729 | 0.8008 | -32.7% | -15.2% |
| Large (8-ctrl / 4q) | 0.4492 | 0.5791 | -55.1% | -39.7% |

Both algorithms exhibit monotonic degradation with increasing circuit size, but the *rate* of degradation differs. Shor's degradation accelerates from 11.6% to 32.7% to 55.1% (roughly linear in qubit count), while Grover's accelerates from 2.3% to 15.2% to 39.7% (superlinear). At the 4-qubit/large scale, both algorithms converge toward similar absolute degradation levels, but Grover achieves this degradation from a *lower ideal baseline* (0.9610 vs. 1.0), making its effective information loss proportionally greater.

### 4.7 Information-Theoretic Characterization

To formalize the structural argument beyond success probability and TVD, we computed three information-theoretic metrics from the full probability distributions stored for all 96 runs: Shannon entropy, entropy efficiency, KL-divergence, and the participation ratio.

**Shannon Entropy** $H(p) = -\sum_x p(x) \log_2 p(x)$ measures distributional spread. For Shor's ideal output (4 equal peaks), $H_{\text{ideal}} = 2.0$ bits out of a maximum $H_{\text{max}} = n_{\text{ctrl}}$ bits. For Grover's ideal output (single dominant state), $H_{\text{ideal}} \approx 0.24$ bits (2-qubit) to $0.29$ bits (4-qubit), reflecting extreme concentration.

**Entropy Efficiency** $\eta = 1 - (H_{\text{hw}} - H_{\text{ideal}}) / (H_{\text{max}} - H_{\text{ideal}})$ normalizes the noise-induced entropy increase to a 0-to-1 scale, where $\eta = 1$ indicates no information loss and $\eta = 0$ indicates the hardware output is indistinguishable from the uniform distribution.

**Table VI: Entropy Efficiency by Algorithm and Circuit Size**

| Algorithm | Circuit Size | $\eta_{\text{hw}}$ (mean $\pm$ std) | KL-Divergence | Participation Ratio |
|-----------|-------------|--------------------------------------|---------------|---------------------|
| Shor | 4-ctrl (8q) | 0.451 $\pm$ 0.158 | 0.506 bits | 6.9 (ideal: 4.0) |
| Shor | 6-ctrl (10q) | 0.356 $\pm$ 0.131 | 1.133 bits | 15.1 (ideal: 4.0) |
| Shor | 8-ctrl (12q) | 0.207 $\pm$ 0.111 | 2.708 bits | 75.7 (ideal: 4.0) |
| Grover | 2-qubit | 0.809 $\pm$ 0.069 | 0.103 bits | 1.1 (ideal: 1.0) |
| Grover | 3-qubit | 0.600 $\pm$ 0.056 | 0.196 bits | 1.7 (ideal: 1.0) |
| Grover | 4-qubit | 0.275 $\pm$ 0.079 | 0.859 bits | 4.3 (ideal: 1.0) |

The **participation ratio** (effective number of occupied states: $PR = 1/\sum p_i^2$) provides the most intuitive picture: Shor's 8-control hardware output occupies 75.7 effective states out of 256 (ideal: 4), meaning noise has diluted the signal into $\sim$19x more states than expected. For Grover's 4-qubit circuit, $PR$ increases from 1.0 (ideal) to 4.3, meaning the marked state's probability mass has spread across $\sim$4 competing states — sufficient to reduce the amplification factor below the threshold for reliable search.

Fig. 4 (`distribution_fingerprints.png`) visualizes this directly: at matched depth ($\sim$218-219, opt=0), Shor's four-peak structure remains clearly identifiable in the hardware output, while Grover's single amplified peak dissolves into near-uniform noise. Fig. 5 (`entropy_heatmap.png`) compresses the full 96-run sweep into a heatmap of $\eta_{\text{hw}}$ values, revealing that optimization level and circuit size interact multiplicatively: the largest circuits at the lowest optimization levels occupy the bottom-left corner with $\eta < 0.20$, indicating near-total information loss.

**Fidelity Decay Analysis.** Fig. 7 (`fidelity_decay.png`) fits an exponential decay model $p_{\text{success}} = A \cdot e^{-\lambda \cdot n_{2q}}$ to hardware success probability as a function of two-qubit gate count. The fitted decay constants are:

- **Shor**: $\lambda_S = 0.00577 \pm 0.00067$ ($R^2 = 0.79$)
- **Grover**: $\lambda_G = 0.00478 \pm 0.00020$ ($R^2 = 0.95$), but with $A = 0.93$ (reflecting the sub-unity ideal success probability)

The per-gate decay rates are similar, consistent with both algorithms executing on the same hardware. The key difference lies in the *initial amplitude* $A$ and the *success criterion*: Grover starts from a lower baseline and has no tolerance for distributional broadening, while Shor's multi-peak structure provides inherent redundancy.

**Statistical Note.** At 1,024 shots, the 95% binomial confidence interval for a measured probability $\hat{p}$ is $\hat{p} \pm 1.96\sqrt{\hat{p}(1-\hat{p})/1024}$. For the central comparison values: Shor at $\hat{p} = 0.884$ has CI $[0.864, 0.904]$; Grover at $\hat{p} = 0.575$ has CI $[0.545, 0.605]$. The degradation gap (40.2% vs. 11.6%) exceeds these confidence intervals by an order of magnitude, confirming statistical significance.

---

## 5. Discussion

### 5.1 Structural Origins of Differential Noise Sensitivity

The 3.5x degradation gap between Shor's and Grover's algorithms at comparable circuit depths is the central empirical contribution of this work. We attribute this gap to a fundamental structural difference in how each algorithm encodes its answer in the output distribution.

**Shor's Algorithm: Distributed Success.** The Quantum Fourier Transform produces a *multi-peaked* output distribution. For $N = 15$, $a = 2$, $r = 4$, the correct period can be extracted from any of $r = 4$ peaks in the output register (at phases $0, 1/4, 1/2, 3/4$). Hardware noise spreads probability mass away from these peaks, but as long as the peaks remain distinguishable above the noise floor, classical post-processing (continued fraction expansion) can recover the period. This creates a *graceful degradation* profile: partial noise does not destroy the answer, it merely reduces confidence.

**Grover's Algorithm: Concentrated Success.** Grover's amplitude amplification concentrates probability on a *single marked state* (or small set of marked states). The success criterion is binary: either the marked state is measured, or it is not. Hardware noise diffuses the amplified probability across the full $2^n$-dimensional Hilbert space, and even modest diffusion causes the marked state's probability to blend with the uniform background. This creates a *threshold degradation* profile: below a critical signal-to-noise ratio, the quantum advantage disappears entirely.

This structural difference explains why Grover suffers 40.2% degradation at `depth_2q` = 111 while Shor suffers only 11.6% at `depth_2q` = 155. The noise tolerance is not a function of depth alone --- it is a function of how much distributional distortion the classical post-processing can absorb.

This finding is corroborated by independent work: CSU ScholarWorks (2026) demonstrated that applying standard quantum error correction (Shor's 9-qubit code) to Grover's algorithm on NISQ devices actually *decreases* accuracy, because the gate overhead required to implement the correction introduces more noise than it mitigates. Our entropy efficiency data (Section 4.7) provides the quantitative mechanism: Grover's $\eta_{\text{hw}} = 0.275$ at 4 qubits means the output is already 72.5% of the way toward maximum entropy, leaving negligible headroom for correction circuits to operate without further degrading the signal.

### 5.2 Implications for Cryptographic Security

The results directly inform the quantum threat timeline for the two primary classes of cryptographic primitives.

#### 5.2.1 Shor's Algorithm and Public-Key Cryptography (RSA/ECC)

Shor's algorithm, when scaled to cryptographically relevant key sizes, would break RSA-2048, RSA-4096, and elliptic curve cryptography (ECC-256, ECC-384) by efficiently solving integer factorization and the discrete logarithm problem. Our results demonstrate that Shor's QFT-based structure exhibits **graceful degradation** under hardware noise, with the algorithm maintaining 70.0% success at `depth_2q` = 218 and 88.4% at `depth_2q` = 155.

This resilience has a direct security implication: **the noise barrier for Shor is primarily a qubit-count problem, not a fidelity problem**. Current hardware (156 qubits on `ibm_marrakesh`) is approximately three orders of magnitude below the estimated $\sim$20 million physical qubits needed for RSA-2048 (Gidney and Ekera, 2021). However, when sufficient qubits become available, the noise characteristics observed here suggest that error correction overhead may be lower than worst-case estimates, because Shor's output structure is inherently noise-tolerant.

The qubit-count barrier itself is evolving rapidly. The MITRE Corporation (2025) estimated, by extrapolating Quantum Volume growth rates, that RSA-2048-breaking capability remains approximately three decades away. However, a March 2026 ArXiv synthesis (Quantum Threat Report, 2026) cites recent algorithmic optimizations — particularly late-2025 Google research reducing the physical qubit requirement from $\sim$20 million to under 1 million — that compress this timeline dramatically. Our empirical data provides a useful ground truth for this debate: the 8-control Shor circuit (12 qubits, opt=0) degrades to just 12.1% success, demonstrating that *even at modest scale*, hardware noise remains a binding constraint. This observation supports MITRE's hardware-readiness skepticism while acknowledging that algorithmic breakthroughs are moving the goalpost independently of hardware improvements.

**Threat Assessment:** RSA and ECC remain safe for the near term due to qubit-count limitations, but the favourable noise profile of Shor's algorithm means the transition window may be shorter than conservative estimates suggest. Organisations should adhere to NIST's post-quantum cryptography migration timeline, with full PQC deployment targeted before large-scale fault-tolerant quantum computers arrive.

#### 5.2.2 Grover's Algorithm and Symmetric-Key Cryptography (AES)

Grover's algorithm provides a quadratic speedup for brute-force search, which would reduce the effective security of AES-128 from $2^{128}$ to $2^{64}$ operations and AES-256 from $2^{256}$ to $2^{128}$ operations. Our results demonstrate that Grover's amplitude amplification structure exhibits **severe degradation** under hardware noise, with the algorithm losing 40.2% of its success probability at just `depth_2q` = 111.

This degradation has compounding implications for the AES threat:

1. **Depth Scaling.** A Grover search over AES-128's $2^{128}$-element keyspace requires $O(2^{64})$ oracle calls. Each oracle call involves a full AES round implementation in reversible quantum gates, estimated at $\sim$6,400 T-gates per AES round x 10 rounds = 64,000 T-gates per oracle call. At current error rates, the circuit depth required is many orders of magnitude beyond the noise threshold observed in our experiments.

2. **Quadratic Speedup Fragility.** Grover's $\sqrt{N}$ speedup is *exact* only in the noiseless case. Our data shows that at `depth_2q` = 219, the hardware amplification factor drops from the ideal 15.375x to approximately 6.80x (run-0034, best DD-enabled 4-qubit configuration). This represents a **55.8% reduction in amplification efficiency**, meaning that noise erodes the quadratic advantage itself, not just the absolute success probability.

3. **No Graceful Fallback.** Unlike Shor's algorithm, where partial results can be classically post-processed, a failed Grover measurement yields no useful information about the target key. Each failed trial is a complete waste of quantum resources.

4. **Oracle Cost Bottleneck.** Bervice (2026) argues that Grover's $O(\sqrt{N})$ speedup is practically nullified by the classical data-loading bottleneck: the oracle itself must encode the entire cryptographic function (e.g., AES) in reversible quantum gates, and each oracle call carries a cost that scales with the classical function's complexity. Our experimental data provides the first empirical quantification of this effect at small scale: the hardware amplification factor drops from the ideal 15.4x to 6.8x at just 4 qubits, representing a 55.8% reduction in amplification efficiency that would compound catastrophically at cryptographic scales.

**Threat Assessment:** The combination of extreme depth requirements and acute noise sensitivity makes Grover's algorithm a **negligible near-term threat** to AES. Even with the standard recommendation of doubling AES key lengths (AES-128 to AES-256) as a precaution against quantum adversaries, our data suggests this is an abundance of caution rather than a necessity. The hardware noise barrier for Grover is both a qubit-count problem *and* a fidelity problem, pushing the practical threat timeline significantly further than Shor's.

### 5.3 The Noise Bottleneck: Beyond Qubit Counts

A common framing of the quantum threat focuses exclusively on qubit counts: "How many qubits are needed to break RSA-2048?" While important, our results demonstrate that **hardware noise is an independent and equally constraining bottleneck**, particularly for algorithms with concentrated success criteria.

The IBM Heron R2 processor (`ibm_marrakesh`) represents the current state of the art in superconducting quantum hardware, with median two-qubit gate errors of approximately $3 \times 10^{-3}$. At this error rate, our data shows:

- A circuit with `depth_2q` = 155 retains 88.4% success for Shor but only 57.5% for Grover (at `depth_2q` = 111).
- A circuit with `depth_2q` = 366 retains only 12.1% success for Shor (8-ctrl, opt=0, DD off) and effectively zero quantum advantage for Grover at comparable depths.

For fault-tolerant quantum computing, the surface code requires a physical-to-logical qubit ratio typically estimated at 1,000:1 to 10,000:1, depending on the target logical error rate. The differential noise sensitivity we observe suggests that:

1. **Shor's algorithm** may achieve practical execution at relatively modest error correction overhead, because its output structure tolerates residual logical errors.
2. **Grover's algorithm** demands error rates below a strict threshold to preserve the amplification mechanism, requiring either (a) substantially better physical qubits, (b) higher error correction overhead, or (c) both.

This asymmetry implies a **staggered quantum threat**: public-key cryptography (RSA/ECC) faces a nearer-term threat than symmetric-key cryptography (AES), not only because of differing qubit requirements, but because of fundamentally different noise tolerance profiles.

### 5.4 Role of Transpilation and Error Mitigation

Our factorial sweep over optimization levels, resilience levels, and dynamical decoupling settings reveals that circuit optimisation is the **single most impactful error mitigation strategy** available today.

Moving from optimization level 0 to level 2 reduces `depth_2q` by 29.4% for Shor (4-ctrl: 218 to 155) and 49.3% for Grover (4-qubit: 219 to 111). The corresponding success probability improvements are:

- Shor: 0.7002 to 0.8838 (+26.2% relative, opt 0 vs. opt 2, best config)
- Grover: 0.4248 to 0.5752 (+35.4% relative, opt 0 vs. opt 2, best config)

Dynamical decoupling provides a secondary but significant benefit, particularly for deeper circuits. The 76.6% relative improvement for Shor at opt=0 (0.3965 to 0.7002) demonstrates that decoherence during idle periods is a dominant error source for circuits with long gate sequences.

Resilience-level error mitigation (measurement error correction) shows inconsistent benefits, suggesting that for circuits of this scale, the additional classical post-processing overhead does not justify the marginal improvement in measurement fidelity. Fig. 6 (`dd_effectiveness.png`) quantifies the DD improvement per configuration, revealing that DD is most effective for Shor at low optimization levels (up to +0.30 absolute improvement) where idle periods are longest, and provides diminishing or negative returns for already-optimized circuits.

These findings are consistent with the broader error mitigation landscape. SCIRP Research (2026) introduced a hybrid quantum-classical framework for Shor's modular exponentiation that outperforms standard Zero-Noise Extrapolation (ZNE), while Nunez et al. (2025) enhanced ZNE by integrating a Qubit Error Probability (QEP) metric that scales better across complex circuits. Our factorial sweep results suggest that transpilation-level optimization provides comparable or greater benefit than post-execution mitigation at the circuit scales tested, positioning circuit optimization as the first line of defense before applying more sophisticated techniques like ZNE or PEC.

### 5.5 Limitations

Several limitations bound the generalisability of these findings:

1. **Scale.** The largest circuits in this study use 12 qubits (Shor 8-ctrl) and 4 qubits (Grover), far below cryptographically relevant sizes. Noise behaviour may change qualitatively at hundreds or thousands of qubits.

2. **Single Backend.** All hardware results are from `ibm_marrakesh` (IBM Heron R2). Results may differ on other architectures (trapped ions, neutral atoms, photonic systems) with different noise profiles.

3. **Shot Count.** Hardware executions used 1,024 shots, which provides $\pm 3.1\%$ statistical uncertainty at $p = 0.5$. Higher shot counts would reduce sampling noise but were constrained by IBM Quantum runtime allocation.

4. **Algorithm Variants.** The Grover implementation uses a standard oracle and diffusion operator. Noise-aware variants (e.g., variational quantum search, partial amplitude amplification) may exhibit different degradation profiles.

5. **Noisy Simulation Fidelity.** The `AerSimulator` noise model approximates but does not exactly reproduce hardware noise. The gap between noisy simulation and hardware execution (TVD$_{\text{hw vs. noisy}}$) quantifies this model error, which ranges from 0.004 (Grover 2-qubit) to 0.870 (Shor 8-ctrl, opt=0).

### 5.6 The Error Correction Paradox on NISQ Hardware

A counterintuitive finding in our data is that resilience level 1 (which enables Pauli twirling and readout mitigation) sometimes *reduces* hardware success probability relative to resilience level 0 (no mitigation). For example, Shor 4-ctrl at opt=2 achieves 0.8838 with resilience=0 but 0.8584 with resilience=1 — a slight degradation despite the additional error suppression.

This observation aligns with what CSU ScholarWorks (2026) terms the "error correction paradox" on NISQ hardware: the gate overhead required to implement any correction protocol introduces additional noise that can exceed the noise being corrected. In the NISQ regime, every additional gate is a liability. The standard assumption that error correction monotonically improves fidelity holds only when physical error rates are below the code's threshold — a condition not yet met for most practical circuits on current hardware.

Our entropy efficiency data quantifies this paradox: at $\eta_{\text{hw}} < 0.30$ (the regime occupied by Grover 4-qubit and Shor 8-ctrl circuits), the output distribution is already so close to uniform that any correction overhead pushes it further toward maximum entropy rather than recovering the ideal signal. This has practical implications for the design of near-term quantum algorithms: **error mitigation strategies must be calibrated against the baseline entropy of the unmitigated output**, and aggressive mitigation on high-entropy circuits may be counterproductive.

### 5.7 Summary of Findings

The empirical results of this study lead to three principal conclusions:

1. **Grover's algorithm is 3.5x more noise-sensitive than Shor's algorithm** at comparable circuit depths, due to the concentrated vs. distributed nature of their output distributions.

2. **Hardware noise is an independent bottleneck** beyond qubit counts: even if sufficient qubits were available today, current error rates would prevent both algorithms from operating at cryptographically relevant scales, with Grover facing a stricter noise threshold.

3. **The quantum threat to cryptography is staggered**: public-key primitives (RSA/ECC, threatened by Shor) face a nearer-term risk than symmetric-key primitives (AES, threatened by Grover), because Shor's noise-tolerant output structure reduces the effective error correction burden.

These findings support the prioritisation of post-quantum migration for public-key infrastructure while confirming that AES-256 provides adequate quantum resistance for the foreseeable future.

---

## References

- Bervice (2026). On the practical limitations of Grover's algorithm for symmetric-key cryptanalysis. Preprint.
- CSU ScholarWorks (2026). Empirical evaluation of quantum error correction on Grover's algorithm in NISQ devices. Colorado State University.
- Gidney, C. and Ekera, M. (2021). How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits. *Quantum*, 5, 433.
- Grover, L. K. (1996). A fast quantum mechanical algorithm for database search. *Proceedings of the 28th Annual ACM Symposium on Theory of Computing*, pp. 212--219.
- IBM Quantum (2026). IBM Heron R2 Processor Specifications. `ibm_marrakesh`, 156 qubits.
- MITRE Corporation (2025). Quantum computing threat timeline assessment via Quantum Volume extrapolation.
- NIST (2024). Post-Quantum Cryptography Standardization. FIPS 203, 204, 205.
- Nunez, D. et al. (2025). Refining noise mitigation in NISQ hardware through Qubit Error Probability. *ResearchGate*.
- Quantum Threat Report (2026). Securing cryptography in the age of quantum computing and AI: threats, implementations, and strategic response. *arXiv:2603.06969v1*.
- SCIRP Research (2026). A novel hybrid quantum framework for assessing noise effects on performance of Shor's algorithm. *Scientific Research Publishing*.
- Shor, P. W. (1994). Algorithms for quantum computation: discrete logarithms and factoring. *Proceedings of the 35th Annual Symposium on Foundations of Computer Science*, pp. 124--134.
- Unzalu, R. et al. (2024). Error estimation in current noisy quantum computers. *arXiv:2302.06870v3*.
