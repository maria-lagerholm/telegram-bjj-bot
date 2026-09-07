import heights as h

OPTIONS = [
    ("nuvarande, maskinanslutning i stacken", h.MACHINE_CONNECTION_HEIGHT + h.DESIGN_TRAP_HEIGHT + h.SBOJ_BEND_HEIGHT),
    ("kromsatsen med teleskoprör, maskinen kopplas separat", h.TELESCOPE_MIN_HEIGHT + h.DESIGN_TRAP_HEIGHT + h.SBOJ_BEND_HEIGHT),
    ("kromsatsen med låg avloppstratt", h.FUNNEL_HEIGHT + h.DESIGN_TRAP_HEIGHT + h.SBOJ_BEND_HEIGHT),
    ("kommodvattenlås med maskinanslutning", h.KOMMOD_TRAP_HEIGHT),
]


def report():
    nuvarande = OPTIONS[0][1]
    print("behöver kortas", h.REDUCTION_NEEDED, "mm")
    print("nuvarande byggmått", nuvarande, "mm")

    for namn, hojd in OPTIONS[1:]:
        vinst = nuvarande - hojd
        if vinst >= h.REDUCTION_NEEDED:
            besked = "räcker"
        else:
            besked = "räcker inte"
        print(namn, "byggmått", hojd, "vinst", vinst, besked)


if __name__ == "__main__":
    report()
