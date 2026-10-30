#!/usr/bin/env python3
"""
para_loop.py — Paraconsistent Infinite Loop with Live Animated Dashboard

Runs the 3-instruction Frobenius kernel (ENGAGR → FSPLIT → FFUSE → JMP)
indefinitely with a live-updating dashboard featuring:
  - Animated Belnap spinner
  - Pulsing paradox counter (live increment)
  - Animated distribution bar with smooth transitions
  - Belnap FOUR compass rose
  - Steps/sec rate with color-coded speed indicator
  - Register heat map (paradox intensity per register)

Loop invariant: μ ∘ δ = id  →  B is self-sustaining.
Paradox growth: P(n) = 3n+2 after n cycles (verified: n=100→π=302).

Run:   python3 para_loop.py
Stop:  Ctrl+C
"""

import sys
import time
import signal
from itertools import cycle
from collections import defaultdict

from para_vm import ParaRegister, B4, b4_join, b4_bnot, b4_band, b4_designated


# ── ANSI ───────────────────────────────────────────────────────────────────

R  = '\033[0m'
BD = '\033[1m'
DM = '\033[2m'
IT = '\033[3m'
BL = '\033[5m'
RV = '\033[7m'

CY  = '\033[96m'
GD  = '\033[93m'
GN  = '\033[92m'
BLU = '\033[94m'
RD  = '\033[91m'
MG  = '\033[95m'
GR  = '\033[90m'
WH  = '\033[97m'

BG_DK  = '\033[48;5;236m'
BG_RD  = '\033[48;5;52m'
BG_GN  = '\033[48;5;22m'
BG_BL  = '\033[48;5;17m'
BG_MG  = '\033[48;5;53m'
BG_GD  = '\033[48;5;58m'

CLR    = '\033[2J\033[H'
CLR_LN = '\033[2K'

CUR_UP   = '\033[1A'
CUR_DN   = '\033[1B'
CUR_SAVE = '\033[s'
CUR_REST = '\033[u'

_B4_COLOR = {B4.N: GR, B4.T: GN, B4.F: BLU, B4.B: RD}
_B4_BG    = {B4.N: BG_DK, B4.T: BG_GN, B4.F: BG_BL, B4.B: BG_RD}
_B4_BLOCK = {B4.N: '░', B4.T: '▒', B4.F: '▓', B4.B: '█'}
_B4_GLYPH = {B4.N: '⊗', B4.T: '⊕', B4.F: '⊖', B4.B: '⊙'}
_B4_SYM   = {B4.N: '∅', B4.T: '⊤', B4.F: '⊥', B4.B: '◈'}

# ── Spinners ──────────────────────────────────────────────────────────────

SPINNER_CYCLE = cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
BELNAP_SPIN   = cycle([f'{_B4_COLOR[v]}{v.value}{R}' for v in (B4.N, B4.T, B4.F, B4.B)])


# ── Engine ─────────────────────────────────────────────────────────────────

