# Parametric simple leader CAD

`build_simple_leader.py` is the source of truth for the eight-piece YAM leader.
Dimensions are millimetres. Generated STEP and print-oriented STL files are in
`generated`.

## Generate and test

```bash
python -m venv .venv-cad
. .venv-cad/bin/activate
pip install -r yam/simple_cad/requirements.txt
python yam/simple_cad/build_simple_leader.py
PYTHONPATH=yam/simple_cad pytest -q yam/simple_cad/test_simple_leader.py
```

The tests check the eight-part manifest, solid validity, purchased-component
fit allowances, zero-pose interference, and sampled motion windows. They do not
replace a physical fit test: FDM hole and snap dimensions vary by printer,
material, layer direction, and cooling.

## Printer fit constants

Tune these values at the top of `build_simple_leader.py` only after printing
`generated/stl/joint_fit_test.stl`:

| Constant | Default | Meaning |
| --- | ---: | --- |
| `BEARING_POCKET_DIAMETER` | 22.20 | Modeled hole for a 22 mm 608 bearing |
| `BEARING_POCKET_DEPTH` | 7.15 | Modeled depth for a 7 mm bearing |
| `AXLE_DIAMETER` | 7.80 | Running fit in the 8 mm bearing bore |
| `MAGNET_POCKET_DIAMETER` | 4.15 | FDM-compensated fit for a 4 mm magnet |
| `PCB_EDGE_CLEARANCE` | 0.30 | Clearance on every AS5600 board edge |

Change one fit at a time, regenerate the coupon, and keep the purchased part
dimensions unchanged.

## Design limitations

This is a first-print prototype, not production-qualified hardware. The snap
tabs are intended for PETG and occasional disassembly. Check layer adhesion,
joint play, cable clearance, sensor gap, and the entire motion range in
simulation before connecting a physical YAM follower.
