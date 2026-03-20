#!/usr/bin/env python3
"""
compare_results.py
------------------
Parse and plot kinetic energy vs. time from LIGGGHTS and BlazeDEM runs of the
same case.

LIGGGHTS output (log file or stdout redirect):
  - thermo lines:  step  atoms  ke  c_rke  vol

BlazeDEM output (stdout redirect):
  - KE lines:  time: <t>  KE: trans = <Kt>  rot = <Kr>  total = <Ktot>

Usage:
  python compare_results.py \
      --liggghts /path/to/liggghts_run.log \
      --blazedem /path/to/blazedem_run.log \
      [--output comparison.png]
"""

import argparse
import re
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_liggghts_log(path):
    """
    Extract (time, ke_trans, ke_rot, ke_total) from a LIGGGHTS log.
    Thermo columns: step atoms ke c_rke vol
    """
    timestep = None
    times, ke_t, ke_r = [], [], []

    in_thermo = False
    col_step = col_ke = col_rke = None

    with open(path) as f:
        for line in f:
            line = line.strip()

            # Capture timestep
            m = re.match(r'^timestep\s+([\d.eE+\-]+)', line)
            if m:
                timestep = float(m.group(1))

            # Detect thermo header
            if line.startswith('Step') or (line.startswith('step') and 'ke' in line.lower()):
                cols = line.lower().split()
                try:
                    col_step = cols.index('step')
                    col_ke   = cols.index('ke')
                    col_rke  = next(i for i, c in enumerate(cols) if 'rke' in c)
                    in_thermo = True
                except (ValueError, StopIteration):
                    in_thermo = False
                continue

            if in_thermo:
                parts = line.split()
                if not parts or not parts[0].lstrip('-').isdigit():
                    in_thermo = False
                    continue
                try:
                    step = int(parts[col_step])
                    ke   = float(parts[col_ke])
                    rke  = float(parts[col_rke])
                    t    = step * (timestep or 1e-5)
                    times.append(t)
                    ke_t.append(ke)
                    ke_r.append(rke)
                except (IndexError, ValueError):
                    continue

    if not times:
        print(f"  WARNING: No thermo data found in {path}", file=sys.stderr)
        return None

    times  = np.array(times)
    ke_t   = np.array(ke_t)
    ke_r   = np.array(ke_r)
    return times, ke_t, ke_r, ke_t + ke_r


def parse_blazedem_log(path):
    """
    Extract (time, ke_trans, ke_rot, ke_total) from BlazeDEM stdout.
    Line format:
      time: <t> KE: trans = <Kt> rot = <Kr> total = <Ktot>
    """
    times, ke_t, ke_r, ke_tot = [], [], [], []

    pat = re.compile(
        r'time:\s*([\d.eE+\-]+)\s+KE:\s+trans\s*=\s*([\d.eE+\-]+)'
        r'\s+rot\s*=\s*([\d.eE+\-]+)\s+total\s*=\s*([\d.eE+\-]+)'
    )

    with open(path) as f:
        for line in f:
            m = pat.search(line)
            if m:
                times.append(float(m.group(1)))
                ke_t.append(float(m.group(2)))
                ke_r.append(float(m.group(3)))
                ke_tot.append(float(m.group(4)))

    if not times:
        print(f"  WARNING: No KE data found in {path}", file=sys.stderr)
        return None

    return (np.array(times), np.array(ke_t),
            np.array(ke_r),  np.array(ke_tot))


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def settling_time(times, ke, threshold_frac=0.01):
    """Time at which KE drops below threshold_frac * initial KE."""
    if ke[0] == 0:
        return None
    thresh = threshold_frac * ke[0]
    idx = np.where(ke < thresh)[0]
    return times[idx[0]] if len(idx) else None


def summary_stats(label, times, ke_total):
    t_set = settling_time(times, ke_total)
    peak  = ke_total.max()
    final = ke_total[-1]
    print(f"  {label}:")
    print(f"    Peak KE:      {peak:.4e} J")
    print(f"    Final KE:     {final:.4e} J  (at t={times[-1]:.4f}s)")
    if t_set:
        print(f"    Settling t:   {t_set:.4f} s  (KE < 1% of peak)")
    else:
        print(f"    Settling t:   not reached within simulation")


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

def make_plot(lig, blaze, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('LIGGGHTS vs BlazeDEM — noCohesion settling case', fontsize=13)

    # --- Left: total KE ---
    ax = axes[0]
    if lig:
        ax.plot(lig[0], lig[3], label='LIGGGHTS (Hertz)', color='steelblue', lw=1.8)
    if blaze:
        ax.plot(blaze[0], blaze[3], label='BlazeDEM (linear spring)', color='tomato',
                lw=1.8, linestyle='--')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Kinetic Energy (J)')
    ax.set_title('Total KE vs time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # --- Right: normalised KE (KE / KE_max) ---
    ax = axes[1]
    if lig:
        ke_max = lig[3].max() or 1.0
        ax.plot(lig[0], lig[3] / ke_max, label='LIGGGHTS', color='steelblue', lw=1.8)
    if blaze:
        ke_max = blaze[3].max() or 1.0
        ax.plot(blaze[0], blaze[3] / ke_max, label='BlazeDEM', color='tomato',
                lw=1.8, linestyle='--')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('KE / KE_max')
    ax.set_title('Normalised KE (settling comparison)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    ax.set_ylim(1e-6, 2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"\n  Plot saved to: {output_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--liggghts', help='LIGGGHTS log file')
    ap.add_argument('--blazedem', help='BlazeDEM stdout log file')
    ap.add_argument('--output',   default='comparison.png',
                    help='Output plot filename (default: comparison.png)')
    args = ap.parse_args()

    if not args.liggghts and not args.blazedem:
        ap.error('Provide at least one of --liggghts or --blazedem')

    lig   = parse_liggghts_log(args.liggghts) if args.liggghts else None
    blaze = parse_blazedem_log(args.blazedem) if args.blazedem else None

    print("\n=== Summary ===")
    if lig:
        summary_stats('LIGGGHTS', lig[0], lig[3])
    if blaze:
        summary_stats('BlazeDEM', blaze[0], blaze[3])

    make_plot(lig, blaze, args.output)
