# Evaluation — AspectSentix

**Date:** 2026-09-14  
**Program:** IBM SkillsBuild × Hacktiv8 Capstone

---

## 1. Methodology

AspectSentix is a **prompt-engineered LLM pipeline**, not a fine-tuned classifier. There is no labeled gold-standard dataset for aspect-based sentiment in Indonesian marketplace reviews, so traditional metrics (precision / recall / F1 per class) are not available.

Instead, evaluation is **qualitative + confidence-gated**:

| Signal | What it measures |
|---|---|
| `confidence` per (review, aspect) pair | Model certainty — used to flag uncertain outputs |
| Coverage rate | % of reviews where ≥1 aspect is detected |
| Low-confidence flag rate | % of outputs below the review threshold |
| Manual spot-check | Human verification of flagged items |

---

## 2. Coverage

### Sample: `dataset/gadget_reviews_90.csv` (90 reviews)

| Metric | Value |
|---|---|
| Total reviews | 90 |
| Reviews with ≥1 aspect detected | 82 |
| **Coverage** | **91.1%** |
| Reviews without any aspect | 8 (IDs: 3, 8, 18, 19, 83, 88, 89) |

The 8 uncovered reviews are predominantly short / ambiguous ("bagus", emoji-only, cut off). This matches the design intent: the pipeline does not force a label when it cannot identify an aspect.

### Full run: `laporan_fokus_pengiriman_cs.md` (125 aspect pairs from a separate focused run)

| Metric | Value |
|---|---|
| Total aspect pairs | 125 |
| Reviews without aspect | 9 (IDs: 3, 8, 18, 19, 22, 75, 82, 88, 90) |
| Coverage | ~92.8% |

The two reports differ in sample size (90 vs. a larger focused run) and distribution, but coverage is consistent (~92%).

---

## 3. Confidence Distribution

From `output/laporan_final.md` — 12 low-confidence rows (threshold: ≤ 0.6):

| Confidence | Count | % of low-confidence |
|---|---|---|
| 0.4 | 1 | 8.3% |
| 0.5 | 1 | 8.3% |
| 0.6 | 9 | 75.0% |
| 0.7 | 1 | (above threshold — appears in table context) |

**Aspects most affected by low confidence:**

| Aspect | Low-confidence count |
|---|---|
| `product_quality` | 7 |
| `shipping` | 2 |
| `packaging` | 1 |
| `price` | 1 |
| `authenticity` | 1 |

`product_quality` dominates because many short reviews ("barang ok", "barang udah nyampe, bagus") are genuinely ambiguous — they imply quality but do not name it explicitly.

---

## 4. Sentiment Distribution Stability

Comparing two independent runs on overlapping data:

| Report | Aspect pairs | Positive | Negative | Neutral | Negativity share |
|---|---|---|---|---|---|
| `laporan_final.md` | 138 | 64 | 73 | 1 | 52.9% |
| `laporan_fokus_pengiriman_cs.md` | 125 | 59 | 62 | 4 | 49.6% |

**Observation:** Negativity share is stable (~50–53%), but absolute counts differ. This is expected for LLM-based extraction without deterministic normalization — the same review can be split into different aspect counts across runs. The PRD acknowledges this risk (Section 12: "Output LLM tidak konsisten antar-tahap") and mitigates it with `temperature=0` + Structured Output Parser. The remaining variance is an acceptable trade-off for a zero-shot pipeline.

---

## 5. Known Limitations

1. **No ground truth.** Without a labeled dataset, there is no way to compute accuracy. The confidence score is a self-reported proxy, not a calibrated probability.
2. **Closed taxonomy.** The 9-aspect scheme misses domain-specific aspects (e.g., "fragrance" for skincare). Out-of-scope aspects are silently dropped.
3. **Indonesian slang normalization is prompt-dependent.** New slang or regional variants may not be caught by the current prompt template.
4. **No reproducibility guarantee for numeric tables.** LLM aggregation is non-deterministic by nature; running the same flow twice can produce slightly different counts. The `temperature=0` setting reduces but does not eliminate this.
5. **Dataset is not bundled.** `build_dataset.py` depends on an external sparse-clone (`_dataset_repo/`). The generated CSVs (`gadget_reviews.csv`, `gadget_reviews_90.csv`) are included, but `build_dataset.py` cannot be re-run from this repo alone.

---

## 6. What Worked Well

- **Coverage at 91%** with zero forced labels — the pipeline correctly identifies when it cannot extract an aspect.
- **Confidence flagging** caught 12 ambiguous reviews (including ID 2 with c=0.4, a truncated review) that would otherwise have been silently mislabeled.
- **Aspect-level granularity** surfaced actionable differences that a global sentiment score would hide — e.g., 15 negative `authenticity` reviews vs. 26 negative `product_quality` reviews lead to different remediation actions.
- **Stratified sampling** ensured balanced representation across ratings 1–5, preventing bias toward the dominant class.

---

## 7. Next Steps (from PRD Section 15)

1. Move statistics computation from LLM to deterministic code component → reproducible tables.
2. Integrate marketplace API for automated daily review ingestion.
3. Add trend monitoring across time windows.
4. Automated alerts when an aspect's negative share exceeds a threshold.
5. Competitor benchmarking in the same category.
