# Palettes (OKLCH recipes)

Author colours in OKLCH (L lightness 0-1, C chroma 0-0.37, h hue 0-360). `dna_generate.py` implements the recipes below with gamut mapping; `Lab.oklch(l,c,h)` does it in the browser.

## Hue wheel (OKLCH degrees, approx.)
red 25-30 | orange 55 | amber 80 | yellow 100 | lime 125 | green 145-155 | teal 185 | cyan 205 | sky 235 | blue 255 | violet 285 | magenta 330 | pink 355.

## Palette logics
| mode | recipe | feels | references |
|---|---|---|---|
| mono (dark) | bg L.14 C.035 h ; bg2 L.32 C.10 ; ink L.97 C.025 ; accent L.86 C.25 ; accent2 L.94 C.09 h+18 | focused, night, techno | v01, v07, v09 |
| mono (light) | bg L.96 C.025 ; ink L.20 ; accent L.58 C.22 | clean, medical, calm | |
| duotone | h1 and h2 = h1 + 110/140/180/210 ; bg paper (L.95 C.03 h85) or dark ; accent h1, accent2 h2 | poster, retro, print | v03 |
| neutral-pop | warm or cool neutral bg/ink + ONE accent L.60-.72 C.21-.22 | premium, editorial, product | v06, v10 |
| tri-accent | neutral base + accents at h, h+dh, h+2dh with dh 100/120/140 | playful explainer | v08 |
| analogous | h, h+s, h+2s (s 22-38) rich | warm sunsets, calm gradients | |
| complementary | bg tinted h ; accent at h+180 | dramatic, glass UI | v05 |
| paper-ink | off-white paper + near-black ink + ONE red | raw, collage | v11 |

## Contrast rules
- ink vs bg >= 4.5:1 (body), display >= 3:1. `--check` enforces ink >= 4.5.
- accent vs bg >= 3:1 if used as text; for shapes >= 2.2:1.
- Never put coloured text on a coloured background of similar lightness: separate by L (difference >= 0.35).
- Glow colours (bloom) = accent at L .86+; keep bg L <= .16 for glow to read.

## Gradients without the AI look
- Single-hue vertical ramps (bg L.14 -> bg2 L.32 same hue) with a floor reflection beat purple-to-blue meshes.
- Use noise to move the gradient centre slowly (`Lab.noise`), never a static linear gradient.
- Add grain on top (texture.grain 0.04-0.12) to kill banding.

## Hue-avoidance list (AI defaults)
Purple/blue on near-black (h 245-305 + L<.22), orange #ff4f1a on #0b0b10, teal-and-magenta mesh. Fine if the brief demands them; otherwise `--check` warns.

## Accessibility of motion colours
Flashes (whiteFlash) <= 3 frames, <= 3 per second; avoid red/green-only distinctions for data (add shape or label).
