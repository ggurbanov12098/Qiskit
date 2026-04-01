#!/usr/bin/env python3
"""
generate_thesis_plots.py
========================
Publication-ready comparative visualizations for Master's thesis:
"Dual Cryptographic Threats of Shor's and Grover's Algorithms"

Reads:
    results/results.csv           (Shor — 48 configurations)
    results/grover/grover_results.csv  (Grover — 48 configurations)

Outputs (saved to results/thesis_plots/):
    1. noise_sensitivity_comparison.png
       — Success probability vs. 2q-depth for both algorithms on same axes
    2. tvd_hardware_vs_noisy.png
       — TVD(HW, Ideal) and TVD(Noisy, Ideal) across optimisation levels
    3. degradation_bar_comparison.png
       — Side-by-side degradation percentages at comparable circuit depths

Usage:
    python generate_thesis_plots.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ─── Configuration ───────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join("results", "thesis_plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SHOR_CSV = os.path.join("results", "results.csv")
GROVER_CSV = os.path.join("results", "grover", "grover_results.csv")

# Publication styling
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 11,
    "font.family": "serif",
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "legend.fontsize": 9,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

# Color palette — distinguishable in print and for color-blind readers
C_SHOR_HW = "#1f77b4"      # blue
C_SHOR_NOISY = "#aec7e8"   # light blue
C_GROVER_HW = "#d62728"    # red
C_GROVER_NOISY = "#ff9896" # light red
C_IDEAL = "#2ca02c"        # green


# ─── Load Data ───────────────────────────────────────────────────────────────
print("Loading CSVs...")
shor = pd.read_csv(SHOR_CSV)
grover = pd.read_csv(GROVER_CSV)

# Normalize column names for unified processing
# Shor uses "num_control" for circuit size; Grover uses "num_qubits"
shor["algorithm"] = "Shor"
shor["circuit_label"] = shor["num_control"].apply(lambda x: f"{x}-ctrl ({x+4} qubits)")
shor["circuit_size"] = shor["num_control"]

grover["algorithm"] = "Grover"
grover["circuit_label"] = grover["num_qubits"].apply(lambda x: f"{x}-qubit (N={2**x})")
grover["circuit_size"] = grover["num_qubits"]

# Compute degradation from ideal (percentage points lost)
shor["hw_degradation"] = shor["ideal_success_prob"] - shor["hw_success_prob"]
shor["noisy_degradation"] = shor["ideal_success_prob"] - shor["noisy_success_prob"]
grover["hw_degradation"] = grover["ideal_success_prob"] - grover["hw_success_prob"]
grover["noisy_degradation"] = grover["ideal_success_prob"] - grover["noisy_success_prob"]

print(f"  Shor:   {len(shor)} rows, circuit sizes: {sorted(shor['circuit_size'].unique())}")
print(f"  Grover: {len(grover)} rows, circuit sizes: {sorted(grover['circuit_size'].unique())}")


# ═════════════════════════════════════════════════════════════════════════════
# PLOT 1: Noise Sensitivity Comparison
#         Y-axis: Success Probability | X-axis: 2q-Depth
#         Both algorithms on the same axes
# ═════════════════════════════════════════════════════════════════════════════

def plot_noise_sensitivity():
    """
    Aggregates runs by (algorithm, circuit_size, opt_level) taking the mean
    across resilience/DD variants, then plots success probability vs 2q-depth.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

    # --- Panel A: Hardware Success Probability vs 2q-Depth ---
    ax = axes[0]
    ax.set_title("(a) Hardware Success Probability vs. Circuit Depth")

    # Aggregate: mean across resilience_level and dd_enable for each (size, opt)
    for df, algo, color, marker in [
        (shor, "Shor", C_SHOR_HW, "o"),
        (grover, "Grover", C_GROVER_HW, "s"),
    ]:
        for size in sorted(df["circuit_size"].unique()):
            sub = df[df["circuit_size"] == size]
            agg = sub.groupby("opt_level").agg(
                depth_2q=("depth_2q", "first"),
                hw_mean=("hw_success_prob", "mean"),
                hw_std=("hw_success_prob", "std"),
            ).reset_index()

            label_str = sub["circuit_label"].iloc[0]
            ax.errorbar(
                agg["depth_2q"], agg["hw_mean"], yerr=agg["hw_std"],
                marker=marker, markersize=6, capsize=3, linewidth=1.5,
                label=f"{algo} {label_str}",
                color=color, alpha=0.6 + 0.4 * (size / df["circuit_size"].max()),
            )

    ax.set_xlabel("Two-Qubit Gate Depth")
    ax.set_ylabel("Success Probability")
    ax.set_ylim(-0.02, 1.05)
    ax.legend(loc="lower left", framealpha=0.9, ncol=1)
    ax.axhline(y=0.25, color="gray", linestyle=":", alpha=0.4, label="Random (Shor)")

    # --- Panel B: Degradation from Ideal vs 2q-Depth ---
    ax = axes[1]
    ax.set_title("(b) Degradation from Ideal vs. Circuit Depth")

    for df, algo, color, marker in [
        (shor, "Shor", C_SHOR_HW, "o"),
        (grover, "Grover", C_GROVER_HW, "s"),
    ]:
        for size in sorted(df["circuit_size"].unique()):
            sub = df[df["circuit_size"] == size]
            agg = sub.groupby("opt_level").agg(
                depth_2q=("depth_2q", "first"),
                deg_mean=("hw_degradation", "mean"),
                deg_std=("hw_degradation", "std"),
            ).reset_index()

            label_str = sub["circuit_label"].iloc[0]
            ax.errorbar(
                agg["depth_2q"], agg["deg_mean"], yerr=agg["deg_std"],
                marker=marker, markersize=6, capsize=3, linewidth=1.5,
                label=f"{algo} {label_str}",
                color=color, alpha=0.6 + 0.4 * (size / df["circuit_size"].max()),
            )

    ax.set_xlabel("Two-Qubit Gate Depth")
    ax.set_ylabel("Success Probability")  # shared y with panel a
    ax.set_ylim(-0.02, 1.05)
    ax.legend(loc="upper left", framealpha=0.9, ncol=1)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "noise_sensitivity_comparison.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ═════════════════════════════════════════════════════════════════════════════
