#!/usr/bin/env python3
"""
Generate KiCAD 10 PCB layout for 300W 13.56MHz Class-D RF Power Amplifier.
2-layer FR4, 80x50mm. Uses exact KiCAD 10 footprint/pad format from demos.

This generator intentionally produces a placement/ratsnest board with a B.Cu
GND pour, not final hand-routing. The previous generated routing used straight
top-layer traces that crossed unrelated pads and created hard shorts.
"""
import uuid as _uuid
def uuid(): return str(_uuid.uuid4())

NET_NAMES = ["", "+72V5", "GND", "VCC", "VB", "MID", "HO_NET", "LO_NET",
             "HIN", "LIN", "GATE1", "GATE2", "TANK_OUT", "RF_OUT"]
NET_IDS = {n: i for i, n in enumerate(NET_NAMES)}

L = []
w = L.append

# Header
w('(kicad_pcb')
w('\t(version 20241229)')
w('\t(generator "pcbnew")')
w('\t(generator_version "9.0")')
w('\t(general')
w('\t\t(thickness 1.6)')
w('\t\t(legacy_teardrops no)')
w('\t)')
w('\t(paper "A4")')
w('\t(title_block')
w('\t\t(title "300W 13.56MHz Class-D RF Power Amplifier")')
w('\t\t(date "2026-06-27")')
w('\t\t(rev "1.0")')
w('\t\t(company "Hackerfab")')
w('\t\t(comment 1 "El-Hamamsy topology, IRF540 + IR2181S")')
w('\t\t(comment 2 "Vdd=72.5V, Pout=305W, eff=83.7%")')
w('\t)')
w('\t(layers')
for ln in ['(0 "F.Cu" signal)', '(2 "B.Cu" signal)',
           '(9 "F.Adhes" user "F.Adhesive")', '(11 "B.Adhes" user "B.Adhesive")',
           '(13 "F.Paste" user)', '(15 "B.Paste" user)',
           '(5 "F.SilkS" user "F.Silkscreen")', '(7 "B.SilkS" user "B.Silkscreen")',
           '(1 "F.Mask" user)', '(3 "B.Mask" user)',
           '(17 "Dwgs.User" user "User.Drawings")', '(19 "Cmts.User" user "User.Comments")',
           '(21 "Eco1.User" user "User.Eco1")', '(23 "Eco2.User" user "User.Eco2")',
           '(25 "Edge.Cuts" user)', '(27 "Margin" user)',
           '(31 "F.CrtYd" user "F.Courtyard")', '(29 "B.CrtYd" user "B.Courtyard")',
           '(35 "F.Fab" user)', '(33 "B.Fab" user)']:
    w('\t\t' + ln)
w('\t)')

# Nets
for i, name in enumerate(NET_NAMES):
    if name:
        w('\t(net %d "%s")' % (i, name))
    else:
        w('\t(net 0 "")')

# Setup
w('\t(setup')
w('\t\t(pad_to_mask_clearance 0)')
w('\t\t(allow_soldermask_bridges_in_footprints no)')
w('\t\t(tenting front back)')
w('\t)')

# Board outline
for x1, y1, x2, y2 in [(0,0,80,0),(80,0,80,50),(80,50,0,50),(0,50,0,0)]:
    w('\t(gr_line')
    w('\t\t(start %d %d)' % (x1, y1))
    w('\t\t(end %d %d)' % (x2, y2))
    w('\t\t(stroke (width 0.2) (type default))')
    w('\t\t(layer "Edge.Cuts")')
    w('\t\t(uuid "%s")' % uuid())
    w('\t)')

def pad(num, x, y, net, size_x=1.5, size_y=1.5, drill=0.8, shape="circle"):
    nid = NET_IDS.get(net, 0)
    w('\t\t\t(pad "%s" thru_hole %s' % (num, shape))
    w('\t\t\t\t(at %.2f %.2f)' % (x, y))
    w('\t\t\t\t(size %.2f %.2f)' % (size_x, size_y))
    if drill > 0:
        w('\t\t\t\t(drill %.2f)' % drill)
    w('\t\t\t\t(layers "*.Cu" "*.Mask")')
    w('\t\t\t\t(remove_unused_layers no)')
    if nid > 0:
        w('\t\t\t\t(net %d "%s")' % (nid, net))
    w('\t\t\t\t(uuid "%s")' % uuid())
    w('\t\t\t)')

