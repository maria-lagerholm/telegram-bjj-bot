import os

import dxf_export
import plan_drawing

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    png_path = os.path.join(OUTPUT_DIR, "bankskiva_badrum_1100x600.png")
    dxf_path = os.path.join(OUTPUT_DIR, "bankskiva_badrum_1100x600.dxf")
    plan_drawing.save_png(png_path)
    dxf_export.save_dxf(dxf_path)
    print(png_path)
    print(dxf_path)


if __name__ == "__main__":
    main()
