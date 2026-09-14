#!/usr/bin/env python3
"""
Pre-flight scanner for Phase 9 (Import from local).

Runs in DISCOVERY mode by default — just inventories what's in the client's
marketing/ folder so the agent can plan the import. Does NOT write anything.

Usage:
    python3 import-from-local.py --workspace "/Users/peetstander/Cowork/partners/<CLIENT>"
    python3 import-from-local.py --workspace "/Users/peetstander/Cowork/partners/Velox/velox"

Reports:
    - Master plan present? (marketing/plans/content-master-plan.md or similar)
    - How many blog markdown files (B*-*.md)
    - How many video folders with rendered .mp4 (V*/ with .mp4 inside)
    - How many social caption files (W*-*.md)
    - How many blog hero images (marketing/images/blog/B*-*.png)
    - Whether social card backgrounds exist (quote-card-bg, stat-card-bg, myth-fact-bg)
    - Firebase Admin credentials reachable
    - AI_API_KEY set

Exit code 0 = ready to import. Anything non-zero = pre-reqs missing.

After this passes, the agent should follow references/09-import-from-local.md
end-to-end. The proven per-phase scripts from the AHS Law run are at
/tmp/ahs_*.py on Peet's machine and can be adapted.
"""

import argparse, sys, os
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True, help="Client workspace root")
    args = ap.parse_args()

    ws = Path(args.workspace).expanduser().resolve()
    mkt = ws / "marketing"
    if not mkt.exists():
        print(f"[FAIL] {mkt} does not exist")
        sys.exit(2)

    print(f"=== Phase 9 pre-flight: {ws.name} ===\n")
    issues = 0

    # 1. Master plan
    candidates = list(mkt.glob("plans/*master-plan*.md")) + \
                 list(mkt.glob("*MASTER_PLAN*.md")) + \
                 list(mkt.glob("plans/*content*plan*.md"))
    if candidates:
        print(f"[ok] master plan: {candidates[0].relative_to(ws)}")
    else:
        print("[warn] no master plan found — you'll have to derive pillars/calendar from the content itself or ask the user")

    # 2. Blogs
    blogs = sorted(mkt.glob("blog-posts/B*-*.md")) or \
            sorted(mkt.glob("blog/B*-*.md"))         or \
            sorted(mkt.glob("blogs/*.md"))
    print(f"[{'ok' if blogs else 'skip'}] blog markdown files: {len(blogs)}")
    for b in blogs[:10]:
        print(f"       {b.relative_to(ws)}")
    if len(blogs) > 10:
        print(f"       ... and {len(blogs) - 10} more")

    # 3. Blog hero images
    hero = sorted(mkt.glob("images/blog/B*.png")) + sorted(mkt.glob("images/blog/B*.jpg"))
    print(f"[{'ok' if hero else 'warn'}] blog hero images: {len(hero)} (need one per blog)")
    if blogs and hero and len(hero) < len(blogs):
        print(f"       MISSING: {len(blogs) - len(hero)} hero images")
        issues += 1

    # 4. Videos with rendered .mp4
    videos = []
    for vd in sorted(mkt.glob("videos/V*")):
        if vd.is_dir():
            mp4s = list(vd.glob("*.mp4"))
            if mp4s:
                videos.append((vd.name, len(mp4s)))
    print(f"[{'ok' if videos else 'skip'}] video folders with rendered .mp4: {len(videos)}")
    for name, n in videos:
        marker = "✓" if n >= 3 else "⚠ only " + str(n) + " cut(s) — expected 3 (reel, youtube, stories)"
        print(f"       {name}: {n} mp4s {marker}")

    # 5. Social captions
    socials = sorted(mkt.glob("social-media/W*-*.md")) or \
              sorted(mkt.glob("social-content/W*-*.md")) or \
              sorted(mkt.glob("social/W*-*.md"))
    print(f"[{'ok' if socials else 'skip'}] social caption files (W01-W12): {len(socials)}")

    # 6. Social card backgrounds
    bg_dir = mkt / "images" / "social"
    needed = ["quote-card-bg", "stat-card-bg", "myth-fact-bg"]
    found_bg = []
    for n in needed:
        for ext in (".png", ".jpg"):
            p = bg_dir / (n + ext)
            if p.exists():
                found_bg.append(n)
                break
    missing_bg = [n for n in needed if n not in found_bg]
    print(f"[{'ok' if not missing_bg else 'warn'}] social card backgrounds: {found_bg}")
    if missing_bg:
        print(f"       MISSING: {missing_bg} — generate via Phase 4 image gen, or repurpose blog images")

    # 7. Credentials
    print()
    if os.environ.get("AI_API_KEY"):
        print("[ok] AI_API_KEY is set")
    else:
        print("[FAIL] AI_API_KEY not in environment — get from Vercel partnersinbiz-web env vars")
        issues += 1

    env_local = Path("/Users/peetstander/Cowork/Partners in Biz — Client Growth/partnersinbiz-web/.env.local")
    if env_local.exists():
        env_text = env_local.read_text()
        has_admin = all(k in env_text for k in ("FIREBASE_ADMIN_PROJECT_ID", "FIREBASE_ADMIN_CLIENT_EMAIL", "FIREBASE_ADMIN_PRIVATE_KEY"))
        if has_admin:
            print("[ok] Firebase Admin credentials reachable in partnersinbiz-web/.env.local")
        else:
            print("[FAIL] partnersinbiz-web/.env.local exists but missing FIREBASE_ADMIN_* keys")
            issues += 1
    else:
        print(f"[FAIL] {env_local} not found — heroImageUrl writes will fail")
        issues += 1

    # 8. SF Pro Display fonts (for compositing card images)
    fonts_ok = (Path("/Library/Fonts/SF-Pro-Display-Bold.otf").exists() and
                Path("/Library/Fonts/SF-Pro-Display-Semibold.otf").exists())
    print(f"[{'ok' if fonts_ok else 'warn'}] SF Pro Display fonts {'present' if fonts_ok else 'missing — composited cards will use fallback'}")

    # ─── Plan summary ─────────────────────────────────────────────────────
    print("\n=== Plan ===")
    print(f"  → POST /campaigns                      (1 campaign)")
    print(f"  → POST /seo/sprints                    (1 sprint)")
    print(f"  → For each blog ({len(blogs)}):")
    print(f"      POST /seo/sprints/{{sid}}/content")
    print(f"      POST /seo/content/{{cid}}/draft")
    print(f"      POST /social/media/upload (hero)")
    print(f"      Firestore-admin write: heroImageUrl + draftPostId")
    print(f"  → Composite + upload 12 social cards")
    print(f"  → For each social ({len(socials) * 3} posts — 3 platforms each):")
    print(f"      POST /social/posts")
    print(f"      POST /social/posts/{{id}}/submit")
    print(f"  → For each video ({len(videos)}):")
    print(f"      Upload 3 .mp4 cuts to Firebase")
    print(f"      POST /social/posts (media[0].type=video)")
    print(f"      POST /social/posts/{{id}}/submit")
    print(f"  → PATCH /campaigns/{{id}} {{status: active}}")

    print(f"\n=== Result ===")
    if issues == 0:
        print(f"[READY] {ws.name} — proceed with Phase 9 import per references/09-import-from-local.md")
        sys.exit(0)
    else:
        print(f"[BLOCKED] {issues} issue(s) above — resolve before importing")
        sys.exit(1)

if __name__ == "__main__":
    main()
