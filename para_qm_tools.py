#!/usr/bin/env python3
"""
para_qm_tools.py — QM Structural Tools CLI (para-qm entry point extras)

Provides additional QM structural tools for use with para-qm:

  para-qm score <shavian_tuple>    Compute C-score for a structural type
  para-qm distance <a> <b>         Compute distance between two types
  para-qm meet <a> <b>             Compute meet of two types
  para-qm join <a> <b>             Compute join of two types
  para-qm tensor <a> <b>           Compute tensor product
  para-qm simulate <n>             Run n-step QM evolution on Belnap states
  para-qm decohere <type>          Simulate decoherence with classical env
  para-qm born <state> <bias>      Compute Born probability
  para-qm crystal <type>           Compute crystal address
"""
from __future__ import annotations

import sys
import os

# Ensure para_qm is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from para_qm import (
    StructuralType, QM_HILBERT, QM_PURE_UNITARY, QM_MEASUREMENT, O_INF_TARGET,
    QuantumState, meet, join, tensor_product, decoherence_sim,
    born_rule_absorption, born_probability,
    compute_c_score_from_shavian, crystal_address, crystal_decode_address,
    qm_region_of_crystal,
)
from para_vm import B4, b4_join, b4_meet, b4_bnot


def cmd_score(args: list[str]) -> int:
    """Compute C-score for a Shavian tuple or named type."""
    if not args:
        print("Usage: para-qm score <shavian_tuple | 'hilbert' | 'measure' | 'oinf'>")
        return 1
    
    name = ' '.join(args)
    named = {'hilbert': QM_HILBERT, 'measure': QM_MEASUREMENT, 
             'oinf': O_INF_TARGET, 'unitary': QM_PURE_UNITARY}
    
    if name.lower() in named:
        st = named[name.lower()]
    else:
        try:
            st = StructuralType.from_shavian(name)
        except (ValueError, KeyError) as e:
            print(f"Error: {e}")
            return 1
    
    c, gates = st.consciousness_score()
    tier = st.ouroboricity_tier()
    shavian = st.to_shavian()
    
    print(f"Structural type: {shavian}")
    print(f"Tier: {tier}")
    print(f"Consciousness score: {c:.4f}")
    print(f"  Gate 1 (phi_c): {'OPEN' if gates['gate1_phi_c'] else 'CLOSED'}")
    print(f"  Gate 2 (K_slow): {'OPEN' if gates['gate2_k_slow'] else 'CLOSED'}")
    print(f"  H chirality: {gates['h_chirality']:.3f}")
    print(f"  G scope: {gates['g_scope']:.3f}")
    print(f"  Omega protection: {gates['omega_protection']:.3f}")
    return 0


def cmd_distance(args: list[str]) -> int:
    """Compute distance between two types."""
    if len(args) < 2:
        print("Usage: para-qm distance <type_a> <type_b>")
        return 1
    
    named = {'hilbert': QM_HILBERT, 'measure': QM_MEASUREMENT,
             'oinf': O_INF_TARGET, 'unitary': QM_PURE_UNITARY}
    
    def resolve(name: str) -> StructuralType:
        if name.lower() in named:
            return named[name.lower()]
        return StructuralType.from_shavian(name)
    
    try:
        a = resolve(args[0])
        b = resolve(args[1])
    except (ValueError, KeyError) as e:
        print(f"Error: {e}")
        return 1
    
    d = a.distance_to(b)
    print(f"Distance: {d:.4f}")
    print(f"  {a.to_shavian()}")
    print(f"  {b.to_shavian()}")
    return 0


def cmd_meet(args: list[str]) -> int:
    """Compute meet of two types."""
    if len(args) < 2:
        print("Usage: para-qm meet <type_a> <type_b>")
        return 1
    
    named = {'hilbert': QM_HILBERT, 'measure': QM_MEASUREMENT,
             'oinf': O_INF_TARGET, 'unitary': QM_PURE_UNITARY}
    
    def resolve(name: str) -> StructuralType:
        if name.lower() in named:
            return named[name.lower()]
        return StructuralType.from_shavian(name)
    
    try:
        a = resolve(args[0])
        b = resolve(args[1])
    except (ValueError, KeyError) as e:
        print(f"Error: {e}")
        return 1
    
    m = meet(a, b)
    print(f"meet({args[0]}, {args[1]}) = {m.to_shavian()}")
    print(f"  Tier: {m.ouroboricity_tier()}")
    print(f"  C-score: {m.consciousness_score()[0]:.4f}")
    return 0