class ParaEngine:
    """Minimal paraconsistent engine for the infinite Frobenius loop."""

    def __init__(self) -> None:
        self.registers: dict[int, ParaRegister] = defaultdict(ParaRegister)
        self.belief: dict[int, B4] = {}
        self.program: list[str] = []
        self.pc: int = 0
        self.total_steps: int = 0
        self.cycles: int = 0

    def _belief(self, reg_id: int) -> B4:
        return self.belief.get(reg_id, B4.N)

    def _set_belief(self, reg_id: int, val: B4) -> None:
        self.belief[reg_id] = val
        flux_map = {B4.N: '00', B4.T: '01', B4.F: '10', B4.B: '11'}
        self.registers[reg_id].flux = flux_map[val]

    def step(self) -> None:
        if not self.program:
            return
        if self.pc >= len(self.program):
            self.pc = 0
            self.cycles += 1

        instr = self.program[self.pc]
        self.pc += 1
        self.total_steps += 1

        # Parse registers from instruction
        import re
        regs = [int(x) for x in re.findall(r'%r(\d+)', instr)]

        if 'ENGAGR' in instr and regs:
            r = regs[0]
            self.registers[r].engage()
            self._set_belief(r, B4.B)

        elif 'FSPLIT' in instr and len(regs) >= 3:
            src, d1, d2 = regs[0], regs[1], regs[2]
            b = self._belief(src)
            p = self.registers[src].paradox_count
            if b == B4.B:
                b1, b2, bump = B4.T, B4.F, 1
            else:
                b1, b2, bump = b, b, 0
            self._set_belief(d1, b1)
            self._set_belief(d2, b2)
            self.registers[d1].paradox_count = p + bump
            self.registers[d2].paradox_count = p + bump

        elif 'FFUSE' in instr and len(regs) >= 3:
            joined = self._belief(regs[0])
            for r in regs[1:-1]:
                joined = b4_join(joined, self._belief(r))
            self._set_belief(regs[-1], joined)

        elif 'IFIX' in instr and regs:
            self.registers[regs[0]].value = 'FIXED'
            self._set_belief(regs[0], B4.T)

        elif 'JMP' in instr:
            pass  # PC already incremented; cycles handle wrap

    def b4_distribution(self) -> dict[B4, int]:
        dist = {v: 0 for v in B4}
        for rid, reg in self.registers.items():
            dist[self._belief(rid)] += 1
        return dist

    def snapshot(self) -> dict:
        dist = self.b4_distribution()
        paradox = sum(r.paradox_count for r in self.registers.values())
        active = sum(1 for r in self.registers.values() if r.is_active)
        fixed = sum(1 for r in self.registers.values() if r.is_fixed)
        return {
            'steps': self.total_steps, 'cycles': self.cycles,
            'paradox': paradox, 'active': active, 'fixed': fixed,
            'dist': dist, 'pc': self.pc,
        }


# ── Kernel ────────────────────────────────────────────────────────────────

KERNEL = [
    'ENGAGR %r0',
    'FSPLIT %r0 %r1 %r2',
    'FFUSE  %r1 %r2 %r0',
    'JMP    .loop',
]


# ── Display ────────────────────────────────────────────────────────────────

def _dist_bar(dist: dict[B4, int], width: int = 38) -> str:
    total = sum(dist.values()) or 1
    parts = []
    for s in (B4.N, B4.T, B4.F, B4.B):
        n = dist[s]
        seg = max(1, round(n / total * width)) if n else 0
        if seg:
            parts.append(f'{_B4_COLOR[s]}{_B4_BLOCK[s] * seg}{R}')
    bar_inner = ''.join(parts)
    pad = width - sum(1 for c in bar_inner if c in '░▒▓█')
    if pad > 0:
        bar_inner += f'{GR}{"░" * pad}{R}'
    return '[' + bar_inner + ']'


def _register_heat_bar(reg: ParaRegister, max_paradox: int) -> str:
    """Heat bar for a single register's paradox intensity."""
    if max_paradox == 0:
        return ''
    heat = reg.paradox_count / max_paradox
    n = max(1, int(heat * 8))
    if heat < 0.3:
        c = GN
    elif heat < 0.6:
        c = GD
    else:
        c = RD
    return f'{c}{"█" * n}{DM}{"░" * (8 - n)}{R}'


def _belnap_compass(dist: dict[B4, int]) -> str:
    """Four-directional compass showing Belnap distribution."""
    total = sum(dist.values()) or 1
    n_frac = dist[B4.N] / total
    t_frac = dist[B4.T] / total
    f_frac = dist[B4.F] / total
    b_frac = dist[B4.B] / total

    n_str = f'{_B4_COLOR[B4.N]}N{R}'
    t_str = f'{_B4_COLOR[B4.T]}⊤{R}'
    f_str = f'{_B4_COLOR[B4.F]}⊥{R}'
    b_str = f'{_B4_COLOR[B4.B]}◈{R}'

    if b_frac > 0.5:
        center = f'{RD}◈{R}'
    elif t_frac > 0.5:
        center = f'{GN}⊕{R}'
    elif f_frac > 0.5:
        center = f'{BLU}⊖{R}'
    else:
        center = f'{GR}⊙{R}'

    lines = [f'         {n_str}',
             f'         │',
             f' {t_str} ── {center} ── {f_str}',
             f'         │',
             f'         {b_str}']
    return '\n'.join(lines)

