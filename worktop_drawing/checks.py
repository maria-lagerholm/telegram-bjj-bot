import math

import materials
import specs as s


def spans():
    edges = [0] + s.BRACKET_CENTERS + [s.TOP_WIDTH]
    result = []
    for i in range(len(edges) - 1):
        result.append(edges[i + 1] - edges[i])
    return result


def bracket_to_basin_gap():
    basin_left = s.BASIN_CENTER_X - s.BASIN_CUTOUT_DIAMETER / 2
    basin_right = s.BASIN_CENTER_X + s.BASIN_CUTOUT_DIAMETER / 2
    gaps = []
    for x in s.BRACKET_CENTERS:
        arm_left = x - s.BRACKET_WIDTH / 2
        arm_right = x + s.BRACKET_WIDTH / 2
        if arm_right < basin_left:
            gaps.append(basin_left - arm_right)
        elif arm_left > basin_right:
            gaps.append(arm_left - basin_right)
        else:
            gaps.append(0)
    return min(gaps)


def basin_to_mixer_bridge():
    d = math.hypot(
        s.MIXER_CENTER_X - s.BASIN_CENTER_X, s.MIXER_CENTER_Y - s.BASIN_CENTER_Y
    )
    return d - s.BASIN_CUTOUT_DIAMETER / 2 - s.MIXER_HOLE_DIAMETER / 2


def mixer_body_to_ceramic():
    d = math.hypot(
        s.MIXER_CENTER_X - s.BASIN_CENTER_X, s.MIXER_CENTER_Y - s.BASIN_CENTER_Y
    )
    return d - s.BASIN_CERAMIC_DIAMETER / 2 - s.MIXER_BODY_DIAMETER / 2


def weight():
    return materials.weight(s.TOP_THICKNESS, s.TOP_DENSITY)


def rows():
    result = []
    result.append(("frihäng framkant", s.FRONT_OVERHANG, s.MAX_OVERHANG, "max"))
    result.append(("största stödavstånd", max(spans()), s.MAX_SUPPORT_SPACING, "max"))
    result.append(("konsol till urtag", bracket_to_basin_gap(), 10, "min"))
    result.append(("material mellan hålen", basin_to_mixer_bridge(), 30, "min"))
    result.append(("blandarhus till keramikkant", mixer_body_to_ceramic(), 5, "min"))
    result.append(("luft över maskinen", s.MACHINE_CLEARANCE, 5, "min"))
    result.append(("färdig höjd", s.FINISHED_HEIGHT, 900, "runt"))
    result.append(("vikt kg", weight(), 15, "max"))
    return result


def passed(value, limit, kind):
    if kind == "max":
        return value <= limit
    if kind == "min":
        return value >= limit
    return abs(value - limit) <= 25


def report():
    lines = []
    for name, value, limit, kind in rows():
        mark = "OK" if passed(value, limit, kind) else "FEL"
        lines.append(f"{mark:4}{name:30}{value:8.1f}  ({kind} {limit})")
    return "\n".join(lines)
