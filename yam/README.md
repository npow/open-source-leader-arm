# Simple no-solder YAM leader

A passive seven-axis potentiometer controller for the I2RT YAM. Each leader uses
seven factory-wired B10K rotary potentiometers, seven 6000-2RS bearings, an
Arduino Nano with soldered headers, a Nano I/O shield, and eight printed PETG
parts. The shopping list covers two leaders.

This is a first-print prototype, not qualified hardware. The tests check nominal
CAD geometry, motion sweeps, and a cable-length model. They do not prove printer
fit, strength, or a collision-free workspace. Print and pull-test the coupon
before committing to a full arm.

## A YAM at 0.68 scale

Teleoperation here is joint-space: each leader angle goes straight to the
matching follower joint. Your hand tracks the follower's gripper only if every
segment carries the same scale factor, so the chain is generated from
[`yam.urdf`](https://github.com/i2rt-robotics/i2rt/blob/main/i2rt/robot_models/arm/yam/v1/yam.urdf)
instead of being drawn to fit a print bed.

| Segment | YAM | Leader |
| --- | ---: | ---: |
| Base to J1 | 68.0 mm | 46.2 mm |
| J1 to J2 (shoulder offset) | 60.2 mm | 40.9 mm |
| J2 to J3 (upper arm) | 272.8 mm | 185.5 mm |
| J3 to J4 (forearm) | 261.5 mm | 177.8 mm |
| J4 to J5 | 90.9 mm | 61.8 mm |
| J5 to J6 | 53.9 mm | 36.7 mm |

The follower's lateral shoulder and elbow offsets are reproduced, so the forearm
folds past the upper arm the way the real arm's does. Assembled, the leader
reaches 321 mm forward and stands 326 mm tall.

It will not go much smaller. A GELLO joint is a 24 mm servo; a joint here is a
26 mm bearing plus a 17 mm potentiometer needing 35 mm of shaft and cradle behind
it. YAM's J5-to-J6 offset is 53.9 mm, or 36.7 mm at this scale, and the wrist
fits only because J5's sensor faces away from it and link 5 reaches J6's bearing
from behind. Below 0.66 the folded forearm hits the base plate. Smaller needs a
9 mm pot on a smaller bearing, or AS5600 encoders.

Two dimensions are not scaled, neither of them a mapped joint: the gripper lever
pivots 72 mm from the wrist roll axis because J6's potentiometer occupies the
first 35 mm of that direction, and the base plate, pedestal, and controller tray
are sized for the parts they hold.

`LEADER_SCALE` in `simple_cad/build_simple_leader.py` sets the size, and
`test_leader_is_a_uniformly_scaled_yam` fails if any segment drifts off it.

## Buy this for two leaders

Put the stated quantity in the cart. Quantities cover both leaders together.
Prices and links checked September 3, 2026.

| Buy this item | Cart quantity | Select exactly this option |
| --- | ---: | --- |
| [TZT WH148 factory-wired potentiometer](https://www.alibaba.com/product-detail/TZT-WH148-Potentiometer-B10K-B100K-Speed_1600768301952.html) | **14** | `B10K`, linear taper, 15 mm shaft, XH2.54 three-pin lead |
| [6000-2RS bearing](https://www.alibaba.com/product-detail/10x26x8-mm-ABEC-7-6000-2rs_1600053563089.html) | **20** | `10×26×8 mm`, sealed `6000-2RS`; fourteen used, six spare |
| [TZT ATmega328P/CH340 Nano V3.0](https://www.alibaba.com/product-detail/TZT-Type-C-USB-Nano-3_1600566932166.html) | **2** | `328P-Welded-TYPE-C USB`; both long header rows already soldered |
| [TZT Nano I/O sensor shield](https://www.alibaba.com/product-detail/TZT-NANO-V3-0-Adapter-Prototype_1601021706384.html) | **2** | Assembled red 58×54 mm board, two Nano socket rows, S/V/G headers |
| [30 cm male-to-female Dupont ribbon, 40 wires](https://www.alibaba.com/product-detail/30cm-40pin-M-to-F-Color_1601699032813.html) | **3** | `30cm`, `M to F`, `40P` |

Three ribbons, because a `40P` ribbon is forty separate one-conductor jumpers
joined side by side, not forty three-wire cables. One leader uses 13 three-wire
segments, or 39 wires, so two leaders use 78. Two ribbons give 80, which covers
that only if the delivered pigtails are 176 mm or longer, and the listing does
not state the length. At 160 mm the arm needs 84. Three ribbons give 120 and
cover leads down to 100 mm.

Expect roughly $33 before tax and import charges: about $18 of items and $26 of
shipping, less roughly $12 in discounts. With
[8.625% San Francisco sales tax](https://www.cdtfa.ca.gov/taxes-and-fees/rates.aspx)
that is about $36. Alibaba shows the exact shipping discount and import charge
only at checkout, so use the final charged total.

Also have a 1 kg spool of PETG, two USB-C data cables, and either eight #8 (about
4 mm) wood screws or two table clamps. Keep cable ties or electrical tape for
strain relief. Solid volume is 313 cm³ per leader, so slice the plate before
ordering only one spool.

## Print

Download this branch as a [ZIP](https://github.com/npow/open-source-leader-arm/archive/refs/heads/yam-encoder-leader.zip)
and use only `yam/simple_cad/generated/stl`. Do not use `cad_files/stl`; those
belong to the upstream SO-ARM design.

![The eight printed parts in assembly order](docs/images/assembly-part-order.png)

Print one [`joint_fit_test.stl`](simple_cad/generated/stl/joint_fit_test.stl)
first. It is a disposable coupon for the bearing pocket, snap axle, split shaft
socket, and pot cradle. Seat a bearing, snap the two pieces together, install a
pot, and pull firmly. Both snap shoulders must stay behind the bearing's inner
race and the printed wall must not crack.

One leader uses one copy of each file. Print two copies of every file for two
leaders:

1. [`simple_base.stl`](simple_cad/generated/stl/simple_base.stl), including the fixed controller tray
2. [`simple_link_1.stl`](simple_cad/generated/stl/simple_link_1.stl)
3. [`simple_link_2.stl`](simple_cad/generated/stl/simple_link_2.stl)
4. [`simple_link_3.stl`](simple_cad/generated/stl/simple_link_3.stl)
5. [`simple_link_4.stl`](simple_cad/generated/stl/simple_link_4.stl)
6. [`simple_link_5.stl`](simple_cad/generated/stl/simple_link_5.stl)
7. [`simple_link_6.stl`](simple_cad/generated/stl/simple_link_6.stl), including the fixed gripper jaw
8. [`simple_gripper_lever.stl`](simple_cad/generated/stl/simple_gripper_lever.stl)

PETG, 0.20 mm layers, five walls, six top/bottom layers, 25% gyroid. Enable
organic or tree supports from the build plate where needed, and about 0.20 mm
elephant-foot compensation. **Do not scale the STL.** The proportions are what
make the arm steer like the follower, and a scaled axle will not carry load. If
the coupon fit is wrong, tune the clearances in
[`simple_cad/README.md`](simple_cad/README.md) and regenerate.

Check your bed against the long parts:

| Part | Footprint as exported |
| --- | --- |
| `simple_link_2` (upper arm) | 35 × 214 mm |
| `simple_link_3` (forearm) | 201 × 75 mm |
| `simple_base` | 149 × 90 mm |

Everything else is under 110 mm. A 220 mm bed takes every part square on; a
180 mm bed takes the two long links only on the diagonal. `simple_link_2` exports
standing 95 mm tall on a 35 mm footprint, so it slices into a lot of support.
Re-orient it if you prefer, but keep the joint faces off the bed.

Editable STEP files are in `simple_cad/generated/step`.

## Assemble one leader

Repeat for the second leader.

### 1. Join the eight printed parts

![How a bearing, child axle, and potentiometer form one joint](docs/images/assembly-joint-sequence.png)

1. Press one 6000-2RS bearing fully into the open round socket on the base and on
   links 1 through 6. Push only on the bearing's outer metal race.
2. Push link 1's axle straight through the base bearing until both printed
   shoulders click behind the inner race.
3. Continue in order: base, link 1, link 2, link 3, link 4, link 5, link 6,
   gripper lever.
4. Check that every joint turns freely and that pulling a child away from its
   bearing does not release the snap shoulders.

The bearing and printed flange carry the load. The potentiometer measures the
angle; it is not the axle. No screws or glue belong in a joint.

### 2. Center and install the seven pots

The printed stops are asymmetric, because each one is the follower joint's own
limit seen from the build pose. Center each pot on the middle of its printed
travel, then set the host offsets from
[the table below](#run-the-follower-software).

One joint at a time:

1. Swing the joint gently to each stop and leave it halfway between. Leave the
   gripper fully open for its zero position.
2. Connect the loose pot to the electronics and turn its shaft until the raw
   reading is about `512`.
3. **Unplug USB.** Push the shaft into the split socket, then lower the pot body
   and threaded bushing into the U-shaped cradle.
4. Do not install the pot's nut, washer, or knob.
5. Reconnect USB and move that joint slowly to both stops. The raw reading should
   stay between about `20` and `1000`, and the pot body must not twist.

### 3. Install the Nano shield and Nano

![How the shield and Nano fit the fixed tray on the base](docs/images/assembly-controller-sequence.png)

1. Rotate the red 58×54 mm shield so the Nano's USB connector faces outward, away
   from the J1 pedestal, then press it flat into the four clips on the base.
2. Match the labels on the Nano to the labels beside the shield sockets, `VIN` to
   `VIN` and `GND` to `GND`. USB-connector direction alone is not reliable.
3. Check every pin is over a socket, with no one-pin or one-row offset, then
   press both header rows down evenly. A shifted or reversed Nano can be
   destroyed when powered.

### 4. Secure the base

Clamp the base to the table, or use its four mounting holes and four #8 (about
4 mm) wood screws. Secure it before moving the arm through its range.

![Neutral and fully folded poses with the controller fixed on the base](docs/images/assembly-folded-clearance.png)

Before routing wires permanently, move slowly into the pictured fold, which puts
five joints on their stops at once: J2 −90°, J3 +90°, J4 −97°, J5 −90°, J6 −120°,
gripper closed. Stop rather than force the arm if a part, board, or cable
catches.

One combination is out of bounds. With the shoulder past J2 +20°, keep the elbow
above J3 −60° or the wrist comes down onto the base plate. A printed stop limits
one joint at a time, so this pair is an operating limit rather than a hardware
one.

The snap axles are serviceable but not meant for repeated disassembly. To remove
one, take out the pot, squeeze both axle shoulders inward through the cradle
opening, support the bearing, and pull the child straight out.

## Wire one leader

![Potentiometer S/V/G wiring and the seven Nano-shield inputs](docs/images/wiring-one-leader.png)

| Shield | Joint |
| ---: | --- |
| A0 | J1 base yaw |
| A1 | J2 shoulder |
| A2 | J3 elbow |
| A3 | J4 wrist pitch |
| A4 | J5 wrist yaw |
| A5 | J6 wrist roll |
| A6 | Gripper/deadman |

### Check every three-wire connector before power

Marketplace wire colors and pin order are not trustworthy. With the pot unpowered
and disconnected, meter its pins: the two outer terminals stay near 10 kΩ apart,
while the center wiper to either outer terminal changes as the shaft turns.
Connect:

- wiper to `S` (signal)
- either outer terminal to `V` (5 V)
- the other outer terminal to `G` (ground)

Swapping the two outer wires only reverses direction. Putting 5 V or ground on
the wiper is wrong. Confirm the XH-style plug or male jumper pins make firm
contact, and never force a housing that does not mate.

Power the Nano and the seven low-current pots from USB only. Do not connect the
shield's barrel jack or an external servo supply.

### Jumper wires per leader

The seller does not specify the factory lead length. The CAD assumes 200 mm, so
measure the delivered pots. At 200 mm, one leader needs:

| Channel | Segments | Wires |
| --- | ---: | ---: |
| J1 | 0 (reaches directly) | 0 |
| J2 | 1 | 3 |
| J3 | 1 | 3 |
| J4 | 2 | 6 |
| J5 | 3 | 9 |
| J6 | 3 | 9 |
| J7 | 3 | 9 |
| Total | 13 | 39 |

A segment is three loose jumpers, one each for S, V, and G, not a three-wire
cable. Peel groups of three off the ribbon and join male to female where a
channel needs more than one. Two leaders use 78 of the 120 wires in three
ribbons.

Leave a loose loop at every moving joint; a taut wire acts like a spring and
distorts the reading. Put junctions on straight link sections, not inside a
bending loop, and secure each one so normal motion cannot pull it apart.

<details>
<summary>CAD cable-length calculation</summary>

| Channel | Centerline route | Moving joints crossed | Total lead needed | 30 cm segments at 200 mm |
| --- | ---: | ---: | ---: | ---: |
| J1 | 61 mm | 0 | 96 mm | 0 |
| J2 | 137 mm | 1 | 226 mm | 1 |
| J3 | 308 mm | 2 | 475 mm | 1 |
| J4 | 468 mm | 3 | 710 mm | 2 |
| J5 | 558 mm | 4 | 857 mm | 3 |
| J6 | 601 mm | 5 | 946 mm | 3 |
| J7 | 653 mm | 6 | 1046 mm | 3 |

The route follows each intervening joint rather than cutting through space, then
adds 25% routing allowance, a 35 mm service loop per moving joint crossed, and
20 mm for connectors and strain relief.

</details>

## Flash and test the controller

Upload
[`firmware/yam_encoder_leader/yam_encoder_leader.ino`](../firmware/yam_encoder_leader/yam_encoder_leader.ino)
in the Arduino IDE:

1. Select Arduino Nano, the correct port, and ATmega328P. If a clone will not
   upload, try ATmega328P (Old Bootloader).
2. Keep the gripper fully released while plugging in USB or resetting. The
   firmware averages that position as the deadman-off baseline.
3. Open Serial Monitor at 115200 baud. It should emit `YAMP1` frames at 100 Hz,
   every raw channel within `[4, 1019]`.
4. Move one joint at a time, confirm the expected channel changes smoothly, then
   pull lightly on its cable and recheck.

The firmware averages four ADC reads per sample. A reading at an ADC endpoint
disables the deadman, but that is a limited wiring check, since an open analog
input can float to a valid-looking value. Squeezing the gripper by about 25
counts sets the protocol's deadman bit. In the hardware host configuration,
releasing it holds the follower at its current measured pose; the simulation
configuration ignores it by default. This is not a safety-rated emergency stop.

## Run the follower software

Use the matching `yam-encoder-leader` branch of
[`npow/gello_software`](https://github.com/npow/gello_software/tree/yam-encoder-leader).
Edit the Nano port in `configs/yam_encoder_sim.yaml`, hold the arm in its neutral
pose with the gripper open, and test one leader in simulation first:

```bash
python experiments/launch_yaml.py \
  --left-config-path configs/yam_encoder_sim.yaml
```

**Those configs do not match this arm out of the box, and this branch does not
change them.** Set each joint's offset so a centered pot reads the follower angle
below, and set `joint_signs` to −1 where shown:

| Joint | Follower angle at a centered pot | `joint_signs` |
| --- | ---: | ---: |
| J1 base yaw | 0° | −1 |
| J2 shoulder | 105° | +1 |
| J3 elbow | 98° | +1 |
| J4 wrist pitch | −3.5° | +1 |
| J5 wrist yaw | 0° | −1 |
| J6 wrist roll | 0° | +1 |

J1 and J5 take −1 because their potentiometers face the other way, which gives
the pedestal and the wrist their clearance. Every axis is one degree of leader
per degree of follower, with no per-joint gain. If a joint still moves backward,
fix it in `joint_signs`; do not swap wires while powered. Use
`configs/yam_encoder_hw.yaml` only after directions, limits, disconnect behavior,
rate limits, and the gripper deadman all work in simulation.

For two leaders, copy the config for the right side with the second Nano's serial
port and the right follower's robot or CAN endpoint, then add
`--right-config-path`. Never point both sides at the same device.

### What the leader cannot reach

Every printed stop is the follower joint's own limit, with two exceptions:

| Joint | Follower travel | Leader travel | Given up |
| --- | --- | --- | --- |
| J1 base yaw | −150° to +180° | ±140° | 40° one way, 10° the other |
| J3 elbow | 0° to 180° | 16° to 180° | 16° at the folded end |

J1 needs 330°, more than one 300° potentiometer can measure, so its stops sit
symmetrically inside what the pot reads. J3 stops short because the printed
forearm, fatter than the real arm's, reaches the upper arm over the last 16° of
its fold.

## Known prototype limitations

- Print and pull-test the coupon. FDM fit and snap strength vary by printer,
  PETG, cooling, and layer adhesion. This design has no certified load rating.
- Every joint clears its full printed-stop range with the whole distal chain
  attached, and the shoulder and elbow are swept as a grid. That does not prove
  every multi-joint combination is free of self-collision, so move slowly and
  never force a fold.
- A faithfully scaled YAM inherits the follower's own folded self-collisions. A
  URDF joint limit is not a promise of a collision-free workspace, on either arm.
- Collision tests use a conservative 78×74×22 mm envelope for the shield, Nano,
  headers, and plugs. Real parts and flexible wire paths still need physical
  inspection.
- WH148 carbon potentiometers are inexpensive wear parts, not precision encoders.
  Verify linearity, backlash, electrical travel, and connector grip.
- This is prototype hand-input equipment, not a payload support or a safety-rated
  control device.

CAD source, regeneration instructions, and geometry tests are in
[`simple_cad`](simple_cad/README.md).
