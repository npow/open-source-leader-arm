# Parametric YAM Wrist Adapter

The YAM needs one more arm axis than the original SO-ARM leader. These files
insert a standard encoder cartridge at 90 degrees between the original wrist
and handle without changing the proven AS5600 housing, bearing housing, or
rotor.

## Parts

- `yam_wrist_axis_base` bolts to the output flange of the original wrist.
- `yam_wrist_axis_upright` slides into the two keyed base sockets and carries
  the added encoder/bearing cartridge.

The two legs leave a 12 mm central passage for the previous joint's rotor and
wiring. Four M3x16 screws clamp the upright to the base. Both cartridge faces
use the original 40 mm envelope and 31.05 mm four-hole pattern.

## Generate

Create an isolated Python environment and run:

```bash
pip install -r yam/cad/requirements.txt
python yam/cad/build_wrist_adapter.py
pytest -q yam/cad/test_wrist_adapter.py
```

The generator writes editable STEP files and print-oriented STL files under
`yam/cad/generated`. Dimensions are millimetres.

## Prototype print

Use PLA or PETG, 0.2 mm layers, four walls, and at least 25% infill. Both STLs
are exported on a flat face and should not require supports. Check the following
before assembling the arm:

1. An M3 screw passes through every 3.2 mm clearance hole.
2. The upright legs slide into the base sockets without forcing them. The
   modeled clearance is 0.3 mm; adjust `SOCKET_SLOT_X/Y` for the printer.
3. A standard encoder or bearing housing aligns with all four flange holes.
4. The previous rotor and cable bundle clear the 12 mm center passage through
   the full required rotation.

This is a first-print prototype. Perform those fit checks on the two adapter
pieces before printing the complete leader.
