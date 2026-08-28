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

## Mechanical prototype

The original five-axis arm chain remains unchanged through wrist pitch. Add a
standard encoder/bearing/rotor set for joint 6 using the two-piece adapter in
[`yam/cad`](cad/README.md), then attach the original encoded handle as the
seventh sensed axis. The additional printed and purchased quantities are:

| Item | Additional quantity |
| --- | ---: |
| AS5600 plus diametric magnet | 1 |
| 608 bearing | 1 |
| `encoder_housing` and `encoder_cap` | 1 each |
| `bearing_housing` and `rotor` | 1 each |
| `yam_wrist_axis_base` | 1 |
| `yam_wrist_axis_upright` | 1 |
| M3x16 clamp screws and nuts | 4 each |

The adapter is an initial fit-test design. Print and verify the adapter against
one cartridge before committing to the complete leader build.
