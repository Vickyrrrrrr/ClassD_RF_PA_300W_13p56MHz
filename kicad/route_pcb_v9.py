#!/usr/bin/env python3
import re
import uuid
import shutil
import sys

# Update the task tracking
try:
    with open('/mnt/c/Users/VICKY/.gemini/antigravity/brain/68b9da98-936f-466c-a057-5068ba514e02/task.md', 'r') as tf:
        t_content = tf.read()
    t_content = t_content.replace("- [ ] Implement layout changes in route_pcb_v9.py", "- [x] Implement layout changes in route_pcb_v9.py")
    t_content = t_content.replace("- [ ] Run route_pcb_v9.py in RHEL8 WSL environment", "- [/] Run route_pcb_v9.py in RHEL8 WSL environment")
    with open('/mnt/c/Users/VICKY/.gemini/antigravity/brain/68b9da98-936f-466c-a057-5068ba514e02/task.md', 'w') as tf:
        tf.write(t_content)
except Exception:
    pass

PCB_FILE = '/home/vickynishad/ClassD_RF_PA_300W_13p56MHz/kicad/rf_pa_300w.kicad_pcb'
BACKUP   = PCB_FILE + '.bak9'

def uid(): return str(uuid.uuid4())

# Make backup of original
shutil.copy2(PCB_FILE, BACKUP)
print(f"Backup created: {BACKUP}")

with open(PCB_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Parse top-level S-expression blocks of kicad_pcb
def get_top_level_blocks(s):
    match = re.search(r'\(kicad_pcb', s)
    if not match:
        raise ValueError("Not a valid kicad_pcb file")
    
    start_pos = match.end()
    blocks = []
    i = start_pos
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] == ')':
            break
        if s[i] == '(':
            start = i
            depth = 0
            for j in range(i, len(s)):
                if s[j] == '(':
                    depth += 1
                elif s[j] == ')':
                    depth -= 1
                    if depth == 0:
                        blocks.append(s[start:j+1])
                        i = j + 1
                        break
        else:
            start = i
            for j in range(i, len(s)):
                if s[j] == '(' or s[j] == ')' or s[j].isspace():
                    blocks.append(s[start:j])
                    i = j
                    break
    return s[:start_pos], blocks, s[i:]

header, blocks, footer = get_top_level_blocks(content)
print(f"Parsed {len(blocks)} top-level blocks inside kicad_pcb.")

# 2. Filter out segment and via blocks
filtered_blocks = []
removed_segments = 0
removed_vias = 0
for b in blocks:
    if b.startswith('(segment') or b.startswith('\n\t(segment'):
        removed_segments += 1
    elif b.startswith('(via') or b.startswith('\n\t(via'):
        removed_vias += 1
    else:
        filtered_blocks.append(b)

print(f"Removed {removed_segments} segments and {removed_vias} vias.")

# ===== Trace/via generation helpers =====
TW = {
    "+72V5":    3.0,   # power (high current)
    "VCC":      1.0,   # logic power  
    "VB":       0.5,   # bootstrap
    "/HIN":     0.3,   # signal
    "/LIN":     0.3,   # signal
    "/HO_NET":  0.5,   # signal
    "/LO_NET":  0.5,   # signal
    "/GATE1":   0.5,   # signal
    "/GATE2":   0.5,   # signal
    "/MID":     3.0,   # switching node (high current)
    "/TANK_OUT": 3.06,  # RF 50 ohm
    "/RF_OUT":  3.06,   # RF 50 ohm
}

def seg(x1, y1, x2, y2, net_name, layer="F.Cu", width=None):
    w = width if width is not None else TW.get(net_name, 0.5)
    t = f'\t(segment\n'
    t += f'\t\t(start {x1:.4f} {y1:.4f})\n'
    t += f'\t\t(end {x2:.4f} {y2:.4f})\n'
    t += f'\t\t(width {w})\n'
    t += f'\t\t(layer "{layer}")\n'
    t += f'\t\t(net "{net_name}")\n'
    t += f'\t\t(uuid "{uid()}")\n'
    t += f'\t)'
    return t

def path(pts, net_name, layer="F.Cu", width=None):
    traces = []
    for i in range(len(pts)-1):
        traces.append(seg(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net_name, layer, width))
    return traces

def via(x, y, net_name="GND"):
    vu = uid()
    return f'\t(via (at {x:.4f} {y:.4f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net "{net_name}") (uuid "{vu}"))'

# ===== NEW ROUTING DEFINITIONS =====
new_elements = []

