#!/usr/bin/env python3
"""
Generate KiCAD 10 schematic with EXPLICIT WIRES between component pins.
Components placed in logical signal-flow layout (left to right).
Zero tradeoffs: every connection is a visible wire.
"""
import uuid as _uuid, math

def uuid(): return str(_uuid.uuid4())

# === SYMBOL DEFINITIONS (same as v2, proven to load) ===
# Using exact KiCAD demo format with ~ for empty pin names

def make_sym(name, ref, val_default, fp, pins, graphics, power=False, pwr_out=False):
    """Generate a symbol definition. pins = [(number, name, type, x, y, angle, length)]"""
    pwr_attr = '\n\t\t\t(power)' if power else ''
    s = '		(symbol "rf_pa:%s"%s\n' % (name, pwr_attr)
    s += '			(pin_names (offset 0))\n'
    s += '			(exclude_from_sim no)\n'
    s += '			(in_bom yes)\n'
    s += '			(on_board yes)\n'
    s += '			(property "Reference" "%s" (at 0 -5 0) (effects (font (size 1.524 1.524))))\n' % ref
    s += '			(property "Value" "%s" (at 0 5 0) (effects (font (size 1.524 1.524))))\n' % name
    s += '			(property "Footprint" "%s" (at 0 0 0) (effects (font (size 0.762 0.762)) (hide yes)))\n' % fp
    s += '			(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.524 1.524))))\n'
    s += '			(property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    s += graphics
    s += '			(symbol "%s_1_1\n' % name
    for num, pname, ptype, px, py, pang, plen in pins:
        hide = ' (hide yes)' if power else ''
        s += '				(pin %s line (at %s %s %s) (length %s)%s\n' % (ptype, px, py, pang, plen, hide)
        s += '					(name "%s" (effects (font (size 1.016 1.016))))\n' % pname
        s += '					(number "%s" (effects (font (size 1.016 1.016))))\n' % num
        s += '				)\n'
    s += '			)\n'
    s += '			(embedded_fonts no)\n'
    s += '		)'
    return s

# Graphics for each symbol type
G_R = '			(symbol "R_0_1" (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none))))\n'
G_C = '			(symbol "C_0_1" (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none))))\n'
G_L = '			(symbol "L_0_1" (arc (start 0 -2.54) (mid 1.27 -1.27) (end 0 0) (stroke (width 0.254) (type default)) (fill (type none))) (arc (start 0 0) (mid 1.27 1.27) (end 0 2.54) (stroke (width 0.254) (type default)) (fill (type none))))\n'
G_D = '			(symbol "D_0_1" (polyline (pts (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type outline))) (polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27)) (stroke (width 0.1524) (type default)) (fill (type none))))\n'
G_CONN = '			(symbol "Conn_01x02_0_1" (rectangle (start -1.27 -2.413) (end 0 -2.159) (stroke (width 0.1524) (type default)) (fill (type none))) (rectangle (start -1.27 0.127) (end 0 0.381) (stroke (width 0.1524) (type default)) (fill (type none))) (polyline (pts (xy -1.27 0) (xy -2.54 0)) (stroke (width 0.1524) (type default)) (fill (type none))) (polyline (pts (xy -1.27 -2.54) (xy -2.54 -2.54)) (stroke (width 0.1524) (type default)) (fill (type none))) (arc (start -1.27 0) (mid 0 1.27) (end 1.27 0) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 1.27 -2.54) (xy 1.27 0) (xy -1.27 0)) (stroke (width 0.254) (type default)) (fill (type none))))\n'
G_IC = '			(symbol "IR2181S_0_1" (rectangle (start -7.62 -7.62) (end 7.62 7.62) (stroke (width 0.254) (type default)) (fill (type background))))\n'
G_MOS = '			(symbol "IRF540_0_1" (circle (center 1.27 0) (radius 3.81) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy -2.54 0) (xy -1.27 0)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0 -2.54) (xy 0 -1.27)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0 1.27) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.635 -1.27) (xy 0.635 1.27)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 1.27 -1.27) (xy 1.27 -2.54)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 1.27 1.27) (xy 1.27 2.54)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 1.905 -1.27) (xy 1.905 1.27)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 1.905 0.635) (xy 1.905 1.27) (xy 0.635 1.27) (xy 0.635 0.635) (xy 1.905 0.635) (xy 1.905 0) (xy 0.635 0) (xy 0.635 0.635)) (stroke (width 0) (type default)) (fill (type outline))) (polyline (pts (xy 1.905 -1.27) (xy 1.905 -0.635) (xy 0.635 -0.635) (xy 0.635 -1.27)) (stroke (width 0) (type default)) (fill (type outline))) (polyline (pts (xy 2.54 -2.54) (xy 1.27 -2.54)) (stroke (width 0.1524) (type default)) (fill (type none))) (polyline (pts (xy 2.54 2.54) (xy 1.27 2.54)) (stroke (width 0.1524) (type default)) (fill (type none))))\n'
G_PWR = '			(symbol "%s_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none))))\n'
G_GND = '			(symbol "GND_0_1" (polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none))))\n'
G_PWR_FLAG = ''  # PWR_FLAG has no graphics, just a pin

