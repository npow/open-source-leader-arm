"""Render README assembly guides directly from the parametric CAD.

The purchased bearing, potentiometer, shield, and Nano are deliberately simple
dimensioned stand-ins.  Every printed part comes from ``build_simple_leader`` so
the diagrams cannot quietly drift to a generic robot-arm shape.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

import cadquery as cq
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from build_simple_leader import (
    CONTROLLER_TRAY_CENTER,
    JOINTS,
    NANO_SHIELD_BOARD_THICKNESS,
    NANO_SHIELD_LONG,
    NANO_SHIELD_SHORT,
    PART_ORDER,
    POT_BODY_DIAMETER,
    POT_BODY_FRONT_X,
    POT_BODY_THICKNESS,
    POT_BUSHING_DIAMETER,
    POT_SHAFT_DIAMETER,
    POT_SHAFT_PROJECTION,
    _v_add,
    build_base,
    build_parts,
    build_plug,
    build_socket,
)
from matplotlib.patches import Circle, FancyBboxPatch, Patch, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

PRINT_COLORS = (
    "#2563eb",
    "#f59e0b",
    "#10b981",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
    "#f97316",
    "#ec4899",
)
PART_LABELS = (
    "1  base + fixed controller tray",
    "2  link 1",
    "3  link 2",
    "4  link 3",
    "5  link 4",
    "6  link 5",
    "7  link 6 + fixed grip",
    "8  gripper lever",
)
GRAY = "#9ca3af"
BLUE = "#2563eb"
STEEL = "#cbd5e1"
RED = "#dc2626"
BLACK = "#111827"


def _mesh(
    shape: cq.Workplane, tolerance: float = 0.55
) -> tuple[np.ndarray, np.ndarray]:
    vertices, triangles = shape.val().tessellate(tolerance)
    return (
        np.asarray([vertex.toTuple() for vertex in vertices]),
        np.asarray(triangles),
    )


def _add_shape(
    axis,
    shape: cq.Workplane,
    color: str,
    *,
    alpha: float = 1.0,
    edge: str = "#273244",
    linewidth: float = 0.10,
) -> np.ndarray:
    vertices, triangles = _mesh(shape)
    axis.add_collection3d(
        Poly3DCollection(
            vertices[triangles],
            facecolor=color,
            edgecolor=edge,
            linewidth=linewidth,
            alpha=alpha,
        )
    )
    return vertices


def _finish_3d(
    axis,
    vertices: Iterable[np.ndarray],
    *,
    elev: float,
    azim: float,
    zoom: float = 1.0,
) -> None:
    points = np.vstack(tuple(vertices))
    minimum = points.min(axis=0)
    maximum = points.max(axis=0)
    padding = np.maximum((maximum - minimum) * 0.08, (4.0, 4.0, 4.0))
    minimum -= padding
    maximum += padding
    axis.set_xlim(minimum[0], maximum[0])
    axis.set_ylim(minimum[1], maximum[1])
    axis.set_zlim(minimum[2], maximum[2])
    axis.set_box_aspect(maximum - minimum, zoom=zoom)
    axis.view_init(elev=elev, azim=azim)
    axis.set_axis_off()
    axis.set_facecolor("white")


def _ring_x(outer_radius: float, inner_radius: float, width: float) -> cq.Workplane:
    return cq.Workplane("YZ").circle(outer_radius).circle(inner_radius).extrude(width)


def _cylinder_x(radius: float, length: float, start: float) -> cq.Workplane:
    return cq.Workplane("YZ", origin=(start, 0.0, 0.0)).circle(radius).extrude(length)


def _potentiometer() -> cq.Workplane:
    body = _cylinder_x(POT_BODY_DIAMETER / 2.0, POT_BODY_THICKNESS, POT_BODY_FRONT_X)
    bushing = _cylinder_x(POT_BUSHING_DIAMETER / 2.0, 3.0, POT_BODY_FRONT_X - 3.0)
    shaft = _cylinder_x(
        POT_SHAFT_DIAMETER / 2.0,
        POT_SHAFT_PROJECTION,
        POT_BODY_FRONT_X - POT_SHAFT_PROJECTION,
    )
    return body.union(bushing).union(shaft)


def render_part_order(output_path: Path) -> None:
    parts = build_parts()
    figure = plt.figure(figsize=(9.0, 12.0), dpi=180, facecolor="white")
    grid = figure.add_gridspec(1, 2, width_ratios=(3.6, 1.5), wspace=0.02)
    axis = figure.add_subplot(grid[0, 0], projection="3d", proj_type="ortho")
    vertices = []
    for index, name in enumerate(PART_ORDER):
        vertices.append(_add_shape(axis, parts[name], PRINT_COLORS[index]))
    _finish_3d(axis, vertices, elev=8, azim=-78, zoom=1.42)

    legend_axis = figure.add_subplot(grid[0, 1])
    legend_axis.axis("off")
    legend_axis.legend(
        [Patch(facecolor=color, edgecolor="#273244") for color in PRINT_COLORS],
        PART_LABELS,
        loc="center left",
        frameon=False,
        fontsize=12,
        labelspacing=1.15,
        handlelength=1.5,
        handleheight=1.2,
    )
    figure.suptitle(
        "Printed-part order — actual assembled CAD", fontsize=19, weight="bold"
    )
    figure.text(
        0.5,
        0.02,
        "Build upward in order 1 → 8. Each color is one STL and one "
        "connected printed part.",
        ha="center",
        fontsize=11,
        color="#374151",
    )
    figure.savefig(output_path, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def _joint_panel(axis, step: int) -> None:
    socket = build_socket()
    bearing = _ring_x(13.0, 5.0, 8.0)
    plug = build_plug()
    pot = _potentiometer()
    vertices: list[np.ndarray] = []

    if step == 1:
        moved_bearing = bearing.translate((-22.0, 0.0, 0.0))
        vertices.append(_add_shape(axis, socket, GRAY, alpha=0.75))
        vertices.append(_add_shape(axis, moved_bearing, STEEL))
        axis.quiver(
            -12, -18, 0, 11, 0, 0, color=BLUE, linewidth=3, arrow_length_ratio=0.25
        )
        title = "1  Press bearing into the open side"
    elif step == 2:
        moved_plug = plug.translate((-34.0, 0.0, 0.0))
        vertices.append(_add_shape(axis, socket, GRAY, alpha=0.55))
        vertices.append(_add_shape(axis, bearing, STEEL))
        vertices.append(_add_shape(axis, moved_plug, BLUE))
        axis.quiver(
            -18, -20, 0, 17, 0, 0, color=BLUE, linewidth=3, arrow_length_ratio=0.22
        )
        title = "2  Push the child axle through until both tabs click"
    else:
        lifted_pot = pot.translate((0.0, 0.0, 28.0))
        vertices.append(_add_shape(axis, socket, GRAY, alpha=0.38))
        vertices.append(_add_shape(axis, bearing, STEEL, alpha=0.75))
        vertices.append(_add_shape(axis, plug, BLUE, alpha=0.90))
        vertices.append(_add_shape(axis, pot, "#92400e", alpha=0.16, edge="#92400e"))
        vertices.append(_add_shape(axis, lifted_pot, "#92400e"))
        axis.quiver(
            28, -19, 24, 0, 0, -20, color=BLUE, linewidth=3, arrow_length_ratio=0.22
        )
        axis.quiver(
            19, -19, 28, -9, 0, 0, color=BLUE, linewidth=3, arrow_length_ratio=0.28
        )
        title = "3  Insert the shaft, then lower the pot into its cradle"

    _finish_3d(axis, vertices, elev=17, azim=-72)
    axis.set_title(title, fontsize=12, weight="bold", pad=10)


def render_joint_sequence(output_path: Path) -> None:
    figure = plt.figure(figsize=(15.0, 5.4), dpi=180, facecolor="white")
    for step in (1, 2, 3):
        axis = figure.add_subplot(1, 3, step, projection="3d", proj_type="ortho")
        _joint_panel(axis, step)
    figure.suptitle(
        "One joint: bearing → snap axle → potentiometer",
        fontsize=18,
        weight="bold",
        y=0.99,
    )
    figure.text(
        0.5,
        0.015,
        "The nut, washer, and knob are not used. Repeat for J1 through J7.",
        ha="center",
        fontsize=11,
        color="#374151",
    )
    figure.tight_layout(rect=(0.0, 0.04, 1.0, 0.94), w_pad=0.4)
    figure.savefig(output_path, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def _board(center_z: float) -> tuple[cq.Workplane, Sequence[cq.Workplane]]:
    center_x, center_y, _ = CONTROLLER_TRAY_CENTER
    board = (
        cq.Workplane("XY")
        .box(NANO_SHIELD_LONG, NANO_SHIELD_SHORT, NANO_SHIELD_BOARD_THICKNESS)
        .translate((center_x, center_y, center_z))
    )
    sockets = tuple(
        cq.Workplane("XY")
        .box(39.0, 2.4, 3.2)
        .translate((center_x, center_y + y, center_z + 2.4))
        for y in (-8.0, 8.0)
    )
    return board, sockets


def _nano(center_z: float) -> cq.Workplane:
    center_x, center_y, _ = CONTROLLER_TRAY_CENTER
    return (
        cq.Workplane("XY")
        .box(45.0, 18.0, 1.6)
        .translate((center_x, center_y, center_z))
    )


def _controller_panel(axis, step: int) -> None:
    base = build_base()
    final_z = CONTROLLER_TRAY_CENTER[2]
    final_board, final_sockets = _board(final_z)
    vertices = [_add_shape(axis, base, GRAY)]
    if step == 1:
        moved_board, moved_sockets = _board(final_z + 38.0)
        vertices.append(_add_shape(axis, moved_board, RED))
        for socket in moved_sockets:
            vertices.append(_add_shape(axis, socket, BLACK))
        axis.quiver(
            CONTROLLER_TRAY_CENTER[0],
            CONTROLLER_TRAY_CENTER[1],
            final_z + 31.0,
            0,
            0,
            -24,
            color=BLUE,
            linewidth=3,
            arrow_length_ratio=0.22,
        )
        title = "1  Press the shield down into the four base clips"
    else:
        vertices.append(_add_shape(axis, final_board, RED))
        for socket in final_sockets:
            vertices.append(_add_shape(axis, socket, BLACK))
        moved_nano = _nano(final_z + 33.0)
        vertices.append(_add_shape(axis, moved_nano, BLUE))
        axis.quiver(
            CONTROLLER_TRAY_CENTER[0],
            CONTROLLER_TRAY_CENTER[1],
            final_z + 28.0,
            0,
            0,
            -21,
            color=BLUE,
            linewidth=3,
            arrow_length_ratio=0.24,
        )
        title = "2  Align both Nano rows, then press straight into the sockets"
    _finish_3d(axis, vertices, elev=30, azim=-52, zoom=1.18)
    axis.set_title(title, fontsize=12, weight="bold", pad=10)


def render_controller_sequence(output_path: Path) -> None:
    figure = plt.figure(figsize=(12.0, 6.0), dpi=180, facecolor="white")
    for step in (1, 2):
        axis = figure.add_subplot(1, 2, step, projection="3d", proj_type="ortho")
        _controller_panel(axis, step)
    figure.suptitle(
        "Controller installation on the fixed base", fontsize=18, weight="bold"
    )
    figure.text(
        0.5,
        0.015,
        "The red and blue boards are dimensioned stand-ins; the gray base "
        "and tray are the actual CAD.",
        ha="center",
        fontsize=10.5,
        color="#374151",
    )
    figure.tight_layout(rect=(0.0, 0.04, 1.0, 0.93), w_pad=0.4)
    figure.savefig(output_path, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def _posed_parts(
    parts: Sequence[cq.Workplane], angles: dict[str, float]
) -> list[cq.Workplane]:
    posed = []
    for index, part in enumerate(parts):
        moved = part
        for joint_index in range(index, 0, -1):
            angle = angles.get(f"j{joint_index}", 0.0)
            if angle:
                center, axis = JOINTS[f"j{joint_index}"]
                moved = moved.rotate(center, _v_add(center, axis), angle)
        posed.append(moved)
    return posed


def render_fold_check(output_path: Path) -> None:
    parts_by_name = build_parts()
    parts = [parts_by_name[name] for name in PART_ORDER]
    folded = {
        "j2": -105.0,
        "j3": 105.0,
        "j4": -90.0,
        "j5": -90.0,
        "j6": -120.0,
        "j7": 45.0,
    }
    poses = (("Neutral", parts), ("Compact folded pose", _posed_parts(parts, folded)))
    figure = plt.figure(figsize=(12.0, 7.2), dpi=180, facecolor="white")
    for panel, (title, posed) in enumerate(poses, start=1):
        axis = figure.add_subplot(1, 2, panel, projection="3d", proj_type="ortho")
        vertices = [
            _add_shape(axis, part, PRINT_COLORS[index])
            for index, part in enumerate(posed)
        ]
        board, sockets = _board(CONTROLLER_TRAY_CENTER[2])
        vertices.append(_add_shape(axis, board, RED))
        for socket in sockets:
            vertices.append(_add_shape(axis, socket, BLACK))
        vertices.append(_add_shape(axis, _nano(CONTROLLER_TRAY_CENTER[2] + 7.0), BLUE))
        _finish_3d(axis, vertices, elev=8, azim=-74, zoom=1.30)
        axis.set_title(title, fontsize=14, weight="bold", pad=10)
    figure.suptitle(
        "The controller stays on the base while the arm folds",
        fontsize=18,
        weight="bold",
    )
    figure.text(
        0.5,
        0.015,
        "Fold shown at J2 −105°, J3 +105°, J4 −90°, J5 −90°, J6 −120°, gripper closed.",
        ha="center",
        fontsize=10.5,
        color="#374151",
    )
    figure.tight_layout(rect=(0.0, 0.04, 1.0, 0.93), w_pad=0.3)
    figure.savefig(output_path, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def render_wiring_guide(output_path: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(14.0, 6.4), dpi=180, facecolor="white")

    axis = axes[0]
    axis.set_xlim(0, 10)
    axis.set_ylim(0, 10)
    axis.set_aspect("equal")
    axis.axis("off")
    axis.set_title("One potentiometer", fontsize=16, weight="bold", pad=14)
    axis.add_patch(
        Circle((2.7, 6.8), 1.55, facecolor="#92400e", edgecolor=BLACK, linewidth=2)
    )
    axis.add_patch(
        Rectangle(
            (2.42, 8.1), 0.56, 1.0, facecolor=STEEL, edgecolor=BLACK, linewidth=1.5
        )
    )
    terminal_x = (1.7, 2.7, 3.7)
    terminal_labels = ("outer", "WIPER", "outer")
    for x, label in zip(terminal_x, terminal_labels):
        axis.add_patch(
            Rectangle((x - 0.12, 4.35), 0.24, 1.1, facecolor=STEEL, edgecolor=BLACK)
        )
        axis.text(
            x,
            4.0,
            label,
            ha="center",
            va="top",
            fontsize=10,
            weight="bold" if label == "WIPER" else None,
        )

    header_y = (7.2, 5.8, 4.4)
    header_labels = (("S", BLUE, "signal"), ("V", RED, "5 V"), ("G", BLACK, "ground"))
    axis.add_patch(
        FancyBboxPatch(
            (7.1, 3.7),
            1.8,
            4.3,
            boxstyle="round,pad=0.15",
            facecolor="#f3f4f6",
            edgecolor=BLACK,
        )
    )
    for y, (letter, color, meaning) in zip(header_y, header_labels):
        axis.add_patch(
            Circle((7.65, y), 0.22, facecolor=color, edgecolor=BLACK, linewidth=1)
        )
        axis.text(
            8.05, y, f"{letter}  {meaning}", va="center", fontsize=11, weight="bold"
        )

    routes = (
        ((2.7, 5.45), (7.4, 7.2), BLUE, 0.12),
        ((1.7, 5.45), (7.4, 5.8), RED, -0.08),
        ((3.7, 5.45), (7.4, 4.4), BLACK, -0.12),
    )
    for start, end, color, bend in routes:
        axis.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops={
                "arrowstyle": "->",
                "color": color,
                "linewidth": 2.6,
                "connectionstyle": f"arc3,rad={bend}",
            },
        )
    axis.text(
        5.0,
        1.55,
        "Find the center wiper with a multimeter.",
        ha="center",
        fontsize=11.5,
        weight="bold",
    )
    axis.text(
        5.0,
        0.85,
        "Either outer pin may be V or G; swapping them reverses direction.",
        ha="center",
        fontsize=10.5,
    )

    axis = axes[1]
    axis.set_xlim(0, 10)
    axis.set_ylim(0, 10)
    axis.axis("off")
    axis.set_title("Seven shield input rows", fontsize=16, weight="bold", pad=14)
    joints = (
        ("A0", "J1  base yaw"),
        ("A1", "J2  shoulder"),
        ("A2", "J3  elbow"),
        ("A3", "J4  wrist pitch"),
        ("A4", "J5  wrist yaw"),
        ("A5", "J6  wrist roll"),
        ("A6", "J7  gripper / deadman"),
    )
    for index, (analog, joint) in enumerate(joints):
        y = 8.6 - index * 1.05
        fill = "#f9fafb" if index % 2 == 0 else "#eef2ff"
        axis.add_patch(
            FancyBboxPatch(
                (0.6, y - 0.37),
                8.8,
                0.75,
                boxstyle="round,pad=0.05",
                facecolor=fill,
                edgecolor="#d1d5db",
            )
        )
        axis.text(1.0, y, analog, va="center", fontsize=11, weight="bold")
        for x, (letter, color, _) in zip((2.4, 3.25, 4.1), header_labels):
            axis.add_patch(
                Circle((x, y), 0.18, facecolor=color, edgecolor=BLACK, linewidth=0.8)
            )
            axis.text(
                x, y - 0.31, letter, ha="center", va="top", fontsize=7.5, weight="bold"
            )
        axis.text(4.75, y, joint, va="center", fontsize=11)
    axis.text(
        5.0,
        0.65,
        "Repeat S / V / G for every row. Power from Nano USB only.",
        ha="center",
        fontsize=11,
        weight="bold",
    )

    figure.suptitle(
        "Plug-in wiring — labels matter, wire colors do not",
        fontsize=19,
        weight="bold",
        y=0.99,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.94), w_pad=1.2)
    figure.savefig(output_path, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs" / "images",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    render_part_order(args.output_dir / "assembly-part-order.png")
    render_joint_sequence(args.output_dir / "assembly-joint-sequence.png")
    render_controller_sequence(args.output_dir / "assembly-controller-sequence.png")
    render_fold_check(args.output_dir / "assembly-folded-clearance.png")
    render_wiring_guide(args.output_dir / "wiring-one-leader.png")
    print(f"Rendered assembly guides to {args.output_dir}")


if __name__ == "__main__":
    main()
