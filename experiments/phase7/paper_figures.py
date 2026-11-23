"""Regenerate the historical Phase 7 figures:
    python -m experiments.phase7.paper_figures

Use paper1/render_audit_figures.py for the revised manuscript. The historical
Figure 8A uses an inferred alignment-disabled series for three settings.

Outputs 8 figures in results/phase7/paper_figures/:
  00_architecture.png              End-to-end ML-DSA-65 + Merkle + RS projection + Cover-bounded verifier
  01_paired_accuracy.png           Clean CIFAR-10 accuracy across matched training seeds (with means)
  02_robustness.png                252-checkpoint verdict breakdown + 512-bit overwrite utility plot
  03_strength_seed0.png            Seed-0 watermark strength (lambda) sweep
  04_false_positive_controls.png   724 null controls vs. Binomial(512, 1/2) & 358 DAMAGED threshold
  05_ecc_quantization.png          RS32 recovery & accuracy decoupling under per-tensor quantization
  06_mechanism_bce_vs_hinge.png    Logit distribution |z_i| & carrier shared-filter weight decomposition
  07_alignment_and_attacks.png     Structural obfuscation recovery (before vs. after alignment) & naive comparison
"""
import argparse
import math
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from embedding.align import evidence_threshold


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
PHASE7 = RESULTS / "phase7"
OUT = PHASE7 / "paper_figures"
DESIGNS = {
    "lam20_n256_rs32": "BCE/RS32",
    "lam20_n256_rs32_hinge1.5": "Hinge/RS32",
    "lam20_n256_rs16": "BCE/RS16",
}
COLORS = {"VERIFIED": "#00796b", "DAMAGED": "#db9b35", "REJECTED": "#a83246"}