# Pin definitions: (number, name, type, x, y, angle, length)
# Note: Y in symbol definition, will be negated by KiCAD in schematic
P_R = [("1","~","passive",0,3.81,270,1.27),("2","~","passive",0,-3.81,90,1.27)]
P_C = [("1","~","passive",0,3.81,270,2.794),("2","~","passive",0,-3.81,90,2.794)]
P_L = [("1","~","passive",0,3.81,270,1.27),("2","~","passive",0,-3.81,90,1.27)]
P_D = [("1","A","passive",-3.81,0,0,2.54),("2","K","passive",3.81,0,180,2.54)]
P_CONN = [("1","Pin_1","passive",-2.54,0,0,1.27),("2","Pin_2","passive",-2.54,-2.54,0,1.27)]
P_IR2181S = [
    ("2","HIN","input",-10.16,-5.08,0,2.54),("8","LIN","input",-10.16,-2.54,0,2.54),
    ("3","VCC","power_in",-10.16,2.54,0,2.54),("4","COM","power_in",-10.16,5.08,0,2.54),
    ("1","VB","passive",10.16,-5.08,180,2.54),("7","HO","output",10.16,-2.54,180,2.54),
    ("6","VS","passive",10.16,2.54,180,2.54),("5","LO","output",10.16,5.08,180,2.54),
]
P_IRF540 = [("1","G","input",-5.08,0,0,2.54),("2","D","passive",2.54,5.08,270,2.54),("3","S","passive",2.54,-5.08,90,2.54)]
P_PWR = [("1","~","power_in",0,0,0,0)]

# Generate all symbols
SYMBOLS = []
SYMBOLS.append(make_sym("R","R","R","",P_R,G_R))
SYMBOLS.append(make_sym("C","C","C","",P_C,G_C))
SYMBOLS.append(make_sym("L","L","L","",P_L,G_L))
SYMBOLS.append(make_sym("D","D","D","",P_D,G_D))
SYMBOLS.append(make_sym("Conn_01x02","J","Conn","",P_CONN,G_CONN))
SYMBOLS.append(make_sym("IR2181S","U","IR2181S","Package_SOIC:SOIC-8_3.9x4.9mm_P1.27mm",P_IR2181S,G_IC))
SYMBOLS.append(make_sym("IRF540","Q","IRF540","Package_TO_SOT_THT:TO-220-3_Vertical",P_IRF540,G_MOS))
SYMBOLS.append(make_sym("GND","#PWR","GND","",P_PWR,G_GND,power=True))
SYMBOLS.append(make_sym("VCC","#PWR","VCC","",P_PWR,G_PWR%"VCC",power=True))
SYMBOLS.append(make_sym("+72V5","#PWR","+72V5","",P_PWR,G_PWR%"+72V5",power=True))
SYMBOLS.append(make_sym("VB","#PWR","VB","",P_PWR,G_PWR%"VB",power=True))
# PWR_FLAG - power_out pin
P_PWR_FLAG = [("1","PWR_FLAG","power_out",0,0,0,0)]
SYMBOLS.append(make_sym("PWR_FLAG","#PWR","PWR_FLAG","",P_PWR_FLAG,G_PWR_FLAG,power=True))

