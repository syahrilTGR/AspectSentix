#!/usr/bin/env python3
"""Build gadget_reviews.csv for AspectSentix.

Samples ~300 Indonesian marketplace reviews from the
revanmd/indonesian-dataset-SA-ML repo (already sparse-checked-out at
_dataset_repo/dataset/<category>/), stratified by rating 1-5.

Composition per category (100 reviews):
  - 95 "rich" reviews  (>= MIN_RICH_LEN chars) -> real ABSA signal
  -  5 "short" reviews (<  MIN_RICH_LEN chars) -> deliberate edge cases
    (emoji-only, one-word, too vague to extract an aspect)

Reproducible: fixed seed, sorted file traversal.
"""

import collections
import csv
import glob
import os
import random
import sys

SEED = 42
CATEGORIES = ["laptop", "handphone", "tablet"]
PER_CATEGORY = 100
N_SHORT_EDGE = 5          # per category
MIN_RICH_LEN = 15         # chars; below this a review rarely mentions an aspect
REPO_DIR = "_dataset_repo"
OUT_PATH = os.path.join("dataset", "gadget_reviews.csv")
RATINGS = ["1", "2", "3", "4", "5"]


def load_pool(cat):
    """Return (rich, short) lists of (review, rating) for one category."""
    rich, short = [], []
    for fp in sorted(glob.glob(os.path.join(REPO_DIR, "dataset", cat, "*.csv"))):
        try:
            with open(fp, encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    rev = (row.get("review") or "").strip()
                    rat = (row.get("rating") or "").strip()
                    if not rev or not rat:
                        continue
                    try:
                        rat = str(int(float(rat)))  # "4.0" -> "4"
                    except ValueError:
                        continue
                    if rat not in RATINGS:
                        continue
                    item = (rev, rat)
                    (rich if len(rev) >= MIN_RICH_LEN else short).append(item)
        except (UnicodeDecodeError, csv.Error) as exc:
            print(f"  warn: skipping {fp}: {exc}", file=sys.stderr)
    return rich, short


def stratified_sample(pool, n, rng):
    """Pick n items from a (review, rating) pool, balanced across ratings.

    Round-robins over shuffled per-rating buckets so each rating is
    represented as evenly as the pool allows.
    """
    buckets = {r: [] for r in RATINGS}
    for rev, rat in pool:
        buckets[rat].append((rev, rat))
    for items in buckets.values():
        rng.shuffle(items)

    cursor = {r: 0 for r in RATINGS}
    chosen = []
    while len(chosen) < n:
        progressed = False
        for rat in RATINGS:
            if len(chosen) >= n:
                break
            items = buckets[rat]
            if cursor[rat] < len(items):
                chosen.append(items[cursor[rat]])
                cursor[rat] += 1
                progressed = True
        if not progressed:  # pool exhausted across all ratings
            break
    return chosen


def main():
    rng = random.Random(SEED)
    if not os.path.isdir(REPO_DIR):
        sys.exit(f"missing {REPO_DIR}/ - run the sparse clone first (see README)")

    rows = []
    print(f"{'category':<11} {'rich':>5} {'short':>6} {'sampled':>8}")
    for cat in CATEGORIES:
        rich, short = load_pool(cat)
        picked_rich = stratified_sample(rich, PER_CATEGORY - N_SHORT_EDGE, rng)
        picked_short = stratified_sample(short, N_SHORT_EDGE, rng)
        picked = picked_rich + picked_short
        rng.shuffle(picked)
        rows.extend((rev, rat, cat) for rev, rat in picked)
        dist = collections.Counter(rat for _, rat in picked)
        print(
            f"{cat:<11} {len(rich):>5} {len(short):>6} {len(picked):>8}   "
            f"rating={dict(sorted(dist.items()))}"
        )

    rng.shuffle(rows)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["review", "rating", "category"])
        for rev, rat, cat in rows:
            writer.writerow([rev, rat, cat])

    lens = sorted(len(rev) for rev, _, _ in rows)
    print(
        f"\nwrote {len(rows)} rows -> {OUT_PATH}\n"
        f"  review length: min={lens[0]} median={lens[len(lens)//2]} max={lens[-1]}\n"
        f"  edge cases (<{MIN_RICH_LEN} chars): "
        f"{sum(1 for v in lens if v < MIN_RICH_LEN)}"
    )


if __name__ == "__main__":
    main()
