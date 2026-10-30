"""
Actual-execution CFG for priests-engine.

Traces a real priests-engine run (kernel_run + ParaVM + REPL dispatch)
using sys.settrace to capture every function call. Builds a directed call
graph from the live trace, then animates it in call-order.

Nodes  = functions that actually fired, labelled by name + module
Edges  = (caller, callee) pairs from the live trace
Gold   = the Frobenius kernel functions: kernel_fsplit, kernel_ffuse,
         kernel_step, kernel_engager

Output: cfg_execution.gif
"""

from __future__ import annotations
import sys
import io
import collections
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx

# ── add priests-engine to path ────────────────────────────────────────────────
REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

OUT = Path(__file__).parent / "cfg_execution.gif"
BG  = "#0a0a15"

# ── trace collector ───────────────────────────────────────────────────────────

_WATCH_FILES = {
    "para_vm", "para_repl", "para_loop",
    "para_rh", "para_ym", "para_nreg",
    "para_alignment", "belnap_shor",
    "para_temporal", "para_category", "para_multiagent",
}

def _short(name: str) -> str:
    return name.replace("para_", "p_").replace("kernel_", "k_").replace("b4_", "b4.")

def collect_trace(n_steps: int = 6) -> tuple[list[str], list[tuple[str, str]]]:
    """Run the kernel for n_steps and trace actual call graph."""
    call_stack: list[str] = []
    edges_seen: dict[tuple[str, str], int] = {}
    order: list[str] = []
    seen_nodes: set[str] = set()

    def tracer(frame, event, arg):
        module = frame.f_globals.get("__name__", "")
        fname  = frame.f_code.co_name
        mod_short = module.split(".")[-1]

        if mod_short not in _WATCH_FILES:
            return tracer

        node = f"{_short(fname)}"

        if event == "call":
            if node not in seen_nodes:
                seen_nodes.add(node)
                order.append(node)
            if call_stack:
                edge = (call_stack[-1], node)
                edges_seen[edge] = edges_seen.get(edge, 0) + 1
            call_stack.append(node)

        elif event == "return":
            if call_stack and call_stack[-1] == node:
                call_stack.pop()

        return tracer

    from para_vm import (KernelState, B4, kernel_run, ParaVM,
                         kernel_fsplit, kernel_ffuse, kernel_step,
                         kernel_engager, b4_join, b4_meet, b4_bnot,
                         b4_band, b4_bor, b4_designated, b4_dialetheic,
                         b4_approx_le, dialetheicImage,
                         B_is_the_only_bifurcation_point,
                         dialetheic_alignment_tri,
                         measure_cost, measure_step, collapse_irreversible)
    from para_repl import (do_command, show_regs, show_snap, show_prog,
                           do_instruction, _b4_color, _reg_line,
                           _dist_bar, _snap_line)
    from para_rh   import main as rh_main
    from para_ym   import main as ym_main
    from para_nreg import main as nreg_main
    from para_alignment import (dialetheicShor,
                                classical_cannot_become_B,
                                sustain_never_collapses)
    from para_temporal  import (generate_trajectory, temporal_always,
                                temporal_eventually, temporal_next,
                                always_B_registers, winding_invariant,
                                temporal_is_O_inf)
    from para_category  import (band_B_idempotent,
                                frobenius_as_terminal_morphism,
                                category_is_O_inf)
    from para_multiagent import (MultiAgentState, init_multi,
                                 multi_step, multi_allB_init)

    sys.settrace(tracer)

    # 1. Kernel run
    s = KernelState(r0=B4.B, r1=B4.N, r2=B4.T)
    kernel_run(s, n_steps)

    # 2. Individual kernel ops
    kernel_fsplit(B4.B)
    kernel_ffuse(B4.T, B4.F)
    kernel_engager(B4.B)

    # 3. Belnap ops
    b4_join(B4.B, B4.N); b4_meet(B4.T, B4.F)
    b4_bnot(B4.B); b4_band(B4.B, B4.T); b4_bor(B4.F, B4.N)
    b4_designated(B4.B); b4_dialetheic(B4.B); b4_approx_le(B4.N, B4.B)
    dialetheicImage(B4.B)
    B_is_the_only_bifurcation_point()
    dialetheic_alignment_tri()
    measure_cost(B4.B, B4.T); measure_step(B4.B, B4.N)
    collapse_irreversible(B4.T)

    # 4. VM execution
    vm = ParaVM()
    prog = """
PUSH B
PUSH N
BAND r0 r1
BOR r0 r1
BNOT r0
FSPLIT r0 r1 r2
FFUSE r1 r2 r0
EVALT r0
"""
    try:
        vm.load(prog)
        vm.run(steps=8)
        show_regs(vm); show_snap(vm); show_prog(vm)
        _b4_color(B4.B); _reg_line(0, B4.B, 0, False)
        _snap_line(vm)
    except Exception:
        pass

    # 5. Millennium bridges
    try:
        rh_main()
    except Exception:
        pass
    try:
        ym_main()
    except Exception:
        pass
    try:
        nreg_main()
    except Exception:
        pass

    # 6. Alignment
    try:
        dialetheicShor(2, 15)
        classical_cannot_become_B(B4.N)
        sustain_never_collapses(3)
    except Exception:
        pass

    # 7. Temporal / Category / Multiagent
    try:
        traj = generate_trajectory(8)
        temporal_always(traj, lambda x: x == B4.B)
        temporal_eventually(traj, lambda x: x == B4.B)
        temporal_next(traj, 0)
        always_B_registers(8)
        winding_invariant(8)
        temporal_is_O_inf()
    except Exception:
        pass
    try:
        band_B_idempotent()
        frobenius_as_terminal_morphism()
        category_is_O_inf()
    except Exception:
        pass
    try:
        ms = init_multi(n=3)
        ms2 = multi_step(ms)
        multi_allB_init(n=3)
    except Exception:
        pass

    sys.settrace(None)

    # Build edge list deduplicated, weighted by call count
    edges = [(u, v) for (u, v), cnt in edges_seen.items() if cnt >= 1]
    return order, edges


