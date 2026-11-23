[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/andikaprp/makefun-news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/andikaprp/makefun-news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# One Page — The World on Monday 23 November 2026

Entry for the make.fun competition **news-image-20261123**: sum up one
day's world news in a single image.
[Bounty: Sum up 23 November's world news in one image](https://make.fun/bounty/news-image-20261123)

## What is in the image

A single-page cream broadsheet of Monday 23 November 2026, built from
the evening census of 36 verified Monday stories. The page presents
**35 items**: **13 headlined cards**, each illustrated with its own
rich-art panel, plus **16 numbered briefs** and a **DATE CHECK box**
of 6 verified Saturday/Sunday items, each day-labelled so they are
not mistaken for Monday's news.

Rich art: every one of the 13 cards carries an original code-authored
panel - layered multi-frequency gradient, deterministic per-channel
grain, glow and vignette, plus a drawn scene for its subject
(68,429 unique colours on the page, date at 106px).

Every story on the page happened, or was first reported, on Monday
23 November 2026 in some time zone. Every figure was checked against
its census source before printing.

## How it runs

- `main.py` — the entrypoint. Standard library only. It copies the
  shipped `entry.png` into the output directory (`MAKEFUN_OUTPUT_DIR`,
  default `/output`). The copy is byte-identical on every run.
- `entry.png` — the finished page (1024 x 1024, under 1 MiB).
- `renderer.py` — the renderer that drew the page: layout, rich-art
  panels and type are all computed from the data file, so the page can
  be rebuilt or revised by editing the data.
- `data.json` — the day's census as data: headlines, summaries,
  figures, places and regions for every presented story, plus the
  held-back not-Monday list.

## Run it

```sh
python3 main.py
```

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