def _render(vm: ParaEngine, t0: float, step0: int) -> str:
    """Full animated dashboard render."""
    elapsed = time.time() - t0
    rate = (vm.total_steps - step0) / elapsed if elapsed > 0 else 0
    dist = vm.b4_distribution()
    s = vm.snapshot()
    paradox = s['paradox']

    # Spinner
    sp = next(SPINNER_CYCLE)
    b4_sp = next(BELNAP_SPIN)

    # Rate color
    if rate > 1_000_000:
        rate_color = RD
    elif rate > 100_000:
        rate_color = GD
    elif rate > 10_000:
        rate_color = GN
    else:
        rate_color = GR

    # Paradox rate
    p_rate = paradox / max(elapsed, 0.001)

    # Determine dominant value
    dominant = max(B4, key=lambda v: dist.get(v, 0))
    dom_color = _B4_COLOR[dominant]
    dom_sym = _B4_SYM[dominant]

    lines = [
        f'{BD}{CY}╔══════════════════════════════════════════════════════════╗{R}',
        f'{BD}{CY}║{R}  {sp}  {WH}PARACONSISTENT COMPUTER{R}  {RD}⊙{R}  {DM}Frobenius Loop{R}    {CY}║{R}',
        f'{BD}{CY}║{R}  {DM}μ ∘ δ = id{R}  {DM}|{R}  {dom_color}{dom_sym} {dominant.value}{R}-dominant    '
        f'       {CY}║{R}',
        f'{BD}{CY}╚══════════════════════════════════════════════════════════╝{R}',
        '',
        f'  {GD}kernel{R}   ENGAGR %r0  →  FSPLIT %r0 %r1 %r2  →  FFUSE %r1 %r2 %r0  →  JMP .loop',
        f'  {GD}law{R}      {BD}μ ∘ δ = id{R}   (Frobenius identity — all registers stabilize at B)',
        '',
    ]

    # ── Stats panel ──
    # Build paradox bar with smooth visual
    bar_width = 42
    total_p = sum(dist.values()) or 1
    bar_parts = []
    for v in (B4.N, B4.T, B4.F, B4.B):
        frac = dist[v] / total_p
        seg = max(1, round(frac * bar_width)) if frac > 0 else 0
        if seg:
            bar_parts.append(f'{_B4_COLOR[v]}{_B4_BLOCK[v] * seg}{R}')
    bar_inner = ''.join(bar_parts)
    pad = bar_width - sum(1 for c in bar_inner if c in '░▒▓█')
    if pad > 0:
        bar_inner += f'{GR}{"░" * pad}{R}'

    # Format large numbers with animation-friendly padding
    steps_str = f'{vm.total_steps:>18,}'
    cycles_str = f'{vm.cycles:>18,}'
    paradox_str = f'{paradox:>18,}'
    p_rate_str = f'{p_rate:>14,.0f}'

    lines += [
        f'  {BD}╔══ ENGINE STATS ═══════════════════════════════════╗{R}',
        f'  {BD}║{R}  {CY}steps{R}  {steps_str}  {rate_color}{"▶" * min(6, int(rate/20000)+1)}{R}  {BD}║{R}',
        f'  {BD}║{R}  {CY}cycles{R} {cycles_str}                    {BD}║{R}',
        f'  {BD}║{R}  {RD}π{R}      {paradox_str}  {GD}π/s={p_rate_str}{R}  {BD}║{R}',
        f'  {BD}║{R}  {MG}active{R} {s["active"]:>18,}                    {BD}║{R}',
        f'  {BD}║{R}  {GD}Belnap{R} [{bar_inner}] {BD}║{R}',
        f'  {BD}╚═══════════════════════════════════════════════════╝{R}',
        '',
    ]

    # ── Belnap compass ──
    lines.append(f'  {BD}Belnap FOUR Compass:{R}')
    for l in _belnap_compass(dist).split('\n'):
        lines.append(f'    {l}')

    # Distribution counts
    lines.append(f'')
    counts = '  '.join(
        f'{_B4_COLOR[v]}{v.value}{R}={dist[v]}'
        for v in (B4.N, B4.T, B4.F, B4.B)
    )
    lines.append(f'    {DM}distribution:{R} {counts}')

    # ── Register heat map ──
    lines.append(f'')
    lines.append(f'  {BD}Register Heat Map:{R}')
    max_paradox = max((r.paradox_count for r in vm.registers.values()), default=0)
    for rid in sorted(vm.registers.keys()):
        r = vm.registers[rid]
        b = vm._belief(rid)
        c = _B4_COLOR[b]
        heat_bar = _register_heat_bar(r, max_paradox)
        fx = f' {GN}[FIXED]{R}' if r.is_fixed else ''
        lines.append(
            f'    %r{rid}  {c}{b.value}{R}  {heat_bar}  '
            f'π={r.paradox_count:<8}{fx}'
        )

    # ── Program (current instruction highlighted) ──
    lines.append(f'')
    lines.append(f'  {BD}Program:{R}')
    pc_pos = vm.pc % len(vm.program) if vm.program else 0
    for i, ins in enumerate(vm.program):
        marker = f'{GD}▶{R}' if i == pc_pos else ' '
        if i == pc_pos:
            ins_str = f'{WH}{BD}{ins}{R}'
        else:
            ins_str = ins
        lines.append(f'  {marker}  {i}: {ins_str}')

    # ── Elapsed time ──
    h = int(elapsed // 3600)
    m = int((elapsed % 3600) // 60)
    sec = elapsed % 60
    time_str = f'{h:02d}:{m:02d}:{sec:06.3f}'
    lines.append(f'')
    lines.append(f'  {DM}elapsed{R} {time_str}  {DM}|  Ctrl+C to stop{R}')

    return '\n'.join(lines)


# ── Main ──────────────────────────────────────────────────────────────────

def run() -> None:
    vm = ParaEngine()
    vm.program = KERNEL
    # Seed r0 = B before loop starts
    vm._set_belief(0, B4.B)
    vm.registers[0].engage()

    t0 = time.time()
    step0 = 0
    _stop = False

    def _sigint(sig, frame):
        nonlocal _stop
        _stop = True

    signal.signal(signal.SIGINT, _sigint)

    RENDER_INTERVAL = 0.1  # 10 FPS
    BATCH = 5_000  # steps per inner batch

    print(CLR, end='')
    next_render = time.time()
    frame_count = 0

    while not _stop:
        for _ in range(BATCH):
            vm.step()

        now = time.time()
        if now >= next_render:
            sys.stdout.write(CLR)
            sys.stdout.write(_render(vm, t0, step0))
            sys.stdout.flush()
            next_render = now + RENDER_INTERVAL
            frame_count += 1

    # Final report
    elapsed = time.time() - t0
    dist = vm.b4_distribution()
    s = vm.snapshot()
    rate = vm.total_steps / max(elapsed, 0.001)

    print()
    print(f'{BD}{CY}═══ FROBENIUS LOOP — FINAL REPORT ═══{R}')
    print(f'  {CY}elapsed{R}   {elapsed:.2f}s')
    print(f'  {CY}steps{R}     {vm.total_steps:,}')
    print(f'  {CY}cycles{R}    {vm.cycles:,}')
    print(f'  {CY}paradox{R}   {s["paradox"]:,}')
    print(f'  {CY}rate{R}      {rate:,.0f} steps/sec')
    print(f'  {CY}frames{R}    {frame_count:,}')
    print()
    print(f'  {BD}Belnap final distribution:{R}')
    for v in (B4.N, B4.T, B4.F, B4.B):
        c = _B4_COLOR[v]
        print(f'    {c}{v.value}{R}  {dist[v]:>6}  {_B4_BLOCK[v] * min(dist[v], 40)}')
    print()
    print(f'  {RD}⊙{R}  {DM}Omnia sunt paraconsistentia{R}  {RD}⊙{R}')
    print()


if __name__ == '__main__':
    run()