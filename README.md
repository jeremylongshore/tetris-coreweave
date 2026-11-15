# Tetris CoreWeave — The Race

Jeremy learns Tetris while a small AI learns beside him. Chat coaches Jeremy; the AI learns by trial and error. The audience watches the failures, the training, and a fair final match. Chess comes later.

**Public repository:** https://github.com/jeremylongshore/tetris-coreweave

## Start in your terminal with Codex or Claude

```bash
git clone https://github.com/jeremylongshore/tetris-coreweave.git
cd tetris-coreweave
```

Open your usual terminal agent in that directory and paste:

> Read AGENTS.md and prompts/01_CREATE_BEADS.md. Execute that prompt: create or recover the real Beads epics, tasks, and dependencies, verify the import, and report the first ready task. Preserve existing work. Do not launch compute or start contestant training.

The handoff contains **8 epics and 30 tasks**, with acceptance criteria, evidence requirements, and 57 blocking relationships. The stable `TCF-*` plan keys are external references. The installed Beads CLI assigns actual issue IDs. **A native Beads database has not been created by writing this plan.** The importer is dry-run by default, recovers partial imports, and preserves existing progress.

- [Create the Beads backlog](prompts/01_CREATE_BEADS.md)
- [Work the first ready task](prompts/02_START_FIRST_BEAD.md)
- [Epic overview](docs/EPICS.md) and [machine-readable plan](planning/beads-plan.json)
- [Beads commands, idempotency, and storage caveats](docs/BEADS.md)

## What is here

| File | Purpose |
| --- | --- |
| `race_env.py` | One shared, seeded Tetris adapter for both players; exact previews, rules, official counters, and training features. |
| `race.py` | Capability check, smoke check, benchmark, Double DQN training, checkpoint/resume, evaluation, final freeze, and local arena server. |
| `arena.html` | Human controls, checkpoint replays, development curve, practice results, and paired final scoreboard; no external assets. |
| [Episode 1 run of show](docs/EPISODE_1_RUN_OF_SHOW.md) | Three-hour screen-by-screen rundown, reward, timing, commands, risks, and fallbacks. |
| [Confirm before live](docs/CONFIRM_BEFORE_LIVE.md) | Seven questions for the CoreWeave contact and a short functionality preflight. |
| [Episode 2 outline](docs/EPISODE_2_OUTLINE.md) | Chess data, raw legality, small-model training, and independent engine evaluation. |
| [Validation record](docs/VALIDATION.md) | What was actually tested, and what is still unverified. |

This is a working CPU-tested prototype plus an execution plan. It has **not** been validated on Jeremy's Forge allocation or B40/H100 hardware. No trained weights, credentials, paid resources, or fabricated native Beads records are included.

## The fixed Tetris rules

This first race uses a **placement variant**: choose a rotation and column, inspect the preview, and drop. Both players use the same 10-by-20 game, piece generator, 40 candidate placements, and information. There is no gravity clock, hold, or next-piece queue. A round ends at top-out or 50 placement decisions. Chat may coach Jeremy.

The final is three paired games. Freeze the latest policy first, then draw three fresh seeds. Jeremy finishes all three games before the AI's final results are revealed. Most total **lines cleared** wins; total line-clear points (`10 × lines_in_one_placement²`) break ties. Remaining ties stand. Practice scores, shaped training reward, and final scores stay separate. The players share rules and information, but do not receive equal numbers of practice experiences.

The default algorithm is a **5,313-parameter shared-afterstate Double DQN**, initialized randomly. Hand-designed board features, game rules, and legal placement previews are supplied openly. This is not a model learning physics or controls from pixels.

The first training budget is **200,000 placements or 90 minutes**, whichever ends first, checked at game boundaries. **I'm not sure how quickly it will improve on the hardware called B40 in Jeremy's access.** Measure the full loop on air, discard benchmark weights, and show the result honestly. Improvement is measured by development line counts; success against Jeremy is measured only by the frozen, paired final. More details and the exact reward are in the [run of show](docs/EPISODE_1_RUN_OF_SHOW.md).

## Environment: confirm access, then install

Use a confirmed GPU sandbox that permits custom Python. Sandboxes, managed Post-Training, hosted Inference, and W&B tracking serve different purposes; this custom learner needs a process that can execute its own PyTorch loop. W&B does not allocate the GPU.

