#!/usr/bin/env python3
"""
Route the 300W Class-D RF PA PCB.
Adds F.Cu ground pour + traces between all connected pads.
"""
import re, uuid, sys

PCB_FILE = 'rf_pa_300w.kicad_pcb'

def uid():
    return str(uuid.uuid4())

# Read PCB
with open(PCB_FILE) as f:
    pcb = f.read()

# ===== Step 1: Add F.Cu GND zone (copy of B.Cu zone but on F.Cu) =====
# Find the existing B.Cu zone and the text section to insert before
zone_start = pcb.find('\t(zone\n\t\t(net "GND")\n\t\t(layer "B.Cu")')
if zone_start < 0:
    print("ERROR: existing zone not found!")
    sys.exit(1)

# Find the closing of the existing zone
zone_end = pcb.find('\t)', zone_start)
# Find the next zone_end by counting parens
depth = 0
i = zone_start
while i < len(pcb):
    if pcb[i] == '(':
        depth += 1
    elif pcb[i] == ')':
        depth -= 1
        if depth == 0:
            zone_end = i + 1
            break
    i += 1

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

# Insert F.Cu zone right after B.Cu zone
pcb = pcb[:zone_end] + '\n' + fcuzone + pcb[zone_end:]

# ===== Step 2: Extract pad positions =====
# Parse footprints to get pad positions with net names
# Pattern: (footprint "..."
#             (at X Y)
#             ...  
#             (pad "N" ... (at dx dy) ... (net netid "NETNAME") ... )
#           )

# First, get net ID to name mapping
net_map = {}
for m in re.finditer(r'\(net (\d+) "([^"]*)"\)', pcb):
    net_map[int(m.group(1))] = m.group(2)

# Also net 0 = ""
net_map[0] = ""

print("Net map:", net_map)

# Now extract all pads with their global coordinates
# We need to find footprints and calculate absolute positions
footprint_pads = []  # list of (net_name, abs_x, abs_y, ref, pad_num, layer)

fp_pattern = re.compile(r'\(footprint "([^"]*)"\s*'
                       r'\(layer "([^"]*)"\)\s*'
                       r'\(uuid "[^"]*"\)\s*'
                       r'\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)', re.DOTALL)

# Find all footprints
fp_iter = fp_pattern.finditer(pcb)
fps = []
for m in fp_iter:
    fps.append((m.start(), m.end(), m.group(1), m.group(3), m.group(4)))

print(f"Found {len(fps)} footprints")

# Extract pads from each footprint
# Simpler approach: just parse pads within each footprint
# Use regex to find pad sections within each footprint
for fp_start, fp_end, fp_name, fp_x, fp_y in fps:
    fp_section = pcb[fp_start:fp_end]
    fp_x_f = float(fp_x)
    fp_y_f = float(fp_y)
    
    # Find reference designator
    ref_m = re.search(r'\(property "Reference" "([^"]*)"', fp_section)
    ref = ref_m.group(1) if ref_m else "??"
    
    # Find all pads
    pad_pattern = re.compile(r'\(pad "([^"]*)" [^)]*\)\s*'
                            r'\(at ([\d.-]+) ([\d.-]+)', re.DOTALL)
    for pm in pad_pattern.finditer(fp_section):
        pad_num = pm.group(1)
        pad_dx = float(pm.group(2))
        pad_dy = float(pm.group(3))
        abs_x = fp_x_f + pad_dx
        abs_y = fp_y_f + pad_dy
        
        # Find net for this pad
        # Search in the pad section for (net ...)
        pad_start = pm.start()
        pad_end = pm.end()
        # Extend to find the closing )
        j = pad_start
        depth = 0
        while j < len(fp_section):
            if fp_section[j] == '(':
                depth += 1
            elif fp_section[j] == ')':
                depth -= 1
                if depth == 0:
                    pad_end = j + 1
                    break
            j += 1
        pad_section = fp_section[pad_start:pad_end]
        net_m = re.search(r'\(net (\d+)(?:\s+"[^"]*")?\)', pad_section)
        net_name = ""
        if net_m:
            net_id = int(net_m.group(1))
            net_name = net_map.get(net_id, "")
        
        footprint_pads.append((net_name, abs_x, abs_y, ref, pad_num, fp_name))

print(f"Found {len(footprint_pads)} pads")
for net, x, y, ref, pad, fp in footprint_pads:
    print(f"  {ref}-{pad} ({fp}): net={net} @ ({x:.2f}, {y:.2f})")