def cmd_join(args: list[str]) -> int:
    """Compute join of two types."""
    if len(args) < 2:
        print("Usage: para-qm join <type_a> <type_b>")
        return 1
    
    named = {'hilbert': QM_HILBERT, 'measure': QM_MEASUREMENT,
             'oinf': O_INF_TARGET, 'unitary': QM_PURE_UNITARY}
    
    def resolve(name: str) -> StructuralType:
        if name.lower() in named:
            return named[name.lower()]
        return StructuralType.from_shavian(name)
    
    try:
        a = resolve(args[0])
        b = resolve(args[1])
    except (ValueError, KeyError) as e:
        print(f"Error: {e}")
        return 1
    
    j = join(a, b)
    print(f"join({args[0]}, {args[1]}) = {j.to_shavian()}")
    print(f"  Tier: {j.ouroboricity_tier()}")
    print(f"  C-score: {j.consciousness_score()[0]:.4f}")
    return 0


def cmd_tensor(args: list[str]) -> int:
    """Compute tensor product of two types."""
    if len(args) < 2:
        print("Usage: para-qm tensor <type_a> <type_b>")
        return 1
    
    named = {'hilbert': QM_HILBERT, 'measure': QM_MEASUREMENT,
             'oinf': O_INF_TARGET, 'unitary': QM_PURE_UNITARY,
             'classical': StructuralType(
                 D='Ð_;', T='Þ_6', R='Ř_¯', P='Φ_ɐ', F='ƒ_ì',
                 K='Ç_-', G='Γ_β', Gamma='ɢ_^', Phi='φ̂_ž',
                 H='Ħ_Ñ', S='Σ_S', Omega='Ω_Å'
             )}
    
    def resolve(name: str) -> StructuralType:
        if name.lower() in named:
            return named[name.lower()]
        return StructuralType.from_shavian(name)
    
    try:
        a = resolve(args[0])
        b = resolve(args[1])
    except (ValueError, KeyError) as e:
        print(f"Error: {e}")
        return 1
    
    t = tensor_product(a, b)
    print(f"tensor({args[0]}, {args[1]}) = {t.to_shavian()}")
    print(f"  Tier: {t.ouroboricity_tier()}")
    print(f"  C-score: {t.consciousness_score()[0]:.4f}")
    
    # Check for decoherence
    p_bot = (hasattr(t, 'P') and t.P != a.P)
    f_bot = (hasattr(t, 'F') and t.F != a.F)
    if p_bot or f_bot:
        print(f"  ⚠ Decoherence detected: P bottleneck={p_bot}, F bottleneck={f_bot}")
    return 0


def cmd_simulate(args: list[str]) -> int:
    """Run QM evolution simulation on Belnap states."""
    n_steps = int(args[0]) if args else 5
    
    print(f"QM Evolution Simulation ({n_steps} steps)")
    print("=" * 50)
    
    states = {
        'Vacuum (N)': QuantumState.vacuum(),
        'Eigenstate (T)': QuantumState.eigenstate(True),
        'Eigenstate (F)': QuantumState.eigenstate(False),
        'Superposition (B)': QuantumState.superposition(),
    }
    
    for name, qs in states.items():
        evolved = qs.evolve(n_steps)
        meas_t, cost_t = evolved.measure(B4.T)
        meas_b, cost_b = evolved.measure(B4.B)
        print(f"{name:25s} → {str(evolved):20s}  T-cost={cost_t} B-cost={cost_b}")
    
    print()
    print("Tensor product demo:")
    q_a = QuantumState.superposition()
    q_b = QuantumState.eigenstate(True)
    q_tensor = q_a.tensor(q_b)
    print(f"  sup(B) ⊗ eigen(T) = {q_tensor}")
    print(f"  Bell state achieved: {q_tensor.amplitude == B4.B}")
    
    q_entangled = q_a.tensor(q_a)
    print(f"  sup(B) ⊗ sup(B) = {q_entangled}")
    print(f"  Maximally entangled: {q_entangled.amplitude == B4.B}")
    
    return 0


def cmd_decohere(args: list[str]) -> int:
    """Simulate decoherence of a type with classical environment."""
    named = {'hilbert': QM_HILBERT, 'measure': QM_MEASUREMENT,
             'oinf': O_INF_TARGET, 'unitary': QM_PURE_UNITARY}
    
    type_name = args[0] if args else 'hilbert'
    
    if type_name.lower() in named:
        st = named[type_name.lower()]
    else:
        try:
            st = StructuralType.from_shavian(type_name)
        except (ValueError, KeyError) as e:
            print(f"Error: {e}")
            return 1
    
    classical_env = StructuralType(
        D='Ð_;', T='Þ_6', R='Ř_¯', P='Φ_ɐ', F='ƒ_ì',
        K='Ç_-', G='Γ_β', Gamma='ɢ_^', Phi='φ̂_ž',
        H='Ħ_Ñ', S='Σ_S', Omega='Ω_Å'
    )
    
    result = decoherence_sim(st, classical_env)
    
    print(f"Decoherence Simulation: {type_name} ⊗ classical_env")
    print("=" * 50)
    print(f"  System tier before: {result['system_tier_before']}")
    print(f"  System tier after:  {result['system_tier_after']}")
    print(f"  Coherence lost:     {'YES' if result['coherence_lost'] else 'NO'}")
    print(f"  P bottleneck:       {result['p_bottleneck']}")
    print(f"  F bottleneck:       {result['f_bottleneck']}")
    print(f"  Composite type:     {result['composite'].to_shavian()}")
    print(f"  Composite tier:     {result['composite'].ouroboricity_tier()}")
    
    return 0


