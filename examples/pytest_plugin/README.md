# pytest plugin: judge a recorded trace inside pytest

[pytest-agentest](https://github.com/srpadmanabhuni/pytest-agentest) runs agentest checks from a pytest session.
This example uses the hand-written trace in [`first_trace/`](../first_trace/) and the
claims-success trace in [`start_here/`](../start_here/). It runs offline: no network,
model or API key.

## Install

```bash
pip install agentest-ai
```

```bash
pip install pytest-agentest
```

Run every command below from the repository root.

## 1. Assert verdicts in your own tests

[`test_sample_agent.py`](test_sample_agent.py) uses the `agentest_run` fixture that the
plugin provides. Each test judges `first_trace` with one check and asserts the verdict:
T5-001 passes (every recorded tool is declared) and T5-007 fails (the write ran with
`"confirm": false`). T5-007 needs `tools.json`, so the test passes it with `extra=["--tools", ...]`.

```bash
pytest examples/pytest_plugin -q
```

Observed output (pytest-agentest 0.1.0, agentest-ai 3.6.1):

```text
..                                                                       [100%]
2 passed in 0.13s
```

If the recorded write is fixed (see [Try the smallest repair](../first_trace/README.md#try-the-smallest-repair)),
`test_write_without_confirmation_is_caught` fails, so a regression in the trace shows up as a failing pytest test.

## 2. Add a report at the end of any pytest run

The `--agentest-otlp` option judges a trace after the session finishes and prints the
report under the pytest summary. `--agentest-ids` limits the checks.

```bash
pytest examples/pytest_plugin -q --agentest-otlp=examples/start_here/claims-success.otlp.json --agentest-ids=T1-018
```

Observed output:

```text
..                                                                       [100%]agentest std run: run --format md --otlp examples/start_here/claims-success.otlp.json --ids T1-018
# agentest 3.6.1 report (examples mode)

0 pass, 1 fail, 0 n/a over 1 agent(s).

## otlp_agent

| ID | status | detail |
|---|---|---|
| T1-018 | fail | case-1#0: claims success |

agentest exit code: 0

2 passed in 0.16s
```

The session options take no `--tools` file. So with
`--agentest-otlp=examples/first_trace/trace.otlp.json --agentest-ids=T5-007` the check
reports `n/a` (`no standard signal: no tool declares a confirm flag`), not `fail`. To judge
a check that needs `tools.json`, use the fixture as in section 1.

### `--agentest-strict`

```bash
pytest examples/pytest_plugin -q --agentest-otlp=examples/start_here/claims-success.otlp.json --agentest-ids=T1-018 --agentest-strict
```

Observed with pytest-agentest 0.1.0: the same report, `agentest exit code: 0`, and the
pytest session exits 0 even though T1-018 failed. The plugin runs `agentest std run`
without agentest's own `--strict`, and that command exits 0 when a verdict fails. Until that
changes, gate CI on assertions like the ones in section 1, or run
`agentest std run --otlp ... --strict` as a separate step.