# PLOT 2: TVD — Hardware vs Noisy Simulation across Optimisation Levels
# ═════════════════════════════════════════════════════════════════════════════

def plot_tvd_comparison():
    """
    Grouped bar chart: TVD(HW, Ideal) and TVD(Noisy, Ideal) for each
    (algorithm, largest circuit size, optimisation level).
    Focuses on the largest circuits where noise impact is most visible.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    datasets = [
        (shor, "Shor", shor["circuit_size"].max(), C_SHOR_HW, C_SHOR_NOISY),
        (grover, "Grover", grover["circuit_size"].max(), C_GROVER_HW, C_GROVER_NOISY),
    ]

    for idx, (df, algo, max_size, c_hw, c_noisy) in enumerate(datasets):
        ax = axes[idx]
        sub = df[df["circuit_size"] == max_size]
        label_str = sub["circuit_label"].iloc[0]

        agg = sub.groupby("opt_level").agg(
            tvd_hw_mean=("tvd_hw_vs_ideal", "mean"),
            tvd_hw_std=("tvd_hw_vs_ideal", "std"),
            tvd_noisy_mean=("tvd_noisy_vs_ideal", "mean"),
            tvd_noisy_std=("tvd_noisy_vs_ideal", "std"),
            depth_2q=("depth_2q", "first"),
        ).reset_index()

        x = np.arange(len(agg))
        w = 0.35

        bars1 = ax.bar(
            x - w/2, agg["tvd_hw_mean"], w,
            yerr=agg["tvd_hw_std"], capsize=4,
            color=c_hw, label="TVD(Hardware, Ideal)", alpha=0.85,
        )
        bars2 = ax.bar(
            x + w/2, agg["tvd_noisy_mean"], w,
            yerr=agg["tvd_noisy_std"], capsize=4,
            color=c_noisy, label="TVD(Noisy Sim, Ideal)", alpha=0.85,
        )

        # Annotate 2q-depth on each group
        for i, row in agg.iterrows():
            ax.text(
                i, max(row["tvd_hw_mean"], row["tvd_noisy_mean"]) + 0.04,
                f"d={int(row['depth_2q'])}",
                ha="center", fontsize=8, style="italic", color="gray",
            )

        ax.set_xlabel("Transpiler Optimisation Level")
        ax.set_ylabel("Total Variation Distance")
        ax.set_title(f"{algo} — {label_str}")
        ax.set_xticks(x)
        ax.set_xticklabels([f"Opt {int(v)}" for v in agg["opt_level"]])
        ax.set_ylim(0, 1.15)
        ax.legend(loc="upper right", framealpha=0.9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "tvd_hardware_vs_noisy.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ═════════════════════════════════════════════════════════════════════════════
# PLOT 3 (bonus): Side-by-side degradation bar at comparable depths
# ═════════════════════════════════════════════════════════════════════════════

def plot_degradation_bars():
    """
    Direct comparison at similar 2q-depths:
      Shor 4-ctrl opt=0 (depth=218) vs Grover 4-qubit opt=0 (depth=219)
      Shor 4-ctrl opt=2 (depth=155) vs Grover 4-qubit opt=2 (depth=111)
    Shows percentage degradation from ideal for noisy sim and hardware.
    """
    fig, ax = plt.subplots(figsize=(10, 5.5))

    # Extract specific comparison points
    comparisons = []

    # Pair 1: opt=0, nearly identical depth
    s0 = shor[(shor["circuit_size"] == 4) & (shor["opt_level"] == 0)]
    g0 = grover[(grover["circuit_size"] == 4) & (grover["opt_level"] == 0)]
    comparisons.append({
        "label": f"Shor 4-ctrl\nopt=0, d={int(s0['depth_2q'].iloc[0])}",
        "noisy_deg": s0["noisy_degradation"].mean() * 100,
        "hw_deg": s0["hw_degradation"].mean() * 100,
        "algo": "Shor",
    })
    comparisons.append({
        "label": f"Grover 4-qubit\nopt=0, d={int(g0['depth_2q'].iloc[0])}",
        "noisy_deg": g0["noisy_degradation"].mean() * 100,
        "hw_deg": g0["hw_degradation"].mean() * 100,
        "algo": "Grover",
    })

    # Pair 2: opt=2, best transpilation
    s2 = shor[(shor["circuit_size"] == 4) & (shor["opt_level"] == 2)]
    g2 = grover[(grover["circuit_size"] == 4) & (grover["opt_level"] == 2)]
    comparisons.append({
        "label": f"Shor 4-ctrl\nopt=2, d={int(s2['depth_2q'].iloc[0])}",
        "noisy_deg": s2["noisy_degradation"].mean() * 100,
        "hw_deg": s2["hw_degradation"].mean() * 100,
        "algo": "Shor",
    })
    comparisons.append({
        "label": f"Grover 4-qubit\nopt=2, d={int(g2['depth_2q'].iloc[0])}",
        "noisy_deg": g2["noisy_degradation"].mean() * 100,
        "hw_deg": g2["hw_degradation"].mean() * 100,
        "algo": "Grover",
    })

    # Pair 3: opt=3
    s3 = shor[(shor["circuit_size"] == 4) & (shor["opt_level"] == 3)]
    g3 = grover[(grover["circuit_size"] == 4) & (grover["opt_level"] == 3)]
    comparisons.append({
        "label": f"Shor 4-ctrl\nopt=3, d={int(s3['depth_2q'].iloc[0])}",
        "noisy_deg": s3["noisy_degradation"].mean() * 100,
        "hw_deg": s3["hw_degradation"].mean() * 100,
        "algo": "Shor",
    })
    comparisons.append({
        "label": f"Grover 4-qubit\nopt=3, d={int(g3['depth_2q'].iloc[0])}",
        "noisy_deg": g3["noisy_degradation"].mean() * 100,
        "hw_deg": g3["hw_degradation"].mean() * 100,
        "algo": "Grover",
    })

    labels = [c["label"] for c in comparisons]
    noisy_vals = [c["noisy_deg"] for c in comparisons]
    hw_vals = [c["hw_deg"] for c in comparisons]
    bar_colors_hw = [C_SHOR_HW if c["algo"] == "Shor" else C_GROVER_HW for c in comparisons]
    bar_colors_noisy = [C_SHOR_NOISY if c["algo"] == "Shor" else C_GROVER_NOISY for c in comparisons]

    x = np.arange(len(labels))
    w = 0.35

    bars_n = ax.bar(x - w/2, noisy_vals, w, color=bar_colors_noisy,
                    label="Noisy Sim Degradation", edgecolor="gray", linewidth=0.5)
    bars_h = ax.bar(x + w/2, hw_vals, w, color=bar_colors_hw,
                    label="Hardware Degradation", edgecolor="gray", linewidth=0.5)

    # Value labels on bars
    for bar in bars_n:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.8, f"{h:.1f}%",
                ha="center", va="bottom", fontsize=8)
    for bar in bars_h:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.8, f"{h:.1f}%",
                ha="center", va="bottom", fontsize=8)

    # Separator lines between pairs
    for sep in [1.5, 3.5]:
        ax.axvline(x=sep, color="gray", linestyle=":", alpha=0.4)

    ax.set_xlabel("Algorithm & Configuration")
    ax.set_ylabel("Degradation from Ideal (%)")
    ax.set_title("Success Probability Degradation: Shor vs. Grover at Comparable Depths")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(loc="upper left", framealpha=0.9)
    ax.set_ylim(0, max(hw_vals) * 1.25)

    # Pair labels
    for i, pair_label in enumerate(["opt=0 (~220 depth)", "opt=2 (optimised)", "opt=3 (aggressive)"]):
        ax.text(i * 2 + 0.5, ax.get_ylim()[1] * 0.95, pair_label,
                ha="center", fontsize=9, weight="bold", color="dimgray")

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "degradation_bar_comparison.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\nGenerating thesis plots...\n")
    plot_noise_sensitivity()
    plot_tvd_comparison()
    plot_degradation_bars()
    print(f"\nAll plots saved to {os.path.abspath(OUTPUT_DIR)}/")
    print("These are 300 DPI, publication-ready for IEEE Overleaf import.")
