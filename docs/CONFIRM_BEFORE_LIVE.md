# Confirm before going live

**Go-live gate:** one verified compute route, one playable arena, a durable checkpoint path, and a tested recovery path. A GPU-specific learning-time estimate is not available yet.

Public docs describe GPU sandboxes as separately enabled private-preview access. Their documented serverless GPU is one RTX PRO 6000 Blackwell Server Edition; CKS allocations can differ. Jeremy's product-manager access may be another offering. Treat “B40 now, H100 next week” as user-reported access until the contact identifies it and `doctor` verifies the allocation. Do not substitute A40, L40, B200, or the public serverless model for B40. [GPU sandbox documentation](https://docs.coreweave.com/products/sandboxes/gpu-sandboxes)

## Seven questions for the CoreWeave contact

1. **Exact compute:** What product/launch path and GPU model does my “B40” access mean? What VRAM, CPU, RAM, PyTorch/CUDA image, and H100 allocation are enabled for my account? Can I run my own persistent PyTorch training process there?
2. **Packages and network:** Which packages are preinstalled, can I use `pip`/virtual environments, and can the sandbox reach PyPI, `files.pythonhosted.org`, required framework-wheel hosts, GitHub, and the later chess-data source? If not, what approved image or wheel-upload route should I use?
3. **Lifetime and disconnects:** What creation-time lifetime should I request for a three-hour stream plus setup? What happens on browser disconnect, idle periods, expiry, or preemption? Is there a queue/startup delay we should budget?
4. **Private display:** How do I open the arena on **port 8765** through a private/authenticated preview? Must the port be declared when creating the sandbox? Does the proxy preserve WebSockets/SSE and strip its path prefix? What listener address does it require?
5. **Durable storage:** What exact writable path survives sandbox termination? How do I download, snapshot, restore, and verify the entire run directory? Does that include the Python environment, or only selected files?
6. **Credits and billing:** What are my actual credits, per-resource rates, spend caps, and concurrency quotas? Which command/UI action fully terminates allocation and billing after the stream?
7. **GPU count and placement:** Is my limit one GPU per sandbox? If multiple GPUs are allowed, through which placement/runner, with what CPU allocation and single-node restrictions? Episode 1 only requires one; Episode 2 must not assume more.

## Twenty-minute functionality preflight

Do not do an off-camera strength run. Do not tune against Jeremy's score or prepare a trained winner. Record what was checked and disclose this brief connectivity/functionality check when the stream starts.

| Minutes | Check | Passing evidence |
| --- | --- | --- |
| 0–4 | Confirm allocation/image and exact dependency-install route; run `python race.py doctor`. | Selected versions and a successful CUDA operation, or an explicitly accepted CPU fallback. |
| 4–7 | Run `python race.py smoke`. | Reproducible positive-seed game and counters, headless operation, no learning. |
| 7–11 | Start `python race.py serve --out preflight --port 8765` through the intended preview route. | Browser controls work, preview matches committed placement, lines/pieces update, OBS captures only the intended scene. |
| 11–15 | Write and retrieve a tiny test file through the approved durable path; close/reopen the preview connection. | Exact bytes recover; reconnect behavior is understood. A claimed durable mount without a readback is not verified. |
| 15–18 | Verify the application's checkpoint/action-log recovery with disposable functionality fixtures or the repo's documented smoke checks. | Recovery behavior is understood without preserving off-camera learned weights. Do not treat this as a full disaster-recovery guarantee. |
| 18–20 | Check the face-camera-only scene, secret entry procedure, local/CPU fallback, and explicit compute stop action. | No credential-bearing URL, token, account details, environment dump, or shell history is captured. |

If a check fails, choose the fallback before announcing a GPU race. The full-loop optimizer benchmark and the real training run occur on stream. Neither the preflight nor installing dependencies constitutes a hidden training day.

## Decisions to record

Record the actual GPU name and image, approved dependency versions, preview/port route, durable path, lifetime, budget, and stopping procedure in the run notes. Mark unanswered entries **UNKNOWN**. Keep credentials and private account identifiers out of those notes and the broadcast.

Use custom PyTorch code in confirmed compute for the Tetris learner. Public managed Serverless Training exposes a supported foundation-model catalog; it is not evidence that arbitrary small DQNs or new chess architectures can be submitted to that service. [Available models](https://docs.coreweave.com/products/post-training/serverless-training/available-models)

Platform details to recheck with the contact: [configuration, network and lifetime](https://docs.coreweave.com/products/sandboxes/client/guides/sandbox-configuration), [endpoint creation/authentication](https://docs.coreweave.com/products/sandboxes/public-endpoints), [notebooks](https://docs.coreweave.com/products/notebooks), and [billing behavior](https://www.coreweave.com/forge-pricing/inference-agents). Public documentation is background evidence, not confirmation of the user's private-preview limits.
