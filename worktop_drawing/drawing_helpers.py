THIN = 0.7
TEXT_SIZE = 9


def dim_h(ax, x1, x2, y, text, tick_to=None):
    ax.annotate(
        "",
        xy=(x1, y),
        xytext=(x2, y),
        arrowprops=dict(arrowstyle="<->", lw=THIN, color="black", shrinkA=0, shrinkB=0),
    )
    if tick_to is not None:
        for x in (x1, x2):
            ax.plot([x, x], [y, tick_to], lw=THIN, color="gray")
    ax.text(
        (x1 + x2) / 2,
        y + 8,
        text,
        ha="center",
        va="bottom",
        fontsize=TEXT_SIZE,
    )


def dim_v(ax, y1, y2, x, text, tick_to=None):
    ax.annotate(
        "",
        xy=(x, y1),
        xytext=(x, y2),
        arrowprops=dict(arrowstyle="<->", lw=THIN, color="black", shrinkA=0, shrinkB=0),
    )
    if tick_to is not None:
        for y in (y1, y2):
            ax.plot([x, tick_to], [y, y], lw=THIN, color="gray")
    ax.text(
        x + 8,
        (y1 + y2) / 2,
        text,
        ha="left",
        va="center",
        rotation=90,
        fontsize=TEXT_SIZE,
    )


def leader(ax, point, label_pos, text, color="black"):
    ax.annotate(
        text,
        xy=point,
        xytext=label_pos,
        fontsize=TEXT_SIZE,
        color=color,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="-", lw=THIN, color=color),
    )


def cross(ax, x, y, size=22, color="black"):
    ax.plot([x - size, x + size], [y, y], lw=THIN, color=color)
    ax.plot([x, x], [y - size, y + size], lw=THIN, color=color)
