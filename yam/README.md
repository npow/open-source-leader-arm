# Simple YAM Encoder Leader

This is the low-cost, low-assembly YAM leader. It keeps seven inexpensive
AS5600 magnetic encoders, but removes the hand-wired perfboard and the repeated
four-piece encoder cartridges from the first prototype.

The complete arm is now:

- **8 final printed pieces**, down from 53;
- **no soldering**: every electrical connection is Qwiic/STEMMA QT;
- **no nuts, joint screws, washers, separate rotors, caps, or cable holders**;
- **no return spring or rubber band**; and
- about **$78 in purchased parts**, or about **$88 if a new PETG spool is
  needed**, before shipping and tax.

This remains first-print prototype hardware. Print and check the small joint
coupon before ordering seven of every component or printing the full arm.

## What changed mechanically

Every structural link now contains both sides of the repeated joint:

- the parent side has a press-fit 608 bearing pocket and a top-loading snap
  carrier sized for Adafruit AS5600 board 6357;
- the child side has the 8 mm axle, two compliant retention barbs, and a 4 x
  2 mm magnet pocket printed into the link; and
- the board slides into the only open end of its carrier and clicks under two
  printed latches. Both Qwiic sockets remain exposed.

The axle barbs compress through the bearing and expand behind it, replacing a
screw, nut, washer, and retaining clip. The link proportions are compact rather
than 1:1 with the follower; teleoperation maps measured joint angles, so link
length does not change the commanded YAM joint angles.

## Complete print list

