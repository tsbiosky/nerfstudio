"""
Convert camera poses from COLMAP convention (Y down, Z forward)
to OpenGL convention (Y up, Z back) for nerfstudio compatibility.

Usage:
    python fix_camera_convention.py --input ./custom_Dataset_blender --output ./custom_Dataset_nerfstudio
"""

import json
import copy
import shutil
import argparse
from pathlib import Path


def convert_poses(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if output_path.resolve() != input_path.resolve():
        if output_path.exists():
            shutil.rmtree(output_path)
        shutil.copytree(input_path, output_path)
        print(f"Copied {input_path} -> {output_path}")
    else:
        print(f"Converting in-place: {input_path}")

    for split in ["train", "test", "val"]:
        json_path = output_path / f"transforms_{split}.json"
        if not json_path.exists():
            continue

        with open(json_path) as f:
            data = json.load(f)

        new_data = copy.deepcopy(data)
        for frame in new_data["frames"]:
            m = frame["transform_matrix"]
            # Flip Y (col 1) and Z (col 2) of the 3x3 rotation block
            # COLMAP (Y down, Z forward) -> OpenGL (Y up, Z back)
            for row in range(3):
                m[row][1] *= -1
                m[row][2] *= -1
            frame["transform_matrix"] = m

        new_data.pop("is_opengl", None)

        with open(json_path, "w") as f:
            json.dump(new_data, f, indent=2)

        print(f"  {split}: converted {len(new_data['frames'])} frames")

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert camera poses from COLMAP to OpenGL convention")
    parser.add_argument("--input", required=True, help="Path to the original dataset directory")
    parser.add_argument("--output", required=True, help="Path to save the converted dataset")
    args = parser.parse_args()

    convert_poses(args.input, args.output)
