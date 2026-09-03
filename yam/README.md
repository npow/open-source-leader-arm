# Simple no-solder YAM leader

This branch is the inexpensive version. Each leader uses seven factory-wired
**rotary** potentiometers with a linear taper, seven bearings, one pre-soldered
Arduino Nano, one plug-in I/O shield, and eight printed structural pieces. The
shopping list below buys enough electronics and bearings for **two complete
leaders**. There are no magnets, encoder boards, muxes, hex nuts, joint screws,
or soldered connections. The gripper's printed PETG leaf is both its return
spring and the firmware deadman input.

This is a generated prototype. Its geometry check moves each joint across the
travel the hardware actually permits, with the whole distal chain attached, and
looks for interference between every pair of the eight parts. It does **not**
claim a self-collision-free workspace: like any serial arm, this one can be
folded into itself. That is a nominal-geometry check on a **first-print
prototype**, not a physically qualified product. Print the joint coupon, load-test its snap axle,
and verify the sourced parts before printing the arm.

## Buy this for two complete leaders

This is the shopping list. Put the stated total quantity in the cart; the
quantities are for **both leaders together**, not per leader. Prices and links
were checked on **September 2, 2026**.

| Buy this item | Cart quantity | Required selection | Listed item total |
| --- | ---: | --- | ---: |
| [TZT WH148 factory-wired potentiometer](https://www.alibaba.com/product-detail/TZT-WH148-Potentiometer-B10K-B100K-Speed_1600768301952.html) | **14** | `B10K`, linear taper, 15 mm shaft, XH2.54 three-pin lead | $6.30 |
| [6000-2RS bearing](https://www.alibaba.com/product-detail/10x26x8-mm-ABEC-7-6000-2rs_1600053563089.html) | **20** | `10×26×8 mm`, sealed `6000-2RS`; fourteen are used and six are spares | $4.40 |
| [TZT ATmega328P/CH340 Nano V3.0](https://www.alibaba.com/product-detail/TZT-Type-C-USB-Nano-3_1600566932166.html) | **2** | `328P-Welded-TYPE-C USB`, with both long header rows already soldered | $5.16 |
| [TZT Nano I/O sensor shield](https://www.alibaba.com/product-detail/TZT-NANO-V3-0-Adapter-Prototype_1601021706384.html) | **2** | Fully assembled red 58×54 mm board with the two Nano sockets and S/V/G headers | $2.30 |
| [30 cm male-to-female Dupont ribbon, 40 wires](https://www.alibaba.com/product-detail/30cm-40pin-M-to-F-Color_1601699032813.html) | **2 ribbons** | `30cm`, `M to F`, `40P` | $0.64 |

**Buy two jumper ribbons.** A `40P` ribbon is forty separate one-conductor
jumper wires joined side by side; it is not forty three-wire cables. If the pot
leads are 20 cm long, five joints per leader need extensions, so the two arms
use 5 joints × 3 wires × 2 leaders = **30 jumper wires**. However, the cheap pot
listing does not specify its lead length. If all fourteen pots need extensions,
they require **42 wires**. Two ribbons provide 80, cover either case, and cost
only $0.32 more than one.

The conservative listed-item subtotal is now **$18.80** before shipping, tax,
or payment fees. To finish below **$50 after 8.625% San Francisco sales tax**,
the complete checkout before tax must be **$46.03 or less**, leaving **$27.23**
for shipping and fees. Alibaba did not expose final freight without completing
the variant and account/CAPTCHA steps, so this is a checkout target rather than
a promised delivered price. Do not buy if the selected variants do not match
the `Required selection` column.

The pots, Nanos, and shields come from the same TZT supplier, which may help
with combined shipping. The bearings and ribbons come from two other suppliers.
Prices, stock, shipping, tax, and delivery dates can change at checkout.

You also need about **1 kg of PETG**, **two USB-C data cables**, and optionally
eight #8 or 4 mm wood screws or two table clamps. Those are not included in the
$18.80 online-parts subtotal.

### Why the shield listing says UNO

The linked red board is a breakout/carrier for an **Arduino Nano V3.0**: the
Nano plugs into the two parallel sockets in its center. It is not an Uno shield,
and an Arduino Uno cannot plug into it. Some generic listings mention Uno
because the shield also breaks signals out around its edge in the classic
Uno/Duemilanove layout; that does not change which controller fits the socket.

The bearing listing is the price choice, not the design limit.
[DigiKey's 6000-2RS data](https://www.digikey.com/en/products/detail/mechatronics-bearing-group/6000-2RS/9608370)
lists roughly 790 lbf dynamic and 440 lbf static bearing ratings.
The printed PETG, layer adhesion, snap axle, base, and desk attachment are much
weaker and remain unqualified. This leader is intended only for hand input; do
not hang a payload from it or infer a safe working load from the bearing rating.

### Connector check before ordering multiples

The pot listing calls its plug JST-XH2.54 while the shield uses ordinary
2.54 mm male headers. That unshrouded combination normally presses together,
but neither listing guarantees a keyed system-level mate. Before ordering all
fourteen pots, be comfortable checking one connector. The crimp contacts can
be reordered in their plastic housing with a small pick if the wire order
differs; that does not require cutting or soldering.

Never trust wire colors. The pot's centre/wiper wire goes to `S`, one outer wire
to `V`, and the other outer wire to `G`. Identify the wiper with a multimeter:
the two outer wires stay near 10 kΩ while resistance from either outer wire to
the wiper changes as the shaft turns. Swapping only `V` and `G` reverses that
joint and is also correctable with `joint_signs` in software.

## Complete print list

Download this branch as a [ZIP](https://github.com/npow/open-source-leader-arm/archive/refs/heads/yam-encoder-leader.zip)
and use only `yam/simple_cad/generated/stl`.

Print this inexpensive coupon first; it is not part of the final arm:

| STL | Qty | Checks |
| --- | ---: | --- |
| [`joint_fit_test.stl`](simple_cad/generated/stl/joint_fit_test.stl) | 1 | 6000 bearing pocket, 9.8 mm snap axle, 6 mm split shaft socket, and WH148 body/bushing carrier. The socket and plug are two separate solids in one STL. Also **pull on the assembled coupon**: the snap barbs retain the axle through a shallow inclined face, and at J1 they carry the arm in tension. |

Each leader is exactly these eight prints, one of each. For two leaders, print
every row **twice**:

| Order | STL | Integral features |
| ---: | --- | --- |
| 1 | [`simple_base.stl`](simple_cad/generated/stl/simple_base.stl) | J1 bearing/pot socket, buttressed pedestal, and four optional mounting holes |
| 2 | [`simple_link_1.stl`](simple_cad/generated/stl/simple_link_1.stl) | J1 axle/coupling and J2 socket |
| 3 | [`simple_link_2.stl`](simple_cad/generated/stl/simple_link_2.stl) | J2 axle/coupling and J3 socket |
| 4 | [`simple_link_3.stl`](simple_cad/generated/stl/simple_link_3.stl) | J3 axle, J4 socket, and snap tray for the 58×54 mm Nano shield |
| 5 | [`simple_link_4.stl`](simple_cad/generated/stl/simple_link_4.stl) | J4 axle/coupling and J5 socket |
| 6 | [`simple_link_5.stl`](simple_cad/generated/stl/simple_link_5.stl) | J5 axle/coupling and J6 socket |
| 7 | [`simple_link_6.stl`](simple_cad/generated/stl/simple_link_6.stl) | J6 axle, gripper socket, fixed palm, and flexure post |
| 8 | [`simple_gripper_lever.stl`](simple_cad/generated/stl/simple_gripper_lever.stl) | Gripper axle, squeeze lever, and integral PETG return leaf |

Do not print the old files under `cad_files/stl`; those belong to the upstream
SO-ARM design. Editable STEP files are next to the STLs under
`simple_cad/generated/step`.

### Print settings

- PETG, 0.20 mm layer height, five walls, six top/bottom layers, and 25% gyroid.
- Use the orientation already stored in each STL. Do not prioritize surface
  finish over the exported axle orientation.
- Enable organic/tree supports from the build plate where your slicer detects
  the open pot carriers or controller clips.
- Use about 0.20 mm elephant-foot compensation if available.
- Do not drill or aggressively sand the axle. Tune the fit constants and
  reprint the coupon instead.

## How the inexpensive joint stays load-bearing

The parent link holds the **outer race** of a 6000-2RS bearing. The child is one
continuous printed part: a 9.8 mm axle passes through the 10 mm inner race and
snaps behind it, while its rear 5 mm is hollow and split to grip the pot shaft.
The bearing and the printed flange carry bending and radial load. The pot shaft
transmits sensing torque only; the pot body clips into a stationary cradle and
is not used as an axle.

A printed pin and recessed arc stop the joint before the pot's internal end
stops. J1 uses a protected 280° leader sweep and software scales it to YAM's
325° range. J2/J3 use 210°, J4/J5 180°, and J6 240°; all stay within the
nominal 300° electrical travel.

**J2 does not actually get its full 210°.** Swinging it negative drives links 2
and 3 into the base plate at about **−90°**, roughly 15° before its printed stop
at −105°. The bare base plate causes this on its own, so it is a link-geometry
limitation rather than a fit constant, and it is unchanged by the pedestal.
`BASE_LIMITED_RANGE_DEG` in the CAD records the measured value, and host
calibration has to respect it or the follower gets commanded to a pose the
leader cannot reach. Fixing it properly means raising J2 or shrinking the base
plate and regenerating every part.

**The controller tray blocks part of the wrist's travel.** The tray on link 3
lies inside the shell link 5 sweeps about J4, so folding the wrist down and
across — roughly J4 below −45° combined with J5 beyond −60° — drives link 5
into it, about 500 mm³ deep at worst rather than a graze. Link 3's own beam is
clear; it is entirely the tray. Moving the tray to the other side of the link
only mirrors the blocked region, because J5 is a yaw axis and the envelope is
symmetric. Relocating it outboard in the arm's own plane
(`CONTROLLER_TRAY_CENTER = (130.0, 0.0, 225.0)`) clears the whole wrist grid and
still fits the cable budget at 424 mm, but it needs different standoffs and its
shield-plus-Nano envelope is not modelled, so this branch keeps the original
position and records the limitation instead.

## Mechanical assembly

1. Print the coupon. Confirm the bearing seats fully, the axle rotates without
   binding, both snap shoulders catch behind the inner race, the remaining
   radial wall is intact, and the pot body/bushing clip into the carrier.
2. If a fit is wrong, change only the printer-clearance constants documented in
   [`simple_cad/README.md`](simple_cad/README.md), regenerate, and print another
   coupon. Do not scale an STL in the slicer.
3. Print the eight final pieces. Remove supports and elephant foot without
   thinning the axle jaws, bearing stop shoulder, controller clips, or flexure.
4. Press one bearing completely into each stationary socket: the base and
   links 1 through 6. Press on the **outer race**, not through the seals.
5. Starting at J1, push the child axle straight through its parent bearing until
   both integral shoulders click behind the inner race. Repeat through J7.
6. Before coupling each pot, move the joint to the middle of its printed travel
   (leave the gripper fully open), connect the electronics temporarily, and
   turn the loose pot gently to about raw count 512.
7. Angle the pot over its open carrier, push its shaft axially into the split
   socket, then lower the round body and threaded bushing into their clips. The
   included metal nut, washer, and knob are not used.
8. Move each joint slowly to both printed stops. The raw value must remain
   between about 20 and 1000 and the pot body must not twist in its carrier.
9. Snap the Nano shield onto link 3, then plug the soldered Nano into the shield
   with every pin aligned. A one-row offset can destroy the board.

The snap axle is serviceable but not meant for frequent disassembly. To remove
a joint, remove the pot first, squeeze both axle shoulders through the carrier
opening, and pull straight while supporting the bearing.

## Plug-in wiring

No mux or daisy-chain electronics are required. Plug the seven pot signals into
the analog rows on the Nano shield:

| Shield input | Joint | Pot position at printed zero |
| ---: | --- | ---: |
| A0 | J1 base yaw | about 512 |
| A1 | J2 shoulder | about 512 |
| A2 | J3 elbow | about 512 |
| A3 | J4 wrist pitch | about 512 |
| A4 | J5 wrist yaw | about 512 |
| A5 | J6 wrist roll | about 512 |
| A6 | Gripper/deadman | about 512, fully released |

For every connector: wiper to `S`, outer terminals to `V` and `G`. USB powers
the low-current pots and Nano; do not connect the shield's barrel jack or an
external servo supply.

### Lead lengths

The reach calculation assumes 20 cm factory pot leads, while the chain is about
40 cm long. No tray position lets both ends of the arm reach.
`build_simple_leader.py` computes this budget and prints it whenever you
generate. With 20 cm pot leads, J3 and J4 reach directly; **J1, J2, J5, J6,
and J7 each need one three-wire group peeled from the 30 cm ribbon**. If the
selected pots have shorter leads, extend J3 and J4 as well; the two ribbon packs
in the shopping list provide enough wires for all seven joints on both leaders.

| Channel | Direct distance | Rotating joints crossed | Lead needed |
| --- | ---: | ---: | ---: |
| J1 | 157 mm | 3 | 321 mm |
| J2 | 144 mm | 2 | 270 mm |
| J3 | 71 mm | 1 | 144 mm |
| J4 | 62 mm | 0 | 97 mm |
| J5 | 119 mm | 1 | 204 mm |
| J6 | 127 mm | 2 | 249 mm |
| J7 | 182 mm | 3 | 353 mm |

"Lead needed" allows 25% over the straight line for following the links, 35 mm
of service loop per rotating joint the run crosses, and 20 mm for connector
bodies and strain relief. Leave those service loops genuinely loose: a taut
cable across a joint is a return spring the potentiometer has to fight, and it
shows up as hysteresis. Verify full motion before pressing cables into
permanent clips or tape.

## Firmware and safe first test

Open and upload
[`firmware/yam_encoder_leader/yam_encoder_leader.ino`](../firmware/yam_encoder_leader/yam_encoder_leader.ino)
in Arduino IDE:

1. Select **Arduino Nano** and the serial port.
2. Select **ATmega328P**. If upload fails on a clone, try **ATmega328P (Old
   Bootloader)**.
3. Keep the gripper fully released while connecting USB or resetting the Nano.
   Firmware averages that position as the deadman-off baseline.
4. Open Serial Monitor at 115200 baud. Every channel should report a raw value
   in `[4, 1019]`, followed by `YAMP1` data frames.

The firmware reads four ADC samples per channel at 100 Hz. Any open/shorted
endpoint reading disables the deadman. Squeezing the gripper by about 25 ADC
counts enables commands; releasing its printed flexure holds the follower at
its measured pose.

Use the matching `yam-encoder-leader` branch of
[`npow/gello_software`](https://github.com/npow/gello_software/tree/yam-encoder-leader),
edit the Nano port in `configs/yam_encoder_sim.yaml`, and test every direction
in simulation first:

```bash
python experiments/launch_yaml.py \
  --left-config-path configs/yam_encoder_sim.yaml
```

Calibrate with the six arm joints in the printed CAD zero pose and the gripper
open. The configuration maps that neutral leader pose to the midpoint of each
YAM joint range. If an axis moves backward, flip its `joint_signs` entry; do
not swap live wires or reprint the link. Only after direction, limits,
disconnect handling, rate limits, and gripper deadman work in simulation should
you use `configs/yam_encoder_hw.yaml` with a physical follower.

## What remains to validate physically

- FDM bearing, axle, pot-body, and shaft fits on your printer.
- Axial pull-out strength of the snap axle. Its retaining face is inclined at
  about 35 degrees rather than square, nominal radial engagement at the bearing
  face is small, and a 6000-2RS inner race is chamfered. J1 hangs the arm from
  this feature in tension.
- Base stiffness. The pedestal reaches the J1 socket through the wedge behind
  J1's travel, which is the governing section of the whole machine.
- The Alibaba pot's connector contact and wire order on the Nano shield.
- Pot linearity, backlash, wear, and real electrical travel. Cheap WH148 carbon
  pots save substantial cost but are wear parts, not precision encoders.
- Flexure force and fatigue in your PETG brand and print orientation.
- Full cable motion and the controller tray clips with the exact boards shipped
  by marketplace sellers. Only the printed tray is modelled: the shield and the
  Nano plugged into it add roughly 20 mm that no geometry check covers.
- A conservative safe working load for the complete printed assembly. No such
  rating is claimed by this prototype.

CAD source, regeneration instructions, and automated geometry tests are in
[`simple_cad`](simple_cad/README.md).
