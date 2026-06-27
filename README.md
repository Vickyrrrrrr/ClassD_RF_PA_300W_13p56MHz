# 300W 13.56MHz Class-D RF Power Amplifier

For hackerfab lithography machine RF plasma source.

## What This Is

A 300W, 13.56MHz Class-D RF power amplifier based on the El-Hamamsy half-bridge
topology. Designed and simulated in Cadence Spectre (305W output, 83.7%
efficiency), then translated to a KiCAD 10 PCB project for fabrication.

## Quick Start

### 1. Open the KiCAD project
```bash
# Install KiCAD 10 (if not already installed)
# Linux: download AppImage from https://www.kicad.org/download/linux/
# Windows/Mac: download from https://www.kicad.org/download/

# Open the project
kicad kicad/rf_pa_300w.kicad_pro
```

### 2. Finish the PCB layout
The PCB has all 21 components placed and most routing done, but needs:
- **Ground pour on B.Cu** (bottom layer)
- **Route ~18 remaining unconnected pads** (mostly diode bypass pins)
- **Fix DRC violations** (overlapping traces, narrow widths)
- **Re-export Gerbers** for fabrication

See `docs/kicad_build_report.md` section 9 for step-by-step instructions.

### 3. Order the PCB
- Send `kicad/gerbers/` folder to JLCPCB, PCBWay, or OSH Park
- Settings: 2-layer, 1.6mm FR4, HASL finish, 80x50mm
- Cost: ~$5 for 5 boards

### 4. Order parts
See `docs/bom.md` for complete parts list (~$92 total including power supplies).

### 5. Assemble
See `docs/pcb_layout.md` for component placement and assembly notes.

### 6. Test
1. Apply 12V VCC only (no 72.5V Vdd)
2. Check gate drive waveforms on oscilloscope (HIN, LIN, HO, LO)
3. Apply 72.5V Vdd
4. Measure RF output at SMA connector
5. Tune dead time for ZVS (~19ns needed, see `docs/gate_driver_spec.md`)

## Project Structure

```
ClassD_RF_PA_300W_13p56MHz/
├── README.md                  # This file - START HERE
├── docs/
│   ├── build_report.md        # Full simulation build report (Spectre)
│   ├── kicad_build_report.md  # KiCAD PCB design report
│   ├── gate_driver_spec.md    # IR2181S gate driver specification
│   ├── bom.md                 # Bill of materials (~$92)
│   └── pcb_layout.md          # PCB layout guide and matching network
├── kicad/
│   ├── rf_pa_300w.kicad_pro   # KiCAD 10 project file
│   ├── rf_pa_300w.kicad_sch   # Schematic (25 components, generated)
│   ├── rf_pa_300w.kicad_pcb   # PCB (80x50mm, 21 footprints, ratsnest + B.Cu GND pour)
│   ├── gen_schematic.py       # Schematic generator script
│   ├── gen_pcb.py             # PCB generator script
│   ├── schematic.pdf          # Schematic PDF
│   ├── pcb_layout.pdf         # PCB layout PDF
│   └── gerbers/               # Fabrication files
│       ├── *.gbr              # Gerber layer files
│       ├── *.drl              # Drill files
│       └── pos.csv            # Pick-and-place positions
├── netlists/
│   ├── classd_pa.scs          # Spectre netlist (IRF540 Level-3, bootstrap)
│   └── analyze_results.py     # Python simulation analysis
├── models/
│   └── irf540.mod             # IRF540 SPICE model
└── results/
    └── classd_irf540_bs_ascii # Final simulation output (305W, 83.7%)
```

## Circuit Design

### Topology
- **Half-bridge Class-D** with 2x IRF540 NMOS power MOSFETs
- **IR2181S** bootstrap gate driver (SOIC-8)
- **LC tank**: 300nH series L, 470pF shunt C, 2.55Ω load
- **L-match network**: 130nH series L, 1nF shunt C (2.55Ω → 50Ω)

### Key Design Parameters

| Parameter | Value |
|-----------|-------|
| Output power | 305W (simulated) |
| Frequency | 13.56MHz |
| Efficiency | 83.7% (simulated) |
| Vdd (power stage) | 72.5V |
| VCC (gate driver) | 12V |
| Dead time | 11.5ns (needs tuning to ~19ns for full ZVS) |
| Load resistance | 2.55Ω |
| RF output impedance | 50Ω (via L-match) |

