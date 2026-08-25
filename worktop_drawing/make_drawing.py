import os

import checks
import dxf_export
import elevation_drawing
import plan_drawing

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plan_path = os.path.join(OUTPUT_DIR, "bankskiva_badrum_plan.png")
    section_path = os.path.join(OUTPUT_DIR, "bankskiva_badrum_sektion.png")
    dxf_path = os.path.join(OUTPUT_DIR, "bankskiva_badrum_1100x600.dxf")
    plan_drawing.save_png(plan_path)
    elevation_drawing.save_png(section_path)
    dxf_export.save_dxf(dxf_path)
    print(checks.report())
    print(plan_path)
    print(section_path)
    print(dxf_path)


if __name__ == "__main__":
    main()
