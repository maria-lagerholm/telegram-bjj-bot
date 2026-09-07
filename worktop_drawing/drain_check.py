import heights as h
import specs as s


def planned_top_surface():
    return h.MACHINE_HEIGHT + h.MACHINE_AIR_GAP + h.BRACKET_ARM_THICKNESS + s.TOP_THICKNESS


def valve_outlet_height(top_surface):
    return top_surface - h.BASIN_BOWL_HEIGHT - h.BASIN_VALVE_DROP


def nipple_height(top_surface):
    return valve_outlet_height(top_surface) - h.MACHINE_NIPPLE_DROP


def trap_outlet_height(top_surface):
    return valve_outlet_height(top_surface) - h.MACHINE_CONNECTION_HEIGHT - h.TRAP_HEIGHT


def extension_needed(top_surface):
    drop = valve_outlet_height(top_surface) - h.DRAIN_INLET_HEIGHT
    return drop - h.SBOJ_KIT_REACH


def report():
    planerad = planned_top_surface()
    matt = h.TOP_SURFACE_MEASURED

    print("planerad färdig höjd", planerad)
    print("uppmätt färdig höjd", matt)
    print("skillnad", matt - planerad)

    print("bottenventilens utlopp", valve_outlet_height(matt))
    print("maskinnippel", nipple_height(matt))
    print("vattenlåsets utlopp", trap_outlet_height(matt))

    nippel = nipple_height(matt)
    if nippel > h.HOSE_MAX_HEIGHT:
        print("maskinnippeln ligger", nippel - h.HOSE_MAX_HEIGHT, "mm över LG max 1000")
    elif nippel < h.HOSE_MIN_HEIGHT:
        print("maskinnippeln ligger", h.HOSE_MIN_HEIGHT - nippel, "mm under LG min 600")
    else:
        print("maskinnippeln ligger inom LG 600 till 1000")

    extra = extension_needed(matt)
    if extra > 0:
        print("förlängningsrör att kapa", extra, "mm")
        print("kvar av kromrör", h.CHROME_PIPE_LENGTH - extra, "mm")
    else:
        print("satsen räcker, kapa bort", -extra, "mm")


if __name__ == "__main__":
    report()
