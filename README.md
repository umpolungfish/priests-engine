# priests-engine

![language](https://img.shields.io/badge/language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![contradiction](https://img.shields.io/badge/contradiction-sustained%2C%20proven-C1440E?style=for-the-badge) ![tier](https://img.shields.io/badge/tier-O%E2%88%9E-8A2BE2?style=for-the-badge) ![μ∘δ](https://img.shields.io/badge/%CE%BC%E2%88%98%CE%B4-id-00A86B?style=for-the-badge) ![licence](https://img.shields.io/badge/licence-LUNLICENSE-1A1A1A?style=for-the-badge)

*OMNIA SUNT PARACONSISTENTIA*

A paraconsistent computer. It runs programs that sustain contradiction permanently and proves they cannot collapse.

**What it is.** A Belnap FOUR (N/T/F/B) machine with a full ParaASM assembly language, interactive REPL, and VM — the operational face of p4rakernel.

**What it does.** Executes ParaASM programs whose contradictory (B) states never collapse; a long-running demo has logged 25B+ paradox firings. Every Belnap type and kernel invariant is *imported from* p4rakernel (`p4ramill_py` mirror of Lean 4 `Belnap.lean`/`Kernel.lean`), enforced at import time as Python assertions — proofs by delegation, not re-assertion.

**Invariants (proved once in Lean 4 at `p4rakernel/p4ramill/`, 0 sorrys):** `frobenius_invariant` (ffuse∘fsplit=id on all 4 values), `run_B3` (∀n, run stays B/B/B), `run_paradox` (paradox count = 4n exactly), `only_B_is_dialetheic`.

## Install & use

```
uv pip install -e .   # Python ≥3.11, no external deps
para-repl             # interactive REPL (kernel: p4ramill_py, Lean 4 verified)
```

ParaASM: `ENGAGR %r0 → r0=B`; `FSPLIT %r0 %r1 %r2`; `FFUSE %r1 %r2 %r0`; REPL cmds `:step :run :load :save :reset :regs :prog :snap :help :q`. Live dashboard: `para_loop.py`. 12 application modules (`para_*.py`) all import `para_vm`; module CFG at `figures/cfg_modules.gif` (`uv run figures/cfg_modules.py`). Bare-metal port: `src/para_vm.rs` + `src/para_commands.rs` (18 opcodes, UART EMIT, READ=N).

Layout: `para_vm.py` (VM on kernel) → `para_repl.py` (UI) → `para_loop.py` (dashboard) + 12 modules. p4rakernel resolved automatically from sibling dir. Full 475-line version: `README_backups/priests-engine_README.md`.

μ∘δ = id