def save(fig, outdir, name):
    fig.savefig(outdir / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


# ------------------------------------------------------------------ 00: Architecture
def architecture(outdir):
    fig, ax = plt.subplots(figsize=(10.5, 4.7))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.7)
    ax.axis("off")

    def box(x, y, w, h, title, sub="", fc="#f4f7fa", ec="#2c4a6b", title_color="#111111", lw=1.2, fs=8.3):
        patch = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.10",
            facecolor=fc, edgecolor=ec, linewidth=lw,
        )
        ax.add_patch(patch)
        if sub:
            ax.text(x + w / 2, y + h * 0.65, title, ha="center", va="center",
                    fontsize=fs, fontweight="bold", color=title_color)
            ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                    fontsize=fs - 1.2, color="#333333")
        else:
            ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                    fontsize=fs, fontweight="bold", color=title_color)

    def arrow(x1, y1, x2, y2, color="#334e68", ls="-", lw=1.25):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.32",
                            color=color, lw=lw, linestyle=ls, shrinkA=0, shrinkB=0),
        )

    # Background lane panels
    dev_panel = mpatches.FancyBboxPatch(
        (0.12, 2.48), 10.26, 2.08, boxstyle="round,pad=0.04,rounding_size=0.12",
        facecolor="#f7fafc", edgecolor="#b8c9d9", linewidth=1.0, linestyle="--",
    )
    aud_panel = mpatches.FancyBboxPatch(
        (0.12, 0.14), 10.26, 2.16, boxstyle="round,pad=0.04,rounding_size=0.12",
        facecolor="#faf9f5", edgecolor="#d4c6a8", linewidth=1.0, linestyle="--",
    )
    ax.add_patch(dev_panel)
    ax.add_patch(aud_panel)

    ax.text(0.28, 4.38, "DEVELOPER  (Commitment, Post-Quantum Signing & Watermarked Training)",
            fontsize=8.6, fontweight="bold", color="#1b3b5c", va="center")
    ax.text(0.28, 2.12, "TRUSTED AUDITOR  (White-Box Extraction, Cover-Bounded Recovery & Three-Way Verdict)",
            fontsize=8.6, fontweight="bold", color="#6b4e16", va="center")

    # Developer row boxes (RS ECC on top feeding CNN; ML-DSA-65 on bottom going cleanly down to Auditor)
    box(0.28, 3.05, 1.55, 0.92, "CIFAR-10 Dataset", "50,000 ordered imgs", fc="#e8f1f8", ec="#2c5d8a")
    box(2.15, 3.05, 1.65, 0.92, "SHA-256 Merkle", "0x00|idx|y|pixels", fc="#e8f1f8", ec="#2c5d8a")
    box(4.12, 3.05, 1.85, 0.92, "Canonical Manifest", "Root + SmallCNN meta", fc="#e8f1f8", ec="#2c5d8a")
    box(6.30, 3.48, 1.85, 0.74, "SHA-256 + RS ECC", "256 b -> 512/384 b", fc="#e6f4f1", ec="#00796b")
    box(6.30, 2.60, 1.85, 0.70, "ML-DSA-65 Sign", "FIPS 204 (3,309 B sig)", fc="#efe7f8", ec="#5c3d8c")
    box(8.48, 2.88, 1.72, 1.18, "Watermarked CNN", r"CE + $\lambda\mathcal{L}_{\mathrm{wm}}(Xv)$" + "\nBCE vs. Hinge", fc="#e6f4f1", ec="#00796b")

    arrow(1.83, 3.51, 2.15, 3.51)
    arrow(3.80, 3.51, 4.12, 3.51)
    arrow(5.97, 3.72, 6.30, 3.85)
    arrow(5.97, 3.24, 6.30, 2.98)
    arrow(8.15, 3.85, 8.48, 3.62)

    # Release transfer arrows (clean non-crossing vertical drops into Auditor)
    arrow(7.22, 2.60, 7.22, 2.30, color="#5c3d8c", ls=":")
    ax.text(7.32, 2.42, "Signed manifest + PK (1,952 B)", fontsize=6.7, color="#5c3d8c", va="center")
    arrow(9.34, 2.88, 9.34, 2.30, color="#00796b", ls=":")
    ax.text(9.42, 2.52, "Suspect\nweights", fontsize=6.8, color="#00796b", va="center")

    # Auditor row boxes
    box(0.28, 0.62, 1.95, 1.05, "1. Crypto & Model", "ML-DSA-65 verify\nSafe load, finite wts", fc="#efe7f8", ec="#5c3d8c")
    box(2.55, 0.62, 1.95, 1.05, "2. Keyed Extraction", r"$z = Xv$ (SHAKE-256)" + "\n" + r"Soft RS (erase $\leq p/2$)", fc="#fff8e8", ec="#a87920")
    box(4.82, 0.62, 2.25, 1.05, "3. Obfuscation Recovery", "Hungarian + HiGHS LP\n" + r"Cover bound $\leq 2^{-64}$", fc="#fff8e8", ec="#a87920")
    box(7.38, 1.32, 1.35, 0.56, "VERIFIED", "Exact 256 b", fc="#d9f2ee", ec=COLORS["VERIFIED"], title_color=COLORS["VERIFIED"], lw=1.4)
    box(7.38, 0.72, 1.35, 0.50, "4. Raw Tail", r"$k \geq 358 / 512$", fc="#fdf3dd", ec=COLORS["DAMAGED"], fs=7.8)
    box(8.98, 1.15, 1.22, 0.52, "DAMAGED", r"$p < 2^{-64}$", fc="#fdf3dd", ec=COLORS["DAMAGED"], title_color="#94620d", lw=1.4)
    box(8.98, 0.34, 1.22, 0.52, "REJECTED", "Fail / null", fc="#fae3e7", ec=COLORS["REJECTED"], title_color=COLORS["REJECTED"], lw=1.4)

    arrow(2.23, 1.14, 2.55, 1.14)
    arrow(4.50, 1.14, 4.82, 1.14)
    arrow(7.07, 1.46, 7.38, 1.58, color=COLORS["VERIFIED"])
    arrow(7.07, 0.98, 7.38, 0.98, color="#8a6216")
    arrow(8.73, 1.08, 8.98, 1.36, color=COLORS["DAMAGED"])
    arrow(8.73, 0.84, 8.98, 0.64, color=COLORS["REJECTED"])
    # Fail arrow from Stage 1 directly to REJECTED
    ax.plot([1.25, 1.25, 9.59, 9.59], [0.62, 0.25, 0.25, 0.34], color=COLORS["REJECTED"], lw=1.0, ls="--")
    arrow(9.59, 0.27, 9.59, 0.34, color=COLORS["REJECTED"], lw=1.0)
    ax.text(5.1, 0.32, "Any signature, structural, or full-payload check fails", fontsize=6.9, color=COLORS["REJECTED"], ha="center")

    save(fig, outdir, "00_architecture")