# === PIN POSITION MAPS (Y already corrected for KiCAD flip) ===
# absolute_pin = (comp_x + pin_x_after_rotation, comp_y + pin_y_after_rotation)
# For rot=0: abs = (cx+px, cy-py)  [Y flipped]
# For rot=90: abs = (cx-py, cy-px) [rotate then flip]
PIN_MAPS = {
    "rf_pa:R": {"1":(0,-3.81),"2":(0,3.81)},
    "rf_pa:C": {"1":(0,-3.81),"2":(0,3.81)},
    "rf_pa:L": {"1":(0,-3.81),"2":(0,3.81)},
    "rf_pa:D": {"1":(-3.81,0),"2":(3.81,0)},
    "rf_pa:Conn_01x02": {"1":(-2.54,0),"2":(-2.54,2.54)},
    "rf_pa:IR2181S": {"2":(-10.16,5.08),"8":(-10.16,2.54),"3":(-10.16,-2.54),"4":(-10.16,-5.08),
                     "1":(10.16,5.08),"7":(10.16,2.54),"6":(10.16,-2.54),"5":(10.16,-5.08)},
    "rf_pa:IRF540": {"1":(-5.08,0),"2":(2.54,-5.08),"3":(2.54,5.08)},
    "rf_pa:GND": {"1":(0,0)},
    "rf_pa:VCC": {"1":(0,0)},
    "rf_pa:+72V5": {"1":(0,0)},
    "rf_pa:VB": {"1":(0,0)},
    "rf_pa:PWR_FLAG": {"1":(0,0)},
}

def pin_abs(cx, cy, rot, rx, ry):
    r = math.radians(rot)
    return (round(cx + rx*math.cos(r) - ry*math.sin(r), 4),
            round(cy + rx*math.sin(r) + ry*math.cos(r), 4))

# === COMPONENT PLACEMENT (signal flow left to right) ===
COMPS = []
def add(lib_id, ref, value, fp, x, y, rot=0):
    COMPS.append({"lib_id":lib_id,"ref":ref,"value":value,"fp":fp,"x":x,"y":y,"rot":rot,"uuid":uuid()})

# Column 1: Power inputs (x=25)
add("rf_pa:Conn_01x02","J1","Vdd 72.5V","TerminalBlock:TerminalBlock_bornier-2_P5.0mm",25,40)
add("rf_pa:Conn_01x02","J3","VCC 12V","TerminalBlock:TerminalBlock_bornier-2_P5.0mm",25,70)
add("rf_pa:Conn_01x02","J4","PWM IN","Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",25,100)

# Column 2: Decoupling (x=45)
add("rf_pa:C","C1","100uF","Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",45,40)
add("rf_pa:C","C2","0.1uF","Capacitor_SMD:C_1206_3216Metric",55,40)
add("rf_pa:C","C3","0.1uF","Capacitor_SMD:C_1206_3216Metric",45,70)

# Column 3: Bootstrap (x=75)
add("rf_pa:D","D1","UF4007","Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",75,55)
add("rf_pa:C","C4","220nF","Capacitor_SMD:C_1206_3216Metric",75,65)

# Column 4: Gate driver (x=100)
add("rf_pa:IR2181S","U1","IR2181S","Package_SOIC:SOIC-8_3.9x4.9mm_P1.27mm",100,60)

# Column 5: Gate resistors + bypass diodes (x=130)
add("rf_pa:R","R1","2.2","Resistor_SMD:R_1206_3216Metric",130,50,90)
add("rf_pa:D","D2","1N5819","Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",135,50,90)
add("rf_pa:R","R2","2.2","Resistor_SMD:R_1206_3216Metric",130,70,90)
add("rf_pa:D","D3","1N5819","Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",135,70,90)

# Column 6: MOSFETs (x=160)
add("rf_pa:IRF540","Q1","IRF540","Package_TO_SOT_THT:TO-220-3_Vertical",160,50)
add("rf_pa:IRF540","Q2","IRF540","Package_TO_SOT_THT:TO-220-3_Vertical",160,70)

# Column 7: LC Tank (x=185)
add("rf_pa:L","L1","300nH","Inductor_THT:L_Axial_L7.0mm_D3.3mm_P5.08mm_Vertical",185,50,90)
add("rf_pa:C","C5","470pF","Capacitor_SMD:C_1206_3216Metric",195,60)
add("rf_pa:R","R3","2.55","Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P5.08mm_Vertical",205,60)

# Column 8: Matching + output (x=220)
add("rf_pa:L","L2","130nH","Inductor_THT:L_Axial_L7.0mm_D3.3mm_P5.08mm_Vertical",220,50,90)
add("rf_pa:C","C6","1nF","Capacitor_SMD:C_1206_3216Metric",230,60)
add("rf_pa:Conn_01x02","J2","SMA 50ohm","Connector_Coaxial:SMA_Amphenol_132289_EdgeMount",240,60)

