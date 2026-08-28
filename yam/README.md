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

| Item | Quantity | Notes |
| --- | ---: | --- |
| AS5600 encoder board plus diametric magnet | 7 | Use the magnet supplied with the encoder kit when possible. |
| 608 bearing | 7 | Standard 8 x 22 x 7 mm bearing. |
| TCA9548A I2C multiplexer | 1 | Seven of its eight channels are used. |
| ESP32 development board | 1 | Use the pin assignments in the [root wiring section](../README.md#wiring). |
| Normally-open momentary push button | 1 | Deadman switch between GPIO 23 and ground. |
| 7 x 9 cm perfboard | 1 | For the ESP32, mux, and cable connections. |
| 28 AWG flexible wire | About 5 m each of 4 colors | 3V3, ground, SDA, and SCL. |
| M3 x 10 mm screws | Buy 80 | The original six-axis build specifies 60; the extra cartridge and adapter flanges need more. |
| M3 x 16 mm screws | 4 | Clamps the two YAM adapter pieces together. |
| M3 nuts | 4 | For the four M3 x 16 mm clamp screws. |
| Rubber band | 1 | Counterbalances elbow droop. |
| USB data cable | 1 | Powers and programs the ESP32. |
| Solder and heat-shrink tubing | As needed | Insulate every joint and provide strain relief. |

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
