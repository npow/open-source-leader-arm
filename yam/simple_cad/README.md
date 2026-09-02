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
solids, adjacent rigid parts do not interfere in the assembly zero pose, and
every potentiometer channel fits the documented cable budget.

The test suite moves each joint across the travel the hardware actually
permits -- the printed stops, less the stop pin's own width, further clipped
where the base blocks the joint first -- **with the entire distal chain
attached**, and checks every pair of the eight parts rather than only
neighbours. It also checks wrist combinations, since that is where the hand
comes closest to the controller tray.

It deliberately does not check whole-arm folds. Any serial arm with this much
travel can be folded into itself, so a self-collision-free workspace is not a
property this design has or claims. What is checked is that no single joint,
and no wrist combination, hits anything on the way from the neutral pose to its
stop, which is what assembly step 8 asks you to do.

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

The potentiometers ship with fixed 200 mm leads and the chain is about 400 mm
long, so no controller position lets both ends of the arm reach. `cable_runs()`
computes each channel's requirement, `validate_cable_reach` fails generation if
any channel exceeds lead plus extension, and running the build prints the table.

| Constant | Default | Meaning |
| --- | ---: | --- |
| `CONTROLLER_TRAY_CENTER` | (30, 45, 225) | Where the Nano shield sits, on link 3 |
| `POT_LEAD_LENGTH` | 200 | Factory lead on the sourced potentiometer |
| `EXTENSION_LEAD_LENGTH` | 300 | One extension lead from the BOM |
| `CABLE_ROUTING_FACTOR` | 1.25 | Allowance for following the links |
| `CABLE_SERVICE_LOOP` | 35 | Slack per rotating joint a run crosses |
| `CABLE_TERMINATION_ALLOWANCE` | 20 | Connector bodies and strain relief |

Five of the seven channels need an extension: J1, J2, J5, J6, and J7.

## Base pedestal

The base reaches the J1 socket through the wedge of azimuth that link 1 never
sweeps. `_link_1_sweep` derives that wedge from J1's permitted travel and the
beam width, so widening J1's range narrows the pedestal. The section between
the flange sweep and the socket, around z = 38, is the governing structural
section of the entire machine: about 470 mm^2, against 77 mm^2 for the pair of
6 mm columns it replaced.

## Parametric limits

`JOINT_LIMITS_DEG` defines the printed pin-and-arc stops. J1 is ±140°, J2/J3
are ±105°, J4/J5 are ±90°, J6 is ±120°, and the gripper is 0–45°. J1's host
mapping scales 280° of safe leader travel to the follower's 325° range.

Three ranges matter here and they are not the same. `JOINT_LIMITS_DEG` is the
declared range. `stop_limited_range` adds the groove clearance and subtracts the
stop pin's own half-width, giving what the printed stops really permit, because
the pin stops on its edge rather than its centre. `usable_range` clips that
further wherever `BASE_LIMITED_RANGE_DEG` records the base blocking a joint
first, which today is J2's negative swing at about −90° instead of −105°.

Two limitations are recorded by tests rather than fixed, because both need
joints or mounts moved rather than a constant tuned:

- **J2** reaches the base plate at about −90°, inside its declared −105°. The
  bare plate causes it, so the pedestal neither created nor worsened it within
  the declared range.
- **The controller tray** sits inside the shell link 5 sweeps about J4, so a
  folded wrist drives link 5 into it across roughly a quarter of the wrist's
  travel. `CONTROLLER_TRAY_CENTER = (130.0, 0.0, 225.0)` clears the whole wrist
  grid and still fits the cable budget, at the cost of new standoffs.

`test_base_blocks_j2_before_its_printed_stop` and
`test_controller_tray_sits_inside_the_wrist_envelope` assert that both are still
true, so neither can quietly change without someone noticing.

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
