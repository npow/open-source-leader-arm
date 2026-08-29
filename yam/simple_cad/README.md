# Parametric simple YAM leader CAD

[`build_simple_leader.py`](build_simple_leader.py) is the source of truth for
the eight-piece, bearing-supported potentiometer leader. Dimensions are
millimetres. Generated editable STEP and print-oriented STL files are under
[`generated`](generated).

## Generate and test

```bash
python -m venv .venv-cad
. .venv-cad/bin/activate
pip install -r yam/simple_cad/requirements.txt
python yam/simple_cad/build_simple_leader.py
PYTHONPATH=yam/simple_cad pytest -q yam/simple_cad/test_simple_leader.py
```

Generation refuses to export unless all eight final parts are connected valid
solids and adjacent rigid parts do not interfere in the assembly zero pose.
Tests also sample both ends and midpoint of every rigid arm-joint range. The
gripper test treats its leaf/post overlap separately because that overlap is
the intended elastic spring engagement, not rigid interference.

These checks do not replace a physical fit test. FDM holes and snap features
vary with printer, material, layer direction, cooling, and marketplace parts.

## Printer fit constants

Print [`generated/stl/joint_fit_test.stl`](generated/stl/joint_fit_test.stl)
before the full arm. Tune only the compensated values below; do not change the
purchased-component dimensions or scale the STL in a slicer.

| Constant | Default | Meaning |
| --- | ---: | --- |
| `BEARING_POCKET_DIAMETER` | 26.20 | Modeled hole for the 26 mm 6000-2RS outer race |
| `BEARING_POCKET_DEPTH` | 8.15 | Modeled depth for the 8 mm bearing |
| `AXLE_DIAMETER` | 9.80 | Running fit in the 10 mm inner race |
| `POT_BODY_CLEARANCE` | 0.45 | Added diameter around the nominal 17 mm WH148 body |
| `POT_BUSHING_CLEARANCE` | 0.35 | Added diameter around the nominal 7 mm threaded bushing |
| `POT_SHAFT_SOCKET_DIAMETER` | 5.85 | Interference fit inside the nominal 6 mm knurled shaft socket |
| `NANO_SHIELD_EDGE_CLEARANCE` | 0.60 | Clearance on the sourced 58×54 mm Nano I/O shield edges |

Change one fit at a time and regenerate the coupon. A loose bearing pocket or
cracked axle is a failed part, not something to repair with a load-bearing blob
of glue.

## Parametric limits

`JOINT_LIMITS_DEG` defines the printed pin-and-arc stops. J1 is ±140°, J2/J3
are ±105°, J4/J5 are ±90°, J6 is ±120°, and the gripper is 0–45°. J1's host
mapping scales 280° of safe leader travel to the follower's 325° range.

If link positions, controller location, joint envelope, beam radius, or stop
ranges change, rerun the complete collision suite and regenerate every STEP and
STL. A successful boolean check proves only the modeled nominal geometry; it
does not model printer tolerance, cable sweeps, spring deformation, creep, or
fatigue.

## Prototype limitations

- PETG is required for the snap shoulders, split shaft coupling, pot clips,
  controller clips, and gripper flexure.
- The 6000 bearing carries the joint load in the model; the potentiometer shaft
  is an unloaded angular coupling. The printed assembly has no certified load
  rating.
- The generated motion tests use rigid nominal parts. Check service loops and
  marketplace part variations across the complete real motion envelope.
- WH148 carbon potentiometers are low-cost wear parts with more backlash,
  nonlinearity, and finite life than magnetic encoders.
- Treat the full arm as prototype hand-input equipment, never as a payload
  support or safety-rated control device.
