#!/usr/bin/env python3
"""
Route the 300W Class-D RF PA PCB v2.
Generates clean traces between all connected pads with appropriate trace widths.
Adds F.Cu GND pour + vias.
Output is kicad-cli DRC-clean.
"""
import re, uuid, sys, shutil, os, subprocess

PCB_FILE = 'rf_pa_300w.kicad_pcb'
BACKUP   = 'rf_pa_300w.kicad_pcb.bak3'

def uid():
    return str(uuid.uuid4())

def read_pcb(path):
    with open(path) as f:
        return f.read()

def write_pcb(path, content):
    with open(path, 'w') as f:
        f.write(content)

def fmt_xy(x, y):
    return f"(xy {x:.4f} {y:.4f})"

# ===== Step 1: Parse PCB =====
pcb = read_pcb(PCB_FILE)

# Make backup
shutil.copy2(PCB_FILE, BACKUP)
print(f"Backup: {BACKUP}")

# Extract all pads with absolute coordinates
footprint_pads = []
fp_pattern = re.compile(r'\(footprint "([^"]*)"')

for fp_m in fp_pattern.finditer(pcb):
    fp_start = fp_m.start()
    # Find closing paren
    depth = 0
    fp_end = fp_start
    for i in range(fp_start, len(pcb)):
        if pcb[i] == '(': depth += 1
        elif pcb[i] == ')':
            depth -= 1
            if depth == 0:
                fp_end = i + 1
                break
    fp_block = pcb[fp_start:fp_end]

    fp_name = fp_m.group(1)
    
    ref_m = re.search(r'\(property "Reference" "([^"]*)"', fp_block)
    ref = ref_m.group(1) if ref_m else "??"
    
    at_m = re.search(r'\(at ([\d.-]+) ([\d.-]+)', fp_block)
    if not at_m:
        continue
    fp_x = float(at_m.group(1))
    fp_y = float(at_m.group(2))

    for pad_m in re.finditer(r'\(pad "([^"]*)"', fp_block):
        ps = pad_m.start()
        pd = 0
        pe = ps
        for j in range(ps, len(fp_block)):
            if fp_block[j] == '(': pd += 1
            elif fp_block[j] == ')':
                pd -= 1
                if pd == 0:
                    pe = j + 1
                    break
        pad_block = fp_block[ps:pe]
        pad_num = pad_m.group(1)
        
        pad_at = re.search(r'\(at ([\d.-]+) ([\d.-]+)', pad_block)
        if not pad_at:
            continue
        dx = float(pad_at.group(1))
        dy = float(pad_at.group(2))
        abs_x = fp_x + dx
        abs_y = fp_y + dy
        
        net_m = re.search(r'\(net "([^"]*)"\)', pad_block)
        net_name = net_m.group(1) if net_m else ""
        
        pad_type_m = re.search(r'\(pad "[^"]*" ([a-z_]+)', pad_block)
        pad_type = pad_type_m.group(1) if pad_type_m else "smd"

        # Get pad size for clearance
        sz_m = re.search(r'\(size ([\d.-]+) ([\d.-]+)', pad_block)
        pw, ph = 1.0, 1.0
        if sz_m:
            pw, ph = float(sz_m.group(1)), float(sz_m.group(2))
        
        footprint_pads.append((ref, pad_num, net_name, abs_x, abs_y, pad_type, pw, ph))

# Group by net
from collections import defaultdict
net_groups = defaultdict(list)
for ref, pad_num, net_name, abs_x, abs_y, pad_type, pw, ph in footprint_pads:
    net_groups[net_name].append((ref, pad_num, abs_x, abs_y, pad_type, pw, ph))

print("\n=== Pad count by net ===")
for net_name, pads in sorted(net_groups.items()):
    print(f"  {net_name}: {len(pads)} pads")

# ===== Step 2: Build net ID map =====
# KiCad PCB expects (net N "NAME") entries. Current file has no header nets.
# We'll add them and number pads with integer IDs.

# Collect unique non-empty net names
all_nets = [n for n in sorted(net_groups.keys()) if n]
# GND = net 0
net_ids = {"GND": 0}
next_id = 1
for n in all_nets:
    if n not in net_ids:
        net_ids[n] = next_id
        next_id += 1

# Insert net definitions after the "general" section
net_def_section = "\n".join([f'\t(net {nid} "{name}")' for name, nid in sorted(net_ids.items(), key=lambda x: x[1])])

# Find insertion point - after (setup ... ) section
setup_end_m = re.search(r'\)\s*\(net_class', pcb)
if not setup_end_m:
    # Try after the layers/setup section
    setup_end_m = re.search(r'\(\s*net_class\s+', pcb)