def smd_pad(num, x, y, net, sx=1.5, sy=1.6):
    nid = NET_IDS.get(net, 0)
    w('\t\t\t(pad "%s" smd roundrect' % num)
    w('\t\t\t\t(at %.2f %.2f)' % (x, y))
    w('\t\t\t\t(size %.2f %.2f)' % (sx, sy))
    w('\t\t\t\t(layers "F.Cu" "F.Paste" "F.Mask")')
    w('\t\t\t\t(roundrect_rratio 0.25)')
    if nid > 0:
        w('\t\t\t\t(net %d "%s")' % (nid, net))
    w('\t\t\t\t(uuid "%s")' % uuid())
    w('\t\t\t)')

def footprint(fp_name, ref, val, x, y, rot=0, attr="through_hole"):
    w('\t(footprint "%s"' % fp_name)
    w('\t\t(layer "F.Cu")')
    w('\t\t(uuid "%s")' % uuid())
    w('\t\t(at %.2f %.2f %d)' % (x, y, rot))
    w('\t\t(descr "%s")' % val)
    w('\t\t(property "Reference" "%s"' % ref)
    w('\t\t\t(at 0 -3 0)')
    w('\t\t\t(layer "F.SilkS")')
    w('\t\t\t(uuid "%s")' % uuid())
    w('\t\t\t(effects (font (size 1 1) (thickness 0.15)))')
    w('\t\t)')
    w('\t\t(property "Value" "%s"' % val)
    w('\t\t\t(at 0 3 0)')
    w('\t\t\t(layer "F.Fab")')
    w('\t\t\t(uuid "%s")' % uuid())
    w('\t\t\t(effects (font (size 1 1) (thickness 0.15)))')
    w('\t\t)')
    w('\t\t(property "Datasheet" ""')
    w('\t\t\t(at 0 0 0)')
    w('\t\t\t(unlocked yes)')
    w('\t\t\t(layer "F.Fab")')
    w('\t\t\t(hide yes)')
    w('\t\t\t(uuid "%s")' % uuid())
    w('\t\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))')
    w('\t\t)')
    w('\t\t(attr %s)' % attr)
    # Footprint body outline using fp_line (4 sides)
    for sx, sy, ex, ey in [(-3,-2,3,-2),(3,-2,3,2),(3,2,-3,2),(-3,2,-3,-2)]:
        w('\t\t(fp_line')
        w('\t\t\t(start %.1f %.1f)' % (sx, sy))
        w('\t\t\t(end %.1f %.1f)' % (ex, ey))
        w('\t\t\t(stroke (width 0.12) (type solid))')
        w('\t\t\t(layer "F.SilkS")')
        w('\t\t\t(uuid "%s")' % uuid())
        w('\t\t)')

def end_footprint():
    w('\t)')

# --- J1: Vdd power input ---
footprint("TerminalBlock:TerminalBlock_bornier-2_P5.0mm", "J1", "Vdd 72.5V", 5, 5)
pad("1", -2.54, 0, "+72V5", 2.5, 2.5, 1.2, "rect")
pad("2", 2.54, 0, "GND", 2.5, 2.5, 1.2)
end_footprint()

# --- J3: VCC logic supply ---
footprint("TerminalBlock:TerminalBlock_bornier-2_P5.0mm", "J3", "VCC 12V", 5, 45)
pad("1", -2.54, 0, "VCC", 2.5, 2.5, 1.2, "rect")
pad("2", 2.54, 0, "GND", 2.5, 2.5, 1.2)
end_footprint()

# --- J4: PWM input ---
footprint("Connector:PinHeader_1x02_P2.54mm_Vertical", "J4", "PWM IN", 5, 25)
pad("1", 0, -1.27, "HIN", 1.5, 1.5, 0.8, "rect")
pad("2", 0, 1.27, "LIN", 1.5, 1.5, 0.8)
end_footprint()

# --- C1: 100uF bulk cap ---
footprint("Capacitor_THT:CP_Radial_D10.0mm_P5.00mm", "C1", "100uF", 18, 5)
pad("1", -2.5, 0, "+72V5", 2.0, 2.0, 0.8, "rect")
pad("2", 2.5, 0, "GND", 2.0, 2.0, 0.8)
end_footprint()

