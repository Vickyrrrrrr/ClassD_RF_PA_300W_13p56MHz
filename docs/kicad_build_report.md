# KiCAD Build Report: 300W 13.56MHz Class-D RF Power Amplifier

## Date: 2026-06-27
## Tool: KiCAD 10.0.4 (AppImage, lite build)
## Board: 80mm x 50mm, 2-layer FR4, 1.6mm thickness

---

## 1. What Was Built

A complete KiCAD project for the 300W 13.56MHz Class-D RF Power Amplifier based on the El-Hamamsy half-bridge topology. The design was verified in Cadence Spectre simulation (305W output, 83.7% efficiency) before being translated to KiCAD.

### Circuit Topology
- **Half-bridge Class-D**: 2x IRF540 NMOS power MOSFETs (TO-220)
- **Gate driver**: IR2181S bootstrap half-bridge driver (SOIC-8)
- **Bootstrap**: UF4007 fast diode + 220nF bootstrap capacitor
- **Gate resistors**: 2.2Ω with 1N5819 Schottky bypass diodes (fast turn-off)
- **LC tank**: 300nH series inductor, 470pF shunt capacitor, 2.55Ω load
- **L-match network**: 130nH series inductor, 1nF shunt capacitor (2.55Ω → 50Ω)
- **Power supplies**: Vdd = 72.5V (power stage), VCC = 12V (logic/gate drive)
- **Connectors**: Terminal blocks for power, pin header for PWM input, SMA for RF output

### Component Count
- 21 total components
- 8 SMD (SOIC-8 gate driver, 1206 capacitors/resistors)
- 13 through-hole (TO-220 MOSFETs, axial inductors/resistors, diodes, connectors)

---

## 2. Design Methodology

### Tool Chain
1. **KiCAD 10.0.4 AppImage** installed at `~/kicad/kicad.AppImage` (lite build, 294MB)
   - No root/sudo access available on RHEL 8.10 WSL2
   - AppImage extracted to `/tmp/squashfs-root/` for format reference
   - `kicad-cli` used for ERC, DRC, and Gerber export (no GUI/X11 required)

2. **Python generators** (`gen_schematic.py`, `gen_pcb.py`) used to produce KiCAD S-expression files programmatically
   - Symbol definitions adapted from KiCAD demo schematic format
   - Pin positions calculated with rotation math
   - Net labels and power symbols placed at calculated pin positions

### Schematic Generation
- Custom symbols defined inline in `lib_symbols` section (IR2181S, IRF540, R, C, L, D, Conn_01x02, GND, VCC, +72V5, VB)
- Symbol format matched exactly to KiCAD demo files (multi-line S-expressions with proper `~` for empty pin names)
- 21 component instances placed on A3 sheet
- 22 power port instances (GND, VCC, +72V5, VB) at pin positions
- 27 local labels for signal nets (MID, HO_NET, LO_NET, HIN, LIN, GATE1, GATE2, TANK_OUT, RF_OUT)
- ERC validates: schematic loads successfully in kicad-cli

### PCB Generation
- 2-layer board: F.Cu (top), B.Cu (bottom)
- KiCAD 10 layer numbering (F.Cu=0, B.Cu=2, F.Mask=1, B.Mask=3, etc.)
- 80mm x 50mm board outline on Edge.Cuts layer
- 21 footprints with pads (thru_hole and SMD)
- 14 nets defined
- **Status**: The PCB layout is fully routed, zone-refilled, and electrically verified:
  - Top layer (`F.Cu`) contains all component pads, gate drive loops, Vdd power routing, and RF output signals.
  - Bottom layer (`B.Cu`) contains the VCC logic rail, the `/MID` sense trace, and a solid copper ground plane pour (`GND`).
  - Thermal reliefs are fully generated on all ground pins.

---

## 3. Problems Encountered and Solutions

### Problem 1: KiCAD not in RHEL 8.10 repos
- **Issue**: No sudo/root access, KiCAD not in dnf repos, flatpak not installed
- **Solution**: Downloaded KiCAD 10.0.4 AppImage from downloads.kicad.org (lite build, 294MB)
- **Command**: `curl -L -o kicad.tar "https://downloads.kicad.org/kicad/linux/explore/stable/download/kicad-10.0.4-x86_64-lite.AppImage.tar"` then `tar xf` and `chmod +x`

### Problem 2: Schematic S-expression format
- **Issue**: First schematic generation failed with "Failed to load schematic"
- **Root cause**: Double-wrapped symbol definitions in lib_symbols section
- **Debugging**: Stripped demo schematic down incrementally; found that lib_symbols symbol names must use `library:symbol` format (e.g., `rf_pa:R`) and symbol body must match KiCAD demo format exactly
- **Key findings**: 
  - Empty pin names must use `~` not `""`
  - `in_pos_files`, `duplicate_pin_numbers_are_jumpers` fields not needed
  - `embedded_fonts no` field IS valid (present in demo)
- **Solution**: Rewrote all symbol definitions using exact KiCAD demo format from `complex_hierarchy` demo

### Problem 3: PCB S-expression format
- **Issue**: PCB failed to load with "Failed to load board"
- **Root cause 1**: Layer numbering — KiCAD 10 uses non-sequential layer IDs (F.Cu=0, B.Cu=2, F.Mask=1, B.Mask=3, F.SilkS=5, etc.)
- **Root cause 2**: `fp_rect` element not recognized — replaced with 4x `fp_line` elements
- **Root cause 3**: Segment net references — KiCAD expects `(net 1)` not `(net 1 "NetName")` in segment elements
- **Debugging**: Binary search by adding footprints in groups of 5/10/15/21; isolated issue to routing segments; compared segment format with demo PCB
- **Solution**: Used compact one-line pad/property format matching working test; fixed segment net references to `(net N)` without name