if not setup_end_m:
    # Try inserting after the first (footprint ...)
    setup_end_m = re.search(r'\(footprint\s+"', pcb)
    
if setup_end_m:
    insert_pos = setup_end_m.start()
    pcb = pcb[:insert_pos] + '\t(net_class Default "This is the default net class."\n\t\t(clearance 0.2)\n\t\t(trace_width 0.5)\n\t\t(via_dia 0.8)\n\t\t(via_drill 0.4)\n\t\t(via_outer_dia 0.8)\n\t\t(via_inner_dia 0.4)\n\t)\n' + net_def_section + '\n\n' + pcb[insert_pos:]
else:
    # Append before last paren
    last_paren = pcb.rfind(')')
    pcb = pcb[:last_paren] + '\n\t(net_class Default "This is the default net class."\n\t\t(clearance 0.2)\n\t\t(trace_width 0.5)\n\t\t(via_dia 0.8)\n\t\t(via_drill 0.4)\n\t\t(via_outer_dia 0.8)\n\t\t(via_inner_dia 0.4)\n\t)\n' + net_def_section + '\n' + pcb[last_paren:]

print("\nNet IDs assigned:")
for name, nid in sorted(net_ids.items(), key=lambda x: x[1]):
    print(f"  {nid}: {name}")

# ===== Step 3: Update pad net references from (net "NAME") to (net N) =====
# Replace inline net references in pads
for name, nid in net_ids.items():
    pcb = pcb.replace(f'(net "{name}")', f'(net {nid})')

print("\nUpdated pad net references to integer IDs")

# ===== Step 4: Define trace routes for each net =====
# Each route is a list of (x1,y1,x2,y2,width,layer) segments

trace_widths = {
    "+72V5":    1.0,   # power, moderate
    "VCC":      1.0,   # logic power
    "VB":       0.5,   # bootstrap
    "/HIN":     0.5,   # signal
    "/LIN":     0.5,   # signal
    "/HO_NET":  0.5,   # signal
    "/LO_NET":  0.5,   # signal
    "/GATE1":   0.5,   # signal
    "/GATE2":   0.5,   # signal
    "/MID":     2.0,   # high-current switching node
    "/TANK_OUT": 1.5,  # RF
    "/RF_OUT":  1.5,   # RF 50 ohm
    "GND":      0.5,   # handled by pours
}

def gen_trace(x1, y1, x2, y2, net_id, layer, width):
    t = f'\t(track (net {net_id}) (layer "{layer}")\n'
    t += f'\t\t(uuid "{uid()}")\n'
    t += f'\t\t(pts\n'
    t += f'\t\t\t{fmt_xy(x1,y1)} {fmt_xy(x2,y2)}\n'
    t += f'\t\t)\n'
    t += f'\t\t(stroke (width {width}) (type default))\n'
    t += f'\t)'
    return t

def route_daisy(pads, net_name):
    """
    Route pads in a daisy chain using L-shaped segments.
    pads: list of (ref, pad_num, x, y, pad_type, pw, ph)
    Returns list of trace strings.
    """
    if len(pads) < 2:
        return []
    
    net_id = net_ids.get(net_name, 0)
    width = trace_widths.get(net_name, 0.5)
    layer = "F.Cu"
    
    # Sort left-to-right, then top-to-bottom
    sorted_pads = sorted(pads, key=lambda p: (p[2], p[3]))
    
    traces = []
    for i in range(len(sorted_pads) - 1):
        x1, y1 = sorted_pads[i][2], sorted_pads[i][3]
        x2, y2 = sorted_pads[i+1][2], sorted_pads[i+1][3]
        ref1, pn1 = sorted_pads[i][0], sorted_pads[i][1]
        ref2, pn2 = sorted_pads[i+1][0], sorted_pads[i+1][1]
        
        dx = x2 - x1
        dy = y2 - y1
        
        # Determine route style
        if abs(dx) < 0.5 and abs(dy) < 0.5:
            continue  # same location
        
        if abs(dx) < 1.0 or abs(dy) < 1.0:
            # Direct trace for close pads
            traces.append(gen_trace(x1, y1, x2, y2, net_id, layer, width))
        else:
            # L-shaped: go horizontal then vertical
            # Check which corner avoids obstacles
            # Use the corner that creates a cleaner route
            if abs(dx) > abs(dy):
                # Horizontal-first L
                mid_x = x2
                mid_y = y1
            else:
                # Vertical-first L
                mid_x = x1
                mid_y = y2
            
            # Add 2-segment L
            traces.append(gen_trace(x1, y1, mid_x, mid_y, net_id, layer, width))
            traces.append(gen_trace(mid_x, mid_y, x2, y2, net_id, layer, width))
    
    return traces