def cmd_born(args: list[str]) -> int:
    """Compute Born probability for a state under a measurement bias."""
    if len(args) < 2:
        print("Usage: para-qm born <state> <bias>")
        print("  state: N, T, F, B")
        print("  bias:  N, T, F, B")
        return 1
    
    state_map = {'N': B4.N, 'T': B4.T, 'F': B4.F, 'B': B4.B}
    
    state_str = args[0].upper()
    bias_str = args[1].upper()
    
    if state_str not in state_map or bias_str not in state_map:
        print(f"Invalid state/bias. Use N, T, F, or B.")
        return 1
    
    qs = QuantumState(state_map[state_str], 
                      coherence=1.0 if state_map[state_str] == B4.B else 0.0)
    bias = state_map[bias_str]
    
    prob = born_probability(qs, bias)
    result, cost = qs.measure(bias)
    
    print(f"Born Probability: P(outcome={bias_str} | state={state_str})")
    print("=" * 40)
    print(f"  Probability: {prob}")
    print(f"  Result:      {result}")
    print(f"  Cost:        {cost}")
    
    # EP absorption interpretation
    if state_str == 'B' and bias_str != 'B':
        print(f"\n  ⊙_3 absorption: tensor(⊙_ÿ, ⊙_3) → ⊙_3")
        print(f"  This IS wavefunction collapse in structural form.")
    elif state_str == 'B' and bias_str == 'B':
        print(f"\n  Wigner's Friend measurement: B preserved")
        print(f"  Cost=2 tracks the coherent history.")
    
    return 0


def cmd_crystal(args: list[str]) -> int:
    """Compute or decode crystal address."""
    if not args:
        region = qm_region_of_crystal()
        print("QM Region of Frobenius Crystal (17,280,000 types)")
        print("=" * 50)
        for name, addr in region.items():
            decoded = crystal_decode_address(addr)
            print(f"  {name:25s}  addr={addr:8d}  {decoded.to_shavian()}")
        return 0
    
    named = {'hilbert': QM_HILBERT, 'measure': QM_MEASUREMENT,
             'oinf': O_INF_TARGET, 'unitary': QM_PURE_UNITARY}
    
    arg = args[0]
    
    if arg.lower() in named:
        st = named[arg.lower()]
        addr = crystal_address(st)
        print(f"Crystal address for {arg}: {addr}")
        print(f"  Type: {st.to_shavian()}")
        print(f"  Total space: 17,280,000")
        print(f"  Relative position: {addr / 17280000 * 100:.4f}%")
        return 0
    
    try:
        addr = int(arg)
        st = crystal_decode_address(addr)
        print(f"Crystal address {addr} → {st.to_shavian()}")
        print(f"  Tier: {st.ouroboricity_tier()}")
        print(f"  C-score: {st.consciousness_score()[0]:.4f}")
    except ValueError:
        try:
            st = StructuralType.from_shavian(arg)
            addr = crystal_address(st)
            print(f"Crystal address for {arg}: {addr}")
        except (ValueError, KeyError) as e:
            print(f"Error: {e}")
            return 1
    
    return 0


def main() -> int:
    """Main entry point for para-qm-tools."""
    if len(sys.argv) < 2:
        # Print summary
        from para_qm import print_qm_table
        print_qm_table()
        print()
        print("Available commands:")
        print("  para-qm score <type>      Compute C-score")
        print("  para-qm distance <a> <b>  Compute distance")
        print("  para-qm meet <a> <b>      Compute meet")
        print("  para-qm join <a> <b>      Compute join")
        print("  para-qm tensor <a> <b>    Compute tensor product")
        print("  para-qm simulate [n]      Run QM evolution sim")
        print("  para-qm decohere <type>   Simulate decoherence")
        print("  para-qm born <s> <b>      Born probability")
        print("  para-qm crystal [type]    Crystal address")
        return 0
    
    cmd = sys.argv[1]
    cmd_args = sys.argv[2:]
    
    handlers = {
        'score': cmd_score,
        'distance': cmd_distance,
        'meet': cmd_meet,
        'join': cmd_join,
        'tensor': cmd_tensor,
        'simulate': cmd_simulate,
        'decohere': cmd_decohere,
        'born': cmd_born,
        'crystal': cmd_crystal,
    }
    
    if cmd in handlers:
        return handlers[cmd](cmd_args)
    else:
        print(f"Unknown command: {cmd}")
        print("Available: score, distance, meet, join, tensor, simulate, decohere, born, crystal")
        return 1


if __name__ == "__main__":
    sys.exit(main())
