# Ranked issues

**Filled by:** session 9, kept current through session 14.

| rank | issue | impact |
|---:|---|---|
| 1 | Lexical retrieval misses paraphrases with no word overlap | A user who asks in their own words can get a refusal for a question the corpus actually supports. |
| 2 | The evaluator checks which doc was cited, not whether the answer is faithful | A citation can look correct while the answer is still unsupported by the cited evidence. |
| 3 | Nothing bounds a provider that hangs rather than failing | A provider that never responds can stall the research flow instead of producing a safe result. |

## Rank 1, fixed

- The fix: improve retrieval so supported paraphrased questions can match relevant corpus content.
- The regression test: `test_regression_rank_1_of_the_issue_list` in `tests/test_contract.py`.
- Before and after: see [EVAL_REPORT.md](EVAL_REPORT.md).
