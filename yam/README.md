# Simple no-solder YAM leader

This branch is the inexpensive version: seven factory-wired linear
potentiometers, seven bearings, a pre-soldered Arduino Nano, one plug-in I/O
shield, and eight printed structural pieces. There are no magnets, encoder
boards, muxes, cable kits, hex nuts, joint screws, or soldered connections.
The gripper's printed PETG leaf is both its return spring and the firmware
deadman input.

This is a generated and collision-checked **first-print prototype**, not a
physically qualified product. Print the joint coupon and verify the sourced
parts before printing the arm.

## Cost delivered to 94114

Prices and listed shipping were rechecked on **August 28, 2026**. The four
core lines below total **$44.98**, each currently shows **free US shipping**,
and the estimated San Francisco total is **$48.86** after
[8.625% sales tax](https://www.cdtfa.ca.gov/taxes-and-fees/rates.aspx).
That excludes filament and a USB cable if you do not already have them.

The estimate is deliberately a reproducible cart, not an optimistic sum of
unit prices from overseas marketplaces. Prices, stock, tax, and delivery dates
can change at checkout.

## Complete BOM

| Buy this exact type | Qty used | Package price | Shipping shown | Why this one |
| --- | ---: | ---: | ---: | --- |
| [Uxcell WH148 B10K linear pots, 20 cm factory wire, 3-pin JST-XH2.54, 10-pack](https://www.walmart.com/ip/17169514309) | 7 | $19.34 sale ($20.35 regular) | Free | Three spares; nominal 17 mm body, 7 mm bushing, 6 mm knurled shaft. Do not substitute switched 5-pin or logarithmic/audio-taper pots. |
| [6000-2RS sealed bearings, 10×26×8 mm, 10-pack](https://www.ebay.com/itm/301956681716) | 7 | $11.25 | Free | Three spares. The larger 10 mm bore leaves a printable load-bearing wall around the 6 mm pot coupling. **608 bearings do not fit this design.** |
| [Classic ATmega328P Nano, USB-C, headers already soldered](https://www.ebay.com/itm/205884861373) | 1 | $10.99 | Free | The listing must say **soldered**. A bare-header Nano defeats the no-solder goal. |
| [Nano I/O expansion sensor shield](https://www.ebay.com/itm/201247537349) | 1 | $3.40 | Free | Match the pictured 58×54 mm red Nano shield with servo-style signal/5V/ground header rows. The seller's title mentions UNO, but the pictured socket is for a Nano. |
| PETG filament | about 500 g | Existing spool, or local purchase | — | PETG is required for the axle snaps, pot clips, and gripper flexure. Do not use brittle silk PLA. |
| USB-C **data** cable | 1 | Reuse | — | Charge-only cables cannot upload firmware or stream positions. |
| #8 or 4 mm wood screws | 4 optional | Reuse/buy locally | — | Only for fastening the base to a board; they drive into wood, so no nuts are used. A table clamp also works. |

The bearing listing is the price choice, not the design limit.
[DigiKey's 6000-2RS data](https://www.digikey.com/en/products/detail/mechatronics-bearing-group/6000-2RS/9608370)
lists roughly 790 lbf dynamic and 440 lbf static bearing ratings.
The printed PETG, layer adhesion, snap axle, base, and desk attachment are much
weaker and remain unqualified. This leader is intended only for hand input; do
not hang a payload from it or infer a safe working load from the bearing rating.

### Connector check before ordering multiples

The pot listing calls its plug JST-XH2.54 while the shield uses ordinary
2.54 mm male headers. That unshrouded combination normally presses together,
but neither listing guarantees a keyed system-level mate. Buy the listed pack
only if you are comfortable checking one connector. The crimp contacts can be
reordered in their plastic housing with a small pick if the wire order differs;
that does not require cutting or soldering.

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
| [`joint_fit_test.stl`](simple_cad/generated/stl/joint_fit_test.stl) | 1 | 6000 bearing pocket, 9.8 mm snap axle, 6 mm split shaft socket, and WH148 body/bushing carrier. The socket and plug are two separate solids in one STL. |

The final arm is exactly these eight prints, one of each:

| Order | STL | Integral features |
| ---: | --- | --- |
| 1 | [`simple_base.stl`](simple_cad/generated/stl/simple_base.stl) | J1 bearing/pot socket and four optional mounting holes |
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
external servo supply. Route each 20 cm lead directly to the mid-arm tray with
a loose service loop. The CAD keeps every sensor within the included lead
length, but verify full motion before pressing cables into permanent clips or
tape.

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
- The exact Walmart pot's connector contact and wire order on the eBay shield.
- Pot linearity, backlash, wear, and real electrical travel. Cheap WH148 carbon
  pots save substantial cost but are wear parts, not precision encoders.
- Flexure force and fatigue in your PETG brand and print orientation.
- Full cable motion and the controller tray clips with the exact boards shipped
  by marketplace sellers.
- A conservative safe working load for the complete printed assembly. No such
  rating is claimed by this prototype.

CAD source, regeneration instructions, and automated geometry tests are in
[`simple_cad`](simple_cad/README.md).
