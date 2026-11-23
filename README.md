[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/andikaprp/makefun-news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/andikaprp/makefun-news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# One Page — The World on Monday 23 November 2026

Entry for the make.fun competition **news-image-20261123**: sum up one
day's world news in a single image.
[Bounty: Sum up 23 November's world news in one image](https://make.fun/bounty/news-image-20261123)

## What is in the image

A single-page cream broadsheet of Monday 23 November 2026. The page
presents **20 items**: **11 headlined cards**, each illustrated with its
own rich-art panel (layered multi-frequency gradient, deterministic
grain, soft glow and vignette, plus a drawn scene for its subject;
banner label and source tag on every panel), plus **3 numbered briefs**
and a **DATE CHECK box** of 6 verified Saturday/Sunday items, each
day-labelled so they are not mistaken for Monday's news, and a
not-yet-reported line naming what had not landed.

The 11 headlined stories: KOSPI falls 4.04% Monday; NZ 190-5 trail 162
LIVE in the Wellington Test; Dymer: 6 dead, boy 7 rescued; Australia
flash PMI 46.1; NZ retail sales +2.2%; Albanese trails Taylor in the
Newspoll; Bitcoin $60,957 Monday; NHS AI trial: 700,000 women; Hang
Seng opens -1.08%; robot maker Microintelligence revives its Hong Kong
IPO (Changzhou); and Molly Meldrum dies at 83 in Melbourne.

Every story on the page happened, or was first reported, on Monday
23 November 2026 in some time zone. Every figure was checked against
its primary source before printing.

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
