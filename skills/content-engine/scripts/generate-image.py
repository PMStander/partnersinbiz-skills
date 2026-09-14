#!/usr/bin/env python3
"""
Partners in Biz image generator.

Uses xAI grok-imagine-image-pro (XAI_API_KEY).
Gemini path removed 2026-05-04 due to runaway billing on Imagen.

Usage:
  python3 generate.py <output_path> "<prompt>" [aspect_ratio]
  aspect_ratio: 1:1, 9:16, 16:9, 4:3, 3:4 (default 16:9)

Examples:
  python3 generate.py blog/B1-hero.png "laptop on dark desk" 16:9
  python3 generate.py social/stat-card-bg.png "dark minimal surface" 1:1
"""
import sys, os, json, base64, urllib.request, urllib.error

MASTER_SUFFIX = (
    "dark editorial studio aesthetic, near-black background #0A0A0B, "
    "warm amber accent lighting #F5A623, Instrument Serif editorial typography, "
    "premium founder-led web development studio, South African tech studio feel, "
    "no stock photos no handshakes no suits no smiling teams, "
    "ultra-sharp focus, cinematic single-key directional light, "
    "photorealistic, no text overlay, no logos, no watermarks"
)


def try_xai(out, prompt, aspect, api_key):
    """Generate image via xAI grok-imagine-image-pro. Returns True on success."""
    body = json.dumps({
        "model": "grok-imagine-image-pro",
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
    }).encode()
    url = "https://api.x.ai/v1/images/generations"
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
        img_b64 = data["data"][0].get("b64_json", "")
        if not img_b64:
            img_url = data["data"][0].get("url", "")
            if not img_url:
                print(f"xAI: no image data — {data}", file=sys.stderr)
                return False
            with urllib.request.urlopen(img_url, timeout=30) as r:
                img_bytes = r.read()
        else:
            img_bytes = base64.b64decode(img_b64)
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "wb") as f:
            f.write(img_bytes)
        print(f"OK (xAI) {out} ({len(img_bytes)//1024}KB)")
        return True
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:200]
        print(f"xAI HTTP {e.code}: {msg}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"xAI error: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out = sys.argv[1]
    prompt = sys.argv[2]
    aspect = sys.argv[3] if len(sys.argv) > 3 else "16:9"

    full_prompt = f"{prompt}, {MASTER_SUFFIX}"

    xai_key = os.environ.get("XAI_API_KEY", "")
    if not xai_key or xai_key == "YOUR_KEY_HERE":
        print(
            "\nERROR: XAI_API_KEY not set.\n"
            "  export XAI_API_KEY=xai-your-key-here\n",
            file=sys.stderr
        )
        sys.exit(2)

    print(f"Generating {out} via xAI…")
    if try_xai(out, full_prompt, aspect, xai_key):
        return

    print(f"\nERROR: xAI generation failed for {out}.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