# 1. +72V5 (Vdd): Route at y=2.2 to clear Edge.Cuts clearance (0.5mm) and J1-2/C1-2 GND pads
new_elements.extend(path([
    (2.46, 5.0), (2.46, 2.2), (10.0, 2.2)
], "+72V5", width=1.5))
new_elements.extend(path([
    (10.0, 2.2), (15.5, 2.2), (15.5, 5.0)
], "+72V5"))
new_elements.extend(path([
    (15.5, 5.0), (15.5, 12.0), (16.4, 12.0)
], "+72V5"))
# Narrow down Q1 Pin 2 entry to 1.5mm for clearance
new_elements.extend(path([
    (16.4, 12.0), (16.4, 2.2), (58.0, 2.2)
], "+72V5"))
new_elements.extend(path([
    (58.0, 2.2), (58.0, 10.0)
], "+72V5"))
new_elements.extend(path([
    (58.0, 10.0), (58.0, 15.0)
], "+72V5", width=1.5))

# 2. VCC: J3-1 -> C3-1 -> D1-1 -> U1-3
new_elements.extend(path([
    (2.46, 45.0), (2.46, 48.0), (16.4, 48.0), (16.4, 45.0)
], "VCC"))
new_elements.append(via(16.4, 42.5, "VCC"))
new_elements.extend(path([
    (16.4, 45.0), (16.4, 42.5)
], "VCC"))
# Route vertically on B.Cu at x=24.92 (clear region) to D1-1
new_elements.extend(path([
    (16.4, 42.5), (24.92, 42.5), (24.92, 8.0)
], "VCC", "B.Cu"))
# Place VCC via directly at (24.92, 20.64) next to U1-3
new_elements.append(via(24.92, 20.64, "VCC"))
new_elements.extend(path([
    (24.92, 20.64), (38.09, 20.64)
], "VCC"))

# 3. VB: D1-2 -> C4-1 -> U1-1
new_elements.extend(path([
    (35.08, 8.0), (35.08, 12.0), (28.4, 12.0), (28.4, 15.0)
], "VB"))
new_elements.extend(path([
    (35.08, 12.0), (35.08, 18.09), (38.09, 18.09)
], "VB"))

# 4. /HIN: J4-1 -> U1-2
new_elements.extend(path([
    (5.0, 25.0), (22.0, 25.0), (22.0, 19.36), (38.09, 19.36)
], "/HIN"))

# 5. /LIN: J4-2 -> U1-8 (via F.Cu to x=28.0, then jump to B.Cu)
new_elements.extend(path([
    (5.0, 27.54), (28.0, 27.54)
], "/LIN"))
new_elements.append(via(28.0, 27.54, "/LIN"))
new_elements.extend(path([
    (28.0, 27.54), (28.0, 18.09), (44.5, 18.09)
], "/LIN", "B.Cu"))
new_elements.append(via(44.5, 18.09, "/LIN"))
new_elements.extend(path([
    (44.5, 18.09), (41.91, 18.09)
], "/LIN"))

# 6. /HO_NET: U1-7 -> D2-1 -> R1-2 (via B.Cu, completely clear of VB on F.Cu)
new_elements.extend(path([
    (41.91, 19.36), (44.5, 19.36)
], "/HO_NET"))
new_elements.append(via(44.5, 19.36, "/HO_NET"))
new_elements.extend(path([
    (44.5, 19.36), (33.92, 19.36), (33.92, 13.0)
], "/HO_NET", "B.Cu"))
new_elements.append(via(33.92, 13.0, "/HO_NET"))
new_elements.extend(path([
    (33.92, 13.0), (33.92, 15.0)
], "/HO_NET"))
# Connect to R1 pin 2 (HO Gate Resistor return)
new_elements.extend(path([
    (41.91, 19.36), (46.5, 19.36), (46.5, 13.4), (48.0, 13.4)
], "/HO_NET"))

# 7. /LO_NET: U1-5 -> D3-1 -> R2-2 (routed on F.Cu at y=23.4, no crossings)
new_elements.extend(path([
    (41.91, 21.91), (41.91, 23.4), (48.0, 23.4)
], "/LO_NET"))
new_elements.extend(path([
    (41.91, 23.4), (33.92, 23.4), (33.92, 25.0)
], "/LO_NET"))

# 8. /GATE1: R1-1 -> D2-2 -> Q1-1
new_elements.extend(path([
    (44.08, 15.0), (55.46, 15.0)
], "/GATE1"))
new_elements.extend(path([
    (48.0, 16.6), (48.0, 15.0)
], "/GATE1"))

# 9. /GATE2: R2-1 -> D3-2 -> Q2-1
new_elements.extend(path([
    (44.08, 25.0), (55.46, 25.0)
], "/GATE2"))
new_elements.extend(path([
    (48.0, 26.6), (48.0, 25.0)
], "/GATE2"))

