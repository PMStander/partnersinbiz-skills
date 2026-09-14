# Phase 4 — Image Generation

8 blog hero images + 4 reusable social card backgrounds. All generated via xAI `grok-imagine-image-pro`. Total wall-clock: ~3–4 minutes.

> **2026-05-04 — DO NOT USE GEMINI/IMAGEN.** Gemini path was removed after a runaway billing incident (~$355 on a single March invoice, est. ~7,000 images). xAI is pay-as-you-go and capped via the xAI dashboard. If a script or skill still references Gemini for image gen, fix it.

## Setup

The client workspace's `marketing/images/` should already have:
- `prompts.md` (copied from `assets/prompts-template.md`, customised with the client's brand mood)
- `generate.py` (copied from `scripts/generate-image.py`)

If not, copy them now:
```bash
cp ~/.claude/skills/client-content-engine/scripts/generate-image.py <workspace>/marketing/images/generate.py
cp ~/.claude/skills/client-content-engine/assets/prompts-template.md <workspace>/marketing/images/prompts.md
```

## Customise the master style suffix

Open `prompts.md` and edit the **Master Style Suffix** at the top to match the client's brand. The default is law-firm gold-on-black:

```
shot on Hasselblad medium format, 50mm lens, f/2.8,
deep black background (#0a0a0a), warm gold rim light (#c9a25a),
single key light from camera-left, dramatic shadow falloff,
luxury law-firm editorial aesthetic, restrained composition,
ultra-sharp details, photorealistic, no text, no logos, no watermarks
```

For other clients, swap:
- The colors (always use hex codes from the master plan)
- The aesthetic descriptor ("luxury law-firm" → "premium B2B SaaS" / "warm small-business" / "premium outdoor lifestyle")
- The camera/lens (Hasselblad/50mm = editorial; swap to "phone camera natural light" for casual brands)

The same suffix should ALSO be hardcoded in `generate.py`'s `MASTER_SUFFIX` constant — update both.

## Pre-requisites

```bash
# Verify XAI_API_KEY is set (Gemini key is no longer used)
[ -n "$XAI_API_KEY" ] && echo "OK" || echo "MISSING — set XAI_API_KEY first"

python3 -c "import json,base64,urllib.request" && echo "stdlib OK"
```

## Generate the 8 blog hero images

Each blog post has a `hero_image_prompt` field in its frontmatter (set during Phase 3 by the blog writer agents). Pull those prompts and pipe them through the generator.

Easy approach — run them in 2 batches of 4 in parallel:

```bash
cd <workspace>/marketing/images

# Batch 1
python3 generate.py blog/B1-[slug].png "[exact prompt from B1 hero_image_prompt]" 16:9 &
python3 generate.py blog/B2-[slug].png "[exact prompt from B2 hero_image_prompt]" 16:9 &
python3 generate.py blog/B3-[slug].png "[exact prompt from B3 hero_image_prompt]" 16:9 &
python3 generate.py blog/B4-[slug].png "[exact prompt from B4 hero_image_prompt]" 16:9 &
wait

# Batch 2
python3 generate.py blog/B5-[slug].png "[exact prompt from B5 hero_image_prompt]" 16:9 &
python3 generate.py blog/B6-[slug].png "[exact prompt from B6 hero_image_prompt]" 16:9 &
python3 generate.py blog/B7-[slug].png "[exact prompt from B7 hero_image_prompt]" 16:9 &
python3 generate.py blog/B8-[slug].png "[exact prompt from B8 hero_image_prompt]" 16:9 &
wait

ls -la blog/   # should show 8 PNGs ~500KB–1MB each
```

The generator script auto-appends the master style suffix to every prompt — you only pass the scene description.

## Generate 4 reusable social card backgrounds

These are reused across all 12 weekly social posts (paired with on-image text added in Canva later):

```bash
cd <workspace>/marketing/images

python3 generate.py social/quote-card-bg.png \
  "Abstract textured marble surface with faint warm accent veining, top-down view, leaving generous flat space in the centre for typography, moody premium feel" 1:1 &
python3 generate.py social/stat-card-bg.png \
  "A polished obsidian surface with a single beam of warm accent light crossing diagonally, leaving the centre clear, extreme negative space, minimal composition" 1:1 &
python3 generate.py social/myth-fact-bg.png \
  "Marble texture with subtle accent veining on the right half and faint red-tinted texture on the left half, premium editorial style, leaving centre clear for headline" 1:1 &
python3 generate.py social/quote-card-vertical.png \
  "Abstract textured marble surface with faint warm accent veining, vertical composition, premium editorial mood with clean negative space top and bottom" 9:16 &
wait
```

Replace "warm accent" with the client's actual accent color description (e.g., "gold", "teal", "warm amber", "cool blue").

## Aspect ratios — what works and what doesn't

Imagen 4.0 only accepts these exact aspect ratios:

| Ratio | Use for |
|---|---|
| `1:1` | Square Instagram/Facebook feed images, social cards |
| `9:16` | Vertical Stories backgrounds, vertical card variants |
| `16:9` | Blog hero images, YouTube thumbnails, presentation slides |
| `4:3` | Standard photo prints |
| `3:4` | Magazine portrait spreads |

**`3:2` is rejected.** This trips people up because pro photography is usually 3:2. Use `16:9` instead — close enough for blog use.

## Common image gen issues

| Symptom | Cause | Fix |
|---|---|---|
| Images all return blue/grey shadows | Default Gemini lighting bias | Add "warm shadows, true black tones" to the suffix |
| Faces in the image have wrong anatomy | Generator is bad at hands/multi-faces | Stick to objects, environments, and silhouettes — avoid prompts with "person looking at camera" |
| Image rejects with "model not found" | Old model name | Use `imagen-4.0-generate-001`, NOT `imagen-3.0-generate-002` |
| Generation succeeds but file is tiny / looks corrupted | Network truncation | Re-run the single image; the generator script will overwrite |
| Wrong colors despite the suffix | Imagen sometimes ignores hex codes | Describe the color in words too: "warm gold rim light (#c9a25a) — restrained, antique brass tone" |

## Watermarking

The generated images are clean (no logos). Watermarking happens at Canva-time by the user when they add the on-image text + AHS wordmark. Don't pre-watermark in this phase — keep originals clean for flexibility.

## Time budget

Phase 4 should take **8–12 minutes** wall-clock:
- Customising prompts.md + generate.py: 3 min
- 8 blog images (2 batches of 4 parallel): 4 min
- 4 social backgrounds (1 batch of 4 parallel): 2 min
- Spot-check + reroll any anatomy issues: 3 min