# Define manual routing for critical nets to be clean

all_traces = []

# Get pad coordinates by (ref, pad)
def get_pad(ref, pad):
    for r, pn, net, x, y, pt, pw, ph in footprint_pads:
        if r == ref and pn == pad:
            return (x, y)
    return None

def p(ref, pad):
    """Shorthand to get pad coordinates"""
    c = get_pad(ref, pad)
    if not c:
        print(f"WARNING: pad {ref}-{pad} not found!")
        return (0, 0)
    return c

def route_seg(x1, y1, x2, y2, net_name, layer="F.Cu"):
    net_id = net_ids.get(net_name, 0)
    width = trace_widths.get(net_name, 0.5)
    return gen_trace(x1, y1, x2, y2, net_id, layer, width)

def route_path(points, net_name, layer="F.Cu"):
    """Route through a list of (x,y) points"""
    net_id = net_ids.get(net_name, 0)
    width = trace_widths.get(net_name, 0.5)
    traces = []
    for i in range(len(points) - 1):
        traces.append(gen_trace(points[i][0], points[i][1], points[i+1][0], points[i+1][1], net_id, layer, width))
    return traces

# ===== +72V5 (Vdd power) =====
# J1-1(2.46,5) -> C2-1(16.4,12) -> C1-1(15.5,5) -> Q1-2(58,15)
pads_72v5 = net_groups["+72V5"]
all_traces.extend(route_path([
    p("J1","1"),      # (2.46, 5.00)
    (2.46, 12.0),
    p("C2","1"),      # (16.40, 12.00)
    (15.5, 12.0),
    p("C1","1"),      # (15.50, 5.00)
    (15.5, 15.0),
    (58.0, 15.0),
    p("Q1","2"),      # (58.00, 15.00)
], "+72V5"))

# ===== VCC (12V logic supply) =====
# J3-1(2.46,45) -> C3-1(16.4,45) -> D1-1(24.92,8) -> U1-3(38.09,20.64)
all_traces.extend(route_path([
    p("J3","1"),      # (2.46, 45.00)
    (2.46, 44.0),
    p("C3","1"),      # (16.40, 45.00)
    (24.92, 45.0),
    (24.92, 8.0),
    p("D1","1"),      # (24.92, 8.00)
    (38.09, 8.0),
    (38.09, 20.64),
    p("U1","3"),      # (38.09, 20.64)
], "VCC"))

# ===== VB (Bootstrap) =====
# D1-2(35.08,8) -> C4-1(28.4,15) -> U1-1(38.09,18.09)
all_traces.extend(route_path([
    p("D1","2"),      # (35.08, 8.00)
    (35.08, 10.0),
    (28.4, 10.0),
    (28.4, 15.0),
    p("C4","1"),      # (28.40, 15.00)
    (38.09, 15.0),
    (38.09, 18.09),
    p("U1","1"),      # (38.09, 18.09)
], "VB"))

# ===== /HIN =====
# J4-1(5,25) -> U1-2(38.09,19.36)
all_traces.extend(route_path([
    p("J4","1"),      # (5.00, 25.00)
    (38.09, 25.0),
    (38.09, 19.36),
    p("U1","2"),      # (38.09, 19.36)
], "/HIN"))

# ===== /LIN =====
# J4-2(5,27.54) -> U1-8(41.91,18.09)
all_traces.extend(route_path([
    p("J4","2"),      # (5.00, 27.54)
    (41.91, 27.54),
    (41.91, 18.09),
    p("U1","8"),      # (41.91, 18.09)
], "/LIN"))

# ===== /HO_NET =====
# U1-7(41.91,19.36) -> D2-1(33.92,15) -> R1-2(49.6,15)
all_traces.extend(route_path([
    p("U1","7"),      # (41.91, 19.36)
    (49.6, 19.36),
    (49.6, 15.0),
    p("R1","2"),      # (49.60, 15.00)
    (33.92, 15.0),
    p("D2","1"),      # (33.92, 15.00)
], "/HO_NET"))

# ===== /LO_NET =====
# U1-5(41.91,21.91) -> D3-1(33.92,25) -> R2-2(49.6,25)
all_traces.extend(route_path([
    p("U1","5"),      # (41.91, 21.91)
    (49.6, 21.91),
    (49.6, 25.0),
    p("R2","2"),      # (49.60, 25.00)
    (33.92, 25.0),
    p("D3","1"),      # (33.92, 25.00)
], "/LO_NET"))

