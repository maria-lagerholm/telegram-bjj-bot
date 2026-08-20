import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

import specs as s
from drawing_helpers import cross, dim_h, dim_v, leader

MACHINE_LINE = 1.0

NOTES = [
    "MATERIAL: kompaktlaminat, tjocklek 12 mm (bekräftas vid order). Antal: 1 st. Alla mått i mm.",
    "Origo = främre vänstra hörnet. X åt höger, Y mot vägg. Tolerans ±1 mm. Ritningen är ej skalenlig, använd måtten.",
    "URTAG Ø350 för Villeroy & Boch Loop & Friends 4A590001, nedsänkt från ovansidan (keramik Ø390, innerkant Ø330,",
    "      höjd 190, avlopp Ø45). Keramikkanten vilar med 20 mm anliggning runt om. Kontrollera mot medföljande",
    "      schablon innan skärning. Godtagbart intervall 340 till 360 mm.",
    "HÅL Ø35 för Vesani Wilma BLWILMACH (tillverkaren anger 32 till 35 mm, blandarhuset Ø55 täcker hålet).",
    "      Blandaren står i högra bakre hörnet, 233 mm snett bakom tvättställets centrum. Pipen är 130 mm,",
    "      så vattnet hamnar väl inne i skålen. Cirka 10 mm mellan blandarhus och keramikkant.",
    "KONSOL: 3 st Svedbergs 47920, arm 403 mm djup, 30 till 40 mm bred, 303 mm hög, skruvas i väggen.",
    "      Centrum X 60, 655 och 1070 ger c/c 595 och 415 mm. Armarna går fria från skålen med minst 10 mm,",
    "      skålen är Ø350 under skivan. Skivan skruvas eller limmas mot armarna underifrån, inga hål ovanifrån.",
    "      Kontrollera att konsolernas väggfästen inte hamnar på rören bakom maskinen.",
    "      Armarnas underkant måste ligga minst 10 mm över maskinens topp (850), färdig höjd blir ca 890 mm.",
    "Tvättmaskin LG F2Y5PYP3W 600 x 475 x 850 mm visas som referens, ingen bearbetning.",
    "Skivan täcker maskinen med 50 mm överhäng på vänster sida. Skålen går fri från maskinen med 40 mm.",
    "Maskinen står 75 mm från vägg för rören. LG rekommenderar 100 mm, då sticker maskinen ut 25 mm framför skivan.",
    "Inget urtag för rör i bakkant. Lägg till om rörstammen sticker fram framför vägglinjen.",
    "Synliga kanter putsade med 1 mm fas.",
]

HOLE_TABLE = [
    "HÅLTABELL (centrum från främre vänstra hörnet)",
    "  Urtag tvättställ      X 865     Y 275     Ø 350",
    "  Hål blandare          X 1000    Y 465     Ø 35",
]


def draw_top(ax):
    ax.add_patch(
        Rectangle((0, 0), s.TOP_WIDTH, s.TOP_DEPTH, fill=False, lw=2.2, edgecolor="black")
    )


def draw_machine(ax):
    ax.add_patch(
        Rectangle(
            (s.MACHINE_LEFT_MARGIN, 0),
            s.MACHINE_WIDTH,
            s.MACHINE_DEPTH,
            facecolor="#f5f5f5",
            edgecolor="#909090",
            lw=MACHINE_LINE,
            ls=(0, (6, 4)),
        )
    )
    ax.text(
        s.MACHINE_LEFT_MARGIN + s.MACHINE_WIDTH / 2,
        s.MACHINE_DEPTH / 2 - 40,
        "TVÄTTMASKIN\nLG F2Y5PYP3W\n600 x 475 (REF)",
        ha="center",
        va="center",
        fontsize=9,
        color="#707070",
    )


def draw_brackets(ax):
    for x in s.BRACKET_CENTERS:
        ax.add_patch(
            Rectangle(
                (x - s.BRACKET_WIDTH / 2, s.TOP_DEPTH - s.BRACKET_DEPTH),
                s.BRACKET_WIDTH,
                s.BRACKET_DEPTH,
                facecolor="#dbe6f0",
                edgecolor="#4a6f96",
                lw=1.0,
                ls=(0, (5, 3)),
            )
        )


def draw_cutouts(ax):
    ax.add_patch(
        Circle(
            (s.BASIN_CENTER_X, s.BASIN_CENTER_Y),
            s.BASIN_CERAMIC_DIAMETER / 2,
            fill=False,
            lw=1.0,
            ls=(0, (6, 4)),
            edgecolor="#909090",
        )
    )
    ax.add_patch(
        Circle(
            (s.BASIN_CENTER_X, s.BASIN_CENTER_Y),
            s.BASIN_CUTOUT_DIAMETER / 2,
            facecolor="white",
            edgecolor="black",
            lw=2.2,
        )
    )
    ax.add_patch(
        Circle(
            (s.MIXER_CENTER_X, s.MIXER_CENTER_Y),
            s.MIXER_BODY_DIAMETER / 2,
            fill=False,
            lw=1.0,
            ls=(0, (6, 4)),
            edgecolor="#909090",
        )
    )
    ax.add_patch(
        Circle(
            (s.MIXER_CENTER_X, s.MIXER_CENTER_Y),
            s.MIXER_HOLE_DIAMETER / 2,
            facecolor="white",
            edgecolor="black",
            lw=2.2,
        )
    )
    ax.plot(
        [s.BASIN_CENTER_X, s.MIXER_CENTER_X],
        [s.BASIN_CENTER_Y, s.MIXER_CENTER_Y],
        lw=0.7,
        ls=(0, (4, 3)),
        color="#a0a0a0",
    )
    ax.text(915, 355, "233", fontsize=8, color="#707070", rotation=55, ha="center")
    cross(ax, s.BASIN_CENTER_X, s.BASIN_CENTER_Y, size=30, color="#909090")
    cross(ax, s.MIXER_CENTER_X, s.MIXER_CENTER_Y, size=40, color="#909090")


