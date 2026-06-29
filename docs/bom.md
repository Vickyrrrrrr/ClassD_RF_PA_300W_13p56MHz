# Bill of Materials: 300W 13.56MHz Class-D RF Power Amplifier

*Verified and confirmed correct on 2026-06-29 for routed PCB.*

*Updated 2026-06-29 to match KiCAD schematic reference designators.*

## Power Stage

| Ref | KiCAD Ref | Part | Spec | Qty | Source |
|-----|-----------|------|------|-----|--------|
| Q1 | Q1 | IRF540 | 100V, 33A, TO-220 | 1 | Digikey, Mouser |
| Q2 | Q2 | IRF540 | 100V, 33A, TO-220 | 1 | Digikey, Mouser |
| L1 | L1 | Custom coil | 300nH, >20A, air core | 1 | Wind yourself |
| C5 | C5 | Capacitor | 470pF, 200V, NP0/C0G, 1206 | 1 | Digikey |
| R3 | R3 | Resistor | 2.55Ω, 300W, wirewound | 1 | Heatsink mounted |

## Gate Driver

| Ref | KiCAD Ref | Part | Spec | Qty | Notes |
|-----|-----------|------|------|-----|-------|
| U1 | U1 | IR2181S | Bootstrap half-bridge driver, SOIC-8 | 1 | HIN/LIN inputs, 600V half-bridge |
| D1 | D1 | UF4007 | Ultrafast diode, 1000V, 1A, trr=75ns | 1 | Bootstrap diode |
| C4 | C4 | Capacitor | 220nF, 100V, X7R, 1206 | 1 | Bootstrap cap |
| R1 | R1 | Resistor | 2.2Ω, 0.25W, 1206 | 1 | Q1 gate turn-on |
| R2 | R2 | Resistor | 2.2Ω, 0.25W, 1206 | 1 | Q2 gate turn-on |
| D2 | D2 | 1N5819 | Schottky, 40V, 1A | 1 | Q1 gate turn-off bypass |
| D3 | D3 | 1N5819 | Schottky, 40V, 1A | 1 | Q2 gate turn-off bypass |

## Matching Network

| Ref | KiCAD Ref | Part | Spec | Qty | Notes |
|-----|-----------|------|------|-----|-------|
| L2 | L2 | Custom coil | 130nH, air core | 1 | Wind yourself |
| C6 | C6 | Capacitor | 1nF, 200V, NP0/C0G, 1206 | 1 | L-match shunt cap |

## Power Supply Decoupling

| Ref | KiCAD Ref | Part | Spec | Qty | Notes |
|-----|-----------|------|------|-----|-------|
| C1 | C1 | Capacitor | 100uF, 100V, electrolytic | 1 | Vdd bulk cap |
| C2 | C2 | Capacitor | 0.1uF, 100V, X7R, 1206 | 1 | Vdd HF decoupling |
| C3 | C3 | Capacitor | 0.1uF, 100V, X7R, 1206 | 1 | VCC decoupling |

## Connectors

| Ref | KiCAD Ref | Part | Spec | Qty | Notes |
|-----|-----------|------|------|-----|-------|
| J1 | J1 | Terminal block | 2-pin, 5mm pitch | 1 | Vdd 72.5V input |
| J3 | J3 | Terminal block | 2-pin, 5mm pitch | 1 | VCC 12V input |
| J4 | J4 | Pin header | 2-pin, 2.54mm pitch | 1 | PWM input (HIN, LIN) |
| J2 | J2 | SMA connector | Edge mount, 50Ω | 1 | RF output |

## External Power Supplies (not on PCB)

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Vdd supply | 72.5V DC, >8A | 1 | Meanwell or bench supply |
| VCC supply | 12V DC, >1A | 1 | Bench supply or regulator |
| PWM controller | STM32G431 or SG3525 | 1 | Dead-time generation |

## Thermal Management

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Heatsink | TO-220, Rth < 2°C/W | 2 | Q1 and Q2 |
| Thermal pad | Silicone, 0.5mm | 2 | Thermal interface |
| Heatsink (R3) | Wirewound resistor heatsink | 1 | For 300W load resistor |

## Custom Inductor Winding

| Ref | Inductance | Wire | Core | Turns | Notes |
|-----|-----------|------|------|-------|-------|
| L1 | 300nH | 2mm dia copper | 10mm dia air core | ~5 turns | >20A peak |
| L2 | 130nH | 1mm dia copper | 8mm dia air core | ~3 turns | L-match |

## Total Estimated Cost

| Category | Cost |
|----------|------|
| Power MOSFETs (2x IRF540) | $6 |
| Gate driver (IR2181S) | $2 |
| Passives (caps, resistors, diodes) | $15 |
| Connectors (terminal blocks, SMA, header) | $8 |
| Heatsinks | $8 |
| PCB fabrication (5 boards) | $5 |
| Custom inductors (wire) | $3 |
| **Total (excl. power supplies)** | **~$47** |
| Vdd power supply (72.5V, 8A) | $40 |
| VCC power supply (12V) | $5 |
| **Grand Total** | **~$92** |

---

*Document version: 2.0, 2026-06-27. Reference designators match KiCAD schematic.*
