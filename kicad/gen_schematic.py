#!/usr/bin/env python3
"""
Generate KiCAD 10 schematic for 300W 13.56MHz Class-D RF Power Amplifier.
Uses EXACT symbol format from KiCAD demo files to ensure compatibility.

Output: rf_pa_300w.kicad_sch (version 20250114, generator "eeschema")
"""

import uuid as _uuid
import math

def uuid():
    return str(_uuid.uuid4())

# ---------------------------------------------------------------------------
# SYMBOL DEFINITIONS
# Adapted from KiCAD 10 demo schematic format (complex_hierarchy)
# Each symbol uses proper multi-line S-expression format with tabs
# ---------------------------------------------------------------------------

# R - Resistor (from demo, adapted)
SYMBOL_R = '''		(symbol "rf_pa:R"
			(pin_numbers
				(hide yes)
			)
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "R"
				(at 2.032 0 90)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Value" "R"
				(at 0 0 90)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Footprint" ""
				(at -1.778 0 90)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Description" "Resistor"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "ki_fp_filters" "R_* Resistor_*"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "R_0_1"
				(rectangle
					(start -1.016 -2.54)
					(end 1.016 2.54)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "R_1_1"
				(pin passive line
					(at 0 3.81 270)
					(length 1.27)
					(name "~"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
				(pin passive line
					(at 0 -3.81 90)
					(length 1.27)
					(name "~"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# C - Capacitor (from demo, adapted)
SYMBOL_C = '''		(symbol "rf_pa:C"
			(pin_numbers
				(hide yes)
			)
			(pin_names
				(offset 0.254)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "C"
				(at 0.635 2.54 0)
				(effects
					(font
						(size 1.524 1.524)
					)
					(justify left)
				)
			)
			(property "Value" "C"
				(at 0.635 -2.54 0)
				(effects
					(font
						(size 1.524 1.524)
					)
					(justify left)
				)
			)
			(property "Footprint" ""
				(at 0.9652 -3.81 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Description" "Capacitor"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "ki_fp_filters" "C_* Capacitor_*"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "C_0_1"
				(polyline
					(pts
						(xy -2.032 0.762) (xy 2.032 0.762)
					)
					(stroke
						(width 0.508)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy -2.032 -0.762) (xy 2.032 -0.762)
					)
					(stroke
						(width 0.508)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "C_1_1"
				(pin passive line
					(at 0 3.81 270)
					(length 2.794)
					(name "~"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
				(pin passive line
					(at 0 -3.81 90)
					(length 2.794)
					(name "~"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# L - Inductor
SYMBOL_L = '''		(symbol "rf_pa:L"
			(pin_numbers
				(hide yes)
			)
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "L"
				(at -1.016 0 90)
				(effects
					(font
						(size 1.524 1.524)
					)
					(justify right)
				)
			)
			(property "Value" "L"
				(at 1.016 0 90)
				(effects
					(font
						(size 1.524 1.524)
					)
					(justify left)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Description" "Inductor"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "ki_fp_filters" "L_* Inductor_*"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "L_0_1"
				(arc
					(start 0 -2.54)
					(mid 1.27 -1.27)
					(end 0 0)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(arc
					(start 0 0)
					(mid 1.27 1.27)
					(end 0 2.54)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "L_1_1"
				(pin passive line
					(at 0 3.81 270)
					(length 1.27)
					(name "~"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
				(pin passive line
					(at 0 -3.81 90)
					(length 1.27)
					(name "~"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# D - Diode
SYMBOL_D = '''		(symbol "rf_pa:D"
			(pin_numbers
				(hide yes)
			)
			(pin_names
				(offset 1.016)
				(hide yes)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "D"
				(at 0 2.54 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Value" "D"
				(at 0 -2.54 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Description" "Diode"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "ki_fp_filters" "D* Diode*"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "D_0_1"
				(polyline
					(pts
						(xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0) (xy 1.27 1.27)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type outline)
					)
				)
				(polyline
					(pts
						(xy -1.27 1.27) (xy -1.27 -1.27)
					)
					(stroke
						(width 0.1524)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "D_1_1"
				(pin passive line
					(at -3.81 0 0)
					(length 2.54)
					(name "A"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
				(pin passive line
					(at 3.81 0 180)
					(length 2.54)
					(name "K"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# GND - Ground power symbol (from demo, adapted)
SYMBOL_GND = '''		(symbol "rf_pa:GND"
			(power)
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "#PWR"
				(at 0 -6.35 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "Value" "GND"
				(at 0 -3.81 0)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Description" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "GND_0_1"
				(polyline
					(pts
						(xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "GND_1_1"
				(pin power_in line
					(at 0 0 0)
					(length 0)
					(hide yes)
					(name "GND"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# VCC - Power supply symbol (modeled after demo +12V)
def make_power_symbol(name, lib_id):
    """Generate a power symbol using the exact demo format."""
    return '''		(symbol "rf_pa:{name}"
			(power)
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "#PWR"
				(at 0 -6.35 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "Value" "{name}"
				(at 0 3.556 0)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Description" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "{name}_0_1"
				(polyline
					(pts
						(xy -0.762 1.27) (xy 0 2.54)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 0 2.54) (xy 0.762 1.27)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "{name}_1_1"
				(pin power_in line
					(at 0 0 0)
					(length 0)
					(hide yes)
					(name "{name}"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''.format(name=name, lib_id=lib_id)

SYMBOL_VCC = make_power_symbol("VCC", "rf_pa:VCC")
SYMBOL_VDD = make_power_symbol("+72V5", "rf_pa:+72V5")
SYMBOL_VB = make_power_symbol("VB", "rf_pa:VB")

# PWR_FLAG - power flag to satisfy ERC "power_pin_not_driven" check
SYMBOL_PWR_FLAG = '''		(symbol "rf_pa:PWR_FLAG"
			(power)
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "#PWR"
				(at 0 -6.35 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "Value" "PWR_FLAG"
				(at 0 3.556 0)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Description" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "PWR_FLAG_0_0"
				(pin power_out line
					(at 0 0 0)
					(length 0)
					(hide yes)
					(name "PWR_FLAG"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# Conn_01x02 - 2-pin connector (from demo CONN_2, adapted)
SYMBOL_CONN2 = '''		(symbol "rf_pa:Conn_01x02"
			(pin_names
				(offset 1.016)
				(hide yes)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "J"
				(at 0 5.08 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Value" "Conn_01x02"
				(at 0 -5.08 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
				)
			)
			(property "Description" "Connector 01x02"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "Conn_01x02_0_1"
				(rectangle
					(start -1.27 -2.413)
					(end 0 -2.159)
					(stroke
						(width 0.1524)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(rectangle
					(start -1.27 0.127)
					(end 0 0.381)
					(stroke
						(width 0.1524)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy -1.27 0) (xy -2.54 0)
					)
					(stroke
						(width 0.1524)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy -1.27 -2.54) (xy -2.54 -2.54)
					)
					(stroke
						(width 0.1524)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(arc
					(start -1.27 0)
					(mid 0 1.27)
					(end 1.27 0)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 1.27 -2.54) (xy 1.27 0) (xy -1.27 0)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "Conn_01x02_1_1"
				(pin passive line
					(at -2.54 0 0)
					(length 1.27)
					(name "Pin_1"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
				(pin passive line
					(at -2.54 -2.54 0)
					(length 1.27)
					(name "Pin_2"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.524 1.524)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# IRF540 - N-channel power MOSFET (modeled after demo MPSA42 transistor)
# Pin 1=Gate(left), Pin 2=Drain(top), Pin 3=Source(bottom)
SYMBOL_IRF540 = '''		(symbol "rf_pa:IRF540"
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "Q"
				(at 5.08 -3.81 0)
				(effects
					(font
						(size 1.524 1.524)
					)
					(justify left)
				)
			)
			(property "Value" "IRF540"
				(at 5.08 3.81 0)
				(effects
					(font
						(size 1.524 1.524)
					)
					(justify left)
				)
			)
			(property "Footprint" "Package_TO_SOT_THT:TO-220-3_Vertical"
				(at 5.08 0 0)
				(effects
					(font
						(size 0.762 0.762)
					)
					(hide yes)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Description" "N-channel MOSFET 100V 28A"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "ki_fp_filters" "TO-220*"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "IRF540_0_1"
				(circle
					(center 1.27 0)
					(radius 3.81)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy -2.54 0) (xy -1.27 0)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 0 -2.54) (xy 0 -1.27)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 0 1.27) (xy 0 2.54)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 0.635 -1.27) (xy 0.635 1.27)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 1.27 -1.27) (xy 1.27 -2.54)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 1.27 1.27) (xy 1.27 2.54)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 1.905 -1.27) (xy 1.905 1.27)
					)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 1.905 0.635) (xy 1.905 1.27) (xy 0.635 1.27) (xy 0.635 0.635) (xy 1.905 0.635) (xy 1.905 0) (xy 0.635 0) (xy 0.635 0.635)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type outline)
					)
				)
				(polyline
					(pts
						(xy 1.905 -1.27) (xy 1.905 -0.635) (xy 0.635 -0.635) (xy 0.635 -1.27)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type outline)
					)
				)
				(polyline
					(pts
						(xy 2.54 -2.54) (xy 1.27 -2.54)
					)
					(stroke
						(width 0.1524)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 2.54 2.54) (xy 1.27 2.54)
					)
					(stroke
						(width 0.1524)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "IRF540_1_1"
				(pin input line
					(at -5.08 0 0)
					(length 2.54)
					(name "G"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin passive line
					(at 2.54 5.08 270)
					(length 2.54)
					(name "D"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin passive line
					(at 2.54 -5.08 90)
					(length 2.54)
					(name "S"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "3"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# IR2181S - Half-bridge gate driver IC (modeled after demo LM358N)
# Pin 1=VB, 2=HIN, 3=VCC, 4=COM, 5=LO, 6=VS, 7=HO, 8=LIN
# Box: rectangle from (-7.62,-7.62) to (7.62,7.62)
# Left pins (inputs): HIN(2) at (-10.16,-5.08), LIN(8) at (-10.16,-2.54),
#                      VCC(3) at (-10.16,2.54), COM(4) at (-10.16,5.08)
# Right pins (outputs): VB(1) at (10.16,-5.08), HO(7) at (10.16,-2.54),
#                       VS(6) at (10.16,2.54), LO(5) at (10.16,5.08)
SYMBOL_IR2184 = '''		(symbol "rf_pa:IR2181S"
			(pin_names
				(offset 1.016)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "U"
				(at 0 -10.16 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Value" "IR2181S"
				(at 0 10.16 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Footprint" "Package_SOIC:SOIC-8_3.9x4.9mm_P1.27mm"
				(at 0 -12.7 0)
				(effects
					(font
						(size 0.762 0.762)
					)
					(hide yes)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(effects
					(font
						(size 1.524 1.524)
					)
				)
			)
			(property "Description" "Half-bridge gate driver"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "IR2181S_0_1"
				(rectangle
					(start -7.62 -7.62)
					(end 7.62 7.62)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type background)
					)
				)
			)
			(symbol "IR2181S_1_1"
				(pin input line
					(at -10.16 -5.08 0)
					(length 2.54)
					(name "HIN"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin input line
					(at -10.16 -2.54 0)
					(length 2.54)
					(name "LIN"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "8"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin power_in line
					(at -10.16 2.54 0)
					(length 2.54)
					(name "VCC"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "3"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin power_in line
					(at -10.16 5.08 0)
					(length 2.54)
					(name "COM"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "4"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin passive line
					(at 10.16 -5.08 180)
					(length 2.54)
					(name "VB"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin output line
					(at 10.16 -2.54 180)
					(length 2.54)
					(name "HO"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "7"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin passive line
					(at 10.16 2.54 180)
					(length 2.54)
					(name "VS"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "6"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
				(pin output line
					(at 10.16 5.08 180)
					(length 2.54)
					(name "LO"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
					(number "5"
						(effects
							(font
								(size 1.016 1.016)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)'''

# ---------------------------------------------------------------------------
# PIN POSITION MAPS
# ---------------------------------------------------------------------------
IR2184_PINS = {
    "2": (-10.16, 5.08), "8": (-10.16, 2.54),
    "3": (-10.16, -2.54), "4": (-10.16, -5.08),
    "1": ( 10.16, 5.08), "7": ( 10.16, 2.54),
    "6": ( 10.16, -2.54), "5": ( 10.16, -5.08),
}
IRF540_PINS = {"1": (-5.08, 0), "2": (2.54, -5.08), "3": (2.54, 5.08)}
R_PINS = {"1": (0, -3.81), "2": (0, 3.81)}
C_PINS = {"1": (0, -3.81), "2": (0, 3.81)}
L_PINS = {"1": (0, -3.81), "2": (0, 3.81)}
D_PINS = {"1": (-3.81, 0), "2": (3.81, 0)}
CONN2_PINS = {"1": (-2.54, 0), "2": (-2.54, 2.54)}
PWR_PINS = {"1": (0, 0)}

PIN_MAPS = {
    "rf_pa:IR2181S": IR2184_PINS, "rf_pa:IRF540": IRF540_PINS,
    "rf_pa:R": R_PINS, "rf_pa:C": C_PINS, "rf_pa:L": L_PINS,
    "rf_pa:D": D_PINS,     "rf_pa:Conn_01x02": CONN2_PINS,
    "rf_pa:PWR_FLAG": {"1": (0, 0)},
}

def pin_abs(cx, cy, rot, rx, ry):
    r = math.radians(rot)
    return (cx + rx * math.cos(r) - ry * math.sin(r),
            cy + rx * math.sin(r) + ry * math.cos(r))

def snap(v):
    return round(v / 2.54) * 2.54

# ---------------------------------------------------------------------------
# COMPONENT PLACEMENT
# ---------------------------------------------------------------------------
COMPS = []
def add(lib_id, ref, value, fp, x, y, rot=0):
    COMPS.append({"lib_id": lib_id, "ref": ref, "value": value,
                  "fp": fp, "x": x, "y": y, "rot": rot, "uuid": uuid()})

# Power input (well-spaced, left side)
add("rf_pa:Conn_01x02", "J1", "Vdd 72.5V", "TerminalBlock:TerminalBlock_bornier-2_P5.0mm", 30, 50)
add("rf_pa:C", "C1", "100uF", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm", 65, 50)
add("rf_pa:C", "C2", "0.1uF", "Capacitor_SMD:C_1206_3216Metric", 90, 50)
# Logic supply (below power input, well-spaced)
add("rf_pa:Conn_01x02", "J3", "VCC 12V", "TerminalBlock:TerminalBlock_bornier-2_P5.0mm", 30, 95)
add("rf_pa:C", "C3", "0.1uF", "Capacitor_SMD:C_1206_3216Metric", 65, 95)
# PWM input (below VCC)
add("rf_pa:Conn_01x02", "J4", "PWM IN", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 30, 135)
# Bootstrap (center-left, above gate driver)
add("rf_pa:D", "D1", "UF4007", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", 130, 50)
add("rf_pa:C", "C4", "220nF", "Capacitor_SMD:C_1206_3216Metric", 130, 80)
# Gate driver (center)
add("rf_pa:IR2181S", "U1", "IR2181S", "Package_SOIC:SOIC-8_3.9x4.9mm_P1.27mm", 170, 65)
# Gate resistors + bypass diodes (right of gate driver, well-spaced)
add("rf_pa:R", "R1", "2.2", "Resistor_SMD:R_1206_3216Metric", 210, 50, 90)
add("rf_pa:D", "D2", "1N5819", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", 240, 50, 90)
add("rf_pa:R", "R2", "2.2", "Resistor_SMD:R_1206_3216Metric", 210, 90, 90)
add("rf_pa:D", "D3", "1N5819", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", 240, 90, 90)
# MOSFETs (right of gate resistors, well-spaced)
add("rf_pa:IRF540", "Q1", "IRF540", "Package_TO_SOT_THT:TO-220-3_Vertical", 280, 50)
add("rf_pa:IRF540", "Q2", "IRF540", "Package_TO_SOT_THT:TO-220-3_Vertical", 280, 90)
# LC Tank (right of MOSFETs, well-spaced)
add("rf_pa:L", "L1", "300nH", "Inductor_THT:L_Axial_L7.0mm_D3.3mm_P5.08mm_Vertical", 320, 50, 90)
add("rf_pa:C", "C5", "470pF", "Capacitor_SMD:C_1206_3216Metric", 320, 90)
add("rf_pa:R", "R3", "2.55", "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P5.08mm_Vertical", 350, 90)
# Matching network (right of tank, well-spaced)
add("rf_pa:L", "L2", "130nH", "Inductor_THT:L_Axial_L7.0mm_D3.3mm_P5.08mm_Vertical", 380, 50, 90)
add("rf_pa:C", "C6", "1nF", "Capacitor_SMD:C_1206_3216Metric", 380, 90)
# RF output (far right)
add("rf_pa:Conn_01x02", "J2", "SMA 50ohm", "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount", 420, 90)

# PWR_FLAG components - one per power net to satisfy ERC power_pin_not_driven
add("rf_pa:PWR_FLAG", "FL1", "PWR_FLAG", "", 30, 25)     # +72V5
add("rf_pa:PWR_FLAG", "FL2", "PWR_FLAG", "", 30, 115)     # VCC
add("rf_pa:PWR_FLAG", "FL3", "PWR_FLAG", "", 30, 160)     # GND
add("rf_pa:PWR_FLAG", "FL4", "PWR_FLAG", "", 130, 25)     # VB

# ---------------------------------------------------------------------------
# NET ASSIGNMENTS
# ---------------------------------------------------------------------------
PIN_NETS = {
    "J1": {"1": "+72V5", "2": "GND"},
    "C1": {"1": "+72V5", "2": "GND"},
    "C2": {"1": "+72V5", "2": "GND"},
    "J3": {"1": "VCC", "2": "GND"},
    "C3": {"1": "VCC", "2": "GND"},
    "D1": {"1": "VCC", "2": "VB"},
    "C4": {"1": "VB", "2": "MID"},
    "U1": {"2": "HIN", "8": "LIN", "3": "VCC", "4": "GND",
           "1": "VB", "7": "HO_NET", "6": "MID", "5": "LO_NET"},
    "R1": {"1": "HO_NET", "2": "GATE1"},
    "D2": {"1": "GATE1", "2": "HO_NET"},
    "R2": {"1": "LO_NET", "2": "GATE2"},
    "D3": {"1": "GATE2", "2": "LO_NET"},
    "Q1": {"1": "GATE1", "2": "+72V5", "3": "MID"},
    "Q2": {"1": "GATE2", "2": "MID", "3": "GND"},
    "L1": {"1": "MID", "2": "TANK_OUT"},
    "C5": {"1": "TANK_OUT", "2": "GND"},
    "R3": {"1": "TANK_OUT", "2": "GND"},
    "L2": {"1": "TANK_OUT", "2": "RF_OUT"},
    "C6": {"1": "RF_OUT", "2": "GND"},
    "J2": {"1": "RF_OUT", "2": "GND"},
    "J4": {"1": "HIN", "2": "LIN"},
    "FL1": {"1": "+72V5"},
    "FL2": {"1": "VCC"},
    "FL3": {"1": "GND"},
    "FL4": {"1": "VB"},
}

POWER_NETS = {"GND", "VCC", "+72V5", "VB"}
PWR_SYMS = {"GND": "GND", "VCC": "VCC", "+72V5": "+72V5", "VB": "VB"}

# ---------------------------------------------------------------------------
# BUILD SCHEMATIC
# ---------------------------------------------------------------------------
SHEET_UUID = uuid()
L = []
w = L.append

w('(kicad_sch')
w('\t(version 20250114)')
w('\t(generator "eeschema")')
w('\t(generator_version "9.0")')
w('\t(uuid "%s")' % SHEET_UUID)
w('\t(paper "A2")')
w('\t(title_block')
w('\t\t(title "300W 13.56MHz Class-D RF Power Amplifier")')
w('\t\t(date "2026-06-27")')
w('\t\t(rev "1.0")')
w('\t\t(company "Hackerfab")')
w('\t\t(comment 1 "El-Hamamsy topology, IRF540 MOSFETs, IR2181S bootstrap driver")')
w('\t\t(comment 2 "Vdd=72.5V, Pout=305W, eff=83.7%")')
w('\t\t(comment 3 "L-match: 2.55ohm to 50ohm RF output")')
w('\t)')

# lib_symbols
w('\t(lib_symbols')
for sym_str in [SYMBOL_IR2184, SYMBOL_IRF540, SYMBOL_R, SYMBOL_C,
                SYMBOL_L, SYMBOL_D, SYMBOL_CONN2, SYMBOL_GND,
                SYMBOL_VCC, SYMBOL_VDD, SYMBOL_VB, SYMBOL_PWR_FLAG]:
    w(sym_str)
w('\t)')

# Calculate pin positions
pin_pos = {}
for c in COMPS:
    pm = PIN_MAPS.get(c["lib_id"], {})
    nets = PIN_NETS.get(c["ref"], {})
    pin_pos[c["ref"]] = {}
    for pn, (rx, ry) in pm.items():
        ax, ay = pin_abs(c["x"], c["y"], c["rot"], rx, ry)
        pin_pos[c["ref"]][pn] = (round(ax, 4), round(ay, 4), nets.get(pn, ""))

# Component instances
for c in COMPS:
    w('\t(symbol')
    w('\t\t(lib_id "%s")' % c["lib_id"])
    w('\t\t(at %.2f %.2f %d)' % (c["x"], c["y"], c["rot"]))
    w('\t\t(unit 1)')
    w('\t\t(exclude_from_sim no)')
    w('\t\t(in_bom yes)')
    w('\t\t(on_board yes)')
    w('\t\t(dnp no)')
    w('\t\t(uuid "%s")' % c["uuid"])
    w('\t\t(property "Reference" "%s"' % c["ref"])
    w('\t\t\t(at %.2f %.2f 0)' % (c["x"], c["y"] - 10))
    w('\t\t\t(effects')
    w('\t\t\t\t(font')
    w('\t\t\t\t\t(size 1.524 1.524)')
    w('\t\t\t\t)')
    w('\t\t\t)')
    w('\t\t)')
    w('\t\t(property "Value" "%s"' % c["value"])
    w('\t\t\t(at %.2f %.2f 0)' % (c["x"], c["y"] + 10))
    w('\t\t\t(effects')
    w('\t\t\t\t(font')
    w('\t\t\t\t\t(size 1.524 1.524)')
    w('\t\t\t\t)')
    w('\t\t\t)')
    w('\t\t)')
    w('\t\t(property "Footprint" "%s"' % c["fp"])
    w('\t\t\t(at %.2f %.2f 0)' % (c["x"], c["y"] + 12))
    w('\t\t\t(effects')
    w('\t\t\t\t(font')
    w('\t\t\t\t\t(size 0.762 0.762)')
    w('\t\t\t\t)')
    w('\t\t\t\t(hide yes)')
    w('\t\t\t)')
    w('\t\t)')
    w('\t\t(property "Datasheet" ""')
    w('\t\t\t(at %.2f %.2f 0)' % (c["x"], c["y"]))
    w('\t\t\t(effects')
    w('\t\t\t\t(font')
    w('\t\t\t\t\t(size 1.524 1.524)')
    w('\t\t\t\t)')
    w('\t\t\t)')
    w('\t\t)')
    w('\t\t(property "Description" ""')
    w('\t\t\t(at %.2f %.2f 0)' % (c["x"], c["y"]))
    w('\t\t\t(effects')
    w('\t\t\t\t(font')
    w('\t\t\t\t\t(size 1.27 1.27)')
    w('\t\t\t\t)')
    w('\t\t\t\t(hide yes)')
    w('\t\t\t)')
    w('\t\t)')
    for pn in PIN_MAPS.get(c["lib_id"], {}):
        w('\t\t(pin "%s"' % pn)
        w('\t\t\t(uuid "%s")' % uuid())
        w('\t\t)')
    w('\t\t(instances')
    w('\t\t\t(project "rf_pa_300w"')
    w('\t\t\t\t(path "/%s"' % SHEET_UUID)
    w('\t\t\t\t\t(reference "%s")' % c["ref"])
    w('\t\t\t\t\t(unit 1)')
    w('\t\t\t\t)')
    w('\t\t\t)')
    w('\t\t)')
    w('\t)')

# Power port instances
pwr_placed = {}
pwr_count = 0
for ref, pins in pin_pos.items():
    for pn, (ax, ay, net) in pins.items():
        if net in POWER_NETS:
            key = (ax, ay, net)
            if key not in pwr_placed:
                pwr_count += 1
                pwr_placed[key] = pwr_count
                sym = PWR_SYMS[net]
                w('\t(symbol')
                w('\t\t(lib_id "rf_pa:%s")' % sym)
                w('\t\t(at %.2f %.2f 0)' % (ax, ay))
                w('\t\t(unit 1)')
                w('\t\t(exclude_from_sim no)')
                w('\t\t(in_bom yes)')
                w('\t\t(on_board yes)')
                w('\t\t(dnp no)')
                w('\t\t(uuid "%s")' % uuid())
                w('\t\t(property "Reference" "#PWR%03d"' % pwr_count)
                w('\t\t\t(at %.2f %.2f 0)' % (ax, ay - 6))
                w('\t\t\t(effects')
                w('\t\t\t\t(font')
                w('\t\t\t\t\t(size 1.27 1.27)')
                w('\t\t\t\t)')
                w('\t\t\t\t(hide yes)')
                w('\t\t\t)')
                w('\t\t)')
                w('\t\t(property "Value" "%s"' % net)
                w('\t\t\t(at %.2f %.2f 0)' % (ax, ay + 3))
                w('\t\t\t(effects')
                w('\t\t\t\t(font')
                w('\t\t\t\t\t(size 1.27 1.27)')
                w('\t\t\t\t)')
                w('\t\t\t)')
                w('\t\t)')
                w('\t\t(property "Footprint" ""')
                w('\t\t\t(at %.2f %.2f 0)' % (ax, ay))
                w('\t\t\t(effects')
                w('\t\t\t\t(font')
                w('\t\t\t\t\t(size 1.524 1.524)')
                w('\t\t\t\t)')
                w('\t\t\t)')
                w('\t\t)')
                w('\t\t(property "Datasheet" ""')
                w('\t\t\t(at %.2f %.2f 0)' % (ax, ay))
                w('\t\t\t(effects')
                w('\t\t\t\t(font')
                w('\t\t\t\t\t(size 1.524 1.524)')
                w('\t\t\t\t)')
                w('\t\t\t)')
                w('\t\t)')
                w('\t\t(pin "1"')
                w('\t\t\t(uuid "%s")' % uuid())
                w('\t\t)')
                w('\t\t(instances')
                w('\t\t\t(project "rf_pa_300w"')
                w('\t\t\t\t(path "/%s"' % SHEET_UUID)
                w('\t\t\t\t\t(reference "#PWR%03d")' % pwr_count)
                w('\t\t\t\t\t(unit 1)')
                w('\t\t\t\t)')
                w('\t\t\t)')
                w('\t\t)')
                w('\t)')

# Wires - connect pins on the same net using multi-line KiCAD format
# Collect all pins by net
net_pins = {}
for ref, pins in pin_pos.items():
    for pn, (ax, ay, net) in pins.items():
        if net:
            if net not in net_pins:
                net_pins[net] = []
            net_pins[net].append((ax, ay))

import math as _m

def seg_hits_pin(x1, y1, x2, y2, my_net):
    """Check if wire segment passes through any pin on a DIFFERENT net."""
    for other_net, other_pins in net_pins.items():
        if other_net == my_net:
            continue
        for ox, oy in other_pins:
            if abs(x1 - x2) < 0.01:  # vertical segment
                if abs(ox - x1) < 1.0 and min(y1,y2) - 1.0 <= oy <= max(y1,y2) + 1.0:
                    return True
            elif abs(y1 - y2) < 0.01:  # horizontal segment
                if abs(oy - y1) < 1.0 and min(x1,x2) - 1.0 <= ox <= max(x1,x2) + 1.0:
                    return True
    return False

for net, pins in sorted(net_pins.items()):
    if len(pins) < 2:
        continue
    # Sort by X then Y
    pins_sorted = sorted(pins, key=lambda p: (p[0], p[1]))
    # Connect adjacent pins with L-shaped wires
    for i in range(len(pins_sorted) - 1):
        x1, y1 = pins_sorted[i]
        x2, y2 = pins_sorted[i + 1]
        dist = _m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if dist < 45:  # wire close pins, use labels for distant ones
            if abs(x1 - x2) < 0.01 or abs(y1 - y2) < 0.01:
                # Straight wire - check no other pin on segment
                if not seg_hits_pin(x1, y1, x2, y2, net):
                    w('\t(wire')
                    w('\t\t(pts')
                    w('\t\t\t(xy %.2f %.2f) (xy %.2f %.2f)' % (x1, y1, x2, y2))
                    w('\t\t)')
                    w('\t\t(stroke (width 0) (type solid))')
                    w('\t\t(uuid "%s")' % uuid())
                    w('\t)')
            else:
                # L-shaped wire - check both segments don't hit other pins
                cx1, cy1 = x2, y1  # horizontal first
                hit1 = seg_hits_pin(x1, y1, cx1, cy1, net) or seg_hits_pin(cx1, cy1, x2, y2, net)
                if hit1:
                    cx1, cy1 = x1, y2  # vertical first
                    hit2 = seg_hits_pin(x1, y1, cx1, cy1, net) or seg_hits_pin(cx1, cy1, x2, y2, net)
                    if hit2:
                        cx1, cy1 = None, None  # skip wire
                if cx1 is not None:
                    w('\t(wire')
                    w('\t\t(pts')
                    w('\t\t\t(xy %.2f %.2f) (xy %.2f %.2f)' % (x1, y1, cx1, cy1))
                    w('\t\t)')
                    w('\t\t(stroke (width 0) (type solid))')
                    w('\t\t(uuid "%s")' % uuid())
                    w('\t)')
                    w('\t(wire')
                    w('\t\t(pts')
                    w('\t\t\t(xy %.2f %.2f) (xy %.2f %.2f)' % (cx1, cy1, x2, y2))
                    w('\t\t)')
                    w('\t\t(stroke (width 0) (type solid))')
                    w('\t\t(uuid "%s")' % uuid())
                    w('\t)')

# Local labels for signal nets
lbl_placed = {}
for ref, pins in pin_pos.items():
    for pn, (ax, ay, net) in pins.items():
        if net not in POWER_NETS:
            key = (ax, ay)
            if key not in lbl_placed:
                lbl_placed[key] = net
                w('\t(label "%s"' % net)
                w('\t\t(at %.2f %.2f 0)' % (ax, ay))
                w('\t\t(effects')
                w('\t\t\t(font')
                w('\t\t\t\t(size 1.27 1.27)')
                w('\t\t\t)')
                w('\t\t\t(justify left bottom)')
                w('\t\t)')
                w('\t\t(uuid "%s")' % uuid())
                w('\t)')

# Sheet instances
w('\t(sheet_instances')
w('\t\t(path "/"')
w('\t\t\t(page "1")')
w('\t\t)')
w('\t)')
w('\t(embedded_fonts no)')
w(')')

output = '\n'.join(L) + '\n'
import sys
outfile = sys.argv[1] if len(sys.argv) > 1 else 'rf_pa_300w.kicad_sch'
with open(outfile, 'w') as f:
    f.write(output)
print("Generated: %s" % outfile)
print("Components: %d, Power ports: %d, Labels: %d, Lines: %d" %
      (len(COMPS), len(pwr_placed), len(lbl_placed), len(L)))
