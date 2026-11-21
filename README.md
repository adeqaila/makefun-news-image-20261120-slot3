# The World in One Day — D3

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/adeqaila/makefun-news-image-20261120-slot3/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/adeqaila/makefun-news-image-20261120-slot3/reward.svg)](https://make.fun/bounty/news-image-20261120)

One image summing up the world's news of **Friday 20 November 2026**:
35 stories across 7 regions, every one dated that Friday. Three big stories
with drawn visuals (Kyiv's bridges hit, Cyclone Akvan's landfall, the AI
sell-off), ten more in a grid, a map of where it happened, 22 more stories,
a by-the-clock strip, and a date-check box naming what was left out
(Thursday 19 November's news and things that had not happened yet).

## Files

- `entry.png` — the image (1024×1024, under 1 MiB).
- `main.py` — stdlib-only entrypoint; copies `entry.png` to the output
  directory as `entry.png`. Deterministic: two runs write the same bytes.
- `compose.py` — the generator (stdlib + PIL) that drew `entry.png`.
  Run `python3 compose.py [out.png]` to re-render it.
- `AUDIT.md` — per-story verification: 28 confirmed, 7 fixed, 0 invented.
  Every number is sourced; three of the reference broadsheet's claims were
  caught and corrected (Bukele's filing was 19 Nov, Seoul's impeachment
  target is the chief justice, Sydney fell 1.6% not 1.8%).

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```
