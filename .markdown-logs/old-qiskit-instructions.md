You are GitHub Copilot Agent working inside the Jupyter notebook file: Qiskit.ipynb (already contains a Shor order-finding demo for N=15 using hard-coded modular multiplication gates M2mod15/M4mod15 and inverse QFT on the control register).

GOAL
Turn this notebook into a “thesis-grade” experiment harness that runs REAL jobs on IBM Quantum hardware (IBM Quantum Platform) using the CURRENT IBM Qiskit Runtime API from https://quantum.cloud.ibm.com/docs/en/api.
Important: DO NOT fabricate or assume outputs. Do not paste “example results”. Every result must come from actual execution (either local Aer sim or IBM hardware jobs). Add code that I can run to obtain real results.

HIGH-LEVEL DELIVERABLES
1) Modernize IBM Runtime usage to V2 primitives:
   - Use qiskit_ibm_runtime.QiskitRuntimeService + Session + SamplerV2 (not legacy Sampler).
   - Follow IBM docs for V2 primitives and options:
     - V2 primitives migration guide: https://quantum.cloud.ibm.com/docs/guides/v2-primitives
     - SamplerV2 API: https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/sampler-v2
     - Session API: https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/session
     - Runtime options: https://quantum.cloud.ibm.com/docs/guides/specify-runtime-options
   - Keep token handling secure (getpass or saved account). Do not hardcode tokens.

2) Add a BENCHMARKING PIPELINE with 3 tiers for the SAME circuit:
   A) Ideal simulation (statevector or exact sampler)
   B) Noisy simulation (Aer with a device noise model derived from the chosen backend properties when feasible)
   C) Real hardware run (IBM backend via SamplerV2)
   For each tier, collect a normalized probability distribution over measured bitstrings.

3) Add EXPERIMENT SWEEPS that are quick but thesis-relevant:
   - Transpilation optimization_level sweep: [0, 1, 2, 3]
   - Control qubit precision sweep (control register size): e.g., [4, 6, 8] (keep target=4)
   - Mitigation knobs (Runtime options) sweep:
       * resilience_level: [0, 1]  (if supported for SamplerV2 options in the current API)
       * dynamical decoupling: enable True/False (use supported options fields from docs; do not guess names)
   Keep sweeps small to limit runtime/queue time.

4) Add METRICS + REPORTING:
   Compute and store for each run:
   - 2-qubit depth and 2-qubit gate count of the transpiled circuit
   - Total variation distance (TVD) between:
       * hardware vs ideal
       * noisy vs ideal
       * hardware vs noisy
   - “Success probability on expected peaks” for Shor(N=15, a=2) order-finding:
       * expected phases near {0, 1/4, 1/2, 3/4}
       * Implement a principled mapping from measured control bitstrings -> phase in [0,1) as int(bitstring)/2^t
       * Define an epsilon window (e.g., within 1/(2^(t+1)) or configurable) and sum probability mass in these windows
   Store all results in a pandas DataFrame and export to:
   - results.csv
   - results.json (raw distributions + metadata)

5) Add PLOTS (no invented numbers):
   - Bar plot of success probability across experiment configs
   - Line/point plot of TVD across tiers/configs
   - Table summary in-notebook

6) Keep the original algorithm cells intact as much as possible, but refactor into clear functions:
   - build_shor_circuit(num_control, num_target=4, a=2, N=15) -> QuantumCircuit
   - transpile_for_backend(circuit, backend, optimization_level, seed=...) -> QuantumCircuit + metrics
   - run_ideal(circuit, shots)
   - run_noisy(circuit, backend, shots)  (derive a noise model if possible; if not possible, document and skip gracefully)
   - run_hardware(circuit, backend, shots, options_dict) -> distribution
   - compute_metrics(distribution, ideal_distribution, noisy_distribution, num_control, epsilon)

   Make these functions reusable, and ensure every run has a unique run_id and timestamp.

IMPORTANT EXECUTION RULES
- DO NOT “simulate” hardware results in text. Only show what the code computes.
- Any cell that submits IBM jobs must:
  - print the backend name
  - print job_id
  - retrieve results via the runtime job result mechanism
- Add safe-guards:
  - If IBM account is not configured, show a clear error message and instructions to set up.
  - If a backend is unavailable, automatically select least busy operational backend with enough qubits.
- Keep the notebook runnable end-to-end.

BACKEND SELECTION LOGIC (must implement)
- Use QiskitRuntimeService() with the correct channel for IBM Quantum Platform (do not guess; follow docs).
- Select backend by:
  - if user specifies BACKEND_NAME variable, try that
  - else use service.least_busy(operational=True, simulator=False, min_num_qubits >= (num_control + num_target))
- Print selected backend, number of qubits, and a short note.

NOTEBOOK EDIT INSTRUCTIONS
- Insert a new section near the top: “Configuration”
  - variables: SHOTS, BACKEND_NAME (optional), SEEDS, SWEEP grids, OUTPUT_DIR
- Replace the existing “Sampler(backend)” usage cell(s) with the V2 primitives approach:
  - Use Session(backend=backend) and SamplerV2(mode=session or mode=backend according to docs)
  - Set options using the supported options classes/fields (from IBM docs).
- Add a final section: “Run all experiments”
  - loops over sweep configs
  - runs ideal + noisy + hardware (hardware optional toggle)
  - stores everything

QUALITY BAR / THESIS-FRIENDLY STYLE
- Add short markdown explanations for:
  - what each tier means (ideal/noisy/hardware)
  - what metrics mean (TVD, success mass)
  - what the sweep is testing (compile vs mitigation vs precision)
- Keep code clean, commented, and minimal.
- Prefer stable APIs from IBM docs; if an option name is uncertain, look it up in the IBM API reference before coding it.

OUTPUT ARTIFACTS
- Create OUTPUT_DIR and save:
  - results.csv
  - results.json (include raw counts/probabilities per run, backend name, job_id when applicable)
  - figures saved as PNG (e.g., success_prob.png, tvd.png)
- Ensure saving uses deterministic filenames and includes run_id.

Finally, after implementing, add a short “How to run on IBM hardware” markdown cell:
- Steps: set token / save_account, choose backend, run cells, check job ids, where outputs saved.

DO NOT ask me for outputs. Write the cells so I can run them and get real outputs from IBM Quantum Platform.