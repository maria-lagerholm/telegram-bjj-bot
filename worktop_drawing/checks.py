import math

import specs as s

BASIN_RADIUS = s.BASIN_CUTOUT_DIAMETER / 2
CERAMIC_RADIUS = s.BASIN_CERAMIC_DIAMETER / 2
MIXER_RADIUS = s.MIXER_HOLE_DIAMETER / 2
BODY_RADIUS = s.MIXER_BODY_DIAMETER / 2
MACHINE_RIGHT = s.MACHINE_LEFT_MARGIN + s.MACHINE_WIDTH


def report():
    print("skiva", s.TOP_WIDTH, "x", s.TOP_DEPTH, "x", s.TOP_THICKNESS)
    print("maskin i djup", s.MACHINE_FRONT_OFFSET, "till", s.MACHINE_FRONT_OFFSET + s.MACHINE_DEPTH)
    print("skål mot maskin", s.BASIN_CENTER_X - BASIN_RADIUS - MACHINE_RIGHT)
    print("keramik mot höger kant", s.TOP_WIDTH - (s.BASIN_CENTER_X + CERAMIC_RADIUS))
    print("keramik mot bakkant", s.TOP_DEPTH - (s.BASIN_CENTER_Y + CERAMIC_RADIUS))
    print("keramik mot framkant", s.BASIN_CENTER_Y - CERAMIC_RADIUS)

    avstand = math.dist(
        (s.BASIN_CENTER_X, s.BASIN_CENTER_Y), (s.MIXER_CENTER_X, s.MIXER_CENTER_Y)
    )
    print("blandare till tvättställ centrum", round(avstand, 1))
    print("blandarhus mot keramikkant", round(avstand - CERAMIC_RADIUS - BODY_RADIUS, 1))
    print("vatten landar från centrum", round(avstand - s.MIXER_SPOUT_REACH, 1))
    print("blandarhål mot bakkant", s.TOP_DEPTH - s.MIXER_CENTER_Y - MIXER_RADIUS)
    print("blandarhål mot höger kant", s.TOP_WIDTH - s.MIXER_CENTER_X - MIXER_RADIUS)

    for x in s.BRACKET_CENTERS:
        vanster = x - s.BRACKET_WIDTH / 2
        hoger = x + s.BRACKET_WIDTH / 2
        if hoger < s.BASIN_CENTER_X:
            marginal = s.BASIN_CENTER_X - BASIN_RADIUS - hoger
        else:
            marginal = vanster - (s.BASIN_CENTER_X + BASIN_RADIUS)
        print("konsol", x, "mot skål", marginal)

    print("konsol mot blandarhål", s.BRACKET_CENTERS[2] - s.BRACKET_WIDTH / 2 - (s.MIXER_CENTER_X + MIXER_RADIUS))
    print("fritt överhäng fram", s.TOP_DEPTH - s.BRACKET_DEPTH)
    print("spann konsol", s.BRACKET_CENTERS[1] - s.BRACKET_CENTERS[0], s.BRACKET_CENTERS[2] - s.BRACKET_CENTERS[1])


if __name__ == "__main__":
    report()
