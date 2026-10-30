"""
Animated Millennium Problem convergence CFG for priests-engine.

Nodes  = the four bridged Millennium Problems + Belnap B convergence
Edges  = structural reduction paths; each problem collapses to B via
         the Frobenius kernel

The convergence spine  RH → B, YM → B, PNP → B, SIC → B  is drawn
with gold edges. UNITY (B as sole fixed point) is the terminal node.

Animation:
  Phase 1 — build: problems appear, then the bridge edges light gold,
             then UNITY emerges.
  Phase 2 — convergence wave: pulse travels each reduction path
             simultaneously, all arriving at B/UNITY.

Output: cfg_millennium.gif
"""

from __future__ import annotations
import io
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx

OUT = Path(__file__).parent / "cfg_millennium.gif"
BG  = "#0a0a15"

_FAMILY: dict[str, str] = {
    # Millennium problems
    "RH":        "problem",
    "YM":        "problem",
    "PNP":       "problem",
    "SIC":       "problem",
    # Belnap bridge nodes
    "bnot(B)=B": "frobenius",
    "N<T=gap":   "frobenius",
    "B-circuit":  "frobenius",
    "B-fixed":   "frobenius",
    # Convergence
    "B":         "terminal_ok",
    "UNITY":     "output",
}

_FAMILY_COLOR: dict[str, str] = {
    "problem":      "#4e79a7",
    "frobenius":    "#ffd700",
    "terminal_ok":  "#59a14f",
    "output":       "#eeeeee",
}

_FROBENIUS_NODES = {"bnot(B)=B", "N<T=gap", "B-circuit", "B-fixed"}
_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))

EDGES: list[tuple[str, str]] = [
    ("RH",   "bnot(B)=B"),
    ("YM",   "N<T=gap"),
    ("PNP",  "B-circuit"),
    ("SIC",  "B-fixed"),
    ("bnot(B)=B", "B"),
    ("N<T=gap",   "B"),
    ("B-circuit",  "B"),
    ("B-fixed",   "B"),
    ("B",    "UNITY"),
]

EXEC_ORDER = [
    "RH", "YM", "PNP", "SIC",
    "bnot(B)=B", "N<T=gap", "B-circuit", "B-fixed",
    "B", "UNITY",
]

_FROBENIUS_EDGES = {
    ("bnot(B)=B", "B"), ("N<T=gap", "B"),
    ("B-circuit", "B"), ("B-fixed", "B"),
    ("B", "UNITY"),
}


def build_graph() -> nx.DiGraph:
    G = nx.DiGraph()
    for n in EXEC_ORDER:
        G.add_node(n, family=_FAMILY[n])
    for u, v in EDGES:
        G.add_edge(u, v)
    return G


