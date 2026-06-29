# PCB Layout Guide: 300W 13.56MHz Class-D RF Power Amplifier

*Verified and confirmed correct on 2026-06-29 for routed PCB.*

## Board Specifications (UPDATED 2026-06-29)

| Parameter | Value |
|-----------|-------|
| Board size | 80mm x 50mm |
| Layers | 2 (F.Cu top, B.Cu bottom) |
| Material | FR4, 1.6mm thickness |
| Copper | 1oz (35um) |
| Finish | HASL (hot air solder leveling) |
| Min trace width | 0.25mm |
| Min clearance | 0.2mm |
| Min via | 0.8mm diameter, 0.4mm drill |

## Component Placement (KiCAD Reference Designators)

```
LEFT SIDE (power inputs):
  J1 (x=5, y=5)    - Vdd 72.5V terminal block
  J3 (x=5, y=45)   - VCC 12V terminal block
  J4 (x=5, y=25)   - PWM input header (HIN, LIN)
  C1 (x=18, y=5)   - 100uF bulk cap on Vdd
  C2 (x=18, y=12)  - 0.1uF Vdd decoupling (SMD 1206)
  C3 (x=18, y=45)  - 0.1uF VCC decoupling (SMD 1206)

CENTER (gate driver + MOSFETs):
  D1 (x=30, y=8)   - UF4007 bootstrap diode
  C4 (x=30, y=15)  - 220nF bootstrap cap (SMD 1206)
  U1 (x=40, y=20)  - IR2181S gate driver (SOIC-8)
  R1 (x=48, y=15)  - 2.2Ω HO gate resistor (SMD 1206, rotated 90)
  D2 (x=48, y=20)  - 1N5819 Schottky bypass HO (rotated 90)
  R2 (x=48, y=25)  - 2.2Ω LO gate resistor (SMD 1206, rotated 90)
  D3 (x=48, y=30)  - 1N5819 Schottky bypass LO (rotated 90)
  Q1 (x=58, y=15)  - IRF540 high-side MOSFET (TO-220)
  Q2 (x=58, y=25)  - IRF540 low-side MOSFET (TO-220)

RIGHT SIDE (LC tank + matching + RF output):
  L1 (x=65, y=15)  - 300nH tank inductor
  C5 (x=65, y=22)  - 470pF tank cap (SMD 1206)
  R3 (x=65, y=30)  - 2.55Ω load resistor
  L2 (x=72, y=15)  - 130nH matching inductor
  C6 (x=72, y=22)  - 1nF matching cap (SMD 1206)
  J2 (x=72, y=42)  - SMA RF output connector (50Ω)
```

## Output Matching Network: 2.55Ω to 50Ω at 13.56MHz

Q = sqrt(50/2.55 - 1) = sqrt(18.6) = 4.31

X_L = Q x 2.55 = 11.0Ω, Lm = 11.0 / (2pi x 13.56e6) = 129nH -> use 130nH
X_C = 50 / 4.31 = 11.6Ω, Cm = 1 / (2pi x 13.56e6 x 11.6) = 1010pF -> use 1nF

## 50Ω Impedance-Controlled RF Traces

On 1.6mm FR4 (er=4.5, 1oz copper), 50Ω microstrip width = 3.06mm.
Applied to: TANK_OUT and RF_OUT signal paths.

## Trace Widths

| Net | Width | Reason |
|-----|-------|--------|
| +72V5 (Vdd) | 3.0mm | 4A DC, minimal voltage drop |
| MID (switching node) | 3.0mm | 15A peak AC at 13.56MHz |
| GND bus | 2.0mm | Main ground return |
| VCC (12V) | 1.0mm | ~100mA logic supply |
| Gate drive (HO_NET, LO_NET, GATE1, GATE2) | 0.5mm | Fast switching |
| Signal input (HIN, LIN) | 0.3mm | Low current |
| TANK_OUT, RF_OUT | 3.06mm | 50Ω impedance controlled |

## Ground Plane

Bottom layer (B.Cu) is a solid ground copper pour covering the entire board
(0.5mm inset from edges). 10 ground vias connect F.Cu ground traces to the
B.Cu ground plane at regular intervals.

## Critical Layout Rules

1. **Power loop** (Vdd -> Q1 -> Q2 -> GND): < 20mm total. Carries 16A peak
   at 13.56MHz. Minimize inductance to reduce ringing.

2. **Gate drive loops** (U1 -> R1/R2 -> Q1/Q2 gate -> source -> U1): < 10mm
   each. These carry 36A peaks during switching transients.

3. **Kelvin source connections**: Q1 and Q2 need separate source connections
   for gate return and power current. Do NOT share the same trace.

4. **L1 inductor**: Place > 10mm from the power loop to avoid magnetic
   coupling. Orient axis perpendicular to PCB if using air-core coil.

5. **Bypass caps**: C1 (100uF) at power input, C2 (0.1uF) within 5mm of
   Q1 drain-to-GND, C3 (0.1uF) within 5mm of U1 VCC pin.

6. **Thermal**: Q1 and Q2 (TO-220) mounted on board edge with heatsinks
   extending off-board. Use thermal vias under drain pads if possible.

7. **RF traces**: TANK_OUT and RF_OUT paths use 3.06mm width for 50Ω
   impedance match on 1.6mm FR4. Keep total RF path < 30mm.

## Assembly Notes

- Wind L1 (300nH): 5 turns of 2mm copper wire on 10mm diameter air core
- Wind L2 (130nH): 3 turns of 1mm copper wire on 8mm diameter air core
- C5 (470pF) and C6 (1nF): use NP0/C0G dielectric for RF stability
- R3 (2.55Ω): use high-power wirewound resistor (300W rated) on heatsink
- Q1/Q2: mount on heatsinks with thermal pads, Rth < 2°C/W each

---

*Document version: 2.0, 2026-06-27. Updated to match KiCAD project.*