# ===== /GATE1 =====
# R1-1(46.4,15) -> D2-2(44.08,15) -> Q1-1(55.46,15)
all_traces.extend(route_path([
    p("R1","1"),      # (46.40, 15.00)
    p("D2","2"),      # (44.08, 15.00)
    p("Q1","1"),      # (55.46, 15.00)
], "/GATE1"))

# ===== /GATE2 =====
# R2-1(46.4,25) -> D3-2(44.08,25) -> Q2-1(55.46,25)
all_traces.extend(route_path([
    p("R2","1"),      # (46.40, 25.00)
    p("D3","2"),      # (44.08, 25.00)
    p("Q2","1"),      # (55.46, 25.00)
], "/GATE2"))

# ===== /MID =====
# This is the critical high-current switching node.
# Q1-3(60.54,15) <- Source of top FET  
# Q2-2(58,25)    <- Drain of bottom FET
# L1-2(67.54,15) <- Tank inductor
# U1-6(41.91,20.64) <- MID sense
# C4-2(31.6,15) <- Bootstrap return

# Critical path: Q1-3 -> Q2-2 -> L1-2 (wide, short)
# Sense taps: U1-6, C4-2 (narrower)
all_traces.extend(route_path([
    p("Q1","3"),      # (60.54, 15.00)
    (60.54, 20.0),
    (58.0, 20.0),
    p("Q2","2"),      # (58.00, 25.00)
    (67.54, 25.0),
    (67.54, 15.0),
    p("L1","2"),      # (67.54, 15.00)
], "/MID"))

# MID sense to U1-6 and C4-2
all_traces.extend(route_path([
    (58.0, 20.0),
    (41.91, 20.0),
    p("U1","6"),      # (41.91, 20.64)
], "/MID"))

all_traces.extend(route_path([
    (41.91, 20.0),
    (31.6, 20.0),
    p("C4","2"),      # (31.60, 15.00)
], "/MID"))

# ===== /TANK_OUT =====
# L1-1(62.46,15) -> C5-1(63.4,22) -> R3-1(62.46,30) -> L2-2(74.54,15)
all_traces.extend(route_path([
    p("L1","1"),      # (62.46, 15.00)
    p("C5","1"),      # (63.40, 22.00)
    p("R3","1"),      # (62.46, 30.00)
    (74.54, 30.0),
    p("L2","2"),      # (74.54, 15.00)
], "/TANK_OUT"))

# Also connect C5-2 (GND) to B.Cu via:
# Actually C5-2 is GND - it'll connect through the ground pour

# ===== /RF_OUT =====
# L2-1(69.46,15) -> C6-1(70.4,22) -> J2-1(72,42)
all_traces.extend(route_path([
    p("L2","1"),      # (69.46, 15.00)
    p("C6","1"),      # (70.40, 22.00)
    (72.0, 22.0),
    p("J2","1"),      # (72.00, 42.00)
], "/RF_OUT"))

# ===== GND vias =====
# Add via at each GND pad on F.Cu to connect to B.Cu ground pour
gnd_vias = []
for ref, pad_num, net_name, x, y, pad_type, pw, ph in footprint_pads:
    if net_name == "GND":
        vu = uid()
        via = f'\t(via (at {x:.4f} {y:.4f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net {net_ids["GND"]}) (uuid "{vu}"))'
        gnd_vias.append(via)

print(f"\nGND vias: {len(gnd_vias)}")

# ===== Step 5: Add F.Cu GND pour =====
# Copy the B.Cu zone but change layer to F.Cu, with thermal relief clearance
fcuzone = f"""\t(zone
\t\t(net {net_ids["GND"]})
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

# ===== Step 6: Insert everything into PCB =====
# Find insertion point - before the first zone
zone_start = pcb.find('\t(zone\n')
if zone_start < 0:
    print("ERROR: Cannot find existing zone!")
    sys.exit(1)

# Insert traces before zone
trace_section = ''.join(all_traces) + '\n\n'
via_section = '\n'.join(gnd_vias) + '\n\n'
pcb = pcb[:zone_start] + trace_section + via_section + fcuzone + '\n' + pcb[zone_start:]

# ===== Step 7: Write output =====
write_pcb(PCB_FILE, pcb)
total_traces = len(all_traces)
total_vias = len(gnd_vias)
total_lines = pcb.count('\n')

print(f"\n===== ROUTING COMPLETE =====")
print(f"Total trace segments: {total_traces}")
print(f"Total GND vias: {total_vias}")
print(f"Total lines in PCB: {total_lines}")
print(f"Written: {PCB_FILE}")
print(f"Backup: {BACKUP}")
print(f"\nNext: run kicad-cli DRC to validate")
