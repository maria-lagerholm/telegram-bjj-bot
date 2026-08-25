import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import specs as s
from drawing_helpers import dim_h, dim_v, leader

WALL_X = s.TOP_DEPTH
PLATE_THICKNESS = 30

NOTES = [
    "HÖJDKEDJA (mått från färdigt golv, sett från vänster sida)",
    f"  Tvättmaskinens topp                                     {s.MACHINE_HEIGHT}",
    f"  Luftspalt över maskinen                                + {s.MACHINE_CLEARANCE:<5}"
    f"= {s.ARM_UNDERSIDE} underkant konsolarm",
    f"  Konsolarmens profilhöjd (REF, mät på din konsol)        + {s.BRACKET_ARM_HEIGHT:<5}"
    f"= {s.TOP_UNDERSIDE} underkant skiva",
    f"  Skivans tjocklek                                        + {s.TOP_THICKNESS:<5g}"
    f"= {s.FINISHED_HEIGHT:g} FÄRDIG HÖJD",
    "",
    f"Färdig höjd {s.FINISHED_HEIGHT:g} mm är ovansidan av skivan, inte underkanten."
    " Standard bänkhöjd är 900 mm.",
    f"Tunnare skiva ger lägre höjd. Med {s.TOP_THICKNESS:g} mm skiva kan du komma ned till"
    f" {s.MACHINE_HEIGHT + 5 + s.BRACKET_ARM_HEIGHT + s.TOP_THICKNESS:g} mm",
    "genom att minska luftspalten till 5 mm, men behåll minst 5 mm så maskinen kan vibrera",
    "fritt och gå att dra ut. Lägre än så går inte, maskinens topp sitter på 850.",
    f"Konsolens överkant ligger i liv med skivans underkant. Konsolen är {s.BRACKET_TOTAL_HEIGHT} mm hög totalt,",
    f"därför hamnar väggfästena mellan cirka {s.BRACKET_BOTTOM:g} och {s.TOP_UNDERSIDE:g} mm över golvet.",
    "Alla infästningar i våtzon 1 och 2 ska tätas mot väggens tätskikt enligt Säker Vatteninstallation.",
    "Skivan skruvas underifrån i armarna med kort skruv och borrstopp, eller limmas med MS polymer.",
    "Borra aldrig igenom skivan ovanifrån.",
]


def draw_room(ax):
    ax.plot([-120, 760], [0, 0], lw=2.0, color="black")
    ax.plot([WALL_X, WALL_X], [0, 1000], lw=2.0, color="black")
    ax.text(WALL_X + 12, 960, "VÄGG", fontsize=9, color="#505050")
    ax.text(-110, 12, "FÄRDIGT GOLV", fontsize=9, color="#505050", va="bottom")


def draw_machine(ax):
    ax.add_patch(
        Rectangle(
            (s.MACHINE_FRONT_OFFSET, 0),
            s.MACHINE_DEPTH,
            s.MACHINE_HEIGHT,
            facecolor="#f5f5f5",
            edgecolor="#909090",
            lw=1.0,
            ls=(0, (6, 4)),
        )
    )
    ax.text(
        s.MACHINE_FRONT_OFFSET + s.MACHINE_DEPTH / 2,
        s.MACHINE_HEIGHT / 2,
        "TVÄTTMASKIN\nLG F2Y5PYP3W\n475 djup x 850 hög (REF)",
        ha="center",
        va="center",
        fontsize=9,
        color="#707070",
    )
    door_front = s.MACHINE_FRONT_OFFSET - s.MACHINE_DOOR_BULGE
    ax.plot(
        [door_front, door_front],
        [150, 700],
        lw=1.0,
        ls=(0, (3, 3)),
        color="#b0b0b0",
    )
    ax.text(
        door_front + 10,
        300,
        "lucka buktar 60",
        fontsize=8,
        color="#909090",
        rotation=90,
        ha="left",
        va="bottom",
    )


