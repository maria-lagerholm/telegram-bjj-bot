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
    "      höjd 190, avlopp Ø45). Keramikkanten vilar då med 20 mm anliggning runt om. Kontrollera mot medföljande",
    "      schablon innan skärning. Godtagbart intervall 340 till 360 mm.",
    "HÅL Ø35 för Vesani Wilma BLWILMACH (tillverkaren anger 32 till 35 mm, blandarhuset Ø55 täcker hålet).",
    "      Blandaren står i högra bakre hörnet, 233 mm snett bakom tvättställets centrum. Pipen är 130 mm,",
    "      så vattnet hamnar väl inne i skålen. Cirka 10 mm mellan blandarhus och keramikkant.",
    "Tvättmaskin LG F2Y5PYP3W 600 x 475 x 850 mm visas som referens, ingen bearbetning.",
    "Skivan täcker maskinen med 50 mm överhäng på vänster sida och 50 mm fri yta på höger sida.",
    "Maskinen står 75 mm från vägg för rören. LG rekommenderar 100 mm, då sticker maskinen ut 25 mm framför skivan.",
    "Inget urtag för rör i bakkant. Lägg till om rörstammen sticker fram framför vägglinjen.",
    "Synliga kanter putsade med 1 mm fas. Skivan behöver stöd mot vägg och mot höger gavel under tvättstället.",
]

HOLE_TABLE = [
    "HÅLTABELL (centrum från främre vänstra hörnet)",
    "  Urtag tvättställ      X 875     Y 275     Ø 350",
    "  Hål blandare          X 1040    Y 440     Ø 35",
]


def build_figure():
    fig = plt.figure(figsize=(13, 12.5))
    ax = fig.add_axes([0.05, 0.40, 0.9, 0.53])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-260, 1380)
    ax.set_ylim(-240, 780)

    ax.add_patch(
        Rectangle((0, 0), s.TOP_WIDTH, s.TOP_DEPTH, fill=False, lw=2.2, edgecolor="black")
    )

    machine_x = s.MACHINE_LEFT_MARGIN
    ax.add_patch(
        Rectangle(
            (machine_x, 0),
            s.MACHINE_WIDTH,
            s.MACHINE_DEPTH,
            facecolor="#f2f2f2",
            edgecolor="#909090",
            lw=MACHINE_LINE,
            ls=(0, (6, 4)),
        )
    )
    ax.text(
        machine_x + s.MACHINE_WIDTH / 2,
        s.MACHINE_DEPTH / 2,
        "TVÄTTMASKIN\nLG F2Y5PYP3W\n600 x 475 (REF)",
        ha="center",
        va="center",
        fontsize=9,
        color="#707070",
    )

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
            fill=False,
            lw=2.2,
            edgecolor="black",
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
            fill=False,
            lw=2.2,
            edgecolor="black",
        )
    )

    ax.plot(
        [s.BASIN_CENTER_X, s.MIXER_CENTER_X],
        [s.BASIN_CENTER_Y, s.MIXER_CENTER_Y],
        lw=0.7,
        ls=(0, (4, 3)),
        color="#b0b0b0",
    )
    ax.text(985, 350, "233", fontsize=8, color="#808080", rotation=45, ha="center")

    cross(ax, s.BASIN_CENTER_X, s.BASIN_CENTER_Y, size=30, color="#909090")
    cross(ax, s.MIXER_CENTER_X, s.MIXER_CENTER_Y, size=40, color="#909090")

    ax.text(
        s.BASIN_CENTER_X,
        s.BASIN_CENTER_Y - 75,
        "URTAG Ø350\nTVÄTTSTÄLL",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
    )
    leader(
        ax,
        (s.BASIN_CENTER_X - 138, s.BASIN_CENTER_Y + 138),
        (430, 690),
        "Keramik Ø390 (REF)",
        color="#707070",
    )
    leader(
        ax,
        (s.MIXER_CENTER_X + 20, s.MIXER_CENTER_Y + 20),
        (1140, 700),
        "HÅL Ø35\nBLANDARE",
    )

    dim_h(ax, 0, s.MACHINE_LEFT_MARGIN, -70, "50", tick_to=0)
    dim_h(ax, s.MACHINE_LEFT_MARGIN, machine_x + s.MACHINE_WIDTH, -70, "600 (REF)", tick_to=0)
    dim_h(ax, machine_x + s.MACHINE_WIDTH, s.TOP_WIDTH, -70, "450", tick_to=0)
    dim_h(ax, 0, s.TOP_WIDTH, -170, "1100", tick_to=-70)

    dim_h(ax, 0, s.BASIN_CENTER_X, 620, "875", tick_to=s.TOP_DEPTH)
    dim_h(ax, s.BASIN_CENTER_X, s.TOP_WIDTH, 620, "225", tick_to=s.TOP_DEPTH)
    dim_h(ax, 0, s.MIXER_CENTER_X, 720, "1040", tick_to=620)
    dim_h(ax, s.MIXER_CENTER_X, s.TOP_WIDTH, 720, "60", tick_to=620)

    dim_v(ax, 0, s.TOP_DEPTH, -80, "550", tick_to=0)
    dim_v(ax, 0, s.MACHINE_DEPTH, -180, "475 (REF)", tick_to=-80)
    dim_v(ax, s.MACHINE_DEPTH, s.TOP_DEPTH, -180, "75 rör", tick_to=-80)

    dim_v(ax, 0, s.BASIN_CENTER_Y, 1190, "275", tick_to=s.TOP_WIDTH)
    dim_v(ax, 0, s.MIXER_CENTER_Y, 1300, "440", tick_to=s.TOP_WIDTH)

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

    fig.text(
        0.05,
        0.965,
        "BÄNKSKIVA BADRUM  1100 x 550 mm  kompaktlaminat",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.05,
        0.945,
        "Planvy ovanifrån, underlag för CNC skärning. Alla mått i mm.",
        fontsize=10,
        color="#505050",
    )

    y = 0.355
    for line in NOTES:
        fig.text(0.05, y, line, fontsize=9.5)
        y = y - 0.0205

    y = y - 0.012
    for line in HOLE_TABLE:
        fig.text(0.05, y, line, fontsize=9.5, family="monospace", fontweight="bold")
        y = y - 0.0205

    return fig


def save_png(path):
    fig = build_figure()
    fig.savefig(path, dpi=200)
    plt.close(fig)
