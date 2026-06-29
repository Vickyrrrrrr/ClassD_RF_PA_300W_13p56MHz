#!/usr/bin/env python3
"""
Route the 300W Class-D RF PA PCB v3.
Adds traces with string-based net references matching existing pad format.
No net ID conversion. Adds F.Cu GND pour + vias.
"""
import uuid, shutil, sys

PCB_FILE = '/home/vickynishad/ClassD_RF_PA_300W_13p56MHz/kicad/rf_pa_300w.kicad_pcb'
BACKUP   = PCB_FILE + '.bak3'

def uid(): return str(uuid.uuid4())

with open(PCB_FILE) as f:
    pcb = f.read()

# Make backup
shutil.copy2(PCB_FILE, BACKUP)
print(f"Backup: {BACKUP}")

# ===== Trace definitions =====
# Each net gets a list of (x1,y1,x2,y2,width,layer) segments

TW = {
    "+72V5":    1.0,   # power
    "VCC":      1.0,   # logic power  
    "VB":       0.5,   # bootstrap
    "/HIN":     0.5,   # signal
    "/LIN":     0.5,   # signal
    "/HO_NET":  0.5,   # signal
    "/LO_NET":  0.5,   # signal
    "/GATE1":   0.5,   # signal
    "/GATE2":   0.5,   # signal
    "/MID":     2.0,   # switching node (high current)
    "/TANK_OUT": 1.5,  # RF
    "/RF_OUT":  1.5,   # RF 50 ohm
}

def seg(x1, y1, x2, y2, net_name, layer="F.Cu"):
    w = TW.get(net_name, 0.5)
    t = f'\t(segment\n'
    t += f'\t\t(start {x1:.4f} {y1:.4f})\n'
    t += f'\t\t(end {x2:.4f} {y2:.4f})\n'
    t += f'\t\t(width {w})\n'
    t += f'\t\t(layer "{layer}")\n'
    t += f'\t\t(net "{net_name}")\n'
    t += f'\t\t(uuid "{uid()}")\n'
    t += f'\t)'
    return t

def path(pts, net_name, layer="F.Cu"):
    traces = []
    for i in range(len(pts)-1):
        traces.append(seg(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net_name, layer))
    return traces

def ref(ref, pad):
    """Return (x,y) for a component reference + pad number by parsing PCB"""
    # Search for reference in the PCB content
    import re
    # Find the footprint with this reference
    pattern = r'\(footprint "[^"]*".*?\(property "Reference" "%s".*?\(at ([\d.-]+) ([\d.-]+).*?\(pad "%s"' % (ref, pad)
    m = re.search(pattern, pcb, re.DOTALL)
    if m:
        return (float(m.group(1)), float(m.group(2)))
    # Try to find the pad inside the footprint
    fp_pattern = r'\(footprint "([^"]*)"(?:(?!\(footprint).)*\(property "Reference" "%s"' % ref
    fp_match = re.search(fp_pattern, pcb, re.DOTALL)
    if not fp_match:
        print(f"WARNING: footprint {ref} not found!")
        return (0, 0)
    
    fp_start = fp_match.start()
    # Find the footprint's position
    at_m = re.search(r'\(at ([\d.-]+) ([\d.-]+)', pcb[fp_start:fp_start+200])
    if not at_m:
        return (0, 0)
    fp_x, fp_y = float(at_m.group(1)), float(at_m.group(2))
    
    # Find pad
    pad_pattern = r'\(pad "%s".*?\(at ([\d.-]+) ([\d.-]+)' % pad
    pad_match = re.search(pad_pattern, pcb[fp_start:fp_start+2000])
    if not pad_match:
        print(f"WARNING: pad {ref}-{pad} not found!")
        return (0, 0)
    
    dx, dy = float(pad_match.group(1)), float(pad_match.group(2))
    return (fp_x + dx, fp_y + dy)

