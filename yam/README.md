# YAM Encoder Leader

This variant adapts the passive AS5600 leader to the six-axis I2RT YAM arm.
Unlike the SO-ARM leader, which senses five arm joints and its jaw, the YAM
leader requires **seven sensed axes**: six arm joints plus one gripper input.

The project is currently an engineering prototype. Validate the complete
leader in simulation before connecting a physical follower.

## Electronics

The original ESP32, TCA9548A, and AS5600 circuit is retained with these
changes:

- Fit seven AS5600 boards, diametric magnets, and bearing-supported rotors.
- Connect joint 1 through joint 6 to mux channels 0 through 5.
- Connect the gripper encoder to mux channel 6.
- Connect a normally-open momentary deadman switch between ESP32 GPIO 23 and
  ground. The internal pull-up is enabled by the firmware.
- Leave mux channel 7 unused.

Flash `firmware/yam_encoder_leader/yam_encoder_leader.ino`. At 100 Hz it emits:

```text
YAM1,sequence,device_ms,count0,count1,count2,count3,count4,count5,count6,deadman
```

`deadman` is `1` only while the GPIO 23 switch is held. A missing encoder is
reported as `-1`; the host software treats that as a fault rather than sending
another follower command.

## Software

Use the `yam-encoder-leader` branch of `npow/gello_software`. Start with its
`configs/yam_encoder_sim.yaml` configuration. Hold the leader in the all-zero
YAM pose with the gripper open while the serial agent takes its first sample.

The default channel mapping is:

| Mux channel | YAM output |
| --- | --- |
| 0 | joint 1 / base yaw |
| 1 | joint 2 / shoulder |
| 2 | joint 3 / elbow |
| 3 | joint 4 / wrist pitch |
| 4 | joint 5 / wrist yaw |
| 5 | joint 6 / wrist roll |
| 6 | gripper |

Encoder direction is a software setting. Do not reprint a part solely to
reverse an axis.

## Complete bill of materials

The quantities below build **one complete YAM encoder leader**. They replace
the six-channel quantities in the repository's root README. The YAM leader has
seven sensed axes: six arm joints and the gripper.

### Electronics and mechanical hardware

Prices were checked in USD on **August 28, 2026** and exclude shipping and
tax. Marketplace prices and selected variants change frequently, so verify the
cart total before ordering. Combining the budget items into one marketplace
order is usually cheaper than paying separate shipping charges.