# ------------------------------------------------------------------ 01: Paired Accuracy
def accuracy(runs, outdir):
    data = runs[runs.run.isin(DESIGNS)].copy()
    data["design"] = data.run.map(DESIGNS)
    table = data.pivot(index="seed", columns="design", values="acc")
    table["Baseline"] = data.groupby("seed").base_acc.first()
    order = ["Baseline", "BCE/RS32", "Hinge/RS32", "BCE/RS16"]
    xs = np.array([0.0, 1.0, 2.0, 3.25])  # slight visual separation for 3-seed RS16

    fig, ax = plt.subplots(figsize=(7.4, 3.9), layout="constrained")
    colors = sns.color_palette("colorblind", len(table))
    for (seed, row), color in zip(table.iterrows(), colors):
        vals = 100 * row[order].to_numpy(dtype=float)
        # Solid line across the 5-seed core comparison (Baseline -> BCE/RS32 -> Hinge/RS32)
        ax.plot(xs[:3], vals[:3], marker="o", ms=5.5, lw=1.5, color=color, alpha=0.88, label=f"Seed {seed}")
        # Dashed connector to 3-seed BCE/RS16 where available
        if not np.isnan(vals[3]):
            ax.plot(xs[2:], vals[2:], marker="o", ms=5.5, lw=1.1, ls=":", color=color, alpha=0.75)

    # Mean markers + numeric annotations
    means = [100 * table[col].dropna().mean() for col in order]
    ax.scatter(xs, means, marker="D", s=62, color="#111111", zorder=5, label="Mean")
    offsets = [(0, 10), (0, -16), (0, 10), (0, -16)]
    for x, m, (dx, dy) in zip(xs, means, offsets):
        ax.annotate(f"{m:.2f}%", (x, m), textcoords="offset points", xytext=(dx, dy),
                    ha="center", fontsize=8.5, fontweight="bold", color="#111111",
                    bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="none", alpha=0.82))

    ax.axvline(2.62, color="#cccccc", ls="--", lw=0.9)
    ax.text(1.0, 86.45, "5 paired seeds (0–4)", ha="center", fontsize=8.2, color="#555555")
    ax.text(3.25, 86.45, "3 seeds (0–2)", ha="center", fontsize=8.2, color="#555555")
    ax.set_xticks(xs)
    ax.set_xticklabels(order)
    ax.set(ylabel="CIFAR-10 test accuracy (%)", ylim=(79.9, 86.75),
           title="Clean accuracy across matched training seeds")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)
    save(fig, outdir, "01_paired_accuracy")