### Component List (21 components on PCB)

| Ref | Part | Value | Package |
|-----|------|-------|---------|
| U1 | IR2181S | Gate driver | SOIC-8 |
| Q1, Q2 | IRF540 | NMOS power | TO-220 |
| D1 | UF4007 | Bootstrap diode | DO-41 |
| D2, D3 | 1N5819 | Schottky bypass | DO-41 |
| R1, R2 | 2.2Ω | Gate resistors | 1206 SMD |
| R3 | 2.55Ω | Load resistor | THT |
| C1 | 100uF | Vdd bulk cap | Radial THT |
| C2, C3 | 0.1uF | Decoupling | 1206 SMD |
| C4 | 220nF | Bootstrap cap | 1206 SMD |
| C5 | 470pF | Tank cap | 1206 SMD |
| C6 | 1nF | Match cap | 1206 SMD |
| L1 | 300nH | Tank inductor | THT (custom wound) |
| L2 | 130nH | Match inductor | THT (custom wound) |
| J1 | Terminal block | Vdd 72.5V input | 5mm pitch |
| J2 | SMA | RF output 50Ω | Edge mount |
| J3 | Terminal block | VCC 12V input | 5mm pitch |
| J4 | Pin header | PWM input (HIN, LIN) | 2.54mm |

## PCB Specifications

| Parameter | Value |
|-----------|-------|
| Board size | 80mm x 50mm |
| Layers | 2 (F.Cu top, B.Cu bottom ground plane) |
| Material | FR4, 1.6mm, 1oz copper |
| Finish | HASL |
| RF traces | 50Ω impedance controlled (3.06mm width) |
| Power traces | 3.0mm (Vdd, MID switching node) |
| Min trace width | 0.25mm |
| Min clearance | 0.2mm |

## Simulation Results

The amplifier was simulated in Cadence Spectre 14.1 using a real IRF540
Level-3 SPICE model with bootstrap gate drive:

- **Output power**: 305W
- **Drain efficiency**: 83.7%
- **Frequency**: 13.56MHz
- **0 simulation errors**

The root cause of a 7-week simulation failure was identified as the gate
drive being referenced to GND instead of the mid (switching) node. With
bootstrap gate drive (Vgs referenced to mid), the simulation works correctly.

See `docs/build_report.md` for the full simulation methodology and debugging.

## What's Left To Do

1. **Finish PCB in KiCAD GUI** (ground pour, routing, DRC cleanup)
2. **Re-export Gerbers** from the final PCB
3. **Order PCB** from JLCPCB/PCBWay (~$5 for 5 boards)
4. **Order parts** from `docs/bom.md` (~$92 total)
5. **Wind custom inductors** (L1=300nH, L2=130nH, see `docs/pcb_layout.md`)
6. **Assemble PCB** (solder components, mount heatsinks on Q1/Q2)
7. **Test**: 12V VCC first, check gate drive, then 72.5V Vdd
8. **Tune dead time** for ZVS on oscilloscope (~19ns target)

## Documentation Index

| Document | What's in it |
|----------|-------------|
| `README.md` (this file) | Project overview, quick start, component list |
| `docs/build_report.md` | Full simulation report (Spectre, IRF540, debugging) |
| `docs/kicad_build_report.md` | KiCAD PCB design report (format, DRC, Gerbers) |
| `docs/gate_driver_spec.md` | IR2181S gate driver circuit, bootstrap, timing |
| `docs/bom.md` | Complete bill of materials with KiCAD refs |
| `docs/pcb_layout.md` | PCB layout guide, trace widths, matching network |

## Tools Used

- **Cadence Spectre 14.1** — circuit simulation
- **KiCAD 10.0.4** — schematic capture and PCB layout
- **Python 3** — simulation analysis and KiCAD file generation
- **OS**: RHEL 8.10 WSL2 on Windows 11

## License

Open source hardware design for hackerfab lithography machine.

---

*Project date: 2026-06-27*
*Simulation: 305W at 83.7% efficiency*
*KiCAD: generated schematic and placement/ratsnest PCB; final ERC/DRC required before fabrication*