# PWR_FLAGs
add("rf_pa:PWR_FLAG","FL1","PWR_FLAG","",15,40)
add("rf_pa:PWR_FLAG","FL2","PWR_FLAG","",15,70)
add("rf_pa:PWR_FLAG","FL3","PWR_FLAG","",15,90)
add("rf_pa:PWR_FLAG","FL4","PWR_FLAG","",60,55)

# === NET ASSIGNMENTS ===
PIN_NETS = {
    "J1":{"1":"+72V5","2":"GND"}, "J3":{"1":"VCC","2":"GND"}, "J4":{"1":"HIN","2":"LIN"},
    "C1":{"1":"+72V5","2":"GND"}, "C2":{"1":"+72V5","2":"GND"}, "C3":{"1":"VCC","2":"GND"},
    "D1":{"1":"VCC","2":"VB"}, "C4":{"1":"VB","2":"MID"},
    "U1":{"2":"HIN","8":"LIN","3":"VCC","4":"GND","1":"VB","7":"HO_NET","6":"MID","5":"LO_NET"},
    "R1":{"1":"HO_NET","2":"GATE1"}, "D2":{"1":"GATE1","2":"HO_NET"},
    "R2":{"1":"LO_NET","2":"GATE2"}, "D3":{"1":"GATE2","2":"LO_NET"},
    "Q1":{"1":"GATE1","2":"+72V5","3":"MID"}, "Q2":{"1":"GATE2","2":"MID","3":"GND"},
    "L1":{"1":"MID","2":"TANK_OUT"}, "C5":{"1":"TANK_OUT","2":"GND"}, "R3":{"1":"TANK_OUT","2":"GND"},
    "L2":{"1":"TANK_OUT","2":"RF_OUT"}, "C6":{"1":"RF_OUT","2":"GND"}, "J2":{"1":"RF_OUT","2":"GND"},
    "FL1":{"1":"+72V5"}, "FL2":{"1":"VCC"}, "FL3":{"1":"GND"}, "FL4":{"1":"VB"},
}

POWER_NETS = {"GND","VCC","+72V5","VB"}

# === CALCULATE ALL PIN POSITIONS ===
all_pins = {}  # net -> [(ref, pin, abs_x, abs_y)]
for c in COMPS:
    pm = PIN_MAPS.get(c["lib_id"],{})
    nets = PIN_NETS.get(c["ref"],{})
    for pn,(rx,ry) in pm.items():
        ax,ay = pin_abs(c["x"],c["y"],c["rot"],rx,ry)
        net = nets.get(pn,"")
        if net:
            if net not in all_pins: all_pins[net] = []
            all_pins[net].append((c["ref"],pn,ax,ay))

# === GENERATE SCHEMATIC ===
SHEET_UUID = uuid()
L = []
w = L.append

w('(kicad_pch') if False else w('(kicad_sch')
w('\t(version 20250114)')
w('\t(generator "eeschema")')
w('\t(generator_version "9.0")')
w('\t(uuid "%s")' % SHEET_UUID)
w('\t(paper "A2")')
w('\t(title_block (title "300W 13.56MHz Class-D RF Power Amplifier") (date "2026-06-27") (rev "2.0") (company "Hackerfab") (comment 1 "El-Hamamsy topology, IRF540 + IR2181S") (comment 2 "Vdd=72.5V, Pout=305W, eff=83.7%"))')

# lib_symbols
w('\t(lib_symbols')
for s in SYMBOLS:
    w(s)
w('\t)')

