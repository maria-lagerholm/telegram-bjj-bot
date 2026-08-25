import specs as s


def line(x1, y1, x2, y2):
    return f"0\nLINE\n8\nCUT\n10\n{x1}\n20\n{y1}\n11\n{x2}\n21\n{y2}\n"


def circle(x, y, diameter):
    return f"0\nCIRCLE\n8\nCUT\n10\n{x}\n20\n{y}\n40\n{diameter / 2}\n"


def build_dxf():
    w = s.TOP_WIDTH
    d = s.TOP_DEPTH
    body = ""
    body += line(0, 0, w, 0)
    body += line(w, 0, w, d)
    body += line(w, d, 0, d)
    body += line(0, d, 0, 0)
    body += circle(s.BASIN_CENTER_X, s.BASIN_CENTER_Y, s.BASIN_CUTOUT_DIAMETER)
    body += circle(s.MIXER_CENTER_X, s.MIXER_CENTER_Y, s.MIXER_HOLE_DIAMETER)
    return "0\nSECTION\n2\nENTITIES\n" + body + "0\nENDSEC\n0\nEOF\n"


def save_dxf(path):
    with open(path, "w") as f:
        f.write(build_dxf())
