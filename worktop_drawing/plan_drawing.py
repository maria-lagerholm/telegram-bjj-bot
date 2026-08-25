import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

import checks
import specs as s
from drawing_helpers import cross, dim_h, dim_v, leader

MACHINE_LINE = 1.0

NOTES = [
    f"MATERIAL: {s.MATERIAL_NAME} {s.TOP_THICKNESS:g} mm, {s.TOP_WIDTH} x {s.TOP_DEPTH} mm. Antal: 1 st. Alla mått i mm.",
    f"      Vikt ca {checks.weight():.0f} kg. Byter du tjocklek ändras färdig höjd, se sektion A-A.",
    "Origo = främre vänstra hörnet. X åt höger, Y mot vägg. Tolerans ±1 mm. Ritningen är ej skalenlig, använd måtten.",
    "URTAG Ø350 för Villeroy & Boch Loop & Friends 4A590001, nedsänkt från ovansidan (keramik Ø390, innerkant Ø330,",
    "      höjd 190, avlopp Ø45). Keramikkanten vilar med 20 mm anliggning runt om. Kontrollera mot medföljande",
    "      schablon innan skärning. Godtagbart intervall 340 till 360 mm.",
    "HÅL Ø35 för Vesani Wilma BLWILMACH (tillverkaren anger 32 till 35 mm, blandarhuset Ø55 täcker hålet).",
    "      Blandaren står i högra bakre hörnet, 233 mm snett bakom tvättställets centrum. Pipen är 130 mm,",
    f"      så vattnet hamnar väl inne i skålen. {checks.mixer_body_to_ceramic():.0f} mm mellan blandarhus och keramikkant,"
    f" {checks.basin_to_mixer_bridge():.0f} mm material",
    "      mellan de två hålen. Fräs hålen, borra inte, så att bryggan mellan dem inte spjälkar.",
    f"KONSOL: 3 st Svedbergs 47920, arm {s.BRACKET_DEPTH} mm djup, {s.BRACKET_WIDTH} mm bred,"
    f" {s.BRACKET_TOTAL_HEIGHT} mm hög totalt, skruvas i väggen.",
    f"      Centrum X {s.BRACKET_CENTERS[0]}, {s.BRACKET_CENTERS[1]} och {s.BRACKET_CENTERS[2]}"
    f" ger största stödavstånd {max(checks.spans()):.0f} mm.",
    f"      Armarna går fria från urtaget med minst {checks.bracket_to_basin_gap():.0f} mm.",
    "      Skivan skruvas underifrån i armarna med borrstopp, eller limmas med MS polymer. Inga hål ovanifrån.",
    "      Kontrollera att konsolernas väggfästen inte hamnar på rören bakom maskinen.",
    f"HÖJD: se sektion A-A. Maskinens topp {s.MACHINE_HEIGHT} + {s.MACHINE_CLEARANCE} luft"
    f" + {s.BRACKET_ARM_HEIGHT} armprofil = {s.TOP_UNDERSIDE} underkant skiva,",
    f"      + {s.TOP_THICKNESS:g} skiva = {s.FINISHED_HEIGHT:g} mm FÄRDIG HÖJD till ovansidan."
    " Mät armprofilen på din konsol innan montering.",
    f"      Främre {s.FRONT_OVERHANG} mm av skivan bärs inte av konsolerna.",
    "      Sitt inte på framkanten. Limma en stödlist 20 x 40 mm under framkanten mellan konsol 2 och 3",
    f"      om du vill styva upp den {s.BASIN_CENTER_Y - s.BASIN_CUTOUT_DIAMETER / 2:.0f} mm smala remsan framför urtaget.",
    f"Tvättmaskin LG F2Y5PYP3W {s.MACHINE_WIDTH} x {s.MACHINE_DEPTH} x {s.MACHINE_HEIGHT} mm visas som referens, ingen bearbetning.",
    f"Maskinen står {s.PIPE_GAP} mm från vägg enligt LG:s rekommendation, därför är skivan {s.TOP_DEPTH} mm djup.",
    f"      Skivan går då {s.MACHINE_FRONT_OFFSET} mm förbi maskinens framkant."
    f" Luckan buktar ut {s.MACHINE_DOOR_BULGE} mm framför maskinens kropp.",
    "Skivan täcker maskinen med 50 mm överhäng på vänster sida. Skålen går fri från maskinen med 40 mm.",
    "Inget urtag för rör i bakkant. Lägg till om rörstammen sticker fram framför vägglinjen.",
    "Synliga kanter putsade med 1 mm fas.",
]

if s.TOP_DENSITY < 1000:
    NOTES.append(
        "KÄRNA: spånskiva, ej vattentät. Täta båda hålens kanter och alla kapsnitt med silikon"
    )
    NOTES.append(
        "      eller tätningslack innan tvättstället monteras. Diffusionsspärr under skivan över maskinen."
    )

HOLE_TABLE = [
    "HÅLTABELL (centrum från främre vänstra hörnet)",
    f"  Urtag tvättställ      X {s.BASIN_CENTER_X:<8}Y {s.BASIN_CENTER_Y:<8}Ø {s.BASIN_CUTOUT_DIAMETER}",
    f"  Hål blandare          X {s.MIXER_CENTER_X:<8}Y {s.MIXER_CENTER_Y:<8}Ø {s.MIXER_HOLE_DIAMETER}",
    f"  Färdig höjd ovansida skiva {s.FINISHED_HEIGHT:g} över golv, underkant skiva {s.TOP_UNDERSIDE:g}",
]


