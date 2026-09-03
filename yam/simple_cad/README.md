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
python yam/simple_cad/render_assembly_guides.py
PYTHONPATH=yam/simple_cad pytest -q yam/simple_cad/test_simple_leader.py
```

The renderer creates the five README figures in `yam/docs/images` from the
same printed-part geometry. Purchased bearings, pots, and boards are shown as
dimensioned stand-ins rather than scanned manufacturer models.

Generation refuses to export unless all eight final parts are connected valid
solids, adjacent rigid parts do not interfere in the assembly zero pose, and
every potentiometer channel fits the documented cable budget.

The test suite moves each joint individually across its complete printed-stop
travel with the entire distal chain attached. It checks every pair of the eight
parts rather than only neighbours, and it includes the fixed controller's
78×74×22 mm electronics envelope.

Additional regressions cover all 27 nominal J4/J5/J6 corner combinations,
shoulder folds across five J1 yaw samples, the former tray-collision pose, and a
compact six-joint fold across the yaw range. They do not exhaustively sample
continuous multi-joint space or prove a self-collision-free workspace.

The gripper's leaf/post overlap is excluded from the pair checks and tested on
its own, because that overlap is the intended elastic spring engagement.

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

## Cable budget

The linked seller does not specify the potentiometer lead length. The model
uses a 200 mm assumption. The controller is fixed at the base, so distant
channels chain as many as three 300 mm male-to-female jumper segments. `cable_runs()`
computes each length and segment count; `validate_cable_reach` fails generation
if two leaders consume more individual conductors than the two 40-wire ribbons
in the BOM provide.

| Constant | Default | Meaning |
| --- | ---: | --- |
| `CONTROLLER_TRAY_CENTER` | (-45, 0, 11.3) | PCB centre on the fixed base sidecar |
| `POT_LEAD_LENGTH` | 200 | Assumed factory lead; measure the delivered parts |
| `EXTENSION_LEAD_LENGTH` | 300 | Length of one M-to-F jumper segment |
| `JUMPER_PACK_COUNT` | 2 | Number of ribbons for two leaders |
| `JUMPER_PACK_WIRES` | 40 | Individual conductors per ribbon |
| `CABLE_ROUTING_FACTOR` | 1.25 | Additional routing slack over the joint-by-joint centerline path |
| `CABLE_SERVICE_LOOP` | 35 | Slack per rotating joint a run crosses |
| `CABLE_TERMINATION_ALLOWANCE` | 20 | Connector bodies and strain relief |

Under the 200 mm assumption, J1 reaches directly, J2/J3 use one segment, J4/J5
use two, and J6/J7 use three. That is 36 individual jumper wires per leader and
72 for two, leaving eight spares. Leads shorter than about 150 mm exceed the
two-ribbon count and require a third ribbon.

## Fixed base and controller

The base reaches the J1 socket through the wedge of azimuth that link 1 never
sweeps. `_link_1_sweep` derives that wedge from J1's permitted travel and the
beam width, so widening J1's range narrows the pedestal. The section between
the flange sweep and the socket, around z = 38, is the governing structural
section of the entire machine: about 470 mm^2, against 77 mm^2 for the pair of
6 mm columns it replaced.

The horizontal Nano-shield sidecar is integral with the base, producing a
133.6×90 mm print footprint. Four risers leave clearance for solder joints on
the shield underside and four flexible clips retain its long edges. The PCB is
oriented with the Nano USB connector facing outwards, away from J1. The
controller and USB cable therefore remain stationary as every joint moves.

J2 and the complete upper chain are 55 mm higher than the rejected prototype.
That restores the complete J2 and J3 printed-stop sweeps while clearing the
base and the controller electronics envelope.

## Parametric limits

`JOINT_LIMITS_DEG` defines the printed pin-and-arc stops. J1 is ±140°, J2/J3
are ±105°, J4/J5 are ±90°, J6 is ±120°, and the gripper is 0–45°. J1's host
mapping scales 280° of safe leader travel to the follower's 325° range.

`JOINT_LIMITS_DEG` is the declared range. `stop_limited_range` adds the groove
clearance and subtracts the stop pin's own half-width, giving what the printed
stops really permit because the pin stops on its edge rather than its centre.
`usable_range` can clip that further if `BASE_LIMITED_RANGE_DEG` records a
future base obstruction; the redesigned geometry currently needs no such clip.

`test_j2_reaches_its_full_printed_stop_without_hitting_the_base` rejects the old
shoulder obstruction. `test_controller_is_fixed_to_the_base_and_old_wrist_collision_is_clear`
rejects the old moving-tray obstruction, and the fold-grid tests keep both from
returning unnoticed.

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