def render_frame(ax, pos, base_colors, base_sizes, revealed, frob_flash,
                 pulse_center, pulse_sigma, N, title):
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.15, 1.15)
    ax.set_title(title, color="white", fontsize=8, pad=6)

    xs = np.array([pos[n][0] for n in EXEC_ORDER])
    ys = np.array([pos[n][1] for n in EXEC_ORDER])
    nidx = {n: i for i, n in enumerate(EXEC_ORDER)}

    if revealed is not None:
        for u, v in EDGES:
            if u not in revealed or v not in revealed:
                continue
            is_frob = (u, v) in _FROBENIUS_EDGES
            col = "#ffd700" if is_frob else "#3a5f80"
            lw  = 2.5 if is_frob else 1.0
            al  = 0.9 if is_frob else 0.4
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        vis = [nidx[n] for n in EXEC_ORDER if n in revealed]
        if not vis:
            return

        colors = base_colors[vis].copy()
        sizes  = base_sizes[vis].copy()

        if frob_flash:
            for i, idx in enumerate(vis):
                if EXEC_ORDER[idx] in _FROBENIUS_NODES or EXEC_ORDER[idx] in ("B", "UNITY"):
                    colors[i] = _PULSE_GOLD
                    sizes[i] *= 2.5

        ax.scatter(xs[vis], ys[vis], c=colors, s=sizes,
                   zorder=3, linewidths=1.2, edgecolors="#ffffff55")

        for n in EXEC_ORDER:
            if n in revealed:
                fam = _FAMILY[n]
                tc = "#000000" if fam in ("output", "terminal_ok") else "#ffffff"
                ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                        fontsize=6, color=tc, fontweight="bold", zorder=4)
    else:
        dists   = np.abs(np.arange(N) - pulse_center)
        dists   = np.minimum(dists, N - dists)
        weights = np.exp(-0.5 * (dists / pulse_sigma) ** 2)
        active  = {EXEC_ORDER[i] for i in range(N) if weights[i] > 0.3}

        for u, v in EDGES:
            is_frob = (u, v) in _FROBENIUS_EDGES
            near    = u in active or v in active
            if is_frob and near:
                col, lw, al = "#ffd700", 3.0, 0.95
            elif is_frob:
                col, lw, al = "#cc9900", 1.8, 0.55
            elif near:
                col, lw, al = "#cc44ff", 1.8, 0.70
            else:
                col, lw, al = "#3a5f80", 0.7, 0.22
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        blended = np.empty_like(base_colors)
        for i, n in enumerate(EXEC_ORDER):
            w = weights[i]
            target = _PULSE_GOLD if n in _FROBENIUS_NODES or n in ("B", "UNITY") \
                     else _PULSE_WHITE
            blended[i] = base_colors[i] * (1 - w) + target * w
        blended = np.clip(blended, 0, 1)
        sizes = base_sizes + base_sizes * 2.0 * weights

        ax.scatter(xs, ys, c=blended, s=sizes, zorder=3,
                   linewidths=1.2, edgecolors="#ffffff33")

        for n in EXEC_ORDER:
            fam = _FAMILY[n]
            tc = "#000000" if fam in ("output", "terminal_ok") else "#ffffff"
            ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                    fontsize=6, color=tc, fontweight="bold", zorder=4)


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def main(build_frames=50, flow_frames=80, fps=15, dpi=110):
    G = build_graph()

    pos = {
        "RH":         (0.15, 0.85),
        "YM":         (0.40, 0.85),
        "PNP":        (0.60, 0.85),
        "SIC":        (0.85, 0.85),
        "bnot(B)=B":  (0.15, 0.55),
        "N<T=gap":    (0.40, 0.55),
        "B-circuit":  (0.60, 0.55),
        "B-fixed":    (0.85, 0.55),
        "B":          (0.50, 0.28),
        "UNITY":      (0.50, 0.08),
    }

    N = len(EXEC_ORDER)
    base_colors = np.array([
        mcolors.to_rgba(_FAMILY_COLOR[_FAMILY[n]]) for n in EXEC_ORDER
    ])
    base_sizes = np.array([
        160 if n in ("B", "UNITY") else
        130 if _FAMILY[n] == "frobenius" else 100
        for n in EXEC_ORDER
    ], dtype=float)

    frob_close_idx = EXEC_ORDER.index("B")
    pulse_sigma    = max(2, N // 4)
    pulse_centers  = np.linspace(0, N - 1, flow_frames).astype(int)
    total_frames   = build_frames + flow_frames

    print(f"Rendering cfg_millennium.gif ({total_frames} frames) …")
    fig, ax = plt.subplots(figsize=(9, 7), facecolor=BG)
    frames_pil = []

    for f in range(total_frames):
        print(f"\r  {(f+1)/total_frames*100:5.1f}%", end="", flush=True)

        if f < build_frames:
            frac     = (f + 1) / build_frames
            k        = max(1, int(frac * N))
            revealed = set(EXEC_ORDER[:k])
            flash    = k - 1 == frob_close_idx
            center_n = EXEC_ORDER[k - 1]
            title = (
                f"priests-engine — Millennium Convergence | step: {center_n} | "
                f"{'B is the unique fixed point' if flash else 'RH · YM · P≠NP · SIC → B'}"
            )
            render_frame(ax, pos, base_colors, base_sizes,
                         revealed, flash, None, pulse_sigma, N, title)
        else:
            fi     = f - build_frames
            center = pulse_centers[fi]
            n_at   = EXEC_ORDER[center]
            title  = (
                f"priests-engine — Millennium Convergence | wave: {n_at} | "
                f"B is the unique bifurcation fixed point"
            )
            render_frame(ax, pos, base_colors, base_sizes,
                         None, False, center, pulse_sigma, N, title)

        frames_pil.append(fig_to_pil(fig, dpi))

    print()
    plt.close(fig)

    frames_rgb = [fr.convert("RGB") for fr in frames_pil]
    frames_rgb[0].save(str(OUT), save_all=True, append_images=frames_rgb[1:],
                       duration=1000 // fps, loop=0, optimize=False)
    print(f"Done: {OUT}  ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
