# README.md

Repository summary and operating notes for Claude Code.

## 1) Project Snapshot

This repository benchmarks Shor and Grover on three tiers:
- Ideal simulation
- Noisy simulation
- Real IBM Quantum hardware

Primary deliverables are CSV/JSON metrics plus plot artifacts used in thesis writing.

Core inputs and scripts:
- Shor notebook: `Shor-Qiskit.ipynb`
- Grover notebook: `Grover-Qiskit.ipynb`
- Cross-algorithm plot generator: `generate_thesis_plots.py`


## 2) Folder Structure (What Exists vs What Is Generated)

Top-level:
- `Shor-Qiskit.ipynb`
  - Main Shor experiment pipeline.
  - Writes outputs into `results/`.
- `Grover-Qiskit.ipynb`
  - Main Grover experiment pipeline.
  - Writes outputs into `results/grover/`.
- `generate_thesis_plots.py`
  - Reads both Shor and Grover CSV outputs.
  - Writes comparative thesis plots into `results/thesis_plots/`.
- `results/`
  - Mixed generated artifacts (Shor outputs + shared comparative plots).
- `Thesis_Results_Discussion.md`
  - Thesis-oriented narrative notes/discussion.
- `gemini-chat-research-logs/`
  - Research/chat logs (contextual notes, not runtime dependencies).
- `bckp/`
  - Backup notebook copies.
- `apikey.json`
  - IBM token helper file (secret; not to be committed/shared).


## 3) How the Structure Is Built (Execution Flow)

Run order to fully rebuild all derived outputs:

1. Execute `Shor-Qiskit.ipynb`
   - Creates `./results` via `os.makedirs(OUTPUT_DIR, exist_ok=True)`.
   - Produces:
     - `results/results.csv`
     - `results/results.json`
     - `results/success_prob_and_tvd.png`
     - `results/success_prob_bar.png`

2. Execute `Grover-Qiskit.ipynb`
   - Creates `./results/grover` via `os.makedirs(OUTPUT_DIR, exist_ok=True)`.
   - Produces:
     - `results/grover/grover_results.csv`
     - `results/grover/grover_results.json`
     - `results/grover/success_prob_and_tvd.png`
     - `results/grover/success_prob_bar.png`
     - `results/grover/search_verification.png`

3. Run `python generate_thesis_plots.py`
   - Reads:
     - `results/results.csv`
     - `results/grover/grover_results.csv`
   - Creates `results/thesis_plots` if needed.
   - Produces:
     - `results/thesis_plots/noise_sensitivity_comparison.png`
     - `results/thesis_plots/tvd_hardware_vs_noisy.png`
     - `results/thesis_plots/degradation_bar_comparison.png`


## 4) Experiment Matrix and Why There Are 48 Rows per Notebook

Both notebooks run a 4D sweep:
- Transpiler optimization level: 4 values (`[0, 1, 2, 3]`)
- Circuit-size axis: 3 values
  - Shor: control qubits `[4, 6, 8]`
  - Grover: search qubits `[2, 3, 4]`
- Resilience level: 2 values (`[0, 1]`)
- Dynamical decoupling: 2 values (`[False, True]`)

Total per algorithm: `4 * 3 * 2 * 2 = 48` runs.


## 5) Output Schemas (Quick Reference)

Shor CSV (`results/results.csv`) includes:
- IDs/metadata: `run_id`, `timestamp`, `backend`, `job_id`
- config fields: `num_control`, `num_target`, `opt_level`, `resilience_level`, `dd_enable`, `shots`
- transpilation metrics: `depth_2q`, `count_2q`, `total_depth`
- quality metrics: `ideal_success_prob`, `noisy_success_prob`, `hw_success_prob`, `tvd_noisy_vs_ideal`, `tvd_hw_vs_ideal`, `tvd_hw_vs_noisy`

Grover CSV (`results/grover/grover_results.csv`) includes all of the above-style metrics plus Grover-specific fields:
- `num_iterations`, `marked_state`, `search_space`
- `ideal_amplification`, `hw_amplification`

JSON files are richer exports:
- top-level metadata (`created`, backend, params)
- full `runs` array
- per-run probability distributions under `distributions`


## 6) Runtime Behavior Details (Important for Agents)

Authentication logic in both notebooks:
1. Try saved IBM account.
2. Fallback to `apikey.json`.
3. Fallback to interactive token prompt.

Backend selection behavior:
- If named backend is unavailable or has too few qubits, notebooks fall back to least-busy operational backend with minimum qubit count.

Noisy simulation behavior:
- Attempts backend-derived Aer noise model.
- If unavailable, falls back to generic depolarizing model.

Hardware behavior:
- Uses SamplerV2 and stores IBM `job_id` per run.
- `RUN_HARDWARE = False` can be used for fast simulation-only iterations.


## 7) Things Claude Code Should Treat Carefully

- Never expose or rewrite secrets in `apikey.json`.
- Treat `results/` as generated data; do not hand-edit results files.
- `bckp/` is archival copy space, not primary source.
- `gemini-chat-research-logs/` are notes/logs, not experiment code inputs.


## 8) Recommended Working Pattern for Changes

If changing experiment logic:
1. Edit one notebook first (Shor or Grover).
2. Re-run that notebook to regenerate its CSV/JSON.
3. Re-run `generate_thesis_plots.py` if comparative charts are affected.
4. Confirm plot outputs update under `results/thesis_plots/`.

If changing metrics/column naming:
- Keep shared cross-algorithm fields aligned where possible:
  - `depth_2q`, `count_2q`, `total_depth`
  - `ideal_success_prob`, `noisy_success_prob`, `hw_success_prob`
  - `tvd_noisy_vs_ideal`, `tvd_hw_vs_ideal`, `tvd_hw_vs_noisy`


## 9) Fast Rebuild Cheatsheet

Environment (example):

```bash
python -m venv .venv
source .venv/bin/activate
pip install "qiskit>=2.1.0" "qiskit-ibm-runtime>=0.40.1" "qiskit-aer>=0.17.0" numpy pandas matplotlib pylatexenc jinja2
```

Then:
- Run all cells in `Shor-Qiskit.ipynb`
- Run all cells in `Grover-Qiskit.ipynb`
- Run `python generate_thesis_plots.py`


## 10) FAQ-Style Clarifications

Why are there separate Shor and Grover result folders?
- Shor writes to `results/` while Grover writes to `results/grover/` to preserve algorithm-specific outputs and avoid filename collisions.

Why is there also `results/thesis_plots/`?
- It contains post-processed, publication-style comparative figures that combine both algorithms.

Why both CSV and JSON?
- CSV is compact and easy for table/stat plotting workflows.
- JSON preserves richer metadata and full distributions for deeper analysis.

Why do runs take long with hardware enabled?
- Each notebook dispatches up to 48 hardware jobs and queue delays dominate wall-time.


## 11) Ground Truth File Roles

Authoritative code/logic:
- `Shor-Qiskit.ipynb`
- `Grover-Qiskit.ipynb`
- `generate_thesis_plots.py`

Derived/generated artifacts:
- Everything in `results/` (including subfolders)

Narrative/reference docs:
- `README.md`
- `Thesis_Results_Discussion.md`
