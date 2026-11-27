# The World in One Day — Friday 27 November 2026

A one-image broadsheet of the world's news of **Friday 27 November 2026**,
drawn deterministically with Python + PIL by `main.py` and written to
`/output/entry.png` (1024×1024, under 1 MiB). An entry for the make.fun
bounty **news-image-20261127**.

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

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Standard library + PIL only. Fonts ship in `assets/fonts/` so the render
is byte-identical anywhere. The build fails loudly if any text would
overflow its box — the submitted render has zero overflow warnings.