# ===== Step 3: Group pads by net =====
net_groups = {}
for net_name, abs_x, abs_y, ref, pad_num, fp_name in footprint_pads:
    if net_name == "":
        continue
    if net_name not in net_groups:
        net_groups[net_name] = []
    net_groups[net_name].append((abs_x, abs_y, ref, pad_num))

print("\nNet groups:")
for net, pads in sorted(net_groups.items()):
    print(f"  {net}: {len(pads)} pads")
    for x, y, ref, p in pads:
        print(f"    {ref}-{p} @ ({x:.2f}, {y:.2f})")

# ===== Step 4: Generate traces =====
# For each net (except GND which uses ground pours), generate L-shaped or straight traces
# between pads in daisy-chain order

traces = []
trace_uuids = []

def add_trace(x1, y1, x2, y2, net_name, layer="F.Cu", width=0.5):
    """Add a straight trace between two points"""
    # Use the net ID from net_map
    net_id = 0
    for nid, nm in net_map.items():
        if nm == net_name:
            net_id = nid
            break
    
    # We need to find net ID from name
    tuid = uid()
    trace = f'\t(track (net {net_id}) (layer "{layer}")\n'
    trace += f'\t\t(uuid "{tuid}")\n'
    trace += f'\t\t\t(pts\n'
    trace += f'\t\t\t\t(xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f})\n'
    trace += f'\t\t\t)\n'
    trace += f'\t\t(stroke (width {width}) (type default))\n'
    trace += f'\t)'
    return trace

def route_net(pads, net_name):
    """Route pads in daisy chain. Returns list of trace strings."""
    traces = []
    if len(pads) < 2:
        return traces
    # Sort by X then Y for a left-to-right route
    sorted_pads = sorted(pads, key=lambda p: (p[0], p[1]))
    
    for i in range(len(sorted_pads) - 1):
        x1, y1, ref1, p1 = sorted_pads[i]
        x2, y2, ref2, p2 = sorted_pads[i+1]
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        # Determine trace width based on net
        width = 0.5  # default
        if net_name in ("+72V5", "VCC"):
            width = 1.0  # power
        elif net_name == "MID":
            width = 2.0  # high current
        elif net_name in ("TANK_OUT", "RF_OUT"):
            width = 1.5  # RF
        
        # If pads are very close (< 5mm), use straight trace
        if dx + dy < 5:
            traces.append(add_trace(x1, y1, x2, y2, net_name, "F.Cu", width))
        else:
            # L-shaped route: horizontal then vertical, clearing other pads
            # Route around other components using via if necessary
            mid_x = (x1 + x2) / 2
            # Simple L-route going around obstacles
            traces.append(add_trace(x1, y1, mid_x, y1, net_name, "F.Cu", width))
            traces.append(add_trace(mid_x, y1, mid_x, y2, net_name, "F.Cu", width))
            traces.append(add_trace(mid_x, y2, x2, y2, net_name, "F.Cu", width))
    
    return traces

# Route each non-GND net
all_traces = []
for net_name, pads in net_groups.items():
    if net_name == "GND":
        continue  # GND is handled by ground pours
    print(f"Routing {net_name} ({len(pads)} pads)...")
    net_traces = route_net(pads, net_name)
    all_traces.extend(net_traces)
    print(f"  Added {len(net_traces)} trace segments")

# Also add vias from F.Cu GND pads to B.Cu ground pour
# Find GND pads and add vias
gnd_pads = net_groups.get("GND", [])
gnd_vias = []
for x, y, ref, pad in gnd_pads:
    # Only add via if pad is on F.Cu (all are by default)
    vu = uid()
    via = f'\t(via (at {x:.4f} {y:.4f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu")'
    via += f' (net "GND") (uuid "{vu}"))'
    gnd_vias.append(via)

print(f"\nAdding {len(gnd_vias)} GND vias")

# ===== Step 5: Insert traces and vias into PCB file =====
# Find the right insertion point - before the zone section
zone_pos = pcb.find('\t(zone\n')
if zone_pos < 0:
    print("ERROR: Cannot find zone insertion point!")
    sys.exit(1)

# Insert before zone
trace_section = '\n'.join(all_traces) + '\n' + '\n'.join(gnd_vias) + '\n'

pcb = pcb[:zone_pos] + trace_section + pcb[zone_pos:]

# ===== Step 6: Write output =====
# First update version
pcb = re.sub(r'\t\(version \d+\)', '\t(version 20260206)', pcb)

output = PCB_FILE
with open(output, 'w') as f:
    f.write(pcb)

print(f"\nWritten: {output}")
print(f"Total trace segments: {len(all_traces)}")
print(f"Total GND vias: {len(gnd_vias)}")

# Count lines
lines = pcb.count('\n')
print(f"Total lines: {lines}")