# ------------------------------------------------------------------ 02: Robustness + Overwrite
def robustness(outdir):
    paths = [RESULTS / "phase6b/attack_results.csv", PHASE7 / "attack_results_hinge1.5.csv",
             PHASE7 / "attack_results_rs16.csv"]
    frames = []
    for design, path in zip(DESIGNS.values(), paths):
        table = pd.read_csv(path).query("source == 'wm'").copy()
        if not table.verdict.isin(COLORS).all():
            raise ValueError(f"Unexpected verifier outcome in {path}")
        table["design"] = design
        frames.append(table)
    data = pd.concat(frames)
    order = list(DESIGNS.values())
    counts = pd.crosstab(data.design, data.verdict).reindex(index=order, columns=["VERIFIED", "DAMAGED", "REJECTED"], fill_value=0)

    fig, (left, right) = plt.subplots(1, 2, figsize=(9.4, 3.8), layout="constrained",
                                      gridspec_kw={"width_ratios": [1.08, 1.0]})

    # Panel A: Horizontal stacked bar + crisp count labels + removal callout
    y = np.arange(len(order))
    left_pos = np.zeros(len(order))
    for v_key, v_label in [("VERIFIED", "Verified"), ("DAMAGED", "Damaged"), ("REJECTED", "Rejected")]:
        vals = counts[v_key].to_numpy()
        left.barh(y, vals, left=left_pos, height=0.52, color=COLORS[v_key], alpha=0.9, label=v_label)
        for i, val in enumerate(vals):
            if val >= 12:
                left.text(left_pos[i] + val / 2, i, str(val), ha="center", va="center",
                          color="white", fontsize=8.5, fontweight="bold")
        left_pos += vals

    # Explicit removal summary tags to the right of each bar
    removals_map = {}
    for design in order:
        sub = data[data.design == design]
        rem = sub[(sub.verdict == "REJECTED") & (sub.acc_drop <= 0.05)]
        removals_map[design] = len(rem)
    for i, design in enumerate(order):
        r_tot = int(counts.loc[design, "REJECTED"])
        r_rem = removals_map[design]
        tag = f"Rej: {r_tot}\n({r_rem} rem.)"
        t_col = COLORS["REJECTED"] if r_rem > 0 else "#444444"
        left.text(257, i, tag, va="center", ha="left", fontsize=8.0,
                  fontweight="bold" if r_rem > 0 else "normal", color=t_col)

    left.set_yticks(y)
    left.set_yticklabels(order)
    left.invert_yaxis()
    left.set(xlim=(0, 312), xlabel="Checkpoints out of 252 (incl. controls)", title="A   Verdict breakdown across 47 attacks")
    left.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.45, -0.18), ncol=3, frameon=False)

    # Panel B: 512-bit overwrite accuracy drop vs 5-point utility limit
    overwrite = data.query("attack_id == 'overwrite_512bit'")
    right.axhspan(3.0, 5.0, color="#fae3e7", alpha=0.35, zorder=0)
    right.axhline(5.0, color="#444444", linestyle="--", linewidth=1.1, label="5-point utility limit")
    right.text(2.40, 4.86, "Useful zone (≤ 5 pt drop)", ha="right", va="top", fontsize=7.5, color="#7a2333")
    for i, design in enumerate(order):
        group = overwrite[overwrite.design == design].sort_values("seed")
        for row in group.itertuples():
            xj = i + (row.seed - 1) * 0.14
            yj = 100 * row.acc_drop
            right.scatter(xj, yj, color=COLORS[row.verdict], s=58, edgecolor="white", linewidth=0.7, zorder=4)
            right.annotate(f"s{row.seed}", (xj, yj), textcoords="offset points", xytext=(0, 6),
                           ha="center", fontsize=7.3, color="#333333")
    for verdict in ["DAMAGED", "REJECTED"]:
        if verdict in set(overwrite.verdict):
            right.scatter([], [], color=COLORS[verdict], s=48, label=verdict.title())
    right.set(xticks=range(3), xticklabels=order, ylabel="Accuracy drop (percentage points)",
              title="B   512-bit overwrite, seeds 0–2", xlim=(-0.48, 2.48), ylim=(3.0, 7.2))
    right.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False)
    save(fig, outdir, "02_robustness")


# ------------------------------------------------------------------ 03: Strength sweep
def strength(runs, outdir):
    matched = runs.query("seed == 0 and wm_loss == 'bce' and ecc == 'rs32' and n_bits == 256 "
                         "and layer == 'features.6.0.weight' and mode == 'mean'").sort_values("lam")
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.4), layout="constrained")
    specs = [
        (100 * matched.acc, "Test accuracy (%)", "{:.2f}%", (82.85, 85.10), [(10, 7), (14, 7), (-6, 8)]),
        (matched.min_margin, "Minimum absolute watermark logit", "{:.2f}", (-0.15, 2.60), [(8, 8), (0, 8), (-4, 8)]),
    ]
    for ax, (y, label, fmt, ylim, offsets) in zip(axes, specs):
        ax.plot(matched.lam, y, marker="o", ms=6, color="#006d77", lw=1.8)
        for xv, yv, (dx, dy) in zip(matched.lam, y, offsets):
            ax.annotate(fmt.format(yv), (xv, yv), textcoords="offset points", xytext=(dx, dy),
                        ha="center", fontsize=8.2, color="#111111")
        ax.set(xlabel="Watermark loss weight ($\\lambda$)", ylabel=label, xticks=matched.lam, ylim=ylim)
    fig.suptitle("Watermark strength at fixed seed 0 (BCE/RS32, 256-bit payload)", fontsize=11)
    save(fig, outdir, "03_strength_seed0")


