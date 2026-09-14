# AHS Law — Video Visual Identity (HyperFrames DESIGN.md)

This file is the source of truth for every AHS Law video composition. Do not deviate.

## Style Prompt

Premium South African law firm. Gold-on-black editorial restraint. Quiet authority. Every frame should feel like a courtroom that respects the viewer's intelligence. No gimmicks, no stock-footage clichés (no gavels, no scales, no judge memes). Words and typography do the heavy lifting. Use motion sparingly — when something moves, it earns the viewer's attention.

## Colors

| Token | Hex | Use |
|---|---|---|
| `--bg-primary` | `#0a0a0a` | Default scene background |
| `--bg-elevated` | `#1a1a1a` | Cards, panels, callouts |
| `--bg-deepest` | `#050505` | Vignette/edge fades |
| `--gold-primary` | `#c9a25a` | Headlines, key emphasis, accent only |
| `--gold-light` | `#d2ae6d` | Hover/secondary highlight |
| `--alert` | `#e07070` | "MYTH" / "WRONG" labels only — never gratuitous |
| `--text` | `#ffffff` | Body and captions |
| `--text-muted` | `#a0a0a0` | Secondary captions, timestamps |

## Typography

| Use | Family | Weight | Letter-spacing |
|---|---|---|---|
| Headlines (h1, callouts) | Raleway | 600 | 0.02em |
| Body / captions | Open Sans | 400 | 0 |
| Numbers / stats (big numerics) | Raleway | 800 | -0.01em |
| Labels (MYTH / FACT / NEW) | Raleway | 700 | 0.15em (uppercase) |

## Motion Defaults

- Easing: `power2.out` (entrances), `power3.inOut` (transforms), `power2.in` (exits)
- Durations: 0.5–0.8s for entrances, 0.3–0.5s for exits, 0.2s max for micro-states
- Minimum scene hold: **1.2 seconds** — no faster cuts
- Caption sweeps (gold underline draw): 0.4s
- Hero number counter: ease `power3.out` over 1.0–1.4s

## What NOT to Do

- No emoji-driven design
- No saturated colors outside the tokens above
- No bouncy easing (back, elastic) — these undermine authority
- No fast cuts — minimum 1.2s per scene
- No cliché legal imagery (gavels, scales of justice, suited men pointing at cameras)
- No more than 2 fonts per composition
- No drop shadows on body text (only on lifted cards if essential)

## Required End Card

Every video ends with:
- AHS Law wordmark in `--gold-primary` on `--bg-primary`
- Tagline: "Know your rights." (Raleway 600)
- URL: `ahslaw.co.za` (Open Sans 400, `--text-muted`)
- Hold for 2.5 seconds before fade out

## Required Watermark

Bottom-right corner of every scene (not just end card):
- "AHS" wordmark in `--gold-primary` at 60% opacity
- 24px font size
- 32px padding from edge

## Audio

- Voiceover: clean, neutral SA-English accent (TTS or recorded)
- Background: ambient string pad at -24dB, no driving rhythm
- Stings: short brass note for "MYTH" reveal, soft chime for "FACT"
- Hard cut to silence on AHS logo (lets the brand land)

## Aspect Ratios

- Default: **1080×1920 vertical** (Reels, TikTok, Shorts)
- Optional 1:1 versions (1080×1080) for LinkedIn / Facebook feed
- Never produce 16:9 unless specifically requested for YouTube

## Caption Style for Mobile

- Sized for thumb-distance viewing (min 64px on 1080-wide canvas)
- Two-line maximum per caption card
- Gold underline animates in beneath key phrases
- Centered horizontally, vertically positioned at 60% screen height (above the like/comment UI on mobile)
