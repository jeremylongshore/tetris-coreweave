# Validation record

This describes prototype checks performed while preparing the source handoff. It does not mark the Beads execution gates complete. No prototype checkpoint or trained weights are included in the repository.

## Observed locally

- Python 3.12, PyTorch 2.6.0+cpu, NumPy 2.2.6, Gymnasium 1.2.3, headless OpenCV 4.10.0.84, and Tetris Gymnasium 0.3.1 with its classic backend.
- Shared environment: 615 candidate-preview versus actual-step comparisons across 18 sampled states, deterministic seed/action replay, finite round cap, top-out behavior, and JSON-serializable frames.
- Scoring fixtures: one cleared line awards 10 line-clear points; four cleared lines award 160. Official counters use actual cleared lines and exclude the upstream alive bonus.
- `race.py smoke` passed with 40 candidates and 16 features.
- Short CPU training and checkpoint resume passed. A split/resumed CPU run matched uninterrupted continuation for model, target, replay, optimizer counters, NumPy RNG, and Torch RNG in the tested case.
- HTTP final-match integration: all three human rounds use the same seeds as the AI, AI final results remain withheld until the human completes the rounds, and six paired results plus replay are produced.
- JavaScript syntax checking passed for the arena. This is not a visual browser/OBS rehearsal.
- Beads plan validation passed: 8 epics, 30 tasks, 57 explicit blocking edges, all dependency targets resolve, and no cycles. The fresh plan has one ready leaf, `TCF-001`.
- Importer syntax and dry-run validation passed; invalid cycles and missing dependency targets are rejected before mutation.

The brief prototype training checks establish functionality only. Those weights were discarded from the deliverable and must never be used as a contestant. The live race starts from new random weights and records checkpoint zero.

## Still unverified

- Actual Forge permissions, install/network policy, image, CPU allocation, GPU identity, usable VRAM, credits/quotas, session duration, multi-GPU policy, persistent storage, and authenticated preview route.
- GPU training throughput, CUDA checkpoint continuation, numerical stability on the chosen provider build, and time to useful Tetris play. No B40 or H100 benchmark was run.
- Actual browser/OBS layout, control latency, protected remote serving, disconnect/restore across sandbox lifetimes, and durable artifact transfer on Jeremy's setup.
- W&B integration on the target environment.
- Native Beads creation/reconciliation against Jeremy's installed release. `bd` was absent in the source-authoring environment. The terminal handoff must run and verify the real import.
- Chess implementation, model training, or claims of chess playing strength. Episode 2 is an outline and gated backlog.

Use the requirements and evidence attached to each Beads task. Existing prototype files are not proof that a deployment or stream gate has passed.