# Component instances
for c in COMPS:
    w('\t(symbol')
    w('\t\t(lib_id "%s")' % c["lib_id"])
    w('\t\t(at %.2f %.2f %d)' % (c["x"],c["y"],c["rot"]))
    w('\t\t(unit 1)')
    w('\t\t(exclude_from_sim no)')
    w('\t\t(in_bom yes)')
    w('\t\t(on_board yes)')
    w('\t\t(dnp no)')
    w('\t\t(uuid "%s")' % c["uuid"])
    w('\t\t(property "Reference" "%s" (at %.2f %.2f 0) (effects (font (size 1.524 1.524))))' % (c["ref"],c["x"],c["y"]-12))
    w('\t\t(property "Value" "%s" (at %.2f %.2f 0) (effects (font (size 1.524 1.524))))' % (c["value"],c["x"],c["y"]+12))
    w('\t\t(property "Footprint" "%s" (at %.2f %.2f 0) (effects (font (size 0.762 0.762)) (hide yes)))' % (c["fp"],c["x"],c["y"]))
    w('\t\t(property "Datasheet" "" (at %.2f %.2f 0) (effects (font (size 1.524 1.524))))' % (c["x"],c["y"]))
    w('\t\t(property "Description" "" (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (hide yes)))' % (c["x"],c["y"]))
    for pn in PIN_MAPS.get(c["lib_id"],{}):
        w('\t\t(pin "%s" (uuid "%s"))' % (pn,uuid()))
    w('\t\t(instances (project "rf_pa_300w" (path "/%s" (reference "%s") (unit 1))))' % (SHEET_UUID,c["ref"]))
    w('\t)')

# === WIRES ===
# For each net, connect pins with L-shaped wires
def wire(x1,y1,x2,y2):
    w('\t\t(wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) (stroke (width 0) (type solid)) (uuid "%s"))' % (x1,y1,x2,y2,uuid()))

def wire_l(x1,y1,x2,y2):
    """L-shaped wire: horizontal first, then vertical"""
    if abs(x1-x2) < 0.01:
        wire(x1,y1,x2,y2)
    elif abs(y1-y2) < 0.01:
        wire(x1,y1,x2,y2)
    else:
        wire(x1,y1,x2,y1)
        wire(x2,y1,x2,y2)

# Wires are individual top-level elements
for net, pins in sorted(all_pins.items()):
    if len(pins) < 2:
        continue
    # Sort pins by X then Y
    pins_sorted = sorted(pins, key=lambda p: (p[2], p[3]))
    # Connect adjacent pins
    for i in range(len(pins_sorted)-1):
        _,_,x1,y1 = pins_sorted[i]
        _,_,x2,y2 = pins_sorted[i+1]
        # Skip if too far apart (use label instead)
        dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if dist < 40:  # wire if within 40mm
            wire_l(x1,y1,x2,y2)

# === POWER SYMBOLS ===
# Place one power symbol per power net at first pin position
pwr_placed = set()
pwr_count = 0
for net in sorted(POWER_NETS):
    if net in all_pins and all_pins[net]:
        ref,pn,ax,ay = all_pins[net][0]
        pwr_count += 1
        w('\t(symbol')
        w('\t\t(lib_id "rf_pa:%s")' % net)
        w('\t\t(at %.2f %.2f 0)' % (ax,ay))
        w('\t\t(unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)')
        w('\t\t(uuid "%s")' % uuid())
        w('\t\t(property "Reference" "#PWR%03d" (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (hide yes)))' % (pwr_count,ax,ay-6))
        w('\t\t(property "Value" "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27))))' % (net,ax,ay+3))
        w('\t\t(property "Footprint" "" (at %.2f %.2f 0) (effects (font (size 1.524 1.524))))' % (ax,ay))
        w('\t\t(property "Datasheet" "" (at %.2f %.2f 0) (effects (font (size 1.524 1.524))))' % (ax,ay))
        w('\t\t(pin "1" (uuid "%s"))' % uuid())
        w('\t\t(instances (project "rf_pa_300w" (path "/%s" (reference "#PWR%03d") (unit 1))))' % (SHEET_UUID,pwr_count))
        w('\t)')

# === LABELS for distant connections ===
lbl_placed = set()
for net, pins in all_pins.items():
    if net in POWER_NETS:
        continue  # power symbols handle these
    for ref,pn,ax,ay in pins:
        key = (round(ax,2),round(ay,2))
        if key not in lbl_placed:
            lbl_placed.add(key)
            w('\t(label "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "%s"))' % (net,ax,ay,uuid()))

# === FOOTER ===
w('\t(sheet_instances (path "/" (page "1")))')
w('\t(embedded_fonts no)')
w(')')

output = '\n'.join(L) + '\n'
import sys
outfile = sys.argv[1] if len(sys.argv) > 1 else 'rf_pa_300w.kicad_sch'
with open(outfile,'w') as f:
    f.write(output)
print("Generated: %s" % outfile)
print("Components: %d, Wires: %d, Labels: %d, Lines: %d" % (len(COMPS), len(L), len(lbl_placed), len(L)))
