#!/usr/bin/env python3
"""Analyze Class-D PA simulation results for power, efficiency, and ZVS.

PSF ASCII variable order (from Spectre save statement):
  0:time | 1:L1:i | 2:M1:vgs | 3:M1:vds | 4:M1:id | 5:M2:vgs
  6:M2:vds | 7:M2:id | 8:Vdd:i | 9:mid | 10:lc_out | 11:rload | 12:vdd

IMPORTANT: Vdd_i includes Cgd1 displacement current spikes (±18A during gate
edges). The true supply current = M1_id (not Vdd_i). All Pin calculations
use M1_id, not Vdd_i.
"""

import sys
import os
import math
import csv
import json

# PSF signal indices (PSF vars 1-12 → var_values[0]-var_values[11])
I_L1i   = 0   # PSF var 1
I_M1vgs = 1   # PSF var 2
I_M1vds = 2   # PSF var 3
I_M1id  = 3   # PSF var 4
I_M2vgs = 4   # PSF var 5
I_M2vds = 5   # PSF var 6
I_M2id  = 6   # PSF var 7
I_Vddi  = 7   # PSF var 8
I_mid   = 8   # PSF var 9
I_lcout = 9   # PSF var 10
I_rload = 10  # PSF var 11
I_vdd   = 11  # PSF var 12

RL = 2.55   # Load resistance (Ohms)
VDD = 72.5  # Supply voltage (V)


def parse_ascii(filename):
    """Parse Spectre nutascii output file."""
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Find where data starts
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == 'Values:':
            start = i + 1
            break

    times = []
    var_values = [[] for _ in range(13)]  # 13 signals

    i = start
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        parts = line.split()
        if len(parts) < 2:
            i += 1
            continue

        try:
            idx = int(parts[0])
            t = float(parts[1])
        except (ValueError, IndexError):
            i += 1
            continue

        # Collect all values for this data point
        vals = []
        if len(parts) > 2:
            for p in parts[2:]:
                try:
                    vals.append(float(p))
                except ValueError:
                    pass

        # Read continuation lines until next data point
        j = i + 1
        while j < len(lines):
            next_line = lines[j].strip()
            if not next_line:
                j += 1
                continue
            next_parts = next_line.split()
            if len(next_parts) >= 1:
                try:
                    int(next_parts[0])
                    if len(next_parts) > 1:
                        float(next_parts[1])
                        # Starts with int+float → new data point
                        break
                except (ValueError, IndexError):
                    pass
            # Continuation: collect values
            for p in next_parts:
                try:
                    vals.append(float(p))
                except ValueError:
                    pass
            j += 1

        if len(vals) >= 12:
            times.append(t)
            for k in range(12):
                var_values[k].append(vals[k])

        i = j

    return times, var_values


def compute_output_power(times, var_values, ss_start, ss_end):
    """Compute output power from load voltage across Rload."""
    ss_i = range(ss_start, ss_end)
    ss_t = [times[i] for i in ss_i]
    ss_rload = [var_values[I_rload][i] for i in ss_i]

    # Output power: trapezoidal integration of V^2/RL
    e_out = 0.0
    for i in range(1, len(ss_t)):
        dt = ss_t[i] - ss_t[i-1]
        p1 = ss_rload[i-1]**2 / RL
        p2 = ss_rload[i]**2 / RL
        e_out += (p1 + p2) / 2.0 * dt

    T = ss_t[-1] - ss_t[0]
    Pout = e_out / T if T > 0 else 0.0

    # RMS load voltage
    v_sq = 0.0
    for i in range(1, len(ss_t)):
        dt = ss_t[i] - ss_t[i-1]
        v_sq += (ss_rload[i-1]**2 + ss_rload[i]**2) / 2.0 * dt
    Vrms = math.sqrt(v_sq / T) if T > 0 else 0.0

    # Peak load metrics
    ss_L1i = [var_values[I_L1i][i] for i in ss_i]
    Ipk = max(abs(x) for x in ss_L1i)
    Vpk = max(max(ss_rload), abs(min(ss_rload)))

    return Pout, Vrms, Ipk, Vpk


