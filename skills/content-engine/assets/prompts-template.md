# AHS Law — Image Generation Prompt Library

Reusable prompts for Gemini (Nano Banana Pro) and xAI (Grok image). Every prompt locks the AHS palette and editorial mood. Copy/paste, swap the [SUBJECT] line, generate.

---

## Master Style Suffix (append to every prompt)

```
shot on Hasselblad medium format, 50mm lens, f/2.8,
deep black background (#0a0a0a), warm gold rim light (#c9a25a),
single key light from camera-left, dramatic shadow falloff,
luxury law-firm editorial aesthetic, restrained composition,
negative space on the right for headline overlay,
ultra-sharp details, photorealistic, 3:2 aspect ratio,
no text, no logos, no watermarks
```

---

## Blog Hero Prompts

### B1 — PIE Act / Eviction
```
An ornate brass key resting in a black antique door lock,
a single shaft of warm gold light from upper left,
dust particles caught in the beam, cinematic depth, deep shadows
[+ master style suffix]
```

### B2 — Labour Law Amendment Bill
```
Overhead view of a dark walnut desk with neatly stacked legal documents,
a Montblanc-style gold-accented pen resting on top, single warm spotlight
pooling on the centre, the rest in deep shadow, top-down angle
[+ master style suffix]
```

### B3 — Arrest Rights
```
Dramatic silhouette of a person standing against a textured concrete wall,
backlit by a single warm gold light, no facial features visible,
mood of quiet contemplation rather than threat, respectful and editorial
[+ master style suffix]
```

### B4 — Marital Regimes (Community of Property vs Accrual)
```
Two simple gold wedding bands slightly interlocked, resting on black velvet,
single soft top-down spotlight, macro detail, jewellery-photography precision
[+ master style suffix]
```

### B5 — Debt / Cannot Be Arrested for Debt
```
An empty leather wallet open on a black slate surface,
subtle warm gold light leak from the right edge,
mood of quiet stress without melodrama, no people, no money visible
[+ master style suffix]
```

### B6 — POPIA / WhatsApp Privacy
```
A modern smartphone face-down on polished black marble surface,
edge of the screen glowing faint gold,
top-down minimalist composition, cool reflective sheen
[+ master style suffix]
```

### B7 — Conveyancing / Property Transfer
```
A modern brass house key resting on rolled architect drawings,
single warm window light from frame-left, professional editorial style,
shallow depth of field
[+ master style suffix]
```

### B8 — Maintenance Unpaid
```
An empty children's metal lunchbox open on a wood kitchen counter,
soft window light from frame-left, melancholic but not dark,
gold tones in the wood grain, no people
[+ master style suffix]
```

---

## Social Quote Card Backgrounds

### Generic Gold-on-Black Texture (reusable)
```
Abstract textured black marble surface with faint warm gold veining,
top-down view, leaving generous flat space in the centre for typography,
moody premium feel
[+ master style suffix]
```

### Stat Card Background (numeric reveal)
```
A polished obsidian surface with a single beam of warm gold light
crossing from upper-left to lower-right diagonally, leaving the centre clear,
extreme negative space, minimal composition
[+ master style suffix]
```

### Myth-vs-Fact Split
Generate two halves separately and composite:
```
Left half: deep red-tinted black marble texture with subtle texture
Right half: warm gold-tinted black marble texture, same composition
Both: premium editorial style, leaving centre clear for headline
[+ master style suffix]
```

---

## Per-Pillar Mood Prompts (for ad-hoc social use)

### Labour
```
A modern empty boardroom at golden hour, gold light streaming through
floor-to-ceiling windows, dark leather chairs, no people, premium corporate feel
```

### Eviction
```
A residential keyring left on a dark windowsill, single warm light from outside,
mood of transition, no faces, restrained editorial
```

### Criminal Rights
```
A close-up of well-worn law book spines on a dark mahogany shelf,
single warm reading lamp light, no titles legible, contemplative
```

### Family Law
```
Two empty coffee cups on a dark kitchen counter at dawn, soft warm window light,
no people, gentle melancholy
```

### Debt
```
A black ceramic piggy bank on a dark surface with a single faint gold coin
beside it, single soft spotlight, restrained, no clutter
```

### POPIA
```
A locked vintage brass padlock on a black slate surface, key absent,
single warm side light, macro detail, sense of secured boundaries
```

### Property
```
An architect's flat-lay: rolled blueprints, brass key, leather notebook,
on dark wood, warm overhead light, top-down composition
```

---

## xAI (Grok Image) — Stylized Variants

For more dramatic / mood-driven shots, use xAI with these adjustments:

```
[SUBJECT], cinematic chiaroscuro lighting, single gold beam,
deep blacks (#0a0a0a), warm highlights (#c9a25a), painterly quality,
sense of weight and gravitas, like a Wes Anderson meets film noir aesthetic,
3:2 ratio, no text
```

---

## Workflow Notes

1. **Always generate at 3:2** (or 9:16 for video b-roll) — never 1:1 unless cropping specifically for Instagram feed
2. **Always inspect for hands/faces** — generators still struggle; reroll if anatomy is off
3. **Save originals** to `marketing/images/blog/originals/` before any cropping
4. **Watermark only the cropped/published versions** — keep originals clean
5. **Color check:** if the generated image's blacks shift toward blue/grey, run a second pass with "warm shadows, true black tones" added to the prompt
