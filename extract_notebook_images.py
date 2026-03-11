import argparse
import base64
import json
from pathlib import Path


def decode_data(value):
    if isinstance(value, list):
        value = "".join(value)
    return base64.b64decode(value)


def save_notebook_images(notebook_path: Path, out_dir: Path) -> int:
    with notebook_path.open("r", encoding="utf-8") as f:
        nb = json.load(f)

    out_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    # Delete all files in the out_dir first
    for file in out_dir.glob("*"):
        file.unlink()

    for cell_idx, cell in enumerate(nb.get("cells", [])):
        outputs = cell.get("outputs", [])
        for output_idx, output in enumerate(outputs):
            data = output.get("data", {})
            for mime_type, ext in (("image/png", "png"), ("image/jpeg", "jpg")):
                if mime_type not in data:
                    continue
                raw = decode_data(data[mime_type])
                filename = f"cell_{cell_idx:03d}_output_{output_idx:03d}.{ext}"
                (out_dir / filename).write_bytes(raw)
                saved += 1

        attachments = cell.get("attachments", {})
        for attach_name, attach_data in attachments.items():
            for mime_type, ext in (("image/png", "png"), ("image/jpeg", "jpg")):
                if mime_type not in attach_data:
                    continue
                raw = decode_data(attach_data[mime_type])
                safe_name = Path(attach_name).stem.replace(" ", "_")
                filename = f"cell_{cell_idx:03d}_attachment_{safe_name}.{ext}"
                (out_dir / filename).write_bytes(raw)
                saved += 1

    return saved


def main():
    parser = argparse.ArgumentParser(
        description="Extract PNG/JPEG images from a Jupyter notebook."
    )
    parser.add_argument("notebook", help="Path to .ipynb notebook file")
    parser.add_argument(
        "-o",
        "--out",
        default="notebook_images",
        help="Output directory (default: notebook_images)",
    )
    args = parser.parse_args()

    notebook_path = Path(args.notebook)
    out_dir = Path(args.out)

    if not notebook_path.exists():
        raise SystemExit(f"Notebook not found: {notebook_path}")

    count = save_notebook_images(notebook_path, out_dir)
    print(f"Saved {count} image(s) to {out_dir}")


if __name__ == "__main__":
    main()