# Pre-compute pad positions
PADS = {}
import re
for fp_m in re.finditer(r'\(footprint "([^"]*)"', pcb):
    start = fp_m.start()
    depth = 0
    end = start
    for i in range(start, len(pcb)):
        if pcb[i] == '(': depth += 1
        elif pcb[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    block = pcb[start:end]
    
    ref_m = re.search(r'\(property "Reference" "([^"]*)"', block)
    if not ref_m: continue
    ref_name = ref_m.group(1)
    
    at_m = re.search(r'\(at ([\d.-]+) ([\d.-]+)', block)
    if not at_m: continue
    fx, fy = float(at_m.group(1)), float(at_m.group(2))
    
    for pad_m in re.finditer(r'\(pad "([^"]*)"', block):
        ps = pad_m.start()
        pd = 0
        pe = ps
        for j in range(ps, len(block)):
            if block[j] == '(': pd += 1
            elif block[j] == ')':
                pd -= 1
                if pd == 0:
                    pe = j + 1
                    break
        pad_block = block[ps:pe]
        pn = pad_m.group(1)
        pa = re.search(r'\(at ([\d.-]+) ([\d.-]+)', pad_block)
        if not pa: continue
        px, py = fx + float(pa.group(1)), fy + float(pa.group(2))
        net = ""
        nm = re.search(r'\(net "([^"]*)"\)', pad_block)
        if nm: net = nm.group(1)
        PADS[(ref_name, pn)] = (px, py, net)

def p(ref, pad):
    k = (ref, pad)
    if k in PADS:
        return (PADS[k][0], PADS[k][1])
    print(f"WARNING: {ref}-{pad} not found!")
    return (0, 0)

all_traces = []

# ===== +72V5: J1-1 → C2-1 → C1-1 → Q1-2 =====
all_traces.extend(path([
    p("J1","1"), (2.46, 12.0), p("C2","1"), 
    (15.5, 12.0), p("C1","1"),
    (15.5, 15.0), (58.0, 15.0), p("Q1","2"),
], "+72V5"))

# ===== VCC: J3-1 → C3-1 → D1-1 → U1-3 =====
all_traces.extend(path([
    p("J3","1"), (2.46, 44.0), p("C3","1"),
    (24.92, 45.0), (24.92, 8.0), p("D1","1"),
    (38.09, 8.0), (38.09, 20.64), p("U1","3"),
], "VCC"))

# ===== VB: D1-2 → C4-1 → U1-1 =====
all_traces.extend(path([
    p("D1","2"), (35.08, 10.0), (28.4, 10.0),
    (28.4, 15.0), p("C4","1"),
    (38.09, 15.0), (38.09, 18.09), p("U1","1"),
], "VB"))

# ===== /HIN: J4-1 → U1-2 =====
all_traces.extend(path([
    p("J4","1"), (38.09, 25.0), (38.09, 19.36), p("U1","2"),
], "/HIN"))

# ===== /LIN: J4-2 → U1-8 =====
all_traces.extend(path([
    p("J4","2"), (41.91, 27.54), (41.91, 18.09), p("U1","8"),
], "/LIN"))

# ===== /HO_NET: U1-7 → D2-1 → R1-2 =====
all_traces.extend(path([
    p("U1","7"), (49.6, 19.36), (49.6, 15.0), p("R1","2"),
    (33.92, 15.0), p("D2","1"),
], "/HO_NET"))

# ===== /LO_NET: U1-5 → D3-1 → R2-2 =====
all_traces.extend(path([
    p("U1","5"), (49.6, 21.91), (49.6, 25.0), p("R2","2"),
    (33.92, 25.0), p("D3","1"),
], "/LO_NET"))

# ===== /GATE1: R1-1 → D2-2 → Q1-1 =====
all_traces.extend(path([
    p("R1","1"), p("D2","2"), p("Q1","1"),
], "/GATE1"))

# ===== /GATE2: R2-1 → D3-2 → Q2-1 =====
all_traces.extend(path([
    p("R2","1"), p("D3","2"), p("Q2","1"),
], "/GATE2"))

# ===== /MID (switching node): Q1-3 → Q2-2 → L1-2 + sense taps =====
all_traces.extend(path([
    p("Q1","3"), (60.54, 20.0), (58.0, 20.0), p("Q2","2"),
    (67.54, 25.0), (67.54, 15.0), p("L1","2"),
], "/MID"))

# MID sense to U1-6 and C4-2
mid_y = 20.0
all_traces.extend(path([
    (58.0, mid_y), (41.91, mid_y), p("U1","6"),
], "/MID"))
all_traces.extend(path([
    (41.91, mid_y), (31.6, mid_y), (31.6, 15.0), p("C4","2"),
], "/MID"))

# ===== /TANK_OUT: L1-1 → C5-1 → R3-1 → L2-2 =====
all_traces.extend(path([
    p("L1","1"), p("C5","1"), p("R3","1"),
    (74.54, 30.0), p("L2","2"),
], "/TANK_OUT"))

# ===== /RF_OUT: L2-1 → C6-1 → J2-1 =====
all_traces.extend(path([
    p("L2","1"), p("C6","1"), (72.0, 22.0), p("J2","1"),
], "/RF_OUT"))

print(f"Traces generated: {len(all_traces)}")

# ===== GND vias =====
gnd_vias = []
for (ref_name, pad_num), (x, y, net) in PADS.items():
    if net == "GND":
        vu = uid()
        via = f'\t(via (at {x:.4f} {y:.4f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net "GND") (uuid "{vu}"))'
        gnd_vias.append(via)
print(f"GND vias: {len(gnd_vias)}")

# ===== F.Cu GND copper pour =====
fcuzone = f"""\t(zone
\t\t(net "GND")
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(hatch edge 0.5)
\t\t(connect_pads
\t\t\t(clearance 0.5)
\t\t)
\t\t(min_thickness 0.25)
\t\t(fill yes
\t\t\t(thermal_gap 0.5)
\t\t\t(thermal_bridge_width 0.5)
\t\t\t(island_removal_mode 0)
\t\t)
\t\t(polygon
\t\t\t(pts
\t\t\t\t(xy 0.5 0.5) (xy 79.5 0.5) (xy 79.5 49.5) (xy 0.5 49.5)
\t\t\t)
\t\t)
\t)"""

# ===== Insert into PCB =====
# Find the existing zone (B.Cu GND pour) - insert before it
zone_pos = pcb.find('\t(zone\n')
if zone_pos < 0:
    # Try finding with \r\n just in case
    zone_pos = pcb.find('\t(zone\r\n')

if zone_pos < 0:
    print("ERROR: No existing zone found!")
    sys.exit(1)

insert = '\n'
for t in all_traces:
    insert += t + '\n'
insert += '\n'
for v in gnd_vias:
    insert += v + '\n'
insert += '\n' + fcuzone + '\n'

pcb = pcb[:zone_pos] + insert + pcb[zone_pos:]

with open(PCB_FILE, 'w') as f:
    f.write(pcb)

total = pcb.count('\n')
print(f"\n=== ROUTING COMPLETE ===")
print(f"Traces: {len(all_traces)}")
print(f"GND vias: {len(gnd_vias)}")
print(f"Added F.Cu GND pour: yes")
print(f"Total lines: {total}")
print(f"\nNow run: kicad-cli pcb drc")
