"""
Animated module dependency CFG for priests-engine.

Nodes  = the 12 Python modules
Edges  = import / dependency relationships

para_vm is the core; all other modules depend on it.
The Frobenius cluster (para_vm → para_loop → para_repl → para_vm)
is highlighted in gold.

Animation:
  Phase 1 — build: modules appear bottom-up from core; dependency
             edges light up; Frobenius cluster flashes gold.
  Phase 2 — flow wave: pulse propagates through the dependency graph.

Output: cfg_modules.gif
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

OUT = Path(__file__).parent / "cfg_modules.gif"
BG  = "#0a0a15"

_FAMILY: dict[str, str] = {
    "para_vm":         "frobenius",
    "para_repl":       "frobenius",
    "para_loop":       "frobenius",
    "para_wasm":       "link",
    "belnap_shor":     "direction",
    "para_alignment":  "direction",
    "para_rh":         "problem",
    "para_ym":         "problem",
    "para_nreg":       "problem",
    "para_temporal":   "self",
    "para_category":   "self",
    "para_multiagent": "output",
}

_FAMILY_COLOR: dict[str, str] = {
    "frobenius":  "#ffd700",
    "direction":  "#f28e2b",
    "link":       "#4e79a7",
    "problem":    "#e15759",
    "self":       "#cc44ff",
    "output":     "#eeeeee",
}

_FROBENIUS_NODES = {"para_vm", "para_repl", "para_loop"}
_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))

EDGES: list[tuple[str, str]] = [
    ("para_vm",        "para_repl"),
    ("para_vm",        "para_loop"),
    ("para_vm",        "para_wasm"),
    ("para_vm",        "belnap_shor"),
    ("para_vm",        "para_alignment"),
    ("para_vm",        "para_rh"),
    ("para_vm",        "para_ym"),
    ("para_vm",        "para_nreg"),
    ("para_vm",        "para_temporal"),
    ("para_vm",        "para_category"),
    ("para_vm",        "para_multiagent"),
    ("para_loop",      "para_repl"),     # loop feeds REPL
    ("para_repl",      "para_vm"),       # REPL drives VM — Frobenius cycle
    ("para_alignment", "belnap_shor"),
    ("para_rh",        "para_alignment"),
    ("para_ym",        "para_alignment"),
    ("para_nreg",      "para_alignment"),
    ("para_temporal",  "para_category"),
    ("para_category",  "para_multiagent"),
]

EXEC_ORDER = [
    "para_vm",
    "para_repl", "para_loop", "para_wasm",
    "belnap_shor", "para_alignment",
    "para_rh", "para_ym", "para_nreg",
    "para_temporal", "para_category", "para_multiagent",
]

_FROBENIUS_EDGES = {
    ("para_vm", "para_loop"), ("para_loop", "para_repl"), ("para_repl", "para_vm"),
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
            al  = 0.9 if is_frob else 0.35
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
                if EXEC_ORDER[idx] in _FROBENIUS_NODES:
                    colors[i] = _PULSE_GOLD
                    sizes[i] *= 2.2

        ax.scatter(xs[vis], ys[vis], c=colors, s=sizes,
                   zorder=3, linewidths=0.8, edgecolors="#ffffff44")

        for n in EXEC_ORDER:
            if n in revealed:
                fam = _FAMILY[n]
                tc = "#000000" if fam == "output" else "#ffffff"
                label = n.replace("para_", "p_")
                ax.text(pos[n][0], pos[n][1], label, ha="center", va="center",
                        fontsize=5, color=tc, fontweight="bold", zorder=4)
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
                col, lw, al = "#3a5f80", 0.7, 0.20
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        blended = np.empty_like(base_colors)
        for i, n in enumerate(EXEC_ORDER):
            w = weights[i]
            target = _PULSE_GOLD if n in _FROBENIUS_NODES else _PULSE_WHITE
            blended[i] = base_colors[i] * (1 - w) + target * w
        blended = np.clip(blended, 0, 1)
        sizes = base_sizes + base_sizes * 2.0 * weights

        ax.scatter(xs, ys, c=blended, s=sizes, zorder=3,
                   linewidths=0.8, edgecolors="#ffffff33")

        for n in EXEC_ORDER:
            fam = _FAMILY[n]
            tc = "#000000" if fam == "output" else "#ffffff"
            label = n.replace("para_", "p_")
            ax.text(pos[n][0], pos[n][1], label, ha="center", va="center",
                    fontsize=5, color=tc, fontweight="bold", zorder=4)


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def main(build_frames=50, flow_frames=80, fps=15, dpi=110):
    G = build_graph()

    pos = {
        "para_vm":         (0.50, 0.88),
        "para_repl":       (0.25, 0.70),
        "para_loop":       (0.50, 0.70),
        "para_wasm":       (0.75, 0.70),
        "belnap_shor":     (0.20, 0.50),
        "para_alignment":  (0.50, 0.50),
        "para_rh":         (0.10, 0.28),
        "para_ym":         (0.32, 0.28),
        "para_nreg":       (0.54, 0.28),
        "para_temporal":   (0.72, 0.50),
        "para_category":   (0.85, 0.35),
        "para_multiagent": (0.85, 0.15),
    }

    N = len(EXEC_ORDER)
    base_colors = np.array([
        mcolors.to_rgba(_FAMILY_COLOR[_FAMILY[n]]) for n in EXEC_ORDER
    ])
    base_sizes = np.array([
        160 if n == "para_vm" else
        120 if _FAMILY[n] == "frobenius" else 80
        for n in EXEC_ORDER
    ], dtype=float)

    frob_close_idx = EXEC_ORDER.index("para_loop")
    pulse_sigma    = max(3, N // 5)
    pulse_centers  = np.linspace(0, N - 1, flow_frames).astype(int)
    total_frames   = build_frames + flow_frames

    print(f"Rendering cfg_modules.gif ({total_frames} frames) …")
    fig, ax = plt.subplots(figsize=(9, 9), facecolor=BG)
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
                f"priests-engine — Module Graph | build: {center_n} | "
                f"{'Frobenius loop closed! μ∘δ=id' if flash else 'para_vm core'}"
            )
            render_frame(ax, pos, base_colors, base_sizes,
                         revealed, flash, None, pulse_sigma, N, title)
        else:
            fi     = f - build_frames
            center = pulse_centers[fi]
            n_at   = EXEC_ORDER[center]
            title  = (
                f"priests-engine — Module Graph | wave: {n_at} | "
                f"12 modules · μ∘δ=id"
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
