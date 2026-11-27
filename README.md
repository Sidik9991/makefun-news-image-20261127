# The World in One Day — Friday 27 November 2026

A one-image broadsheet of the world's news of **Friday 27 November 2026**.
The page was drawn deterministically with Python + PIL by `draw.py` and
is committed here as `entry.png` (1024×1024, under 1 MiB). The graded
entrypoint is `main.ts` — Node standard library only — which checks the
committed PNG against the file rules (signature, closing IEND chunk,
size and dimension caps) and copies it byte-for-byte to
`/output/entry.png`. An entry for the make.fun bounty
**news-image-20261127**.

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/Sidik9991/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/Sidik9991/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127)

Bounty page: https://make.fun/bounty/news-image-20261127

## What's on the page

- Giant serif masthead: **FRIDAY 27 NOVEMBER 2026**, red sub-headline
  naming the three leads, and a KPI strip of six checkable numbers
  (600,000+ US homes without power · 10 killed in Gaza · 2 Italians dead
  in Kuwait · Brent $94.71 · VIX +60% in November · 42,000 US flights
  due Friday).
- **Three big pictured leads** (32% of the page): the Kuwait drone strike
  that killed two Italian Rheinmetall technicians, with Iran's denial;
  Hamas weighing its reply after Israel killed 10 in Gaza; world stocks
  steadying on Friday after the tariff-and-AI rout.
- **Twelve small pictured panels** — the Thanksgiving nor'easter's
  fallout, Ukrainian drones at Nevinnomyssk, Zelenskyy's assault warning,
  Netanyahu's trial, the Ibiza tanker capsize, the Depardieu trial
  ruling, the Gukesh–Sindarov draw, Hong Kong's fire anniversary,
  Dhaka's garment-worker protest, the Australia–Solomon Islands pact,
  the $621.9m F-16 package for Kyiv, and Myanmar rejecting parts of the
  ICJ ruling.
- A dotted world map with numbered pins for the pictured stories only,
  a 22-line digest (**37 stories, 15 pictured, 9 regions** in all), a
  DATE CHECK box naming the big other-days stories left out (the Karachi
  collapse fell on Wednesday), and the sourcing key in the footer.
  Per-story sources: see `SOURCES.md`.

## Run it

Ship the entry (what the grader runs):

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Redraw the page from source (regenerates `entry.png`):

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 draw.py
```

`main.ts` needs nothing beyond Node itself. `draw.py` uses the standard
library + PIL; fonts ship in `assets/fonts/` so its render is
byte-identical anywhere. Text that would overflow its box is shrunk
step by step until it fits, and anything still overflowing is logged
as a warning rather than failing the build — the submitted render has
zero overflow warnings.