Download the whole branch as a [ZIP](https://github.com/npow/open-source-leader-arm/archive/refs/heads/yam-encoder-leader.zip),
then use the STLs under `yam/simple_cad/generated/stl`.

### Print this first (not part of the final arm)

| STL | Quantity | Purpose |
| --- | ---: | --- |
| [`joint_fit_test.stl`](simple_cad/generated/stl/joint_fit_test.stl) | 1 | Checks the bearing, axle snap, magnet, and AS5600 carrier fits with little filament. The STL contains a separate socket and plug. |

### Final arm: eight pieces total

| Order | STL | Quantity | Contains |
| ---: | --- | ---: | --- |
| 1 | [`simple_base.stl`](simple_cad/generated/stl/simple_base.stl) | 1 | J1 bearing/sensor socket and controller tray |
| 2 | [`simple_link_1.stl`](simple_cad/generated/stl/simple_link_1.stl) | 1 | J1 snap axle and J2 socket |
| 3 | [`simple_link_2.stl`](simple_cad/generated/stl/simple_link_2.stl) | 1 | J2 axle, J3 socket, and mid-arm Qwiic mux pad |
| 4 | [`simple_link_3.stl`](simple_cad/generated/stl/simple_link_3.stl) | 1 | J3 axle and J4 socket |
| 5 | [`simple_link_4.stl`](simple_cad/generated/stl/simple_link_4.stl) | 1 | J4 axle and J5 socket |
| 6 | [`simple_link_5.stl`](simple_cad/generated/stl/simple_link_5.stl) | 1 | J5 axle and J6 socket |
| 7 | [`simple_link_6.stl`](simple_cad/generated/stl/simple_link_6.stl) | 1 | J6 axle, gripper-input socket, and fixed palm grip |
| 8 | [`simple_gripper_lever.stl`](simple_cad/generated/stl/simple_gripper_lever.stl) | 1 | Gripper-input axle and squeeze lever |

Do **not** print the old files under `cad_files/stl` for this version. They are
retained only so the upstream SO-ARM design and the earlier YAM prototype remain
available.

### Print settings

- PETG is required for the integral axle barbs and PCB latches. PLA can crack
  when those features flex.
- 0.2 mm layers, four walls, five top/bottom layers, and 20-25% gyroid infill.
- The generated STLs put the proximal axle in its strongest practical print
  orientation. Enable organic/tree supports from the build plate where the
  slicer identifies an unsupported sensor carrier.
- Use 0.2 mm first-layer elephant-foot compensation if available; an enlarged
  axle base can make the first snap unnecessarily hard.
- One 1 kg spool is ample for the coupon and final arm.

## Complete no-solder BOM

Prices were checked in USD on **August 28, 2026** and exclude shipping and tax.
The low-price column minimizes line-item cost; the alternative can be cheaper
overall when it consolidates shipping. Check the exact variant in every cart.

| Item | Buy | Quantity | Observed price | Exact requirement |
| --- | --- | ---: | ---: | --- |
| Plug-in AS5600 sensor | [Adafruit 6357](https://www.adafruit.com/product/6357) | 7 | $5.95 each / $41.65 | Use this **25.4 x 17.78 mm** STEMMA-QT board. Generic 23 x 23 mm boards do not fit. No header soldering is used. |
| Qwiic 8-channel mux | [SparkFun BOB-16784](https://www.sparkfun.com/sparkfun-qwiic-mux-breakout-8-channel-tca9548a.html) | 1 | $6.95 | Must be the assembled revision with ten Qwiic sockets: main in/pass-through plus channels 0-7. |
| USB controller with Qwiic | [Adafruit QT Py ESP32-S2, product 5325](https://www.adafruit.com/product/5325) | 1 | $12.50 | Use the ESP32-S2 version with USB-C, STEMMA QT, and the GPIO 0 BOOT button. |
| Qwiic cable, 100 mm | [Adafruit cable 4399, select 100 mm](https://www.adafruit.com/product/4399) | 2 | $0.95 each / $1.90 | Mux to J2 and J3. JST-SH 4-pin at both ends. |
| Qwiic cable, 200 mm | [Adafruit cable 4399, select 200 mm](https://www.adafruit.com/product/4399) | 1 | $1.25 | Mux to J1. |
| Qwiic cable, 300 mm | [Adafruit cable 4399, select 300 mm](https://www.adafruit.com/product/4399) | 3 | $1.25 each / $3.75 | Controller to mux, then mux to J4 and J5. |
| Qwiic cable, 400 mm | [Adafruit cable 4399, select 400 mm](https://www.adafruit.com/product/4399) | 2 | $1.50 each / $3.00 | Mux to J6 and gripper input. |
| 608-2RS bearing, 8 x 22 x 7 mm | [Value Hobby 10-pack](https://valuehobby.com/608-2rs-10pcs.html) | 1 pack | $4.00 | Seven are used; three are spares. [DigiKey singles](https://www.digikey.com/en/products/detail/mechatronics-bearing-group/608-2RS-W-CHEVRONSRI2/9608369) were $1.24 each if the budget pack is unavailable. |
| Diametric magnet, 4 x 2 mm | [MagnetDD MD2685](https://www.magnetdd.com/index.php?main_page=product_info&products_id=2715) | 10 | 7.25 THB each; about $2.25 for 10 before shipping | It must be **diametrically**, not axially, magnetized. A US-stock bulk alternative is the [BuyNeoMagnets 100-pack](https://www.buyneomagnets.com/p/4mm-x-2mm-diametrically-magnetized-disc-magnet-neodymium-round-magnets-n35-rare-earth-radial-magnets-100-pack/) at $14.59. |
| PETG filament | [SUNLU PETG](https://store.sunlu.com/collections/fdm-3d-printing) or an existing spool | 1 kg | about $10-15 | PETG is important for the printed snap tabs. |
| Thin removable foam mounting tape | Reuse or buy locally | about 100 mm | about $2 | Attaches the QT Py to the base tray and mux to the link-2 pad. No standoffs or nuts. |
| USB-C data cable | Reuse a known data cable | 1 | $0 | Charge-only cables will not work. |
| #8 or 4 mm wood screws | Buy locally; optional | 4 | about $1 | Only needed to fasten the base to a scrap board. They drive into the board directly; no nuts are used. A table clamp also works. |

The listed core electronics, cables, bearings, and budget magnets total about
**$78**. Add roughly **$10** if a PETG spool must be purchased. The original
soldered version could be built for $45-60, so the roughly $20-30 difference is
the cost of factory-assembled sensor boards and terminated cables—not expensive
Dynamixel servos. It remains far below a roughly $300 servo GELLO build.

## Tool-free wiring

The AS5600 has a fixed I2C address, so seven of them cannot share one literal
daisy chain. BOB-16784 gives each sensor an isolated plug-in branch; assembly is
still just clicking pre-terminated cables into labeled sockets.

1. Put the QT Py in the base tray with its USB-C and GPIO 0 buttons accessible.
2. Put the mux on the flat pad on `simple_link_2`.
3. Connect QT Py STEMMA QT to either mux **Main** socket with the 300 mm cable.
4. Connect mux channels 0-6 to the matching joints below. Leave channel 7 open.

| Mux channel | Input | Suggested cable |
| ---: | --- | ---: |
| 0 | J1 / base yaw | 200 mm |
| 1 | J2 / shoulder | 100 mm |
| 2 | J3 / elbow | 100 mm |
| 3 | J4 / wrist pitch | 300 mm |
| 4 | J5 / wrist yaw | 300 mm |
| 5 | J6 / wrist roll | 400 mm |
| 6 | gripper squeeze | 400 mm |

Route each cable with a loose service loop at moving joints. Do not pull a cable
tight across a rotation axis. Small pieces of painter's tape are adequate for
the first bench test; add permanent printed cable clips only after the motion
test confirms where they are needed.

## Mechanical assembly

1. Print `joint_fit_test`. Confirm a bearing seats fully, the axle turns without
   binding, both barbs click behind the bearing, a magnet sits flush in the
   4.15 mm pocket, and an Adafruit 6357 board slides down the carrier and
   latches. Adjust the constants at the top of
   [`build_simple_leader.py`](simple_cad/build_simple_leader.py) for the printer
   if any fit is wrong, then regenerate.
2. Print the eight final parts. Clean supports and elephant foot from every
   bearing pocket and axle, but do not sand the flexible barbs thin.
3. Press one 4 x 2 mm diametric magnet into every moving axle: links 1-6 and the
   gripper lever. The flat magnet face must finish flush with the axle tip.
4. Press one 608 bearing fully into every stationary socket: the base and links
   1-6.
5. Starting at J1, align a moving axle with its parent bearing and press straight
   until both barbs click behind the inner race. Do not twist during insertion.
6. At each assembled joint, slide an AS5600 board into the carrier's open end,
   with the populated/chip side facing the magnet. Push until both top latches
   catch the board edge.
7. Attach the QT Py and mux with removable foam tape, plug in the eight cables,
   and verify that every joint rotates freely without tugging a connector.

Disassembly is possible but not intended to be frequent: remove the sensor
board, squeeze both axle barbs inward through the carrier window, and pull the
joint straight apart.

## Firmware and first test

Flash [`firmware/yam_encoder_leader/yam_encoder_leader.ino`](../firmware/yam_encoder_leader/yam_encoder_leader.ino)
with Arduino IDE using **Adafruit QT Py ESP32-S2** as the board. It uses the
board-default STEMMA-QT bus at 100 kHz and requires no additional Arduino
library.

The QT Py's built-in GPIO 0 / BOOT button is the prototype deadman input. Leave
it released while powering or flashing the board; after the serial stream has
started, hold it to enable follower commands. This preserves a no-solder build.

At boot, the serial monitor at 115200 baud should report `magnet ok` on channels
0-6. A missing sensor or bad magnet gap is reported as `-1` and the host refuses
to send another follower command.

Use the `yam-encoder-leader` branch of `npow/gello_software` and start in
simulation:

```bash
python experiments/launch_yaml.py \
  --left-config-path configs/yam_encoder_sim.yaml
```

Hold the leader in its reference pose with the gripper open during initial
calibration. Encoder direction and zero offsets are software settings; do not
reprint a link just to reverse an axis.

## Editable CAD and validation

STEP files, STLs, the parametric generator, and tests live in
[`simple_cad`](simple_cad/README.md). The automated checks require exactly eight
connected final solids, verify the purchased-component allowances, reject
adjacent-part interference, and sample the required motion window of all seven
axes.
