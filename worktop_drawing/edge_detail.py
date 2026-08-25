from matplotlib.patches import Polygon, Rectangle

import specs as s
from drawing_helpers import dim_h, dim_v

CUT_EDGE_X = 120
RIM_X = CUT_EDGE_X - s.BASIN_RIM_OVERLAP


def draw_top_section(ax):
    ax.add_patch(
        Rectangle(
            (-60, -s.TOP_THICKNESS),
            CUT_EDGE_X + 60,
            s.TOP_THICKNESS,
            facecolor="#efe4d2",
            edgecolor="black",
            lw=1.4,
        )
    )
    ax.add_patch(
        Rectangle((-60, -2.5), CUT_EDGE_X + 60, 2.5, facecolor="#5a5a5a", edgecolor="none")
    )


def draw_basin_section(ax):
    ax.add_patch(
        Polygon(
            [
                (RIM_X, 3),
                (RIM_X, 16),
                (RIM_X + 30, 16),
                (150, -30),
                (185, -110),
                (210, -110),
                (168, -45),
                (126, 3),
            ],
            facecolor="white",
            edgecolor="black",
            lw=1.4,
        )
    )
    ax.add_patch(
        Polygon(
            [(RIM_X, 0), (CUT_EDGE_X, 0), (CUT_EDGE_X, 3), (RIM_X, 3)],
            facecolor="#c0392b",
            edgecolor="none",
        )
    )
    ax.text(150, 32, "TVÄTTSTÄLL", fontsize=8, ha="left", va="center")


def draw_detail(ax):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-150, 260)
    ax.set_ylim(-115, 90)

    draw_top_section(ax)
    draw_basin_section(ax)

    dim_v(ax, -s.TOP_THICKNESS, 0, -95, "28")
    dim_h(ax, RIM_X, CUT_EDGE_X, 40, "20", tick_to=16)

    ax.annotate(
        "keramikkanten\ntäcker 20 mm",
        xy=(RIM_X + 4, 16),
        xytext=(-145, 55),
        fontsize=8,
        arrowprops=dict(arrowstyle="-", lw=0.7),
    )
    ax.annotate(
        "silikon",
        xy=(RIM_X + 10, 2),
        xytext=(150, 52),
        fontsize=8,
        color="#c0392b",
        arrowprops=dict(arrowstyle="-", lw=0.7, color="#c0392b"),
    )
    ax.annotate(
        "skuren kant i spånskiva,\ntäta med lack eller silikon",
        xy=(CUT_EDGE_X, -16),
        xytext=(-70, -100),
        fontsize=8,
        arrowprops=dict(arrowstyle="-", lw=0.7),
    )
    ax.text(-150, 78, "SNITT GENOM URTAGETS KANT (1:1)", fontsize=9, fontweight="bold")