def compute_input_power(times, var_values, ss_start, ss_end):
    """Compute DC input power.

    Uses M1_id (not Vdd_i) because Vdd_i includes Cgd1 displacement
    current spikes that are purely reactive and cancel over a full cycle
    but create numerical artifacts in trapezoidal integration.

    The true supply current = integral of M1_id over the full cycle / T.
    All energy flows from Vdd through M1's channel to the load.
    """
    ss_i = range(ss_start, ss_end)
    ss_t = [times[i] for i in ss_i]
    ss_M1id = [var_values[I_M1id][i] for i in ss_i]
    ss_Vddi = [var_values[I_Vddi][i] for i in ss_i]

    # Pin from M1_id: integral of Vdd * M1_id dt / T
    e_in_m1 = 0.0
    for i in range(1, len(ss_t)):
        dt = ss_t[i] - ss_t[i-1]
        id_avg = (ss_M1id[i-1] + ss_M1id[i]) / 2.0
        e_in_m1 += id_avg * VDD * dt

    T = ss_t[-1] - ss_t[0]
    Pin_m1 = e_in_m1 / T if T > 0 else 0.0
    Iavg_m1 = Pin_m1 / VDD if VDD > 0 else 0.0

    # Verify: also compute from Vdd_i (should match when well-sampled)
    e_in_vdd = 0.0
    for i in range(1, len(ss_t)):
        dt = ss_t[i] - ss_t[i-1]
        I_avg = (ss_Vddi[i-1] + ss_Vddi[i]) / 2.0
        e_in_vdd += (-I_avg) * VDD * dt  # -I_avg because Vdd_i < 0 means supply
    Pin_vdd = e_in_vdd / T if T > 0 else 0.0

    return Pin_m1, Iavg_m1, Pin_vdd


def check_zvs(times, var_values, ss_start, ss_end):
    """Count ZVS events and failures."""
    M1_vgs = var_values[I_M1vgs]
    M1_vds = var_values[I_M1vds]
    M2_vgs = var_values[I_M2vgs]
    M2_vds = var_values[I_M2vds]
    Vth = 3.5
    thresh = 2.0  # Vds threshold for "zero" voltage

    q1_ok = q1_fail = 0
    q2_ok = q2_fail = 0

    for i in range(ss_start + 3, ss_end - 3):
        # Q1 turning on: Vgs crosses Vth upward
        if M1_vgs[i-1] < Vth and M1_vgs[i] >= Vth:
            vds_before = M1_vds[i-1]
            if vds_before <= thresh:
                q1_ok += 1
            else:
                q1_fail += 1

        # Q2 turning on: Vgs crosses Vth upward
        if M2_vgs[i-1] < Vth and M2_vgs[i] >= Vth:
            vds_before = M2_vds[i-1]
            if vds_before <= thresh:
                q2_ok += 1
            else:
                q2_fail += 1

    return q1_ok, q1_fail, q2_ok, q2_fail