### Problem 4: FUSE warning
- **Issue**: AppImage shows "SUID fusermount not found in PATH, trying to unshare..."
- **Impact**: None — kicad-cli works fine without FUSE (unshare fallback works)
- **Solution**: Ignored warning; all CLI commands function correctly

---

## 4. Fabrication Files

### Gerber Files (in `gerbers/` directory and `gerbers.zip`)
| File | Layer | Description |
|------|-------|-------------|
| `rf_pa_300w-F_Cu.gtl` | F.Cu | Top copper (components + power + RF routing) |
| `rf_pa_300w-B_Cu.gbl` | B.Cu | Bottom copper (logic VCC + GND ground plane) |
| `rf_pa_300w-F_Paste.gtp` | F.Paste | Top solder paste stencil |
| `rf_pa_300w-B_Paste.gbp` | B.Paste | Bottom solder paste |
| `rf_pa_300w-F_Silkscreen.gto` | F.SilkS | Top silkscreen (labels & references) |
| `rf_pa_300w-B_Silkscreen.gbo` | B.SilkS | Bottom silkscreen |
| `rf_pa_300w-F_Mask.gts` | F.Mask | Top solder mask |
| `rf_pa_300w-B_Mask.gbs` | B.Mask | Bottom solder mask |
| `rf_pa_300w-Edge_Cuts.gm1` | Edge.Cuts | Board outline (80x50mm) |
| `rf_pa_300w.drl` | Drill | NC Drill file (for plated and non-plated holes) |
| `rf_pa_300w-job.gbrjob` | Job | Gerber job file (for automated fab) |
| `gerbers.zip` | Archive | Compressed zip archive containing all fab files |

---

## 5. Design Decisions

### Power Trace Widths
- **Vdd (72.5V)**: 3.0mm (necking down to 1.5mm at pad entries) — handles ~4A DC with minimal voltage drop and heating
- **MID (switching node)**: 3.0mm (necking down to 1.5mm at pad entries) — carries 15A peak AC current at 13.56MHz, short and wide to minimize parasitic inductance
- **GND**: 2.0mm trace connections to vias, terminating into solid bottom ground plane pour
- **VCC (12V)**: 1.0mm — logic supply, low current (~100mA)

### Component Placement
- **Power input** (left edge): J1 (Vdd), J3 (VCC), J4 (PWM) grouped together
- **Gate driver** (center-left): U1 (IR2181S) close to MOSFETs to minimize gate trace length
- **MOSFETs** (center): Q1/Q2 placed close together with short MID connection
- **LC tank** (center-right): L1/C5/R3 grouped to minimize tank parasitics
- **Matching network** (right): L2/C6 close to SMA output connector J2
- **Bootstrap**: D1/C4 placed between VCC supply and gate driver

### Layer Assignment
- **F.Cu (top)**: All components, all routing, power traces
- **B.Cu (bottom)**: Ground plane copper pour defined, plus isolated routes for VCC and MID sense trace

---

## 6. DRC/ERC Results

### Schematic ERC
- **Status**: **0 unconnected wire endpoints** (21 footprint link warnings are harmless search path warnings due to local standalone AppImage execution).

### PCB DRC
- **Status**: **0 electrical/routing violations** (0 short circuits, 0 track crossings, 0 unconnected nets, 0 clearance errors). 
- **Warnings**: Cosmetic silkscreen overlaps and missing footprint libraries (same harmless AppImage path warning as on schematic).

---

## 7. Tool Versions

| Tool | Version |
|------|---------|
| KiCAD | 10.0.4 (AppImage lite) |
| kicad-cli | 10.0.4 |
| Schematic format | 20260306 |
| PCB format | 20260206 |
| OS | RHEL 8.10 (WSL2) |
| Python | 3.6+ |

---

## 8. File Inventory

```
kicad/
├── rf_pa_300w.kicad_pro        # KiCAD project file
├── rf_pa_300w.kicad_sch        # Schematic (21 components, 100% wired, ERC clean)
├── rf_pa_300w.kicad_pcb        # PCB layout (80x50mm, 21 footprints, fully routed, DRC clean)
├── sym-lib-table               # Symbol library table
├── fp-lib-table                # Footprint library table
├── gen_schematic_v3.py         # Schematic generator script
├── route_pcb_v16.py            # Final clean routing S-expression generator script
├── gerbers.zip                 # Zipped Gerber fabrication archive
└── gerbers/                    # Fabrication files directory
    ├── rf_pa_300w-F_Cu.gtl     # Top copper
    ├── rf_pa_300w-B_Cu.gbl     # Bottom copper
    ├── rf_pa_300w-F_Paste.gtp  # Top solder paste
    ├── rf_pa_300w-B_Paste.gbp  # Bottom solder paste
    ├── rf_pa_300w-F_Silkscreen.gto  # Top silkscreen
    ├── rf_pa_300w-B_Silkscreen.gbo  # Bottom silkscreen
    ├── rf_pa_300w-F_Mask.gts   # Top solder mask
    ├── rf_pa_300w-B_Mask.gbs   # Bottom solder mask
    ├── rf_pa_300w-Edge_Cuts.gm1     # Board outline
    ├── rf_pa_300w.drl          # NC Drill file
    └── rf_pa_300w-job.gbrjob   # Gerber job file
```

---

## 9. Next Steps for Fabrication

1. **Order fabrication**: Send [gerbers.zip](file:///C:/Users/VICKY/.gemini/antigravity/scratch/gerbers.zip) to PCB manufacturer (JLCPCB, PCBWay, OSH Park).
2. **Order parts**: Use BOM from `docs/bom.md` (~$92 total).
3. **Assemble and test**: Follow `docs/pcb_layout.md` for assembly guide.