# --- C2: 0.1uF Vdd decoupling (SMD) ---
footprint("Capacitor_SMD:C_1206_3216Metric", "C2", "0.1uF", 18, 12, attr="smd")
smd_pad("1", -1.6, 0, "+72V5")
smd_pad("2", 1.6, 0, "GND")
end_footprint()

# --- C3: 0.1uF VCC decoupling (SMD) ---
footprint("Capacitor_SMD:C_1206_3216Metric", "C3", "0.1uF", 18, 45, attr="smd")
smd_pad("1", -1.6, 0, "VCC")
smd_pad("2", 1.6, 0, "GND")
end_footprint()

# --- D1: UF4007 bootstrap diode ---
footprint("Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", "D1", "UF4007", 30, 8)
pad("1", -5.08, 0, "VCC", 2.0, 2.0, 0.8, "rect")
pad("2", 5.08, 0, "VB", 2.0, 2.0, 0.8)
end_footprint()

# --- C4: 220nF bootstrap cap (SMD) ---
footprint("Capacitor_SMD:C_1206_3216Metric", "C4", "220nF", 30, 15, attr="smd")
smd_pad("1", -1.6, 0, "VB")
smd_pad("2", 1.6, 0, "MID")
end_footprint()

# --- U1: IR2181S gate driver (SOIC-8 SMD) ---
footprint("Package_SOIC:SOIC-8_3.9x4.9mm_P1.27mm", "U1", "IR2181S", 40, 20, attr="smd")
smd_pad("1", -1.905, -1.905, "VB", 0.6, 0.6)
smd_pad("2", -1.905, -0.635, "HIN", 0.6, 0.6)
smd_pad("3", -1.905, 0.635, "VCC", 0.6, 0.6)
smd_pad("4", -1.905, 1.905, "GND", 0.6, 0.6)
smd_pad("5", 1.905, 1.905, "LO_NET", 0.6, 0.6)
smd_pad("6", 1.905, 0.635, "MID", 0.6, 0.6)
smd_pad("7", 1.905, -0.635, "HO_NET", 0.6, 0.6)
smd_pad("8", 1.905, -1.905, "LIN", 0.6, 0.6)
end_footprint()

# --- R1: 2.2 ohm HO gate resistor (SMD, rotated 90) ---
footprint("Resistor_SMD:R_1206_3216Metric", "R1", "2.2", 48, 15, 90, attr="smd")
smd_pad("1", -1.6, 0, "HO_NET")
smd_pad("2", 1.6, 0, "GATE1")
end_footprint()

# --- D2: 1N5819 Schottky bypass HO ---
footprint("Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", "D2", "1N5819", 39, 15, 0)
pad("1", -5.08, 0, "GATE1", 2.0, 2.0, 0.8, "rect")
pad("2", 5.08, 0, "HO_NET", 2.0, 2.0, 0.8)
end_footprint()

# --- R2: 2.2 ohm LO gate resistor ---
footprint("Resistor_SMD:R_1206_3216Metric", "R2", "2.2", 48, 25, 90, attr="smd")
smd_pad("1", -1.6, 0, "LO_NET")
smd_pad("2", 1.6, 0, "GATE2")
end_footprint()

# --- D3: 1N5819 Schottky bypass LO ---
footprint("Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", "D3", "1N5819", 39, 25, 0)
pad("1", -5.08, 0, "GATE2", 2.0, 2.0, 0.8, "rect")
pad("2", 5.08, 0, "LO_NET", 2.0, 2.0, 0.8)
end_footprint()

# --- Q1: IRF540 high-side MOSFET (TO-220) ---
footprint("Package_TO_SOT_THT:TO-220-3_Vertical", "Q1", "IRF540", 58, 15)
pad("1", -2.54, 0, "GATE1", 1.5, 1.5, 0.8, "rect")
pad("2", 0, 0, "+72V5", 1.5, 1.5, 0.8)
pad("3", 2.54, 0, "MID", 1.5, 1.5, 0.8)
end_footprint()

