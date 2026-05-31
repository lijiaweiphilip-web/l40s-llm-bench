# Fake Server Validation Experiment

This experiment checks whether the benchmark client can recover known
streaming latency values before any GPU time is spent.

The fake server implements the OpenAI chat-completions shape and emits
server-sent events with controlled delays:

- `ttft_ms`: delay before the first streamed token
- `tpot_ms`: delay between later streamed tokens
- `tokens`: maximum streamed token events

Run the server in one terminal:

```bash
python scripts/fake_openai_server.py --port 18000 --ttft-ms 120 --tpot-ms 25 --tokens 8
```

Run the benchmark in another terminal:

```bash
python scripts/bench_openai_compatible.py \
  --config configs/fake_server_matrix.yaml \
  --models-config configs/models.yaml \
  --output results/raw/fake_server_streaming.jsonl \
  --stream

python scripts/summarize_results.py --input results/raw/fake_server_streaming.jsonl --output-dir results/tables
```

Expected behavior:

- `ttft_ms` should be close to the server's configured `--ttft-ms`.
- `tpot_ms` should be close to the server's configured `--tpot-ms`.
- small deviations are normal on a desktop OS because scheduling and socket
  buffering add noise.

This is not a model benchmark. It is a measurement harness sanity check.

For the packaged suite, run:

```bash
python scripts/run_sanity_checks.py
```

The suite starts local fake servers for:

- baseline streaming
- high TTFT
- slow TPOT
- HTTP 500 error handling

It writes raw JSONL to `results/raw/sanity_checks.jsonl` and a short report to
`results/tables/sanity_checks.md`.
