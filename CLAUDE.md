# CLAUDE.md

Project instructions for Claude Code in this repository.
Keep this file short, practical, and focused on commands and conventions.

See @README.md for thesis-level narrative and detailed context.

## Project Summary

- This repo benchmarks Shor and Grover with Qiskit.
- Each algorithm runs across ideal simulation, noisy simulation, and IBM hardware.
- Main outputs are CSV/JSON metrics and publication figures.

## Key Files

- `Shor-Qiskit.ipynb`: Shor experiment sweep and exports.
- `Grover-Qiskit.ipynb`: Grover experiment sweep and exports.
- `generate_thesis_plots.py`: comparative figure generation from both CSV files.

## Generated Output Locations

- `results/results.csv`
- `results/results.json`
- `results/success_prob_and_tvd.png`
- `results/success_prob_bar.png`
- `results/grover/grover_results.csv`
- `results/grover/grover_results.json`
- `results/grover/success_prob_and_tvd.png`
- `results/grover/success_prob_bar.png`
- `results/grover/search_verification.png`
- `results/thesis_plots/noise_sensitivity_comparison.png`
- `results/thesis_plots/tvd_hardware_vs_noisy.png`
- `results/thesis_plots/degradation_bar_comparison.png`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install "qiskit>=2.1.0" "qiskit-ibm-runtime>=0.40.1" "qiskit-aer>=0.17.0" numpy pandas matplotlib pylatexenc jinja2
```

## Rebuild Workflow

1. Run all cells in `Shor-Qiskit.ipynb`.
2. Run all cells in `Grover-Qiskit.ipynb`.
3. Run:

```bash
python generate_thesis_plots.py
```

## Validation

There is no formal test suite in this repo. Validate by regenerating outputs and checking files:

```bash
python generate_thesis_plots.py
ls -la results
ls -la results/grover
ls -la results/thesis_plots
```

## Metrics Conventions

Shared columns should remain coherent across Shor and Grover outputs:
- `depth_2q`, `count_2q`, `total_depth`
- `ideal_success_prob`, `noisy_success_prob`, `hw_success_prob`
- `tvd_noisy_vs_ideal`, `tvd_hw_vs_ideal`, `tvd_hw_vs_noisy`

Grover-specific columns:
- `num_iterations`, `marked_state`, `search_space`
- `ideal_amplification`, `hw_amplification`

## Runtime Behavior

- Notebook auth order:
  1) saved IBM account
  2) `apikey.json`
  3) interactive token prompt
- Backend fallback: least-busy operational backend with sufficient qubits.
- Noisy sim fallback: backend noise model, then generic depolarizing model.
- Hardware execution uses SamplerV2 and records `job_id`.

## Editing Rules for Claude

- Make minimal, targeted edits.
- Do not manually edit generated files under `results/` unless explicitly requested.
- If changing metric definitions or columns, update both notebooks and plotting logic.
- Preserve directory layout unless user asks for restructuring.

## Security

- Treat `apikey.json` as secret. Never print or commit tokens.

## Performance Notes

- Hardware mode can be slow due to queueing and 48-run sweeps.
- For fast iteration, set `RUN_HARDWARE = False` in notebook config cells.
