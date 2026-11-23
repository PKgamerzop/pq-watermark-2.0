"""Regenerate the revised manuscript figures from recorded artifacts.

Run from any directory with matplotlib and CPU PyTorch installed.
Only manuscript PNGs are written. No watermark key is needed.
"""
import argparse
import csv
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = Path(__file__).resolve().parent / "figures"
DESIGNS = {
    "BCE/RS32": ("phase6b/attack_results.csv", "lam20_n256_rs32", "#00726f"),
    "BCE/RS16": ("phase7/attack_results_rs16.csv", "lam20_n256_rs16", "#435a86"),
    "Hinge/RS32": ("phase7/attack_results_hinge1.5.csv", "lam20_n256_rs32_hinge1.5", "#a14717"),
}
VERDICT_COLORS = {"VERIFIED": "#00726f", "DAMAGED": "#a14717", "REJECTED": "#a52e58"}


def read_rows(name):
    with (RESULTS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def save(fig, name, out):
    fig.savefig(out / name, dpi=300, facecolor="white")
    plt.close(fig)


def workflow(out):
    fig, ax = plt.subplots(figsize=(8.8, 3.2), layout="constrained")
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    rows = (
        (0.77, ("Commit ordered dataset\nSHA-256 Merkle root",
                "Sign manifest\nML-DSA-65",
                "RS-encode digest\n256-bit payload",
                "Train marked classifier\nKeyed weight projection")),
        (0.29, ("Check release and model\nTrusted public key",
                "Read raw carrier\nPinned profile + secret key",
                "Retry failed extraction\nAssignment and scale fit",
                "Issue verdict\nUse exact or raw evidence")),
    )
    xs = (0.115, 0.370, 0.625, 0.880)
    for y, labels in rows:
        for x, label in zip(xs, labels):
            ax.text(x, y, label, ha="center", va="center", fontsize=9, color="#17354a",
                    bbox={"boxstyle": "round,pad=.65", "fc": "#edf4f7", "ec": "#67879b"})
        for start, end in zip(xs, xs[1:]):
            ax.annotate("", xy=(end - .111, y), xytext=(start + .111, y),
                        arrowprops={"arrowstyle": "->", "color": "#456474", "lw": 1.3})
    ax.text(.01, .98, "Release preparation", fontsize=10, weight="bold", va="top")
    ax.text(.01, .53, "White-box verification", fontsize=10, weight="bold", va="top")
    ax.text(.5, .03, "Exact digest match: VERIFIED   •   Residual threshold: DAMAGED   •   Otherwise: REJECTED",
            ha="center", fontsize=8.5)
    save(fig, "00_architecture.png", out)


def controls(out):
    rows = read_rows("phase6b/false_accept.csv")
    scores = [int(row["raw_agree"]) for row in rows]
    threshold = 358
    fig, ax = plt.subplots(figsize=(4.5, 2.65), layout="constrained")
    ax.hist(scores, bins=range(min(scores) // 5 * 5, max(scores) + 6, 5), color="#435a86")
    ax.axvline(threshold, color="#a14717", ls="--", lw=1.5, label=f"Threshold: {threshold}")
    ax.axvline(max(scores), color="#344957", ls=":", lw=1.4, label=f"Observed maximum: {max(scores)}")
    ax.set(xlabel="Raw agreements out of 512", ylabel="Recorded cases",
           title=f"RS32 extraction controls ({len(scores)} cases)", xlim=(min(scores) - 4, threshold + 10))
    ax.legend(frameon=False, loc="upper right", bbox_to_anchor=(.94, 1))
    save(fig, "04_false_positive_controls.png", out)


def quantization(out):
    rows = [r for r in read_rows(DESIGNS["BCE/RS32"][0])
            if r["source"] == "wm" and r["attack_id"].startswith("quant_pt_")]
    bits = sorted({int(r["attack_id"].rsplit("_", 1)[1]) for r in rows})
    groups = {n: [r for r in rows if r["attack_id"] == f"quant_pt_{n}"] for n in bits}
    fig, ax = plt.subplots(figsize=(4.5, 3.05), layout="constrained")
    acc = ax.twinx()
    acc.spines["right"].set_visible(True)
    acc.plot(bits, [mean(float(r["attacked_acc"]) for r in groups[n]) for n in bits],
             color="#52616e", ls="--", marker="s", markersize=3, label="Mean accuracy")
    for verdict in VERDICT_COLORS:
        examples = [(n + (int(r["seed"]) - 1) * .09, float(r["flip_rate"]))
                    for n in bits for r in groups[n] if r["verdict"] == verdict]
        if examples:
            ax.scatter(*zip(*examples), color=VERDICT_COLORS[verdict], s=20, label=verdict.title())
    ax.set(xlabel="Per-tensor quantization (bits)", ylabel="Raw sign changes", xticks=bits, ylim=(-.02, .40))
    acc.set(ylabel="CIFAR-10 test accuracy", ylim=(0, 1))
    for axis in (ax.yaxis, acc.yaxis):
        axis.set_major_formatter(PercentFormatter(1, decimals=0))
    handles, labels = ax.get_legend_handles_labels()
    other_handles, other_labels = acc.get_legend_handles_labels()
    ax.legend(handles + other_handles, labels + other_labels, frameon=False, loc="upper center", ncol=2)
    save(fig, "05_ecc_quantization.png", out)


def carrier_measurements(out):
    import torch

    runs = {
        "Baseline": (ROOT / "runs/baseline", "#52616e"),
        **{name: (ROOT / "runs/wm_v1" / run, color)
           for name, (_, run, color) in DESIGNS.items() if name != "BCE/RS16"},
    }
    fig, (left, right) = plt.subplots(1, 2, figsize=(8.7, 2.75), layout="constrained")
    for index, (name, (path, color)) in enumerate(runs.items()):
        for seed, marker in enumerate(("o", "s", "^")):
            state = torch.load(path / f"seed{seed}/model.pt", map_location="cpu", weights_only=True)
            filters = state["features.6.0.weight"].float().flatten(1)
            shared = filters.mean(dim=0).norm().item()
            energy = filters.shape[0] * shared ** 2 / filters.norm().item() ** 2
            x = index + .12 * (seed - 1)
            left.scatter(x, shared, color=color, s=30, marker=marker, label=f"Seed {seed}" if index == 0 else None)
            right.scatter(x, energy, color=color, s=30, marker=marker)
    for ax in (left, right):
        ax.set_xticks(range(len(runs)), runs.keys())
        ax.set_xlim(-.45, len(runs) - .55)
    left.set(ylabel="Shared mean-filter norm", ylim=(0, 5.5))
    right.set(ylabel="Shared fraction of layer energy", ylim=(0, 1.05))
    right.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    left.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(.5, -.14))
    save(fig, "06_mechanism_bce_vs_hinge.png", out)


def alignment_and_naive(out):
    variants = {
        "permute_out_carrier": "Permute out",
        "permute_in_carrier": "Permute in",
        "permute_all": "Permute all",
        "scale_in_carrier_x2": "Scale in ×2",
        "scale_in_carrier_x10": "Scale in ×10",
        "scale_in_carrier_x100": "Scale in ×100",
        "permute_scale_in_x10": "Permute + scale ×10",
    }
    fig, (left, right) = plt.subplots(1, 2, figsize=(9.3, 4.2), layout="constrained")
    for index, (design, (source, _, color)) in enumerate(DESIGNS.items()):
        rows = [r for r in read_rows(source) if r["source"] == "wm"]
        groups = [[r for r in rows if r["attack_id"] == key] for key in variants]
        positions = [item + .22 * (index - 1) for item in range(len(groups))]
        means = [mean(float(row["flip_rate"]) for row in group) for group in groups]
        left.barh(positions, means, height=.20, color=color, label=design)
        for y, value, group in zip(positions, means, groups):
            exact = sum(row["verdict"] == "VERIFIED" for row in group)
            left.text(value + .008, y, f"{exact}/{len(group)}", va="center", fontsize=7, color=color)
    left.set_yticks(range(len(variants)), variants.values())
    left.invert_yaxis()
    left.set(xlim=(0, .64), xlabel="Mean raw sign-change rate",
             title="A  Structural edits · saved verdicts")
    left.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    left.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(.5, -.17), ncol=3)

    rows = read_rows("phase7/scheme_comparison.csv")
    families = {
        "noise": "Noise", "prune_global": "Global\nprune", "prune_layer": "Layer\nprune",
        "quantize": "Quant.", "rescale": "Scale\nout", "permute": "Permute", "scale_in": "Scale\nin",
    }
    for offset, (prefix, label, color) in zip((-.18, .18), (
        ("naive", "Naive", "#a14717"), ("proj", "Projection", "#00726f"),
    )):
        groups = [[r for r in rows if r["family"] == family] for family in families]
        positions = [item + offset for item in range(len(groups))]
        for metric, opacity, label_suffix in (("detected", .3, "exact or residual"), ("verified", 1, "exact")):
            rates = [mean(float(r[f"{prefix}_{metric}"]) for r in group) for group in groups]
            right.bar(positions, rates, width=.33, color=color, alpha=opacity, label=f"{label}: {label_suffix}")
    right.set_xticks(range(len(families)), families.values())
    right.set(ylim=(0, 1.04), ylabel="Mean rate over configurations", title="B  Exploratory pipeline comparison")
    right.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    right.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(.5, -.17), ncol=2)
    save(fig, "07_alignment_and_attacks.png", out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=FIGURES)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
    for render in (workflow, controls, quantization, carrier_measurements, alignment_and_naive):
        render(args.out)


if __name__ == "__main__":
    main()