# --- Q2: IRF540 low-side MOSFET ---
footprint("Package_TO_SOT_THT:TO-220-3_Vertical", "Q2", "IRF540", 58, 25)
pad("1", -2.54, 0, "GATE2", 1.5, 1.5, 0.8, "rect")
pad("2", 0, 0, "MID", 1.5, 1.5, 0.8)
pad("3", 2.54, 0, "GND", 1.5, 1.5, 0.8)
end_footprint()

# --- L1: 300nH tank inductor ---
footprint("Inductor_THT:L_Axial_L7.0mm_D3.3mm_P5.08mm_Vertical", "L1", "300nH", 65, 15)
pad("1", -2.54, 0, "MID", 1.5, 1.5, 0.8, "rect")
pad("2", 2.54, 0, "TANK_OUT", 1.5, 1.5, 0.8)
end_footprint()

# --- C5: 470pF tank cap (SMD) ---
footprint("Capacitor_SMD:C_1206_3216Metric", "C5", "470pF", 65, 22, attr="smd")
smd_pad("1", -1.6, 0, "TANK_OUT")
smd_pad("2", 1.6, 0, "GND")
end_footprint()

# --- R3: 2.55 ohm load ---
footprint("Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P5.08mm_Vertical", "R3", "2.55", 65, 30)
pad("1", -2.54, 0, "TANK_OUT", 1.5, 1.5, 0.8, "rect")
pad("2", 2.54, 0, "GND", 1.5, 1.5, 0.8)
end_footprint()

# --- L2: 130nH matching inductor ---
footprint("Inductor_THT:L_Axial_L7.0mm_D3.3mm_P5.08mm_Vertical", "L2", "130nH", 72, 15)
pad("1", -2.54, 0, "TANK_OUT", 1.5, 1.5, 0.8, "rect")
pad("2", 2.54, 0, "RF_OUT", 1.5, 1.5, 0.8)
end_footprint()

# --- C6: 1nF matching cap (SMD) ---
footprint("Capacitor_SMD:C_1206_3216Metric", "C6", "1nF", 72, 22, attr="smd")
smd_pad("1", -1.6, 0, "RF_OUT")
smd_pad("2", 1.6, 0, "GND")
end_footprint()

# --- J2: SMA RF output ---
footprint("Connector_Coaxial:SMA_Amphenol_132289_EdgeMount", "J2", "SMA 50ohm", 72, 42)
pad("1", 0, 0, "RF_OUT", 2.0, 2.0, 0.9, "rect")
pad("2", -2.54, 0, "GND", 2.0, 2.0, 0.9)
end_footprint()

# B.Cu ground pour. Final high-current/RF routing should still be done and
# checked in the KiCad GUI; this file avoids fake copper that creates shorts.
w('\t(zone')
w('\t\t(net %d)' % NET_IDS["GND"])
w('\t\t(net_name "GND")')
w('\t\t(layer "B.Cu")')
w('\t\t(uuid "%s")' % uuid())
w('\t\t(hatch edge 0.5)')
w('\t\t(connect_pads (clearance 0.5))')
w('\t\t(min_thickness 0.25)')
w('\t\t(filled_areas_thickness no)')
w('\t\t(fill (thermal_gap 0.5) (thermal_bridge_width 0.5))')
w('\t\t(polygon')
w('\t\t\t(pts')
w('\t\t\t\t(xy 0.5 0.5) (xy 79.5 0.5) (xy 79.5 49.5) (xy 0.5 49.5)')
w('\t\t\t)')
w('\t\t)')
w('\t)')

# Silkscreen
w('\t(gr_text "300W 13.56MHz Class-D RF PA"')
w('\t\t(at 40 2 0)')
w('\t\t(layer "F.SilkS")')
w('\t\t(uuid "%s")' % uuid())
w('\t\t(effects (font (size 1.5 1.5) (thickness 0.15)))')
w('\t)')
w('\t(gr_text "Hackerfab Rev 1.0"')
w('\t\t(at 40 48 0)')
w('\t\t(layer "F.SilkS")')
w('\t\t(uuid "%s")' % uuid())
w('\t\t(effects (font (size 1 1) (thickness 0.15)))')
w('\t)')

w(')')

import sys
outfile = sys.argv[1] if len(sys.argv) > 1 else 'rf_pa_300w.kicad_pcb'
with open(outfile, 'w') as f:
    f.write('\n'.join(L) + '\n')
print("Generated: %s (%d lines, %d footprints)" % (outfile, len(L), 21))