def analyze(times, var_values):
    """Compute power, efficiency, ZVS."""
    n = len(times)
    if n < 10:
        print("ERROR: Not enough data.")
        return

    # Steady-state window: last 60%
    ss_start = int(n * 0.35)
    ss_end = n

    # Output power
    Pout, Vrms, Ipk, Vpk = compute_output_power(times, var_values, ss_start, ss_end)

    # Input power from M1_id (true supply current)
    Pin, Iavg, Pin_vdd = compute_input_power(times, var_values, ss_start, ss_end)

    # Efficiency
    Eff = Pout / Pin * 100 if Pin > 0 else 0.0

    # ZVS
    q1_ok, q1_fail, q2_ok, q2_fail = check_zvs(times, var_values, ss_start, ss_end)

    # Timing stats
    ss_t = times[ss_start:]

    print("=" * 55)
    print("  Class-D RF Power Amplifier - Simulation Results")
    print("  Based on: El-Hamamsy, IEEE Trans. PE, May 1994")
    print("=" * 55)
    print(f"  DC Supply Voltage:        {VDD:.1f} V")
    print(f"  Load Resistance:          {RL:.2f} Ohm")
    print(f"  Switching Frequency:      13.56 MHz")
    print(f"  Dead Time:                11.5 ns")
    print(f"  MOSFET Model:             Level-1 + external linear caps")
    print(f"  Simulation Time:          {times[-1]*1e9:.0f} ns")
    print(f"  Steady-State Window:      {ss_t[0]*1e9:.1f} to {ss_t[-1]*1e9:.1f} ns")
    print(f"  Samples in Window:        {len(ss_t)}")
    print("-" * 55)
    print(f"  [Power from M1_id - filters out Cgd1 reactive spikes]")
    print(f"  Average Supply Current:   {Iavg:.3f} A")
    print(f"  DC Input Power:           {Pin:.2f} W")
    print(f"  Average Output Power:     {Pout:.2f} W")
    print(f"  Drain Efficiency:         {Eff:.1f} %")
    print("  (Comparison: raw Vdd_i gives Pin=" +
          f"{Pin_vdd:.1f}W - corrupted by Cgd1 edges)")
    print("-" * 55)
    print(f"  Peak Load Voltage:        ±{Vpk:.2f} V")
    print(f"  Peak Load Current:        ±{Ipk:.2f} A")
    print(f"  Load Voltage RMS:         {Vrms:.2f} V")
    print(f"  Estimated Crest Factor:   {Vpk/Vrms:.2f}")
    print("-" * 55)
    print(f"  ZVS Check (Q1):          {q1_ok} ok, {q1_fail} fail",
          f"{'[PASS]' if q1_fail==0 else '[PARTIAL]'}")
    print(f"  ZVS Check (Q2):          {q2_ok} ok, {q2_fail} fail",
          f"{'[PASS]' if q2_fail==0 else '[PARTIAL]'}")
    print("=" * 55)

    return {
        'Pin': Pin, 'Pout': Pout, 'Efficiency(%)': Eff,
        'I_supply_avg': Iavg, 'I_load_pk': Ipk, 'Vout_rms': Vrms,
        'ZVS_Q1_ok': q1_ok, 'ZVS_Q1_fail': q1_fail,
        'ZVS_Q2_ok': q2_ok, 'ZVS_Q2_fail': q2_fail,
    }


if __name__ == '__main__':
    result_file = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.expanduser('~/ClassD_RF_PA_300W_13p56MHz/results/classd_tran_ascii')

    print(f"Parsing: {result_file}")
    times, var_values = parse_ascii(result_file)
    print(f"  Parsed {len(times)} time points, {len(var_values)} signal groups")

    if len(times) < 10:
        print("ERROR: Not enough data points parsed.")
        sys.exit(1)

    results = analyze(times, var_values)

    # Write corrected CSV (decimated every 10th sample)
    out_csv = os.path.join(os.path.dirname(result_file), 'classd_waveforms.csv')
    with open(out_csv, 'w') as f:
        f.write("time_ns,mid_V,rload_V,L1_i_A,Vdd_i_A,M1_vds_V,M1_vgs_V,"
                "M2_vds_V,M2_vgs_V,M1_id_A,M2_id_A\n")
        for i in range(len(times)):
            if i % 10 == 0:
                f.write(f"{times[i]*1e9:.3f},")
                f.write(f"{var_values[I_mid][i]:.4f},")
                f.write(f"{var_values[I_rload][i]:.4f},")
                f.write(f"{var_values[I_L1i][i]:.4f},")
                f.write(f"{var_values[I_Vddi][i]:.4f},")
                f.write(f"{var_values[I_M1vds][i]:.4f},")
                f.write(f"{var_values[I_M1vgs][i]:.4f},")
                f.write(f"{var_values[I_M2vds][i]:.4f},")
                f.write(f"{var_values[I_M2vgs][i]:.4f},")
                f.write(f"{var_values[I_M1id][i]:.6f},")
                f.write(f"{var_values[I_M2id][i]:.6f}\n")
    print(f"\n  Waveform CSV: {out_csv}")

    # Save results as JSON for build report
    json_path = os.path.join(os.path.dirname(out_csv), 'analysis_results.json')
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  Analysis JSON: {json_path}")
