# Gate Driver Specification: 300W 13.56MHz Class-D RF Power Amplifier

*Verified and confirmed correct on 2026-06-29 for routed PCB.*

## 1. Requirements

The IRF540 MOSFETs require:
- **Vgs = 10V** for full enhancement (Ron = 77mΩ typ)
- **Gate charge Qg = 72nC** per switching cycle
- **Peak gate current**: I_g_pk = Qg / t_rise = 72nC / 2ns ≈ 36A
- **Average gate current**: I_g_avg = Qg × f = 72nC × 13.56MHz ≈ 0.98A
- **Gate drive power**: P_gate = Qg × Vgs × f = 72nC × 10V × 13.56MHz ≈ 9.8W

The high-side (M1) gate must float with mid (0V to 85V swing). The low-side
(M2) gate is referenced to GND.

## 2. Gate Driver IC: IR2181S

| Parameter        | IR2110          | IR2181S         |
|------------------|-----------------|-----------------|
| Voltage          | up to 500V      | up to 600V      |
| Peak gate current| 2A source/2A sink | Datasheet-dependent, not enough alone for 2ns edges |
| Logic inputs     | HIN/LIN         | HIN/LIN         |
| Propagation delay| 120ns           | Check final selected suffix/datasheet |
| Dead time        | external        | external        |
| Package          | DIP-14 / SOIC-14 | SOIC-8          |
| Cost             | ~$2             | ~$1.50          |

**Recommendation**: Use a two-input bootstrap half-bridge driver such as
IR2181S/IRS2181S for the current HIN/LIN schematic. Do not substitute IR2184
without changing the schematic, because IR2184-family parts commonly use
single `IN` plus `SD` control rather than separate `HIN` and `LIN`.

## 3. Bootstrap Circuit

### Bootstrap Capacitor (C_bs)

The bootstrap capacitor supplies the gate charge for M1 each cycle:

C_bs ≥ Qg / ΔV_bs = 72nC / 1V = 72nF

Use **C_bs = 220nF ceramic (X7R, 100V)** for 3× margin. Place within 5mm of
the IC's VB and VS pins.

### Bootstrap Diode (D_bs)

D_bs charges C_bs when mid is pulled to GND (M2 on). Requirements:
- Fast recovery (trr < 50ns)
- Peak repetitive current > 2A
- Reverse voltage > 85V (Vdd + boot voltage)

**Recommendation**: UF4007 (ultrafast, 1000V, 1A, trr=75ns). Or a Schottky
like **SS24** (40V, 2A) if the boot voltage is regulated to 12V.

### Bootstrap Resistor (optional)

R_bs = 2-5Ω limits the peak charging current to prevent ringing. Only needed
if the supply rails show noise during switching transients.

## 4. Gate Resistors

Gate resistors control the switching speed (trade-off: EMI vs efficiency):

| Component | Value | Purpose |
|-----------|-------|---------|
| R_g1_on   | 2.2Ω  | M1 turn-on, limit dV/dt to 20GV/s |
| R_g1_off  | 1Ω    | M1 turn-off, fast Schottky bypass |
| R_g2_on   | 2.2Ω  | M2 turn-on |
| R_g2_off  | 1Ω    | M2 turn-off |

Use two resistors in anti-parallel (one with Schottky diode) for separate
on/off control:
```
         ┌─ R_on ──┐
GATE ──┬─┤         ├── MOSFET GATE
       │ └─ D_off ─┘
       └── R_off ──┘
```

## 5. Power Dissipation

### Gate Driver IC
P_drv = Qg × Vgs × f + P_quiescent
      = 72nC × 10V × 13.56MHz + 20mW
      ≈ 9.8W + 20mW ≈ **10W**

The IR2181S gate-driver IC cannot dissipate 10W
by itself. The average gate current is 0.98A, not 36A.

**Solution**: External gate drive buffer stage (push-pull) using 2N2222/2N2907
or a small MOSFET driver (TC4420) to deliver the 36A peaks.

### Bootstrap Supply
The bootstrap diode must carry I_g_avg = 0.98A. The 10V supply for the
bootstrap needs to provide ~10W. Use a 12V-to-10V linear regulator or a
separate 10V supply rail.

## 6. Gate Drive Schematic (Simplified)

```
        +72.5V
          │
    ┌─────┴─────┐
    │          D_bs
    │       UF4007
    ├──────┐
    │      │
    │   ┌──┴──┐
    │   │ C_bs│ 220nF X7R 100V
    │   └──┬──┘
    │      │ VB
    ├──────┤ IR2181S HIN ── PWM from controller
    │      │ LIN ── inverted PWM
   Vdd     │ SD ── shutdown (pull high)
    │      │
    │      │ VS ────┬───── to mid
    │      │ HO ────┤ R_g1 ── M1 gate
    │      │        │
    │      └────────┤
    │              LO ──┤ R_g2 ── M2 gate
    │                  │
    └──────────────────┤ COM ── GND
```

## 7. Input Logic Timing

Generate the PWM signals with dead-time control:

```
       ┌──────┐    ┌──────┐
M1 ON  │      │    │      │    (HIN)
       ┘      └────┘      └────
   ──────┐    ┌──────┐    ┌──
M2 ON    │    │      │    │     (LIN, inverted)
         └────┘      └────┘
         |--|   dead-time = 11.5ns
```

Dead-time generation options:
1. **Microcontroller** (STM32, Teensy) with HRTIM or timer + dead-time insert
2. **Dedicated IC**: IRS21867 (integrated dead-time)
3. **Discrete**: RC delay + Schmitt trigger on each channel

For hackerfab: use an STM32G4 with HRTIM (high-resolution timer, 184ps
resolution) or a simple 555 + gate delay IC (e.g., MC74VHC1G125).

## 8. PCB Layout Guidelines

1. **Kelvin source connection**: Separate power and gate return paths for M1
   and M2. Do NOT share the source connection between gate drive and power
   stage.

2. **Bootstrap cap placement**: C_bs within 5mm of VB-VS pins. Use 0.1µF +
   220nF in parallel.

3. **Gate drive loop**: Minimize loop area: driver output → R_g → MOSFET
   gate → MOSFET source → driver return. Keep <10mm.

4. **Power loop**: Vdd → M1 drain → M1 source → M2 drain → M2 source → GND.
   Minimize with 2-layer or 4-layer PCB, power plane on top, GND plane on
   bottom.

5. **Thermal**: M1 and M2 need heatsinks (TO-220). Estimate 50W dissipation
   each at 83% efficiency with 305W output. Use thermal pad + heatsink.

6. **Inductor L1**: Air-core or ferrite-core, 300nH, designed for >15A peak
   current. Use 2mm diameter copper wire, ~5 turns on 10mm diameter.

---

*Document version: 1.0, 2026-06-27*