| Item | Quantity to order | Lowest-priced source found | Faster/reputable alternative | Compatibility notes |
| --- | ---: | --- | --- | --- |
| AS5600 encoder board plus diametric magnet | 7 | [AliExpress, about $1.70 each](https://www.aliexpress.us/item/1005008123249732.html) | [Amazon AS5600 module](https://www.amazon.com/dp/B094F8H591) | **Buy the generic 23 x 23 mm module with an included diametric magnet.** Adafruit and Grove boards do not fit the current housing without a CAD change. |
| 608-2RS bearing, 8 x 22 x 7 mm | 7 | [Value Hobby, 10 pack about $4 when stocked](https://valuehobby.com/608-2rs-10pcs.html) | [DigiKey, $1.24 each with quantity discounts](https://www.digikey.com/en/products/detail/mechatronics-bearing-group/608-2RS-W-CHEVRONSRI2/9608369) | A 10 pack provides three useful spares. 608-ZZ also fits, but 2RS seals handle dust better. |
| TCA9548A I2C multiplexer | 1 | [AliExpress, about $0.46](https://www.aliexpress.us/item/1005012625811097.html) | [Adafruit, $6.95](https://www.adafruit.com/product/2717) | Must expose all eight mux channels; seven are used. |
| ESP32 development board | 1 | [AliExpress ESP32-DevKitC, about $4](https://www.aliexpress.us/item/1005006825457876.html) | [Amazon HiLetgo ESP-WROOM-32](https://www.amazon.com/dp/B0718T232Z) | Use the classic ESP32-WROOM-32/DevKitC family with GPIO 18, 19, and 23 exposed. |
| Normally-open momentary push button | 1 | [Tayda 12 mm panel button, $0.22](https://www.taydaelectronics.com/push-button-switch-momentary-spst-3a-250vac-12mm-green.html) | [Adafruit 16 mm panel button, $0.95](https://www.adafruit.com/product/1505) | It must be normally open and comfortable to hold continuously as a deadman switch. |
| 7 x 9 cm perfboard | 1 | [ElectroDragon, five-board pack from about $1](https://www.electrodragon.com/product/prototype-board-5cm-x-7cm-holes-copper-solder-pads/) | [Elliott Electronic Supply](https://www.elliottelectronicsupply.com/64-8911.html) | Select **7 x 9 cm**, 2.54 mm pitch. A slightly smaller board is usable if the ESP32 and mux fit. |
| 28 AWG flexible silicone wire | About 5 m each of 4 colors | [AliExpress five-color wire, from about $3](https://www.aliexpress.us/item/1005011988351450.html) | [Adafruit flexible ribbon cable](https://www.adafruit.com/product/3891) | Select **28 AWG and 5 m per color**; the displayed base price may be for a shorter option. |
| M3 x 10 mm socket-head screws | 80 required; buy 100 | [Bolt Depot 100 pack, $4.27](https://boltdepot.com/Product-Details?product=6380) | [McMaster-Carr 100 pack, part 91502A104](https://www.mcmaster.com/91502A104) | Select M3 x 0.5 x 10 mm. The extra 20 cover dropped or stripped screws. |
| M3 x 16 mm socket-head screws | 4 | [Bolt Depot, $0.12 each](https://boltdepot.com/Product-Details?product=13638) | [McMaster-Carr 100 pack, part 91502A107](https://www.mcmaster.com/91502A107) | M3 x 0.5 x 16 mm; these clamp the two YAM adapter pieces. |
| M3 x 0.5 hex nuts | 4 | [Bolt Depot, $0.05 each](https://boltdepot.com/Product-Details?product=4783) | [McMaster-Carr 100 pack, part 90592A085](https://www.mcmaster.com/90592A085) | Standard 5.5 mm-across-flats DIN 934 nuts. |
| PLA or PETG filament | 1 kg | [SUNLU PLA, from $10.29](https://store.sunlu.com/collections/fdm-3d-printing) | [Elegoo PLA, $13.99](https://us.elegoo.com/products/pla-filament-1-75mm-colored-1kg) | The complete meshes contain about 752 g of plastic even at 100% infill, so one 1 kg spool is sufficient at the recommended infill. |
| Rubber band | 1 | Reuse a medium household rubber band | Buy locally | Counterbalances elbow droop; exact tension is selected during assembly. |
| USB data cable | 1 | Reuse a known data-capable cable | [Adafruit USB-A to Micro-B, $4.95](https://www.adafruit.com/product/2185) | Match the connector on the ESP32 board and avoid charge-only cables. |
| Solder | About 25 g | Reuse existing electronics solder | [Adafruit 50 g lead-free solder, $12.50](https://www.adafruit.com/product/2473) | Rosin-core electronics solder; do not use plumbing solder or acid flux. |
| Heat-shrink tubing | About 1 m mixed sizes | [Harbor Freight 120-piece set, $4.99](https://go.harborfreight.com/sku/67530/) | [Adafruit heat-shrink pack, $4.95](https://www.adafruit.com/product/344) | Use on every soldered wire joint and at moving-joint strain-relief points. |

Using the lowest observed item prices, expect roughly **$45 to $60 before shipping,
tax, and printing-service charges** if a USB cable and soldering tools are
already available. Ordering everything from fast-shipping US distributors is
typically closer to $85 to $120. The ranges are estimates rather than quoted
cart totals because shipping, coupons, and marketplace variants change by
location.

No Dynamixel servos, U2D2, servo power supply, or Dynamixel frames are needed.
Those items belong to the active/passive servo GELLO in `gello_mechanical`, not
this AS5600 encoder build.

## Complete print list

Print the quantities in this table for one leader. The links point directly to
every required STL in this branch. The result is **21 unique files and 53
printed pieces**.

> Do not print only the two files under `yam/cad/generated/stl`; those are the
> YAM-specific additions. The inherited parts under `cad_files/stl` make up the
> rest of the arm. You can [download the entire branch as a
> ZIP](https://github.com/npow/open-source-leader-arm/archive/refs/heads/yam-encoder-leader.zip).

| Subassembly | STL | Quantity |
| --- | --- | ---: |
| Base | [`base.stl`](../cad_files/stl/base.stl) | 1 |
| Base | [`base_connector.stl`](../cad_files/stl/base_connector.stl) | 1 |
| Every sensed axis | [`bearing_housing.stl`](../cad_files/stl/bearing_housing.stl) | 7 |
| Every sensed axis | [`encoder_housing.stl`](../cad_files/stl/encoder_housing.stl) | 7 |
| Every sensed axis | [`encoder_cap.stl`](../cad_files/stl/encoder_cap.stl) | 7 |
| Every sensed axis | [`rotor.stl`](../cad_files/stl/rotor.stl) | 7 |
| Gripper | [`handle_base.stl`](../cad_files/stl/handle_base.stl) | 1 |
| Gripper | [`handle_body.stl`](../cad_files/stl/handle_body.stl) | 1 |
| Arm link | [`link_shoulder_to_elbow.stl`](../cad_files/stl/link_shoulder_to_elbow.stl) | 1 |
| Arm link | [`link_elbow_to_shoulder.stl`](../cad_files/stl/link_elbow_to_shoulder.stl) | 1 |
| Wrist | [`link_perpendicular_base.stl`](../cad_files/stl/link_perpendicular_base.stl) | 1 |
| Wrist | [`link_perpendicular_body.stl`](../cad_files/stl/link_perpendicular_body.stl) | 1 |
| Wrist | [`link_tooltip.stl`](../cad_files/stl/link_tooltip.stl) | 1 |
| Joint spacers | [`washer_round.stl`](../cad_files/stl/washer_round.stl) | 4 |
| Joint spacers | [`washer_perpendicular_link.stl`](../cad_files/stl/washer_perpendicular_link.stl) | 2 |
| Cable routing | [`wire_holder.stl`](../cad_files/stl/wire_holder.stl) | 5 |
| Counterbalance | [`rubberband_housing.stl`](../cad_files/stl/rubberband_housing.stl) | 1 |
| Rest fixture | [`rest_pose_holder_base.stl`](../cad_files/stl/rest_pose_holder_base.stl) | 1 |
| Rest fixture | [`rest_pose_holder_body.stl`](../cad_files/stl/rest_pose_holder_body.stl) | 1 |
| Added YAM joint | [`yam_wrist_axis_base.stl`](cad/generated/stl/yam_wrist_axis_base.stl) | 1 |
| Added YAM joint | [`yam_wrist_axis_upright.stl`](cad/generated/stl/yam_wrist_axis_upright.stl) | 1 |

The first 19 unique files reconstruct the original project's documented
47-piece arm. The extra encoder cartridge adds four pieces and the YAM wrist
adapter adds two, giving 53 pieces total. The rest fixture is included in that
total because it makes calibration repeatable.

### Print settings

- PLA or PETG, 0.2 mm layers, and no supports.
- Use at least three walls and 15% infill for the inherited parts.
- Use four walls and at least 25% infill for both YAM wrist adapter parts.
- The STLs are print-oriented. If a slicer imports one at an odd angle, place
  its broad flat face on the bed.
- Print the two adapter parts and one encoder cartridge first. Complete the fit
  checks in [`cad/README.md`](cad/README.md) before printing the remaining set.

## Mechanical assembly order

1. Build seven identical sensor cartridges. Each uses one AS5600, magnet, 608
   bearing, `encoder_housing`, `encoder_cap`, `bearing_housing`, and `rotor`.
2. Assemble the inherited base and arm chain through wrist pitch using the
   linked base, arm-link, spacer, and cable-holder parts.
3. Bolt `yam_wrist_axis_base` to the original wrist output. Slide
   `yam_wrist_axis_upright` into its sockets and secure it with four M3 x 16 mm
   screws and nuts.
4. Install cartridge 6 on the upright to create YAM joint 6. Attach the encoded
   handle after it; the handle's cartridge is the gripper input.
5. Install the rubber-band counterbalance and the two-piece rest fixture.
6. Route mux channels 0 through 5 to joints 1 through 6, and channel 6 to the
   gripper. Leave channel 7 unused.
7. Flash the firmware, check that all seven startup diagnostics report a valid
   magnet, and calibrate with the arm in the rest fixture before enabling a
   follower.

The adapter remains an initial fit-test design. Verify screw fit, cartridge
alignment, cable clearance, and full joint motion on the first test print.