# 10. /MID: Q1-3 -> Q2-2 -> L1-2 + U1-6 + C4-2
# Route power traces going UP to y=10.0 to clear L1-1 (at 62.46, 15.0)
new_elements.extend(path([
    (60.54, 15.0), (60.54, 10.0)
], "/MID", width=1.5))
new_elements.extend(path([
    (60.54, 10.0), (67.54, 10.0)
], "/MID"))
new_elements.extend(path([
    (67.54, 10.0), (67.54, 15.0)
], "/MID", width=1.5))
# Connect Q2 pin 2 to MID
new_elements.extend(path([
    (58.0, 25.0), (58.0, 18.0), (60.54, 18.0), (60.54, 15.0)
], "/MID", width=1.5))
# Sense lines (0.5mm, routed on B.Cu and F.Cu via, no crossings)
new_elements.append(via(44.5, 20.64, "/MID"))
new_elements.append(via(31.6, 13.0, "/MID"))
new_elements.extend(path([
    (44.5, 20.64), (31.6, 20.64), (31.6, 13.0)
], "/MID", "B.Cu", width=0.5))
new_elements.extend(path([
    (44.5, 20.64), (41.91, 20.64)
], "/MID", width=0.5))
new_elements.extend(path([
    (31.6, 13.0), (31.6, 15.0)
], "/MID", width=0.5))

# 11. /TANK_OUT: L1-1 -> C5-1 -> R3-1 -> L2-2
new_elements.extend(path([
    (62.46, 15.0), (63.4, 22.0), (62.46, 30.0)
], "/TANK_OUT"))
# Shift vertical segment to x=77.0 to clear C6 GND pad (at 73.6, 22.0)
new_elements.extend(path([
    (62.46, 30.0), (62.46, 35.0), (77.0, 35.0), (77.0, 15.0), (74.54, 15.0)
], "/TANK_OUT"))

# 12. /RF_OUT: L2-1 -> C6-1 -> J2-1 (via B.Cu, entering J2-1 from right at x=74.0 to avoid J2 GND pad short)
new_elements.extend(path([
    (69.46, 15.0), (70.4, 15.0)
], "/RF_OUT", width=1.5))
new_elements.extend(path([
    (70.4, 15.0), (70.4, 22.0), (70.4, 24.5)
], "/RF_OUT"))
new_elements.append(via(70.4, 24.5, "/RF_OUT"))
new_elements.extend(path([
    (70.4, 24.5), (74.0, 24.5), (74.0, 42.0), (72.0, 42.0)
], "/RF_OUT", "B.Cu"))

# 13. GND Vias for SMD components
# C2 pin 2 (19.6, 12.0)
new_elements.append(via(19.6, 14.5, "GND"))
new_elements.extend(path([(19.6, 12.0), (19.6, 14.5)], "GND"))

# C3 pin 2 (19.6, 45.0) - shift via to (21.5, 45.0) to clear VCC bottom trace
new_elements.append(via(21.5, 45.0, "GND"))
new_elements.extend(path([(19.6, 45.0), (21.5, 45.0)], "GND"))

# U1 pin 4 (38.09, 21.91) - shift via UP to (38.09, 20.0) to clear LO_NET on F.Cu
new_elements.append(via(38.09, 20.0, "GND"))
new_elements.extend(path([(38.09, 21.91), (38.09, 20.0)], "GND"))

# C5 pin 2 (66.6, 22.0)
new_elements.append(via(66.6, 24.5, "GND"))
new_elements.extend(path([(66.6, 22.0), (66.6, 24.5)], "GND"))

# C6 pin 2 (73.6, 22.0) - shift via to (76.0, 22.0) to clear RF_OUT bottom trace
new_elements.append(via(76.0, 22.0, "GND"))
new_elements.extend(path([(73.6, 22.0), (76.0, 22.0)], "GND"))

# 14. Q2 GND low-impedance trace and via
new_elements.extend(path([(60.54, 25.0), (60.54, 28.0)], "GND", width=1.5))
new_elements.append(via(60.54, 28.0, "GND"))

print(f"Generated {len(new_elements)} new segments and vias.")

# Assemble S-expression content
output_blocks = filtered_blocks + [f"\n{item}" for item in new_elements]

# Write out the new PCB file
with open(PCB_FILE, 'w', encoding='utf-8') as f:
    f.write(header)
    for b in output_blocks:
        f.write(b)
    f.write(footer)

print("=== PCB ROUTING RE-BUILT (V9) SUCCESSFULLY ===")
