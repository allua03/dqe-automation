---
name: generate-parquet-dq-tests
description: >-
  TODO: One or two sentences — what the skill generates, when to invoke it,
  and what it must refuse (framework/Jenkins/conftest). Example pattern:
  "Creates parquet_files test modules from docs/parquet-aggregated-data-mapping.md …"
disable-model-invocation: true
---

# Generate Parquet DQ tests

Complete this skill as **Step 2** of the PyTest DQ assignment. Read first:

- `PyTest DQ Framework/docs/test-automation-strategy.md` — **§5 Skill contract**, **§6 Test design standard**
- `docs/parquet-aggregated-data-mapping.md` — dataset definitions (expected SQL comes from here)

**Do not** paste expected SQL for the three named datasets into this skill.  
**Do not** instruct the agent to copy SQL from `data_dev/`.

When finished, every `TODO` below must be replaced. Run the **Skill review** checklist before using the skill to generate tests.

## When this skill applies

TODO: When the agent should use this skill; what must already exist (framework); allowed paths; when to refuse.

## Inputs you must have

TODO: Required inputs and where mapping lives (`docs/parquet-aggregated-data-mapping.md`). What to do if mapping is missing. Forbidden sources.

## Hard rules

TODO: Numbered rules — at minimum cover file path, source vs target, mapping-only SQL, no dataset SQL in SKILL.md, library methods only, markers, not-null columns. Use TAS §5.4 as your checklist.

## Workflow

TODO: Steps from mapping → SQL → module → markers. Keep it operational, not a copy of TAS prose.

## Template

Paste the **full** module skeleton from TAS §6.2 (placeholders only). Align source/target with TAS, not swapped names in `test_examples.py`.

```python
# TODO: replace with full template from TAS §6.2
```

## SQL derivation (generic)

TODO: Generic rules only (joins, dates, names, aggregates, GROUP BY). No SQL for a specific dataset.

## After generation

TODO: Running pytest only if asked; do not rewrite expected SQL to force green runs.

---

## Skill review (self-check before Step 3)

Reject your own skill if any of these are true:

- [ ] Contains concrete expected SQL for `facility_name_min_time_spent_per_visit_date`, `facility_type_avg_time_spent_per_visit_date`, or `patient_sum_treatment_cost_per_facility_type`
- [ ] Tells the agent to use `data_dev/` or parquet loader SQL
- [ ] Omits completeness, count, uniqueness, or not-null
- [ ] Swaps Postgres vs Parquet fixtures or generates trivial always-pass checks
- [ ] Any section still says `TODO`