def draw_top(ax):
    ax.add_patch(
        Rectangle((0, 0), s.TOP_WIDTH, s.TOP_DEPTH, fill=False, lw=2.2, edgecolor="black")
    )


def draw_machine(ax):
    ax.add_patch(
        Rectangle(
            (s.MACHINE_LEFT_MARGIN, s.MACHINE_FRONT_OFFSET),
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
        s.MACHINE_FRONT_OFFSET + s.MACHINE_DEPTH / 2 - 40,
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
    ax.text(915, 380, "233", fontsize=8, color="#707070", rotation=55, ha="center")
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
        (330, 740),
        "Keramik Ø390 (REF)",
        color="#707070",
    )
    leader(
        ax,
        (s.MIXER_CENTER_X + 20, s.MIXER_CENTER_Y + 12),
        (1150, 750),
        "HÅL Ø35\nBLANDARE",
    )
    leader(
        ax,
        (s.BRACKET_CENTERS[0], 230),
        (120, 80),
        "3 st KONSOL SVEDBERGS 47920\narm 403 djup, 30 bred (REF)",
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
    dim_h(ax, 0, b1, -70, f"{b1}", tick_to=0)
    dim_h(ax, b1, b2, -70, f"{b2 - b1} c/c", tick_to=0)
    dim_h(ax, b2, b3, -70, f"{b3 - b2} c/c", tick_to=0)
    dim_h(ax, b3, s.TOP_WIDTH, -70, f"{s.TOP_WIDTH - b3}", tick_to=0)

    machine_right = s.MACHINE_LEFT_MARGIN + s.MACHINE_WIDTH
    dim_h(ax, 0, s.MACHINE_LEFT_MARGIN, -170, f"{s.MACHINE_LEFT_MARGIN}", tick_to=-70)
    dim_h(ax, s.MACHINE_LEFT_MARGIN, machine_right, -170, f"{s.MACHINE_WIDTH} (REF)", tick_to=-70)
    dim_h(ax, machine_right, s.TOP_WIDTH, -170, f"{s.TOP_WIDTH - machine_right}", tick_to=-70)
    dim_h(ax, 0, s.TOP_WIDTH, -260, f"{s.TOP_WIDTH}", tick_to=-170)

    dim_h(ax, 0, s.BASIN_CENTER_X, 670, f"{s.BASIN_CENTER_X}", tick_to=s.TOP_DEPTH)
    dim_h(ax, s.BASIN_CENTER_X, s.TOP_WIDTH, 670, f"{s.TOP_WIDTH - s.BASIN_CENTER_X}", tick_to=s.TOP_DEPTH)
    dim_h(ax, 0, s.MIXER_CENTER_X, 770, f"{s.MIXER_CENTER_X}", tick_to=670)
    dim_h(ax, s.MIXER_CENTER_X, s.TOP_WIDTH, 770, f"{s.TOP_WIDTH - s.MIXER_CENTER_X}", tick_to=670)

    machine_back = s.MACHINE_FRONT_OFFSET + s.MACHINE_DEPTH
    dim_v(ax, 0, s.TOP_DEPTH, -80, f"{s.TOP_DEPTH}", tick_to=0)
    dim_v(ax, 0, s.MACHINE_FRONT_OFFSET, -180, f"{s.MACHINE_FRONT_OFFSET}", tick_to=-80)
    dim_v(ax, s.MACHINE_FRONT_OFFSET, machine_back, -180, f"{s.MACHINE_DEPTH} (REF)", tick_to=-80)
    dim_v(ax, machine_back, s.TOP_DEPTH, -180, f"{s.PIPE_GAP} rör", tick_to=-80)
    dim_v(ax, s.TOP_DEPTH - s.BRACKET_DEPTH, s.TOP_DEPTH, b1, f"{s.BRACKET_DEPTH} (REF)")

    dim_v(ax, 0, s.BASIN_CENTER_Y, 1190, f"{s.BASIN_CENTER_Y}", tick_to=s.TOP_WIDTH)
    dim_v(ax, 0, s.MIXER_CENTER_Y, 1300, f"{s.MIXER_CENTER_Y}", tick_to=s.TOP_WIDTH)


def build_figure():
    fig = plt.figure(figsize=(13, 18))
    ax = fig.add_axes([0.05, 0.50, 0.9, 0.44])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-260, 1400)
    ax.set_ylim(-330, 830)

    draw_top(ax)
    draw_machine(ax)
    draw_brackets(ax)
    draw_cutouts(ax)
    draw_labels(ax)
    draw_dimensions(ax)

    fig.text(
        0.05,
        0.965,
        f"BÄNKSKIVA BADRUM  {s.TOP_WIDTH} x {s.TOP_DEPTH} x {s.TOP_THICKNESS:g} mm  {s.MATERIAL_NAME}",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.05,
        0.947,
        "Planvy ovanifrån, underlag för CNC skärning. Höjder finns på sektion A-A. Alla mått i mm.",
        fontsize=10,
        color="#505050",
    )

    y = 0.465
    for line in NOTES:
        fig.text(0.05, y, line, fontsize=9.5)
        y = y - 0.0125

    y = y - 0.010
    for line in HOLE_TABLE:
        fig.text(0.05, y, line, fontsize=9.5, family="monospace", fontweight="bold")
        y = y - 0.0125

    return fig


def save_png(path):
    fig = build_figure()
    fig.savefig(path, dpi=200)
    plt.close(fig)