def draw_labels(ax):
    ax.text(
        s.BASIN_CENTER_X,
        s.BASIN_CENTER_Y - 80,
        "URTAG Ø350\nTVÄTTSTÄLL",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
    )
    leader(
        ax,
        (s.BASIN_CENTER_X - 138, s.BASIN_CENTER_Y + 138),
        (330, 690),
        "Keramik Ø390 (REF)",
        color="#707070",
    )
    leader(
        ax,
        (s.MIXER_CENTER_X + 20, s.MIXER_CENTER_Y + 12),
        (1150, 700),
        "HÅL Ø35\nBLANDARE",
    )
    leader(
        ax,
        (s.BRACKET_CENTERS[0], 200),
        (120, 60),
        "3 st KONSOL SVEDBERGS 47920\narm 403 djup, 40 bred (REF)",
        color="#33608f",
    )
    ax.text(
        s.TOP_WIDTH / 2,
        s.TOP_DEPTH + 18,
        "BAKKANT MOT VÄGG",
        ha="center",
        va="bottom",
        fontsize=9,
        color="#505050",
    )
    ax.text(
        s.TOP_WIDTH / 2,
        -22,
        "FRAMKANT",
        ha="center",
        va="top",
        fontsize=9,
        color="#505050",
    )
    ax.plot([0], [0], marker="o", ms=4, color="black")
    ax.text(-20, -30, "0,0", ha="right", va="top", fontsize=9)


def draw_dimensions(ax):
    b1, b2, b3 = s.BRACKET_CENTERS
    dim_h(ax, 0, b1, -70, "60", tick_to=0)
    dim_h(ax, b1, b2, -70, "595 c/c", tick_to=0)
    dim_h(ax, b2, b3, -70, "415 c/c", tick_to=0)
    dim_h(ax, b3, s.TOP_WIDTH, -70, "30", tick_to=0)

    machine_right = s.MACHINE_LEFT_MARGIN + s.MACHINE_WIDTH
    dim_h(ax, 0, s.MACHINE_LEFT_MARGIN, -170, "50", tick_to=-70)
    dim_h(ax, s.MACHINE_LEFT_MARGIN, machine_right, -170, "600 (REF)", tick_to=-70)
    dim_h(ax, machine_right, s.TOP_WIDTH, -170, "450", tick_to=-70)
    dim_h(ax, 0, s.TOP_WIDTH, -260, "1100", tick_to=-170)

    dim_h(ax, 0, s.BASIN_CENTER_X, 620, "865", tick_to=s.TOP_DEPTH)
    dim_h(ax, s.BASIN_CENTER_X, s.TOP_WIDTH, 620, "235", tick_to=s.TOP_DEPTH)
    dim_h(ax, 0, s.MIXER_CENTER_X, 720, "1000", tick_to=620)
    dim_h(ax, s.MIXER_CENTER_X, s.TOP_WIDTH, 720, "100", tick_to=620)

    dim_v(ax, 0, s.TOP_DEPTH, -80, "550", tick_to=0)
    dim_v(ax, 0, s.MACHINE_DEPTH, -180, "475 (REF)", tick_to=-80)
    dim_v(ax, s.MACHINE_DEPTH, s.TOP_DEPTH, -180, "75 rör", tick_to=-80)
    dim_v(ax, s.TOP_DEPTH - s.BRACKET_DEPTH, s.TOP_DEPTH, b1, "403 (REF)")

    dim_v(ax, 0, s.BASIN_CENTER_Y, 1190, "275", tick_to=s.TOP_WIDTH)
    dim_v(ax, 0, s.MIXER_CENTER_Y, 1300, "465", tick_to=s.TOP_WIDTH)


def build_figure():
    fig = plt.figure(figsize=(13, 13.5))
    ax = fig.add_axes([0.05, 0.44, 0.9, 0.50])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-260, 1400)
    ax.set_ylim(-330, 780)

    draw_top(ax)
    draw_machine(ax)
    draw_brackets(ax)
    draw_cutouts(ax)
    draw_labels(ax)
    draw_dimensions(ax)

    fig.text(
        0.05,
        0.965,
        "BÄNKSKIVA BADRUM  1100 x 550 mm  kompaktlaminat",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.05,
        0.947,
        "Planvy ovanifrån, underlag för CNC skärning. Alla mått i mm.",
        fontsize=10,
        color="#505050",
    )

    y = 0.405
    for line in NOTES:
        fig.text(0.05, y, line, fontsize=9.5)
        y = y - 0.0185

    y = y - 0.010
    for line in HOLE_TABLE:
        fig.text(0.05, y, line, fontsize=9.5, family="monospace", fontweight="bold")
        y = y - 0.0185

    return fig


def save_png(path):
    fig = build_figure()
    fig.savefig(path, dpi=200)
    plt.close(fig)
