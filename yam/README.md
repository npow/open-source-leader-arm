# Simple no-solder YAM leader

This branch builds a passive, seven-axis potentiometer controller for a YAM
robot. Each leader uses seven factory-wired B10K rotary potentiometers, seven
6000-2RS bearings, one Arduino Nano with soldered headers, one Nano I/O shield,
and eight printed PETG parts. The shopping list buys enough for **two leaders**.

This is a first-print prototype, not qualified hardware. Automated tests check
the nominal CAD, selected motion sweeps, and a documented cable-length model;
they do not prove printer fit, strength, cable clearance, or a collision-free
workspace. Print and pull-test the coupon before committing to the full arm.

## Buy this for two complete leaders

This is the shopping list. Put the stated total quantity in the cart; the
quantities are for **both leaders together**, not per leader. Prices and links
were checked on **September 3, 2026**.

| Buy this item | Cart quantity | Select exactly this option |
| --- | ---: | --- |
| [TZT WH148 factory-wired potentiometer](https://www.alibaba.com/product-detail/TZT-WH148-Potentiometer-B10K-B100K-Speed_1600768301952.html) | **14** | `B10K`, linear taper, 15 mm shaft, XH2.54 three-pin lead |
| [6000-2RS bearing](https://www.alibaba.com/product-detail/10x26x8-mm-ABEC-7-6000-2rs_1600053563089.html) | **20** | `10×26×8 mm`, sealed `6000-2RS`; fourteen are used and six are spares |
| [TZT ATmega328P/CH340 Nano V3.0](https://www.alibaba.com/product-detail/TZT-Type-C-USB-Nano-3_1600566932166.html) | **2** | `328P-Welded-TYPE-C USB`; both long header rows must already be soldered |
| [TZT Nano I/O sensor shield](https://www.alibaba.com/product-detail/TZT-NANO-V3-0-Adapter-Prototype_1601021706384.html) | **2** | Fully assembled red 58×54 mm board with two Nano socket rows and S/V/G headers |
| [30 cm male-to-female Dupont ribbon, 40 wires](https://www.alibaba.com/product-detail/30cm-40pin-M-to-F-Color_1601699032813.html) | **2 ribbons** | `30cm`, `M to F`, `40P` |

**Buy two jumper ribbons.** A `40P` ribbon is forty separate one-conductor
jumper wires joined side by side; it is not forty three-wire cables. With the
controller fixed at the base and the CAD's 200 mm pot-lead assumption, one arm
uses twelve three-wire extension segments, or **36 individual jumper wires**.
Two arms use 72; the two ribbons provide 80. Some channels use three 30 cm
segments chained end to end. The pot listing does not state the pigtail length:
if the delivered leads are shorter than about 150 mm, add a third ribbon.

A cart containing exactly those quantities showed a **$17.94 item
subtotal**, **−$0.60 item discount**, **$26.16 shipping**, and **−$11.16
shipping discount**. That is **$32.34 before tax and import charges**. Applying
the current [8.625% San Francisco sales-tax rate](https://www.cdtfa.ca.gov/taxes-and-fees/rates.aspx)
to the entire subtotal gives a conservative estimate of **$35.13**, leaving
**$14.87** for import or additional checkout charges before reaching $50.
Alibaba says the exact import charge appears at checkout, so use the final
charged total as the deciding number. Prices and discounts can change.

Also have one **1 kg spool of PETG**, **two USB-C data cables**, and either eight
#8 (about 4 mm) wood screws or two table clamps. Keep small reusable cable ties
or electrical tape for strain relief. The CAD's total solid volume is about
258 cm³ per leader, so a 1 kg spool leaves margin for the coupon and supports.

## Print

Download this branch as a [ZIP](https://github.com/npow/open-source-leader-arm/archive/refs/heads/yam-encoder-leader.zip)
and use only `yam/simple_cad/generated/stl`. Do not use `cad_files/stl`; those
are parts for the upstream SO-ARM design.

![The eight printed parts in assembly order](docs/images/assembly-part-order.png)

First print one [`joint_fit_test.stl`](simple_cad/generated/stl/joint_fit_test.stl).
It is a disposable coupon for checking the bearing pocket, snap axle, split
shaft socket, and pot cradle. Seat a bearing, snap the two coupon pieces
together, install a pot, and pull firmly on the joint. Both snap shoulders must
remain behind the bearing's inner race and the printed wall must not crack.

One leader uses one copy of each file below; **print two copies of every file
for two leaders**:

1. [`simple_base.stl`](simple_cad/generated/stl/simple_base.stl), including the fixed controller tray
2. [`simple_link_1.stl`](simple_cad/generated/stl/simple_link_1.stl)
3. [`simple_link_2.stl`](simple_cad/generated/stl/simple_link_2.stl)
4. [`simple_link_3.stl`](simple_cad/generated/stl/simple_link_3.stl)
5. [`simple_link_4.stl`](simple_cad/generated/stl/simple_link_4.stl)
6. [`simple_link_5.stl`](simple_cad/generated/stl/simple_link_5.stl)
7. [`simple_link_6.stl`](simple_cad/generated/stl/simple_link_6.stl), including the fixed gripper jaw
8. [`simple_gripper_lever.stl`](simple_cad/generated/stl/simple_gripper_lever.stl)

Use PETG, 0.20 mm layers, five walls, six top/bottom layers, and 25% gyroid.
Keep each STL's exported orientation and enable organic/tree supports from the
build plate where needed. Use about 0.20 mm elephant-foot compensation if your
slicer supports it. If the coupon fit is wrong, tune the clearances described
in [`simple_cad/README.md`](simple_cad/README.md) and regenerate it; do not
scale the STL or drill out a load-bearing axle.

Editable STEP files are in `simple_cad/generated/step`.

## Assemble one leader

Repeat this section for the second leader.

### 1. Join the eight printed parts

![How a bearing, child axle, and potentiometer form one joint](docs/images/assembly-joint-sequence.png)

1. Press one 6000-2RS bearing fully into the open round socket on the base and
   on links 1 through 6. Push only on the bearing's **outer metal race**, not
   its seal or inner race.
2. Push link 1's axle straight through the base bearing until both printed
   shoulders click behind the inner race.
3. Continue in order: base → link 1 → link 2 → link 3 → link 4 → link 5 →
   link 6 → gripper lever.
4. Check that every joint turns freely and that gently pulling the child away
   from its bearing does not release the snap shoulders.

The bearing and printed flange carry the joint load. The potentiometer only
measures the angle; it is not the axle. No screws or glue belong in a joint.

### 2. Center and install the seven pots

Do one joint at a time:

1. Put the printed joint at the middle of its travel. Leave the gripper fully
   open for its zero position.
2. Temporarily connect the loose pot to the electronics as described below and
   rotate its shaft gently until the raw reading is about `512`.
3. **Unplug USB.** Push the shaft straight into the split socket, then lower the
   round pot body and threaded bushing into the U-shaped cradle.
4. Do not install the pot's metal nut, washer, or knob.
5. Reconnect USB and move only that joint slowly to both printed stops. Its raw
   reading should stay roughly between `20` and `1000`, and the pot body must
   not twist in its cradle.

### 3. Install the Nano shield and Nano

![How the shield and Nano fit the fixed tray on the base](docs/images/assembly-controller-sequence.png)

1. Rotate the red 58×54 mm Nano I/O shield so the Nano's USB connector will
   face outward, away from the J1 pedestal, then press the shield flat into the
   four clips on the base.
2. Match the labels on the Nano to the labels beside the shield sockets—for
   example, `VIN` to `VIN` and `GND` to `GND`. USB-connector direction alone is
   not a reliable guide.
3. Verify that every pin is over a socket, with no one-pin or one-row offset,
   then press both long header rows down evenly. A shifted or reversed Nano can
   destroy it when powered.

### 4. Secure the base

Clamp the base to the table or use its four mounting holes and four #8 (about
4 mm) wood screws. Secure it before moving the arm through its range.

![Neutral and compact folded poses with the controller fixed on the base](docs/images/assembly-folded-clearance.png)

Before routing wires permanently, move slowly into the pictured compact fold:
J2 −105°, J3 +105°, J4 −90°, J5 −90°, J6 −120°, and the gripper closed. The
CAD collision test checks this fold at five J1 yaw positions. Stop rather than
force the arm if a real printed part, board, or cable catches.

The snap axles are serviceable but not intended for repeated disassembly. To
remove one, first remove the pot, squeeze both axle shoulders inward through
the cradle opening, support the bearing, and pull the child straight out.

## Wire one leader

Connect the seven pot wipers to the shield in this order:

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

Marketplace wire colors and pin order are not trustworthy. With the pot
unpowered and disconnected, use a multimeter to identify its pins: resistance
between the two outer terminals stays near 10 kΩ, while resistance from the
center wiper to either outer terminal changes as the shaft turns. Connect:

- wiper → `S` (signal)
- either outer terminal → `V` (5 V)
- the other outer terminal → `G` (ground)

Swapping the two outer wires only reverses direction; putting 5 V or ground on
the wiper is incorrect. Confirm that the XH-style pot plug or individual male
jumper pins make firm contact before relying on them. The female ends of the
male-to-female jumpers fit the shield's male S/V/G headers. Never force a
housing that does not mate.

Power the Nano and seven low-current pots from USB only. Do not connect the
shield barrel jack or an external servo supply.

### How many jumper wires are used?

The pot seller does **not** specify the factory lead length. The CAD uses a
200 mm assumption, so measure the actual leads when they arrive.

- At 200 mm, J1 reaches directly; J2 and J3 use one 30 cm three-wire segment;
  J4 and J5 use two segments; J6 and J7 use three segments chained end to end.
- That consumes 36 individual jumper wires per leader and 72 for two leaders.
  Peel the ribbon into groups of three and join male to female where a second
  or third segment is required.
- Two 40-wire ribbons provide 80 wires and therefore eight spares under that
  assumption. If the delivered pot pigtails are shorter than about 150 mm, buy a
  third ribbon.

Leave a loose loop at every moving joint. A taut wire acts like a spring and
can distort the reading. Put male-to-female junctions on straight link sections,
not inside a bending loop, and secure each junction so normal motion cannot pull
it apart.

<details>
<summary>CAD cable-length calculation</summary>

| Channel | Centerline route | Moving joints crossed | Total lead needed | 30 cm jumper segments at 200 mm |
| --- | ---: | ---: | ---: | ---: |
| J1 | 102 mm | 0 | 148 mm | 0 |
| J2 | 205 mm | 1 | 311 mm | 1 |
| J3 | 291 mm | 2 | 454 mm | 1 |
| J4 | 376 mm | 3 | 595 mm | 2 |
| J5 | 462 mm | 4 | 738 mm | 2 |
| J6 | 484 mm | 5 | 801 mm | 3 |
| J7 | 575 mm | 6 | 948 mm | 3 |

The centerline route follows each intervening joint rather than cutting
straight through space. The total then adds 25% routing allowance, a 35 mm
service loop for every moving joint crossed, and 20 mm for connectors and
strain relief.

</details>

## Flash and test the controller

Open and upload
[`firmware/yam_encoder_leader/yam_encoder_leader.ino`](../firmware/yam_encoder_leader/yam_encoder_leader.ino)
in Arduino IDE:

1. Select **Arduino Nano**, the correct serial port, and **ATmega328P**. If the
   clone will not upload, try **ATmega328P (Old Bootloader)**.
2. Keep the gripper fully released while plugging in USB or resetting. The
   firmware averages that position as the deadman-off baseline.
3. Open Serial Monitor at 115200 baud. It should emit `YAMP1` frames at 100 Hz,
   and every raw channel should remain within `[4, 1019]`.
4. Move one joint at a time, confirm the expected channel changes smoothly,
   then pull lightly on its cable and recheck it.

The firmware averages four ADC reads per reported sample. A reading at an ADC
endpoint disables the deadman, but this is only a limited wiring check: an open
analog input can float to an apparently valid value. Squeezing the gripper by
about 25 counts sets the protocol's deadman bit. In the supplied hardware host
configuration, releasing it holds the follower at its current measured pose;
the simulation configuration ignores it by default. This is not a redundant
or safety-rated emergency stop.

## Run the follower software

Use the matching `yam-encoder-leader` branch of
[`npow/gello_software`](https://github.com/npow/gello_software/tree/yam-encoder-leader).
Edit the Nano port in `configs/yam_encoder_sim.yaml`, put the six arm joints in
the printed neutral pose with the gripper open, and test one leader in
simulation first:

```bash
python experiments/launch_yaml.py \
  --left-config-path configs/yam_encoder_sim.yaml
```

The configuration maps that neutral pose to the middle of each YAM joint
range. If a joint moves backward, change its `joint_signs` entry; do not swap
wires while powered. Use `configs/yam_encoder_hw.yaml` only after directions,
limits, disconnect behavior, rate limits, and the gripper deadman all work in
simulation.

The command above launches one leader. For two, copy the config for the right
side, give it the second Nano's distinct serial port and the right follower's
distinct robot/CAN endpoint, then add `--right-config-path` to the command.
Never configure both sides to use the same serial or CAN device.

## Known prototype limitations

- Print and pull-test the coupon. FDM fit and snap strength vary by printer,
  PETG, cooling, and layer adhesion; this design has no certified load rating.
- The redesigned J2 reaches its complete printed-stop range, and the fixed
  controller clears the checked wrist-corner and compact-fold poses. These
  samples do not prove that every arbitrary multi-joint combination is free of
  self-collision; move slowly and never force a fold.
- Collision tests include a conservative 78×74×22 mm envelope for the shield,
  Nano, headers, and plugs. The exact marketplace parts and flexible wire paths
  still require physical inspection.
- WH148 carbon potentiometers are inexpensive wear parts, not precision
  encoders. Verify linearity, backlash, electrical travel, and connector grip.
- This is prototype hand-input equipment, not a payload support or a
  safety-rated control device.

CAD source, regeneration instructions, and geometry tests are in
[`simple_cad`](simple_cad/README.md).
