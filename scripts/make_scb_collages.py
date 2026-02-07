#!/usr/bin/env python3
"""
Generate SCBench bucket collages + a combined intro collage.

Sources:
- MB tasks: /Users/jashvira/code/MeshBenchmark/images/<qnum>.png
- VGB tasks: VisGeomBench blog_prep question PNGs, plus a generated thumbnail for
  topology_edge_classify_curated (no pre-rendered questions_gt directory).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
VGB_ROOT = REPO_ROOT / "VisGeomBench"


def _ensure_import_paths() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    if VGB_ROOT.is_dir() and str(VGB_ROOT) not in sys.path:
        sys.path.insert(0, str(VGB_ROOT))


@dataclass(frozen=True)
class Tile:
    code: str
    image_path: Path


@lru_cache(maxsize=8)
def _load_default_font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ):
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _open_as_rgb(path: Path) -> Image.Image:
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def _fit_to_tile(img: Image.Image, tile_w: int, tile_h: int, *, bg: tuple[int, int, int]) -> Image.Image:
    contained = ImageOps.contain(img, (tile_w, tile_h), method=Image.Resampling.LANCZOS)
    tile = Image.new("RGB", (tile_w, tile_h), bg)
    x = (tile_w - contained.width) // 2
    y = (tile_h - contained.height) // 2
    tile.paste(contained, (x, y))
    return tile


def _draw_heading(canvas: Image.Image, text: str, *, padding: int = 10, font_size: int = 18) -> int:
    draw = ImageDraw.Draw(canvas)
    font = _load_default_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (canvas.width - text_w) // 2
    y = padding
    draw.text((x, y), text, fill=(50, 50, 50), font=font)
    return y + text_h + padding // 2


_LABEL_FONT_SIZE = 11
_LABEL_H = 16


def _compose_bucket(
    heading: str,
    tiles: list[Tile],
    *,
    cols: int,
    tile_w: int,
    tile_h: int,
    gap: int,
    pad: int,
    bg: tuple[int, int, int] = (255, 255, 255),
    tile_bg: tuple[int, int, int] = (245, 245, 245),
    heading_font_size: int = 18,
) -> Image.Image:
    cell_h = tile_h + _LABEL_H
    rows = (len(tiles) + cols - 1) // cols
    width = pad * 2 + cols * tile_w + (cols - 1) * gap

    hbox = _load_default_font(heading_font_size).getbbox(heading)
    heading_h = pad + (hbox[3] - hbox[1]) + pad // 2
    height = heading_h + 4 + rows * cell_h + (rows - 1) * gap + pad

    canvas = Image.new("RGB", (width, height), bg)
    y0 = _draw_heading(canvas, heading, padding=pad, font_size=heading_font_size) + 4

    label_font = _load_default_font(_LABEL_FONT_SIZE)
    draw = ImageDraw.Draw(canvas)
    for idx, tile in enumerate(tiles):
        r = idx // cols
        c = idx % cols
        x = pad + c * (tile_w + gap)
        y = y0 + r * (cell_h + gap)
        img = _open_as_rgb(tile.image_path)
        canvas.paste(_fit_to_tile(img, tile_w, tile_h, bg=tile_bg), (x, y))
        lbl_bbox = draw.textbbox((0, 0), tile.code, font=label_font)
        lbl_w = lbl_bbox[2] - lbl_bbox[0]
        draw.text((x + (tile_w - lbl_w) // 2, y + tile_h + 1), tile.code,
                  fill=(100, 100, 100), font=label_font)
    return canvas


def _stack_horizontal(images: Iterable[Image.Image], *, gap: int, bg: tuple[int, int, int]) -> Image.Image:
    imgs = list(images)
    if not imgs:
        raise ValueError("No images to stack")
    height = max(i.height for i in imgs)
    width = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    canvas = Image.new("RGB", (width, height), bg)
    x = 0
    for img in imgs:
        canvas.paste(img, (x, 0))
        x += img.width + gap
    return canvas


def _resolve_blog_prep_run_dir(run_dir_arg: str | None) -> Path:
    blog_prep_root = VGB_ROOT / "blog_prep"
    if not blog_prep_root.is_dir():
        raise FileNotFoundError(f"Missing blog_prep directory: {blog_prep_root}")

    if run_dir_arg:
        candidate = Path(run_dir_arg)
        if not candidate.is_absolute():
            candidate = blog_prep_root / candidate
        if not candidate.is_dir():
            raise FileNotFoundError(f"VGB blog run directory not found: {candidate}")
        return candidate

    run_dirs = sorted(
        p for p in blog_prep_root.iterdir()
        if p.is_dir() and p.name.startswith("visual_geometry_bench.evaluation--")
    )
    if not run_dirs:
        raise FileNotFoundError(f"No VGB evaluation run directories found under: {blog_prep_root}")
    if len(run_dirs) > 1:
        names = ", ".join(p.name for p in run_dirs)
        raise ValueError(
            "Multiple VGB evaluation run directories found; pass --vgb-blog-run-dir explicitly. "
            f"Found: {names}"
        )
    return run_dirs[0]


def _blog_prep_questions_dir(dataset: str, blog_prep_run_dir: Path) -> Path:
    return (
        blog_prep_run_dir
        / dataset
        / "questions_gt"
    )


def _resolve_vgb_question_image(dataset: str, blog_prep_run_dir: Path, filename: str = "question_001.png") -> Path:
    path = _blog_prep_questions_dir(dataset, blog_prep_run_dir) / filename
    if path.exists():
        return path
    raise FileNotFoundError(f"Missing VGB question PNG: {path}")


def _render_topology_edge_classify_question(out_path: Path) -> None:
    _ensure_import_paths()
    # Avoid importing `visualisations` package root because it eagerly imports all
    # renderers (some require optional deps). We only need the topology-edge renderer.
    from visualisations.render import RenderMode, visualise_record
    import visualisations.topology_edge  # noqa: F401

    dataset_path = REPO_ROOT / "data" / "vgb" / "topology_edge_classify_curated.jsonl"
    lines = dataset_path.read_text(encoding="utf-8").splitlines()
    record = json.loads(next(line for line in lines if line.strip()))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    visualise_record(
        record,
        answer=None,
        detail=True,
        save_dir=out_path.parent,
        fmt=out_path.suffix.lstrip("."),
        output_stub=out_path.stem,
        mode=RenderMode.GROUND_TRUTH,
    )


def _vgb3_classify_tile(generated_root: Path) -> Tile:
    generated = generated_root / "topology_edge_classify_curated" / "question_001.png"
    if not generated.exists():
        _render_topology_edge_classify_question(generated)
    return Tile("VGB3", generated)


def _tiles_for_buckets(blog_prep_run_dir: Path, generated_root: Path) -> dict[str, list[Tile]]:
    mb_images = REPO_ROOT / "images"
    buckets: dict[str, list[Tile]] = {
        # /Users/jashvira/Desktop/Writing/VGBench/notes/notes.tex task table.
        "Axiomatic": [
            Tile("VGB1", _resolve_vgb_question_image("topology_enumeration_curated", blog_prep_run_dir)),
            Tile("VGB2", _resolve_vgb_question_image("topology_edge_enumerate_curated", blog_prep_run_dir)),
            _vgb3_classify_tile(generated_root),
            Tile("VGB4", _resolve_vgb_question_image("half_subdivision", blog_prep_run_dir)),
            Tile("VGB6", _resolve_vgb_question_image("delaunay_dataset", blog_prep_run_dir)),
            Tile("VGB5", _resolve_vgb_question_image("two_segments_curated", blog_prep_run_dir)),
        ],
        "Constructive": [
            Tile("MB2", mb_images / "2.png"),
            Tile("MB3", mb_images / "3.png"),
            Tile("MB4", mb_images / "4.png"),
            Tile("MB6", mb_images / "6.png"),
            Tile("VGB7", _resolve_vgb_question_image("shikaku_curated", blog_prep_run_dir)),
            Tile("MB8", mb_images / "8.png"),
            Tile("MB13", mb_images / "13.png"),
            Tile("MB29", mb_images / "29.png"),
        ],
        "Planning": [
            Tile("MB7", mb_images / "7.png"),
            Tile("MB9", mb_images / "9.png"),
            Tile("MB11", mb_images / "11.png"),
            Tile("MB12", mb_images / "12.png"),
            Tile("MB16", mb_images / "16.png"),
            Tile("MB23", mb_images / "23.png"),
            Tile("MB28", mb_images / "28.png"),
            Tile("MB30", mb_images / "30.png"),
        ],
    }

    for bucket, tiles in buckets.items():
        for tile in tiles:
            if not tile.image_path.exists():
                raise FileNotFoundError(f"Missing tile image for {bucket} {tile.code}: {tile.image_path}")
    return buckets


def main() -> int:
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ required (VisGeomBench visualisations use PEP604 types).")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory to write collages into (e.g. /Users/jashvira/Desktop/Writing/VGBench/figures)",
    )
    parser.add_argument("--tile-w", type=int, default=140)
    parser.add_argument("--tile-h", type=int, default=105)
    parser.add_argument("--gap", type=int, default=8)
    parser.add_argument("--pad", type=int, default=10)
    parser.add_argument(
        "--vgb-blog-run-dir",
        default=None,
        help=(
            "VGB blog_prep run directory path or name under VisGeomBench/blog_prep. "
            "If omitted, exactly one run must exist."
        ),
    )
    parser.add_argument(
        "--generated-vgb-cache-dir",
        type=Path,
        default=REPO_ROOT / "results" / "generated_questions_gt",
        help="Writable directory for generated VGB question renders (defaults outside the submodule).",
    )
    args = parser.parse_args()

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    blog_prep_run_dir = _resolve_blog_prep_run_dir(args.vgb_blog_run_dir)

    buckets = _tiles_for_buckets(blog_prep_run_dir, args.generated_vgb_cache_dir)

    bucket_images: dict[str, Image.Image] = {}
    bucket_cols = {"Axiomatic": 3, "Constructive": 4, "Planning": 4}
    for bucket_name, tiles in buckets.items():
        cols = bucket_cols.get(bucket_name, 4)
        bucket_images[bucket_name] = _compose_bucket(
            bucket_name,
            tiles,
            cols=cols,
            tile_w=args.tile_w,
            tile_h=args.tile_h,
            gap=args.gap,
            pad=args.pad,
        )

    intro = _stack_horizontal(
        [bucket_images["Axiomatic"], bucket_images["Constructive"], bucket_images["Planning"]],
        gap=12,
        bg=(255, 255, 255),
    )

    # Write outputs
    intro.save(out_dir / "scbench_intro_collage.png", format="PNG", optimize=True)
    for name, img in bucket_images.items():
        img.save(out_dir / f"scbench_bucket_{name.lower()}.png", format="PNG", optimize=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