Before installing anything, confirm the image, actual GPU and VRAM, outbound package access, permitted installs, CPU allocation, session lifetime, credit/quota limits, persistent storage, and authenticated preview access. Multi-GPU support is unknown and unnecessary for this default. The public [GPU sandbox guide](https://docs.coreweave.com/products/sandboxes/gpu-sandboxes) is not evidence of Jeremy's particular access.

**Keep credentials off screen.** Use a face-camera scene during authentication and provider secret entry. Do not print environment variables, shell history, CLI credential files, or credential-bearing preview URLs.

The tested classic backend uses Python 3.12, NumPy 2.2.6, Gymnasium 1.2.3, headless OpenCV 4.10.0.84, and Tetris Gymnasium 0.3.1. Local validation used PyTorch 2.6.0+cpu. **For GPU use, keep the provider-approved PyTorch/CUDA build; these instructions do not replace it.** If the image cannot import Torch, have the terminal agent follow the provider's installation guidance before continuing.

If the provider permits virtual environments and pip installs, isolate the classic game dependencies while retaining the supplied Torch installation:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -r requirements-classic.txt
python -m pip install --no-deps tetris-gymnasium==0.3.1
```

`--no-deps` is deliberate: this starter uses the NumPy/classic environment, not the upstream package's optional JAX path or GUI window. The classic requirements are supplied explicitly and were tested together. This is not a complete installation of every upstream backend. If installs are blocked, use the approved image/wheel-upload path confirmed with CoreWeave; do not guess around the policy.

## One system at a time

These commands assume the installed environment above. They do not provision a sandbox.

### Capability check

```bash
python race.py doctor
```

Expected: nonsecret package versions and, when CUDA is available, the GPU name and an actual CUDA matrix multiplication/synchronization result. This does not establish quota, network policy, or lifetime.

### Shared game check and arena

```bash
python race.py smoke
```

Expected: deterministic seeded behavior and a `40 placements x 16 features` check. No learning occurs.

In terminal A:

```bash
python race.py serve --out run1 --port 8765
```

Locally, open `http://127.0.0.1:8765/`. A remote sandbox needs the confirmed authenticated forwarding/preview route. If that route requires a non-loopback listener, see the explicit proxy command in the run of show. The application does not provide its own login; never expose its controls through an unauthenticated public endpoint.

### On air: benchmark, then begin from random weights

In terminal B, after announcing the algorithm, time budget, and score:

```bash
python race.py benchmark --device cuda --seconds 60
```

Expected: warmup, then full-loop placements/second and estimated minutes per 100k placements. Benchmark weights are discarded. This measures speed, not time to competence. Run this on air because it includes optimizer updates.

```bash
python race.py train --out run1 --device cuda --steps 200000 --seconds 5400
```

Expected: checkpoint zero, baseline evaluation, training logs, periodic checkpoints, and updated arena metrics/replays. Use `--device cpu` for an announced CPU fallback. A new race needs a new output directory. Optional W&B logging is documented in the run of show; local JSON logs are the default.

### Freeze and play the final

After training stops:

```bash
python race.py freeze --out run1
```

Expected: a frozen policy identity and three fresh final seeds. Jeremy plays all three finals through the arena, then the AI results appear. Never use final seeds for training, model selection, or practice.

Preserve the run directory through the confirmed durable storage path, then explicitly stop the compute allocation. Stopping Python alone may leave the allocation running.

## CodeRabbit and repository policy

This repository is public. Automatic CodeRabbit reviews and replies are disabled in [`.coderabbit.yaml`](.coderabbit.yaml). Do not enable them, add a CodeRabbit workflow, or change repository visibility. Jeremy's account-level CodeRabbit installation was already suspended when this repository was created; it was left suspended.

No GitHub Actions workflows are included. Checkpoints, run data, private local configuration, and environment directories are excluded from git.

## Licensing

Original project code and documentation are under the [MIT license](LICENSE). The external Tetris environment is MIT licensed and is installed as a dependency; see [third-party notices](THIRD_PARTY_NOTICES.md). No commercial ROMs are used. Chess dependencies and data have separate licenses; consult the Episode 2 outline before adding or distributing them.