# ------------------------------------------------------------------ 04: False positives
def false_positives(outdir):
    data = pd.read_csv(RESULTS / "phase6b/false_accept.csv")
    threshold = evidence_threshold(512)
    worst = int(data.raw_agree.max())

    fig, ax = plt.subplots(figsize=(7.3, 3.6), layout="constrained")
    bins = np.arange(data.raw_agree.min() - 2, data.raw_agree.max() + 5, 4)
    ax.hist(data.raw_agree, bins=bins, density=True, color="#477da0", alpha=0.80,
            edgecolor="white", linewidth=0.5, label=f"Observed null controls ({len(data)} cases)")
    ks = np.arange(210, 366)
    pmf = np.array([math.exp(math.lgamma(513) - math.lgamma(k + 1) - math.lgamma(513 - k) - 512 * math.log(2)) for k in ks])
    ax.plot(ks, pmf, color="#111111", lw=1.4, label="Exact Binomial(512, 1/2)")
    ax.axvline(threshold, color=COLORS["DAMAGED"], linewidth=2.0,
               label=f"DAMAGED threshold ({threshold}, " + r"$p < 2^{-64}$" + ")")
    ax.annotate(f"Worst null: {worst}/512", xy=(worst, 0.002), xytext=(worst - 2, 0.013),
                ha="center", fontsize=8.3, fontweight="bold", color="#224466",
                arrowprops=dict(arrowstyle="->", color="#224466", lw=1.0))
    ax.annotate("", xy=(threshold - 1, 0.020), xytext=(worst + 1, 0.020),
                arrowprops=dict(arrowstyle="<->", color="#555555", lw=1.0))
    ax.text((threshold + worst) / 2, 0.0218, f"{threshold - worst}-bit safety gap",
            ha="center", fontsize=8.0, color="#333333")
    ax.set(xlim=(215, 366), ylim=(0, 0.039), xlabel="Codeword positions agreeing out of 512 (unaligned)",
           ylabel="Probability density",
           title=f"Negative-control distribution ({len(data)} cases: 0 VERIFIED, 0 DAMAGED)")
    ax.legend(frameon=True, facecolor="white", framealpha=0.92, edgecolor="#dddddd",
              fontsize=8.1, loc="upper right", bbox_to_anchor=(0.94, 0.98))
    save(fig, outdir, "04_false_positive_controls")


# ------------------------------------------------------------------ 05: ECC under Quantization (FIXED!)
def ecc_recovery(outdir):
    # Use the unified Phase 6b verifier outputs (no outdated "Phase 6 verifier" title!)
    data = pd.read_csv(RESULTS / "phase6b/attack_results.csv")
    data = data[(data.source == "wm") & (data.attack_id.str.fullmatch(r"quant_pt_\d+"))].copy()
    data["bits"] = data.attack_id.str.rsplit("_", n=1).str[1].astype(int)

    fig, ax = plt.subplots(figsize=(7.3, 3.7), layout="constrained")
    ax2 = ax.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.grid(False)

    # Secondary curve: mean CIFAR-10 accuracy across bit widths
    acc_curve = data.groupby("bits")["attacked_acc"].mean().reset_index().sort_values("bits")
    ax2.plot(acc_curve["bits"], 100 * acc_curve["attacked_acc"], color="#666666",
             ls="--", marker="s", ms=4.5, lw=1.4, alpha=0.85, label="Mean test accuracy (%)")
    ax2.set_ylabel("CIFAR-10 test accuracy (%)", color="#555555")
    ax2.set_ylim(0, 96)
    ax2.tick_params(axis="y", colors="#555555")

    # Primary scatter: raw codeword bit flips colored by verifier verdict
    for row in data.itertuples():
        ax.scatter(row.bits + (row.seed - 1) * 0.14, 100 * row.flip_rate,
                   s=58, color=COLORS[row.verdict], edgecolor="white", lw=0.6, zorder=4)
    for verdict in ["VERIFIED", "DAMAGED", "REJECTED"]:
        if verdict in set(data.verdict):
            ax.scatter([], [], color=COLORS[verdict], s=48, label=f"Verdict: {verdict.title()}")

    ax.annotate("3-bit: RS32 repairs 5.3 bytes avg\n→ 3/3 exact VERIFIED (acc 24.4%)",
                xy=(3.0, 1.3), xytext=(4.6, 12.5), fontsize=8.0, color=COLORS["VERIFIED"],
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["VERIFIED"], lw=1.0))
    ax.annotate("2-bit: classifier ruined\n(9.5% acc ≈ chance)",
                xy=(2.0, 29.0), xytext=(3.4, 30.0), fontsize=8.0, color=COLORS["REJECTED"],
                arrowprops=dict(arrowstyle="->", color=COLORS["REJECTED"], lw=1.0))

    ax.set(xticks=sorted(data.bits.unique()), ylim=(-2.0, 39.0),
           xlabel="Per-tensor quantization precision (bits)",
           ylabel="Raw codeword positions flipped (%)",
           title="RS32 error correction and classifier accuracy under quantization (BCE/RS32)")
    # Combine legends cleanly
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="center right", frameon=True, facecolor="white", framealpha=0.9, fontsize=8.0)
    save(fig, outdir, "05_ecc_quantization")


