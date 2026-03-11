# DeGem

Automatically removes the Google Gemini star watermark from AI-generated images using AI inpainting — similar quality to Photoshop's content-aware fill, but fully automated.

## Before / After

| Before | After |
|--------|-------|
| Gemini star visible in bottom-right corner | Watermark removed, background filled naturally |

## How It Works

Google Gemini places a small 4-pointed star logo in the bottom-right corner of every image it generates. DeGem masks that region and uses the [LaMa inpainting model](https://github.com/advimman/lama) to reconstruct the background — no manual editing required.

## Requirements

- Python 3.8 or higher
- pip
- ~200MB of free disk space (for the LaMa model, downloaded once on first run)

## Installation

**1. Clone the repo**

```bash
git clone https://github.com/earlduque/DeGem.git
cd DeGem
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

That's it. The LaMa AI model (~200MB) will download automatically the first time you run the script.

---

## Usage

### Batch Mode — Process a folder of images

1. Drop your Gemini-generated images into the `input/` folder
2. Run:

```bash
python degem.py
```

3. Cleaned images will appear in the `output/` folder with `_clean` added to the filename (e.g. `image.png` → `image_clean.png`)

---

### Watch Mode — Auto-process images as you drop them in

Start the watcher:

```bash
python degem.py --watch
```

Now any image you drop into the `input/` folder will be automatically processed and saved to `output/`. Press `Ctrl+C` to stop.

---

## Supported Formats

`.jpg` `.jpeg` `.png` `.webp`

## Example Output

```
Loading LaMa inpainting model (first run downloads ~200MB)...
Model ready.

Found 3 image(s) to process.

  Processing photo1.png (2816x1536)...
  Saved -> output\photo1_clean.png
  Processing photo2.jpg (1024x1024)...
  Saved -> output\photo2_clean.jpg
  Processing photo3.webp (2048x2048)...
  Saved -> output\photo3_clean.webp

Done. 3/3 images saved to output/
```

## Troubleshooting

**"simple-lama-inpainting not installed" error**
Run `pip install -r requirements.txt` and try again.

**The watermark is still faintly visible**
The mask includes padding around the watermark region for cleaner edges. If results aren't clean, the image may have an unusual size. Open an issue with the image dimensions.

**Slow processing**
LaMa runs on CPU by default. If you have an NVIDIA GPU with CUDA installed, it will automatically be used for faster processing.

**Output looks blurry or wrong in that corner**
This can happen with very complex backgrounds (e.g. fine text or detailed patterns right at the corner). LaMa generally handles this well but isn't perfect — for tricky cases Photoshop's content-aware fill may still give better results.

## Notes

- Original images in `input/` are never modified
- The `input/` and `output/` folder contents are gitignored — your images won't be committed if you fork this repo
- The LaMa model is cached after the first download at `~/.cache/torch/hub/checkpoints/big-lama.pt`

## License

MIT
