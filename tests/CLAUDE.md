# tests/CLAUDE.md — Testing Agent Spec

## 🧪 Testing Agent
**Trigger:** After pipeline or API is built
**Delegate when:** Writing `tests/test_pipeline.py`, running the full test suite, reporting results.
**Input to provide:** Pipeline path, label encoder path, data path, expected accuracy threshold.
**Agent must:** Write the test script (artifact integrity, single-sample predictions, full test-set evaluation, per-class accuracy, consistency check, probability check); run it; return ONLY the test summary output.
**Returns:** Pass/fail per test, overall accuracy, confirmation of 16/16 checks or list of failures.
