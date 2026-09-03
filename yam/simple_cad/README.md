# Parametric simple YAM leader CAD

[`build_simple_leader.py`](build_simple_leader.py) is the source of truth for
the eight-piece, bearing-supported potentiometer leader. Dimensions are
millimetres. Generated editable STEP and print-oriented STL files are under
[`generated`](generated).

## The chain comes from the follower

`YAM_URDF_CHAIN` holds the joint origins, axes, and limits copied out of
`i2rt/robot_models/arm/yam/v1/yam.urdf`. `yam_chain()` runs forward kinematics
over those rows at `YAM_BUILD_POSE_DEG` and multiplies by `LEADER_SCALE`, which
is the single number that sets the arm's size. `JOINTS` and `JOINT_LIMITS_DEG`
are derived from that and must not be hand-edited.

Joint-space teleoperation only tracks the follower if the leader is a *uniform*
scaling of it, so `test_leader_is_a_uniformly_scaled_yam` compares every segment
against the URDF at both 1.0 and `LEADER_SCALE`. Per-segment adjustment is the
failure this guards against: it leaves every angle legal and silently removes
the correspondence the operator steers by.

`YAM_BUILD_POSE_DEG` uses multiples of 90 degrees so every axis lands on a world
axis, which is all `_orient_x` can build, and it sits near the middle of every
follower joint range. Printed stops then follow as `follower limit - build
angle`, clipped by `POT_USABLE_TRAVEL_DEG` and `SELF_COLLISION_LIMIT_DEG`.
`follower_travel_lost_deg()` reports everything the leader gives up.

`POT_MOUNT_SIGN` flips J1, J5, and J7. The socket and its potentiometer always
extend along +axis, so the sign picks which side of a joint the sensor sticks
out of, and each flip costs a `joint_signs` of −1 in the host config. J1 faces
down so its pedestal is a column under the socket instead of a wedge threaded
through link 1's sweep; J5 faces up so link 5 has a corridor down to J6.

### How small can it go?

`LEADER_SCALE` was searched downward against this suite. At 0.75 every part is a
valid single solid and all 34 tests pass. Below about 0.66 the folded arm starts
hitting the base plate and the controller envelope, which are sized by purchased
parts and do not shrink with the arm. Between those, the wrist link's boolean
construction is unreliable at some scales: J5 and J6 are 40 mm apart at 0.75
while a 25 mm neck and a 35 mm pot carrier have to fit between them, and the
routing degenerates. Going smaller is a joint-hardware change, not a parameter
change.

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
shoulder folds across five J1 yaw samples, the former tray-collision pose, a
a six-joint fold onto the printed stops across the yaw range, and a shoulder/elbow grid that
checks the documented fold envelope in both directions — everything inside it
clears, and the corner it excludes really does collide. They do not exhaustively
sample continuous multi-joint space or prove a self-collision-free workspace.

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
channels chain as many as four 300 mm male-to-female jumper segments. `cable_runs()`
computes each length and segment count; `validate_cable_reach` fails generation
if two leaders consume more individual conductors than the three 40-wire ribbons
in the BOM provide.

| Constant | Default | Meaning |
| --- | ---: | --- |
| `CONTROLLER_TRAY_CENTER` | derived | PCB centre, set behind the pedestal |
| `POT_LEAD_LENGTH` | 200 | Assumed factory lead; measure the delivered parts |
| `EXTENSION_LEAD_LENGTH` | 300 | Length of one M-to-F jumper segment |
| `JUMPER_PACK_COUNT` | 3 | Number of ribbons for two leaders |
| `JUMPER_PACK_WIRES` | 40 | Individual conductors per ribbon |
| `CABLE_ROUTING_FACTOR` | 1.25 | Additional routing slack over the joint-by-joint centerline path |
| `CABLE_SERVICE_LOOP` | 35 | Slack per rotating joint a run crosses |
| `CABLE_TERMINATION_ALLOWANCE` | 20 | Connector bodies and strain relief |

Under the 200 mm assumption, J1 reaches directly, J2 uses one segment, J3/J4 use
two, J5/J6 use three, and J7 uses four. That is 45 individual jumper wires per
leader and 90 for two, leaving 30 spares. Three ribbons still cover the arm at a
100 mm factory lead, so the budget no longer depends on the unstated length.

## Fixed base and controller

J1's socket faces down, so `_pedestal` is a plain column carrying the whole
underside of that socket, open toward the arm so the potentiometer still slides
into its cradle after printing. The alternative — socket facing up — forces the
pedestal to reach through a gap in link 1's own sweep, and the follower's
33.9 mm shoulder offset swings link 1 about 21 degrees wide in plan view, which
leaves no such gap at J1's full travel. The governing section between the plate
and the socket is over 1500 mm^2, against 77 mm^2 for the pair of 6 mm columns
the design started with.

The horizontal Nano-shield sidecar is integral with the base, producing a
149×90 mm print footprint. Four risers leave clearance for solder joints on the
shield underside and four flexible clips retain its long edges. The PCB is
oriented with the Nano USB connector facing outwards, away from J1. The
controller and USB cable therefore remain stationary as every joint moves.

## Two links do not take the direct route

`_link` builds a link as a plug, a radial neck, a beam, and the next socket.
Two joints cannot use it:

- `build_link_5` reaches J6's socket from the sector opposite J5. J5 and the
  gripper are both on the same side of J6, and J6 rolls 240 degrees, so its
  moving link sweeps every radial direction but a 120 degree sector on the far
  side. A straight beam into that socket locks the wrist.
- `build_link_6` runs parallel to the roll axis until it is clear of J6's
  bearing seat and pot holder before turning toward the lever pivot.

Both use `_beam_path_pieces`, which puts a ball at each corner. Two cylinders
meeting exactly at a shared end plane are a tangency rather than a shared
volume, and the boolean will quietly drop one of them, leaving a link in two
pieces that happen to touch.

## Parametric limits

`JOINT_LIMITS_DEG` defines the printed pin-and-arc stops, and it is derived
rather than chosen: each stop is the follower's own limit seen from the build
pose. J1 is clipped to ±140° because its 330° of follower travel exceeds what
one potentiometer measures, and J3 is clipped to −74° because the printed
forearm reaches the upper arm before the follower's fold ends. Everything else
matches the follower exactly, so the host needs no per-joint gain.

`stop_limited_range` adds the groove clearance and subtracts the stop pin's own
half-width, giving what the printed stops really permit because the pin stops on
its edge rather than its centre. That, not the declared range, is what the
collision suite sweeps.

`COUPLED_FOLD_LIMIT_DEG` and `fold_is_permitted` record the one pair of joints a
single-joint stop cannot protect: shoulder forward past J2 +20° with the elbow
below J3 −60° puts the wrist on the base plate.

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
