"""
DeGem - Gemini Watermark Remover
Removes the Google Gemini star watermark from AI-generated images.

Usage:
    python degem.py              # batch process all images in ./input/
    python degem.py --watch      # watch ./input/ and auto-process new images
"""

import sys
import time
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Gemini watermark specs (from Google's implementation):
# - Images where either dimension <= 1024px: 48x48 star, 32px margin from edges
# - Images where both dimensions > 1024px: 96x96 star, 64px margin from edges
SMALL_STAR, SMALL_MARGIN = 48, 32
LARGE_STAR, LARGE_MARGIN = 96, 64
MASK_PADDING = 20  # extra pixels around watermark for clean inpaint edges


def get_watermark_region(img_w: int, img_h: int) -> tuple[int, int, int, int]:
    """Return (x0, y0, x1, y1) bounding box of the Gemini watermark."""
    if img_w <= 1024 or img_h <= 1024:
        star_size, margin = SMALL_STAR, SMALL_MARGIN
    else:
        star_size, margin = LARGE_STAR, LARGE_MARGIN

    x0 = img_w - margin - star_size - MASK_PADDING
    y0 = img_h - margin - star_size - MASK_PADDING
    x1 = img_w - margin + MASK_PADDING
    y1 = img_h - margin + MASK_PADDING

    # Clamp to image bounds
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(img_w, x1)
    y1 = min(img_h, y1)

    return x0, y0, x1, y1


def make_mask(img_w: int, img_h: int) -> Image.Image:
    """Create a binary mask: white (255) = inpaint, black (0) = keep."""
    mask = Image.new("L", (img_w, img_h), 0)
    draw = ImageDraw.Draw(mask)
    region = get_watermark_region(img_w, img_h)
    draw.rectangle(region, fill=255)
    return mask


def process_image(img_path: Path, lama) -> Path | None:
    """Remove Gemini watermark from a single image. Returns output path or None on error."""
    try:
        img = Image.open(img_path).convert("RGB")
        mask = make_mask(img.width, img.height)

        print(f"  Processing {img_path.name} ({img.width}x{img.height})...")
        result = lama(img, mask)

        out_path = OUTPUT_DIR / f"{img_path.stem}_clean{img_path.suffix}"
        result.save(out_path)
        print(f"  Saved -> {out_path}")
        return out_path
    except Exception as e:
        print(f"  ERROR processing {img_path.name}: {e}")
        return None


def load_lama():
    """Load the LaMa inpainting model (downloads ~200MB on first run)."""
    try:
        from simple_lama_inpainting import SimpleLama
    except ImportError:
        print("ERROR: simple-lama-inpainting not installed.")
        print("Run: pip install simple-lama-inpainting watchdog Pillow")
        sys.exit(1)

    print("Loading LaMa inpainting model (first run downloads ~200MB)...")
    lama = SimpleLama()
    print("Model ready.\n")
    return lama


def batch_mode():
    """Process all images currently in the input folder."""
    images = [p for p in INPUT_DIR.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS]

    if not images:
        print(f"No images found in {INPUT_DIR}/")
        print("Drop .jpg/.jpeg/.png/.webp files there and try again.")
        return

    lama = load_lama()
    print(f"Found {len(images)} image(s) to process.\n")

    success = 0
    for img_path in sorted(images):
        if process_image(img_path, lama):
            success += 1

    print(f"\nDone. {success}/{len(images)} images saved to {OUTPUT_DIR}/")


def watch_mode():
    """Watch the input folder and auto-process new images as they're dropped in."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("ERROR: watchdog not installed.")
        print("Run: pip install simple-lama-inpainting watchdog Pillow")
        sys.exit(1)

    lama = load_lama()
    print(f"Watching {INPUT_DIR.resolve()} for new images...")
    print("Drop images in and they'll be processed automatically. Ctrl+C to stop.\n")

    class ImageHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return
            path = Path(event.src_path)
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                return
            # Brief wait to ensure file is fully written before opening
            time.sleep(0.5)
            process_image(path, lama)

    observer = Observer()
    observer.schedule(ImageHandler(), str(INPUT_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped.")
    observer.join()


def main():
    parser = argparse.ArgumentParser(
        description="DeGem: Remove Gemini watermarks from AI-generated images."
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch input/ folder and auto-process new images (default: batch mode)",
    )
    args = parser.parse_args()

    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    if args.watch:
        watch_mode()
    else:
        batch_mode()


if __name__ == "__main__":
    main()