# ── colour assignment ─────────────────────────────────────────────────────────

_FROBENIUS = {"k_fsplit", "k_ffuse", "k_step", "k_engager",
              "kernel_run"}
_BELNAP    = {"b4.join", "b4.meet", "b4.bnot", "b4.band", "b4.bor",
              "b4.designated", "b4.dialetheic", "b4.approx_le",
              "b4.to_wh2", "wh2_to_b4"}
_VM        = {"assemble", "load", "step", "run", "reset"}
_REPL      = {"do_command", "show_regs", "show_snap", "repl",
              "do_instruction", "_reg_line", "_snap_line"}

_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))

def _family(n: str) -> str:
    if n in _FROBENIUS:  return "frobenius"
    if n in _BELNAP:     return "belnap"
    if n in _VM:         return "vm"
    if n in _REPL:       return "repl"
    return "other"

_FAM_COLOR = {
    "frobenius": "#ffd700",
    "belnap":    "#f28e2b",
    "vm":        "#4e79a7",
    "repl":      "#cc44ff",
    "other":     "#9c9c9c",
}


# ── rendering ─────────────────────────────────────────────────────────────────

def render_frame(ax, pos, nodes, base_colors, base_sizes,
                 frob_nodes, revealed, frob_flash,
                 pulse_center, pulse_sigma, edges, title):
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_title(title, color="white", fontsize=7, pad=5)

    N    = len(nodes)
    nidx = {n: i for i, n in enumerate(nodes)}
    xs   = np.array([pos[n][0] for n in nodes])
    ys   = np.array([pos[n][1] for n in nodes])

    _frob_edges = {(u, v) for (u, v) in edges
                   if u in frob_nodes or v in frob_nodes}

    if revealed is not None:
        for u, v in edges:
            if u not in revealed or v not in revealed or u not in pos or v not in pos:
                continue
            is_f = (u, v) in _frob_edges
            col  = "#ffd700" if is_f else "#3a5f80"
            ax.annotate("", xy=pos[v], xytext=pos[u],
                        arrowprops=dict(arrowstyle="-|>", color=col,
                                        lw=2.2 if is_f else 0.8,
                                        alpha=0.9 if is_f else 0.35),
                        zorder=1)

        vis = [nidx[n] for n in nodes if n in revealed]
        if not vis:
            return
        colors = base_colors[vis].copy()
        sizes  = base_sizes[vis].copy()
        if frob_flash:
            for i, idx in enumerate(vis):
                if nodes[idx] in frob_nodes:
                    colors[i] = _PULSE_GOLD
                    sizes[i] *= 2.2
        ax.scatter(xs[vis], ys[vis], c=colors, s=sizes,
                   zorder=3, linewidths=0.6, edgecolors="#ffffff33")
        for n in nodes:
            if n in revealed and n in pos:
                tc = "#000000" if _family(n) in ("repl",) else "#ffffff"
                ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                        fontsize=4.5, color=tc, fontweight="bold", zorder=4)
    else:
        dists   = np.abs(np.arange(N) - pulse_center)
        dists   = np.minimum(dists, N - dists)
        weights = np.exp(-0.5 * (dists / pulse_sigma) ** 2)
        active  = {nodes[i] for i in range(N) if weights[i] > 0.3}

        for u, v in edges:
            if u not in pos or v not in pos:
                continue
            is_f = (u, v) in _frob_edges
            near = u in active or v in active
            if is_f and near:
                col, lw, al = "#ffd700", 2.8, 0.95
            elif is_f:
                col, lw, al = "#cc9900", 1.5, 0.5
            elif near:
                col, lw, al = "#cc44ff", 1.5, 0.65
            else:
                col, lw, al = "#3a5f80", 0.5, 0.18
            ax.annotate("", xy=pos[v], xytext=pos[u],
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        blended = np.empty_like(base_colors)
        for i, n in enumerate(nodes):
            w = weights[i]
            target = _PULSE_GOLD if n in frob_nodes else _PULSE_WHITE
            blended[i] = base_colors[i] * (1 - w) + target * w
        blended = np.clip(blended, 0, 1)
        sizes  = base_sizes + base_sizes * 2.0 * weights
        ax.scatter(xs, ys, c=blended, s=sizes, zorder=3,
                   linewidths=0.6, edgecolors="#ffffff22")
        for n in nodes:
            if n in pos:
                tc = "#000000" if _family(n) in ("repl",) else "#ffffff"
                ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                        fontsize=4.5, color=tc, fontweight="bold", zorder=4)


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def main(build_frames=60, flow_frames=90, fps=15, dpi=110):
    print("Tracing priests-engine execution …")
    order, edges = collect_trace(n_steps=8)
    print(f"  {len(order)} functions traced, {len(edges)} call edges")

    if not order:
        print("No trace collected — check that para_vm.py is importable.")
        return

    # Build graph for layout
    G = nx.DiGraph()
    G.add_nodes_from(order)
    G.add_edges_from(edges)

    # Layout
    try:
        pos_raw = nx.nx_agraph.graphviz_layout(G, prog="dot")
    except Exception:
        try:
            pos_raw = nx.drawing.nx_pydot.graphviz_layout(G, prog="dot")
        except Exception:
            pos_raw = nx.spring_layout(G, seed=42, k=2.0 / max(len(order)**0.5, 1))

    all_xy = np.array(list(pos_raw.values()), dtype=float)
    mn, mx = all_xy.min(0), all_xy.max(0)
    rng = mx - mn + 1e-9
    pos = {n: ((np.array(v, dtype=float) - mn) / rng * 0.85 + 0.075).tolist()
           for n, v in pos_raw.items()}
    pos = {n: (v[0], v[1]) for n, v in pos.items()}

    N = len(order)
    frob_nodes = {n for n in order if n in _FROBENIUS}

    base_colors = np.array([
        mcolors.to_rgba(_FAM_COLOR[_family(n)]) for n in order
    ])
    base_sizes = np.array([
        140 if n in frob_nodes else 80 for n in order
    ], dtype=float)

    # Find first frame where a Frobenius node is first revealed
    frob_close_idx = next(
        (i for i, n in enumerate(order) if n in frob_nodes), len(order) - 1
    )

    pulse_sigma   = max(3, N // 5)
    pulse_centers = np.linspace(0, N - 1, flow_frames).astype(int)
    total_frames  = build_frames + flow_frames

    print(f"Rendering cfg_execution.gif ({total_frames} frames, {N} nodes) …")
    fig, ax = plt.subplots(figsize=(10, 10), facecolor=BG)
    frames_pil = []

    for f in range(total_frames):
        print(f"\r  {(f+1)/total_frames*100:5.1f}%", end="", flush=True)

        if f < build_frames:
            frac     = (f + 1) / build_frames
            k        = max(1, int(frac * N))
            revealed = set(order[:k])
            flash    = k - 1 == frob_close_idx
            center_n = order[k - 1]
            title    = (
                f"priests-engine — Live Execution Trace | "
                f"call #{k}: {center_n}"
                + (" | μ∘δ=id" if flash else "")
            )
            render_frame(ax, pos, order, base_colors, base_sizes,
                         frob_nodes, revealed, flash,
                         None, pulse_sigma, edges, title)
        else:
            fi     = f - build_frames
            center = pulse_centers[fi]
            n_at   = order[center]
            title  = (
                f"priests-engine — Live Execution Trace | "
                f"wave: {n_at} | {N} fns · {len(edges)} edges"
            )
            render_frame(ax, pos, order, base_colors, base_sizes,
                         frob_nodes, None, False,
                         center, pulse_sigma, edges, title)

        frames_pil.append(fig_to_pil(fig, dpi))

    print()
    plt.close(fig)

    frames_rgb = [fr.convert("RGB") for fr in frames_pil]
    frames_rgb[0].save(str(OUT), save_all=True, append_images=frames_rgb[1:],
                       duration=1000 // fps, loop=0, optimize=False)
    print(f"Done: {OUT}  ({OUT.stat().st_size / 1e6:.1f} MB)")
    print(f"Frobenius nodes traced: {sorted(frob_nodes)}")


if __name__ == "__main__":
    main()
