# l40s-llm-bench

minimal scaffold for reproducible llm inference benchmark experiments.

## purpose

this repository starts as a small benchmark skeleton. it does not claim performance results yet. the first goal is to make future results traceable through configs, raw logs, environment notes, summary tables, and clear limitations.

## mvp scope

first path is vllm. llama cpp comes after the vllm path is working. the first real run should use one small open model. the first metrics should cover latency, output tokens per second, error status, and environment notes. dry run comes before real gpu runs.

## result policy

no benchmark number should be shown without model version, framework version, hardware notes, config, raw log path, and a repeated run policy.

## current status

starting repository. no benchmark results are claimed yet.

## next steps

add benchmark config schema. add dry run benchmark script. add jsonl result schema and validation tests. add csv and markdown summarizer. run the first real benchmark after the dry run path is verified.

## limitations

this is not yet a complete benchmark suite. early results, when added, should be treated as local measurements rather than universal claims about any gpu, model, or inference framework.
