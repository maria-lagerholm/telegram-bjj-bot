import math

import specs as s

MIN_CLEARANCE = 5

BOARDS = [
    ("GetaCore 10 mm solid surface", 10, 1400, "ja", 1250),
    ("kompaktlaminat 12 mm", 12, 1450, "ja", 1290),
    ("Corian 12 mm solid surface", 12, 1700, "ja", 930),
    ("kompaktlaminat 13 mm", 13, 1450, "ja", 1290),
    ("Hafa OnTop laminat 19,6 mm", 19.6, 730, "nej", 462),
    ("Svedbergs Tvatt o Tork laminat 28 mm", 28, 680, "nej", 630),
    ("kokslaminat pa spanskiva 30 mm", 30, 680, "nej", 635),
]


def area():
    a = s.TOP_WIDTH * s.TOP_DEPTH
    a = a - math.pi * (s.BASIN_CUTOUT_DIAMETER / 2) ** 2
    a = a - math.pi * (s.MIXER_HOLE_DIAMETER / 2) ** 2
    return a


def weight(thickness, density):
    return area() * thickness * density / 1000000000


def finished_height(thickness):
    return s.ARM_UNDERSIDE + s.BRACKET_ARM_HEIGHT + thickness


def lowest_height(thickness):
    return s.MACHINE_HEIGHT + MIN_CLEARANCE + s.BRACKET_ARM_HEIGHT + thickness


def deep_enough(max_depth):
    return "ja" if max_depth >= s.TOP_DEPTH else "nej"


def report():
    lines = ["material                              höjd  lägst   vikt  vattentät  600 djup"]
    for name, thickness, density, waterproof, max_depth in BOARDS:
        lines.append(
            f"{name:38}{finished_height(thickness):5.0f}"
            f"{lowest_height(thickness):7.0f}"
            f"{weight(thickness, density):7.1f}"
            f"{waterproof:>11}"
            f"{deep_enough(max_depth):>10}"
        )
    return "\n".join(lines)
