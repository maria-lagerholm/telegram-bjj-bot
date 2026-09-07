import heights as h

OPTIONS = [
    (
        "nuvarande, maskinanslutning i stacken",
        h.MACHINE_CONNECTION_HEIGHT + h.DESIGN_TRAP_HEIGHT + h.SBOJ_BEND_HEIGHT,
        "vit",
    ),
    (
        "kromsatsen med teleskoprör, maskinen på eget kromlås",
        h.TELESCOPE_MIN_HEIGHT + h.DESIGN_TRAP_HEIGHT + h.SBOJ_BEND_HEIGHT,
        "krom",
    ),
    (
        "kompakt mässingslås i krom, maskinen på eget kromlås",
        h.TELESCOPE_MIN_HEIGHT + h.BRASS_TRAP_HEIGHT + h.SBOJ_BEND_HEIGHT,
        "krom",
    ),
    (
        "kommodvattenlås med maskinanslutning",
        h.KOMMOD_TRAP_HEIGHT,
        "vit",
    ),
]


def report():
    nuvarande = OPTIONS[0][1]
    print("behöver kortas", h.REDUCTION_NEEDED, "mm")
    print("nuvarande byggmått", nuvarande, "mm")

    for namn, hojd, farg in OPTIONS[1:]:
        vinst = nuvarande - hojd
        if vinst >= h.REDUCTION_NEEDED:
            besked = "räcker"
        else:
            besked = "räcker inte"
        print(farg, namn, "byggmått", hojd, "vinst", vinst, besked)


if __name__ == "__main__":
    report()
