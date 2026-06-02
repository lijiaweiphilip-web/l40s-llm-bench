# Feedback Request Template

Use this template when asking a real person to try the first-user smoke test.
Do not record invented testers, assumed reactions, or feedback that has not
actually been received.

Keep the ask small: dry-run plus fake-server only, no GPU, no real model
server, no private endpoints.

## English Outreach Text

Subject: Quick dry-run feedback request for `l40s-llm-bench`

Hi [name],

I am looking for early usability feedback on `l40s-llm-bench`, a small
reproducible benchmark harness scaffold. This request does not require a GPU or
a model server. The goal is only to see whether the dry-run and local fake
server path is clear on a fresh machine.

If you have 10 to 15 minutes, could you try:

1. Open `[repo URL]`.
2. Follow `docs/first-user-smoke-test.md`.
3. Share what was confusing, what failed, and whether the expected files were
   created.

Please do not run a real benchmark for this request, and please do not share
API keys, private endpoint URLs, private hostnames, or confidential benchmark
data. Feedback can go in `[issue form URL]` or directly to `[preferred
channel]`.

Thank you, and no pressure if now is not a good time.

## Chinese Outreach Text

Subject: 想请你帮忙做一次 `l40s-llm-bench` 的 dry-run 反馈

你好 [name]，

我想收集一次 `l40s-llm-bench` 的早期易用性反馈。这个请求不需要 GPU，
也不需要真实模型服务器；目标只是确认 dry-run 和本地 fake server 的流程
在新环境里是否清楚、是否能跑通。

如果你有 10 到 15 分钟，可以请你试一下：

1. 打开 `[repo URL]`。
2. 按照 `docs/first-user-smoke-test.md` 操作。
3. 告诉我哪里不清楚、哪一步失败了，以及预期文件是否生成。

这次请不要运行真实 benchmark，也不要分享 API key、私有 endpoint、私有
主机名或任何保密的 benchmark 数据。反馈可以发到 `[issue form URL]`，也
可以直接发给 `[preferred channel]`。

谢谢！如果现在不方便也完全没关系。

## Feedback Questions

Copy these into a message or issue if a tester prefers not to use the GitHub
issue form:

```text
Repository commit tested:
OS and Python version:
Which path did you try? dry-run / fake-server sanity suite / both
Did installation work?
Did the expected files appear?
What was the first confusing step?
What was the first failure, if any?
How long did the dry-run and fake-server path take?
What should be changed before asking another first-time user?
Anything you removed or redacted before sharing?
```

## Follow-Up Text

English:

Thanks for trying the dry-run/fake-server path. I will treat this as usability
feedback only, not as benchmark evidence. If you noticed anything confusing
after sending the first note, feel free to add it to the same thread.

Chinese:

谢谢你试了 dry-run/fake-server 流程。我会把这些内容只当作易用性反馈，
不会当作 benchmark 证据。如果你之后又想到哪里不清楚，可以继续补充在
同一个反馈里。