# ------------------------------------------------------------------ 06: Mechanism (BCE vs Hinge)
def mechanism_bce_vs_hinge(outdir):
    """Compute |logit| distributions and carrier weight-energy decomposition directly from saved checkpoints."""
    import torch
    from embedding.keys import load_key
    from embedding.projection import ProjectionWatermark, get_weight
    from training.model import SmallCNN

    wm_key_path = ROOT / "keys" / "watermark_key.bin"
    layer = "features.6.0.weight"
    groups = [
        ("Baseline", [ROOT / f"runs/baseline/seed{s}/model.pt" for s in range(3)]),
        ("Hinge 1.5/RS32", [ROOT / f"runs/wm_v1/lam20_n256_rs32_hinge1.5/seed{s}/model.pt" for s in range(3)]),
        ("BCE/RS32", [ROOT / f"runs/wm_v1/lam20_n256_rs32/seed{s}/model.pt" for s in range(3)]),
    ]

    weight_stats = {}
    logits_map = {}
    key = load_key(wm_key_path) if wm_key_path.exists() else None
    for name, paths in groups:
        shared_norms, own_norms, energy_pcts, all_z = [], [], [], []
        for p in paths:
            sd = torch.load(p, map_location="cpu", weights_only=True)
            w = sd[layer].float().flatten(1)
            c = w.mean(0)
            own = (w - c).norm(dim=1).mean().item()
            sn = c.norm().item()
            ep = 100.0 * (sn ** 2 * w.shape[0]) / (w.norm().item() ** 2)
            shared_norms.append(sn)
            own_norms.append(own)
            energy_pcts.append(ep)
            if key is not None and name != "Baseline":
                m = SmallCNN(width=32)
                m.load_state_dict(sd)
                m.eval()
                wm = ProjectionWatermark(key, layer, 512, "mean", get_weight(m, layer).shape)
                _, z = wm.extract(m)
                all_z.extend(np.abs(np.asarray(z, dtype=float)).tolist())
        weight_stats[name] = (float(np.mean(shared_norms)), float(np.mean(own_norms)), float(np.mean(energy_pcts)))
        if all_z:
            logits_map[name] = np.asarray(all_z)

    fig, (left, right) = plt.subplots(1, 2, figsize=(9.4, 3.8), layout="constrained")

    # Panel A: Logit magnitude distributions (BCE vs Hinge)
    if "BCE/RS32" in logits_map and "Hinge 1.5/RS32" in logits_map:
        bins = np.linspace(0, 14, 36)
        left.hist(np.clip(logits_map["BCE/RS32"], 0, 14), bins=bins, density=True,
                  color="#2c5d8a", alpha=0.58, edgecolor="white", lw=0.4,
                  label=f"BCE/RS32 (median {np.median(logits_map['BCE/RS32']):.2f})")
        left.hist(np.clip(logits_map["Hinge 1.5/RS32"], 0, 14), bins=bins, density=True,
                  color="#db9b35", alpha=0.72, edgecolor="white", lw=0.4,
                  label=f"Hinge 1.5/RS32 (median {np.median(logits_map['Hinge 1.5/RS32']):.2f})")
        left.axvline(1.5, color="#a83246", ls="--", lw=1.4, label="Hinge margin cap (m = 1.5)")
        left.annotate("Bits pile at cliff\n(vulnerable to overwrite)", xy=(1.55, 0.62), xytext=(4.6, 0.72),
                      fontsize=8.0, color="#7a2333", fontweight="bold",
                      arrowprops=dict(arrowstyle="->", color="#7a2333", lw=1.0))
        left.set(xlabel=r"Absolute projection logit $|z_i|$ (clipped at 14; 512 bits $\times$ 3 seeds)",
                 ylabel="Density", title="A   Projection margin distribution")
        left.legend(frameon=False, fontsize=8.0, loc="upper right")
    else:
        left.text(0.5, 0.5, "keys/watermark_key.bin not found", ha="center", va="center")

    # Panel B: Shared mean filter vs. per-filter own norm
    names = ["Baseline", "Hinge 1.5/RS32", "BCE/RS32"]
    x = np.arange(len(names))
    w = 0.34
    shared_vals = [weight_stats[n][0] for n in names]
    own_vals = [weight_stats[n][1] for n in names]
    ep_vals = [weight_stats[n][2] for n in names]

    b1 = right.bar(x - w / 2, shared_vals, w, color="#2c5d8a", label=r"Shared mean filter $\|v\|_2$")
    b2 = right.bar(x + w / 2, own_vals, w, color="#6aa84f", label="Per-filter own norm (mean)")
    for rect, sn, ep in zip(b1, shared_vals, ep_vals):
        right.text(rect.get_x() + rect.get_width() / 2, sn + 0.12, f"{sn:.2f}\n({ep:.0f}% E)",
                   ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#1b3b5c")
    for rect, on in zip(b2, own_vals):
        right.text(rect.get_x() + rect.get_width() / 2, on + 0.12, f"{on:.2f}",
                   ha="center", va="bottom", fontsize=7.8, color="#2d5a1e")

    right.set_xticks(x)
    right.set_xticklabels(names)
    right.set(ylabel="L2 norm in features.6.0.weight", ylim=(0, 6.2),
              title="B   Carrier weight-energy decomposition (seeds 0–2)")
    right.legend(frameon=False, fontsize=8.0, loc="upper left")

    save(fig, outdir, "06_mechanism_bce_vs_hinge")


# ------------------------------------------------------------------ 07: Obfuscation Recovery + Naive Comparison
def alignment_and_naive(outdir):
    fig, (left, right) = plt.subplots(1, 2, figsize=(10.2, 3.9), layout="constrained",
                                      gridspec_kw={"width_ratios": [1.0, 1.15]})

    # Panel A: Before vs After Cover-bounded alignment on structural obfuscation attacks (BCE/RS32)
    p6 = pd.read_csv(RESULTS / "phase6/attack_results.csv").query("source == 'wm'")
    p6b = pd.read_csv(RESULTS / "phase6b/attack_results.csv").query("source == 'wm'")
    obf_ids = [
        ("permute_out_carrier", "Permute\nOut"),
        ("permute_in_carrier", "Permute\nIn"),
        ("permute_all", "Permute\nAll"),
        ("scale_in_carrier_x10", "Scale In\n×10"),
        ("scale_in_carrier_x100", "Scale In\n×100"),
        ("permute_scale_in_x10", "Permute +\nScale ×10"),
    ]
    # Without alignment: Phase 6 had 0% exact verification for permute_in/all, and scale_x10/x100/permute_scale
    # fail raw exact decode (raw flip rates 23.8%, 31.9%, 51.0% exceed RS32's 16-byte error capacity).
    before_rates, after_rates = [], []
    for aid, _ in obf_ids:
        sub_b = p6b[p6b.attack_id == aid]
        after_rates.append(100.0 * (sub_b.verdict == "VERIFIED").mean())
        sub_6 = p6[p6.attack_id == aid]
        if len(sub_6):
            before_rates.append(100.0 * (sub_6.verdict == "VERIFIED").mean())
        else:
            # Unaligned exact decode rate: raw flip rate >= 15% exceeds RS32 exact decode limit
            before_rates.append(100.0 * (sub_b.flip_rate == 0).mean())

    x = np.arange(len(obf_ids))
    w = 0.36
    left.bar(x - w / 2, before_rates, w, color=COLORS["REJECTED"], alpha=0.85, label="Without alignment")
    left.bar(x + w / 2, after_rates, w, color=COLORS["VERIFIED"], alpha=0.92, label="With Cover-bounded alignment")
    for i, (b, a) in enumerate(zip(before_rates, after_rates)):
        left.text(i - w / 2 - (0.04 if b >= 100 else 0.0), b + 2.5, f"{b:.0f}%",
                  ha="center", va="bottom", fontsize=7.1, color="#7a2333")
        left.text(i + w / 2 + (0.04 if b >= 100 else 0.0), a + 2.5, f"{a:.0f}%",
                  ha="center", va="bottom", fontsize=7.1, fontweight="bold", color=COLORS["VERIFIED"])
    left.set_xticks(x)
    left.set_xticklabels([lbl for _, lbl in obf_ids], fontsize=8.0)
    left.set(ylim=(0, 118), ylabel="Exact VERIFIED rate (%)",
             title="A   Structural obfuscation recovery (BCE/RS32, 0 pt acc drop)")
    left.legend(frameon=False, fontsize=8.0, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)

    # Panel B: Naive sign-based vs Keyed projection + ECC + alignment (from scheme_comparison.csv)
    comp = pd.read_csv(PHASE7 / "scheme_comparison.csv")
    fam_labels = {
        "noise": "Noise",
        "prune_global": "Prune\nGlobal",
        "prune_layer": "Prune\nLayer",
        "quantize": "Quantize",
        "rescale": "Rescale\nOut",
        "permute": "Permute",
        "scale_in": "Scale\nIn",
    }
    fams = [f for f in fam_labels if f in set(comp.family)]
    x2 = np.arange(len(fams))
    w2 = 0.36
    for idx, (pre, label, col) in enumerate([
        ("naive", "Naive sign-based", COLORS["REJECTED"]),
        ("proj", "Projection + RS32 + align", COLORS["VERIFIED"]),
    ]):
        det = [100.0 * comp[comp.family == f][f"{pre}_detected"].mean() for f in fams]
        ver = [100.0 * comp[comp.family == f][f"{pre}_verified"].mean() for f in fams]
        pos = x2 + (idx - 0.5) * w2
        right.bar(pos, det, w2 * 0.92, color=col, alpha=0.28, label=f"{label}: traced")
        right.bar(pos, ver, w2 * 0.92, color=col, alpha=0.92, label=f"{label}: exact VERIFIED")
    right.set_xticks(x2)
    right.set_xticklabels([fam_labels[f] for f in fams], fontsize=8.0)
    right.set(ylim=(0, 112), ylabel="Mean share of attacked copies (%)",
              title="B   Naive single-weight sign vs. keyed projection")
    right.legend(frameon=False, fontsize=7.6, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)

    save(fig, outdir, "07_alignment_and_attacks")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT), help="Output directory for PNG figures")
    ap.add_argument("--also-copy", default="", help="Optional second directory for historical PNGs")
    args = ap.parse_args()
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.08,
                  rc={"axes.spines.top": False, "axes.spines.right": False})
    runs = pd.read_csv(PHASE7 / "wm_runs.csv")
    architecture(outdir)
    accuracy(runs, outdir)
    robustness(outdir)
    strength(runs, outdir)
    false_positives(outdir)
    ecc_recovery(outdir)
    mechanism_bce_vs_hinge(outdir)
    alignment_and_naive(outdir)

    if args.also_copy:
        dst = Path(args.also_copy)
        dst.mkdir(parents=True, exist_ok=True)
        for png in sorted(outdir.glob("*.png")):
            shutil.copy2(png, dst / png.name)
        print(f"Copied {len(list(outdir.glob('*.png')))} PNGs to {dst}")
    print(f"Saved 8 PNG figures to {outdir}")


if __name__ == "__main__":
    main()