def draw_bracket(ax):
    ax.add_patch(
        Rectangle(
            (s.FRONT_OVERHANG, s.ARM_UNDERSIDE),
            s.BRACKET_DEPTH,
            s.BRACKET_ARM_HEIGHT,
            facecolor="#dbe6f0",
            edgecolor="#4a6f96",
            lw=1.2,
        )
    )
    ax.add_patch(
        Rectangle(
            (WALL_X - PLATE_THICKNESS, s.BRACKET_BOTTOM),
            PLATE_THICKNESS,
            s.TOP_UNDERSIDE - s.BRACKET_BOTTOM,
            facecolor="#dbe6f0",
            edgecolor="#4a6f96",
            lw=1.2,
        )
    )


def draw_top(ax):
    ax.add_patch(
        Rectangle(
            (0, s.TOP_UNDERSIDE),
            s.TOP_DEPTH,
            s.TOP_THICKNESS,
            facecolor="#e8e8e8",
            edgecolor="black",
            lw=2.2,
        )
    )


def draw_labels(ax):
    leader(
        ax,
        (250, s.TOP_UNDERSIDE + s.TOP_THICKNESS / 2),
        (-190, 980),
        f"BÄNKSKIVA {s.TOP_THICKNESS:g} mm {s.MATERIAL_NAME}",
    )
    leader(
        ax,
        (400, s.ARM_UNDERSIDE + s.BRACKET_ARM_HEIGHT / 2),
        (-190, 700),
        f"KONSOL SVEDBERGS 47920\narm {s.BRACKET_DEPTH} djup, {s.BRACKET_WIDTH} bred (REF)",
        color="#33608f",
    )
    ax.text(
        s.FRONT_OVERHANG / 2,
        s.TOP_UNDERSIDE - 55,
        "FRIHÄNG",
        ha="center",
        fontsize=9,
        color="#505050",
    )
    ax.text(-140, -75, "FRAMKANT", fontsize=9, color="#505050")


def draw_dimensions(ax):
    dim_v(ax, 0, s.MACHINE_HEIGHT, 460, f"{s.MACHINE_HEIGHT} (REF)")
    dim_v(ax, 0, s.FINISHED_HEIGHT, -60, f"{s.FINISHED_HEIGHT:g} FÄRDIG HÖJD", tick_to=0)

    dim_v(ax, s.BRACKET_BOTTOM, s.TOP_UNDERSIDE, 620, f"{s.BRACKET_TOTAL_HEIGHT} (REF)", tick_to=WALL_X)
    dim_v(ax, s.MACHINE_HEIGHT, s.ARM_UNDERSIDE, 670, f"{s.MACHINE_CLEARANCE} luft", tick_to=WALL_X)
    dim_v(ax, s.ARM_UNDERSIDE, s.TOP_UNDERSIDE, 720, f"{s.BRACKET_ARM_HEIGHT} arm", tick_to=WALL_X)
    dim_v(ax, s.TOP_UNDERSIDE, s.FINISHED_HEIGHT, 770, f"{s.TOP_THICKNESS:g} skiva", tick_to=WALL_X)

    dim_h(ax, 0, s.FRONT_OVERHANG, -80, f"{s.FRONT_OVERHANG}", tick_to=s.ARM_UNDERSIDE)
    dim_h(ax, s.FRONT_OVERHANG, WALL_X, -80, f"{s.BRACKET_DEPTH}", tick_to=s.ARM_UNDERSIDE)
    dim_h(ax, 0, WALL_X, -180, f"{s.TOP_DEPTH}", tick_to=-80)


def build_figure():
    fig = plt.figure(figsize=(11, 14))
    ax = fig.add_axes([0.06, 0.34, 0.88, 0.58])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-200, 860)
    ax.set_ylim(-230, 1010)

    draw_room(ax)
    draw_machine(ax)
    draw_bracket(ax)
    draw_top(ax)
    draw_labels(ax)
    draw_dimensions(ax)

    fig.text(
        0.05,
        0.965,
        "BÄNKSKIVA BADRUM  sektion A-A  höjder",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.05,
        0.947,
        "Vy från vänster sida. Alla mått i mm. Ritningen är ej skalenlig, använd måtten.",
        fontsize=10,
        color="#505050",
    )

    y = 0.30
    for line in NOTES:
        fig.text(0.05, y, line, fontsize=9.5, family="monospace")
        y = y - 0.0166

    return fig


def save_png(path):
    fig = build_figure()
    fig.savefig(path, dpi=200)
    plt.close(fig)
