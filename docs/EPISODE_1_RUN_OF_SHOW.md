# Episode 1 — The Tetris Race

**Show promise:** Jeremy and a randomly initialized policy learn in front of the audience. The first stream ends with a real result, including a loss, a draw, or no improvement. No trained checkpoint is prepared off camera.

**Default:** a 5,313-parameter, shared-afterstate Double DQN; one GPU if available; a target of **200,000 placements or 90 minutes**, ending at an episode boundary. Training time to useful play is unknown until measured. Success means improving held-out line counts and then competing with Jeremy on **three fresh, identical piece sequences**, under the same rules.

This is a placement-based Tetris variant: both players select a rotation and column, inspect the resulting board, then commit. It is not a test of real-time keyboard dexterity. The model starts with random weights; the game rules, board features, and learning algorithm are supplied openly.

## The three-hour show

Times are elapsed stream time. Complete one system before introducing the next. Training may run while Jeremy plays after the game, training process, and display have each been demonstrated.

| Time | Story beat and action | On screen | Exit or fallback |
| --- | --- | --- | --- |
| 00:00–00:08 | Introduce the race. Chat predicts the winner. Read the rules and explain random weights versus supplied rules/features. | Face camera, empty scoreboard, rules card. | Promise an honest result, not a guaranteed AI win. |
| 00:08–00:18 | Inspect the allocation and imports. Run `doctor`; show the actual GPU name and CUDA test. | Terminal plus small face camera. | If CUDA fails, label the CPU fallback and continue. Never guess a replacement CUDA wheel. |
| 00:18–00:30 | Run `smoke`, start the arena, and make a few placements. Show that the preview matches the actual result. | Human board, rotation/column controls, official counters. | If preview access fails, use the same code locally; keep remote training separate. |
| 00:30–00:40 | Jeremy's opening practice games. Chat can coach. Explain holes, top-out, and line clears through actual mistakes. | Human board large; practice results visible. | These are practice scores, not the final match. |
| 00:40–00:50 | Run the full-loop throughput benchmark live. Explain the reward and show the small network. Benchmark weights are discarded. | Terminal benchmark output, then estimated time for 100k and 200k placements. | If slow, keep the 90-minute time budget and report the achieved placement count. |
| 00:50–01:00 | Start the real run from random weights. Show checkpoint zero and the random baseline. | Training terminal, then arena checkpoint replay with an explicit REPLAY label. | If the initial evaluation takes longer, Jeremy plays another practice game. |
| 01:00–01:20 | Chat coaches Jeremy while the learner collects experience. Predict the next checkpoint's lines. | Human game; training step and elapsed clock in the corner. | Spend at most five minutes on a fix before returning to a playable scene. |
| 01:20–01:40 | First checkpoint review: watch an entire saved game, including the failure. Compare evaluation mean/median with checkpoint zero. | AI replay, official line count, evaluation curve. | A rising training reward alone does not count as progress. |
| 01:40–02:00 | Jeremy tries one lesson from chat. Explain one AI mistake using its board. | Human practice, then one checkpoint replay. | Do not change rules, rewards, or model selection criteria mid-race. |
| 02:00–02:20 | Last practice block and checkpoint review. Announce the training cutoff. | Both boards, evaluation curve, cumulative placements and elapsed time. | If training reached 200k early, keep the stopped run and use the time for practice/analysis. |
| 02:20–02:25 | Stop at the declared budget, preserve the run, and freeze the latest checkpoint. Only then draw final seeds. | Terminal freeze confirmation and final-round card. | If interrupted, resume the saved run openly; never substitute an undisclosed model. |
| 02:25–02:52 | Jeremy completes all three final games. Then the frozen AI plays those same seeds and its scores/replays are revealed. | Human FINAL badge first; then final scoreboard and AI replay. | No retries on a bad seed. If the game/server disconnects, restore recorded actions and continue the same round. |
| 02:52–03:00 | Read the result and save the evidence. Choose the next live question. Stop compute explicitly. | Paired totals, checkpoint identity, actual training duration; closing face camera. | A flat curve becomes the next stream's question. It does not become an invented win. |

If setup consumes the training window, shorten the announced budget before training starts. Keep the final three rounds and label the actual experience received. If a match overruns, finish the rounds or mark it unfinished; do not invent a winner to meet the clock.

## Fixed race contract

| Item | Rule |
| --- | --- |
| Engine | `tetris-gymnasium==0.3.1`, classic NumPy backend, through the shared `RaceEnv` adapter. Upstream is MIT licensed; no commercial ROM or commercial game client is used. [Upstream source/license](https://github.com/Max-We/Tetris-Gymnasium) |
| Board | 10 columns × 20 rows; same upstream piece generator and rotation semantics for both players. |
| Controls | 40 possible column/rotation combinations; unavailable placements are masked for both players. No gravity clock, hold, or next-piece queue. |
| Information | Both receive the current piece and the same exact after-placement previews, projected line clears, and immediate top-out warnings. The AI's numerical features are derived from those boards. |
| Round end | Top-out or 50 placement decisions, including a final failed placement. |
| Official score | Total lines across three paired final games. Tie-break: total line-clear points, adding `10 × lines_this_placement²` per move. Remaining ties stand. These are this series' rules, not a claim of official competitive Tetris scoring. |
| Practice | Separate history and personal bests. Chat may coach Jeremy. Show the AI's training placements and Jeremy's practice volume; they do not have equal numbers of experiences. |
| Evaluation | Five fixed development seeds every five minutes; no exploration during evaluation. Track mean, median, best, and every individual result. This repeated set measures development progress, not final generalization. |
| Final | Freeze the latest policy after the declared budget, then generate three fresh seeds outside the training/development ranges. Jeremy plays all three before AI final scores/replays become visible. No final seeds are used for training or checkpoint selection. |

The shared controls deliberately remove keyboard speed from the contest. If later episodes add falling speed, hold, or a next queue, give them to both players, version the rules, and begin a new comparison.

## Learning setup and expected time

The policy scores each candidate placement with a shared `16 → 64 → 64 → 1` network: **5,313 trainable parameters**. Inputs are ten column heights, maximum height, holes, bumpiness, lines cleared by the placement, immediate top-out, and remaining placement budget. This is a feature-based learner, not a pixel model or a language model.

The implemented training reward is:

```text
r = 10 × lines_cleared
    − 0.5 × change_in_holes
    − 0.05 × change_in_sum_of_column_heights
    − 5 × topout
```

Changes are `after − before`; removing holes/height earns a shaping benefit. Shaping makes early feedback denser but can favor behavior that does not maximize official lines. Keep shaped return off the winner's scoreboard and watch real line counts for reward exploitation.

The defaults are Adam at `0.0003`, discount `0.99`, batch size `256`, replay capacity `20,000`, a `1,024`-placement warmup, one update every four placements, and target-network synchronization every `1,000` updates. Epsilon falls from `1.0` to `0.05` over `50,000` placements. Double DQN selects the next action with the online network and evaluates it with the target network. [Double Q-learning paper](https://arxiv.org/abs/1509.06461)

**There is no verified B40 learning-time claim.** The exact GPU denoted by that access label, CPU allocation, image, and environment throughput must be confirmed. This tiny network may spend more time simulating candidate placements on the CPU than computing on the GPU. More GPU memory does not guarantee a faster loop.

Use the on-stream benchmark's measured full-loop rate `R`:

```text
minutes for N placements ≈ N / (60 × R)
total budget also includes evaluation, checkpoint writes, and startup
```

Illustrations, not hardware benchmarks:

| Measured placements/s | 100,000 placements | 200,000 placements |
| ---: | ---: | ---: |
| 20 | 83 minutes | 167 minutes |
| 50 | 33 minutes | 67 minutes |
| 100 | 17 minutes | 33 minutes |

Use 100k as a review milestone and 200k as the placement target. The default 90-minute wall-clock budget can end the run earlier. Budget checks occur at episode boundaries, so a run can slightly exceed the declared count/time while finishing its current game. No placement count guarantees a first line clear, improvement, or a win over Jeremy.

## Commands for the live session

Run from the `tetris-coreweave` repository root using the approved environment and installed dependencies described in [README.md](../README.md). Keep the arena and trainer in separate terminals. Use a new output directory for each new race; the examples use `run1`.

**Before showing any terminal, preview URL, login page, or tracking setup:** switch to the face-camera scene while entering credentials. Use the provider's secret mechanism. Do not display environment dumps, shell history, tokens, or credential-bearing URLs.

Inspect nonsecret capabilities:

```bash
python race.py doctor
```

Expected: selected package versions, GPU name if available, and `CUDA matrix multiply + synchronization: PASS` when the selected image can actually run CUDA. This does not verify network, quotas, lifetime, storage, or preview access.

Verify shared rules without learning:

```bash
python race.py smoke
```

Expected: identical seeded game/counter check and `40 placements x 16 features`; no optimizer runs.

Start the arena in terminal A:

```bash
python race.py serve --out run1 --port 8765
```

Expected: server-listening message and a playable practice board through the confirmed preview/forwarding route. This binds to loopback. Only when the provider has confirmed a protected proxy that requires a non-loopback listener, use:

```bash
python race.py serve --out run1 --host 0.0.0.0 --port 8765 --behind-auth-proxy
```

The flag acknowledges an existing authenticated proxy; it does not create authentication.

Measure the full loop in terminal B, on stream:

```bash
python race.py benchmark --device cuda --seconds 60
```

Expected: a warmup message, then placements/second and projected minutes per 100k, excluding evaluations. Warmup is additional time. The benchmark trains disposable weights and does not save a race checkpoint. If GPU execution fails, rerun with `--device cpu` and label that measurement accordingly.

Start the declared race in terminal B:

```bash
python race.py train --out run1 --device cuda --steps 200000 --seconds 5400
```

Expected: random initial checkpoint, random baseline, repeated evaluations, logs, and updated arena metrics/replay. Defaults request evaluation every 300 seconds and saving every 120 seconds, performed at episode boundaries. The five-minute boundary is approximate, not a real-time guarantee. Replace `cuda` with `cpu` for the announced CPU fallback.

Tracking is optional. Local JSON logs and the arena work without W&B authentication. If installed, `--wandb offline` records locally; use `--wandb online` only after credentials are supplied off screen. Logging itself does not allocate a GPU.

If interrupted, resume openly rather than starting fresh:

```bash
python race.py train --out run1 --device cuda --steps 200000 --seconds 1800 --resume
```

Here `--steps` remains a cumulative target; `--seconds 1800` is a **new** 30-minute invocation budget. The trainer preserves replay, optimizer, target network, and RNG state. State changes across devices may prevent bitwise-identical continuation; disclose them.

After training has stopped, freeze the latest saved policy:

```bash
python race.py freeze --out run1
```

Expected: checkpoint-step confirmation and three freshly drawn final seeds. Use the arena's final button for each of Jeremy's three rounds. The server records AI results only after all human rounds are complete. Do not evaluate the final seeds separately before Jeremy finishes.

Archive `run1` using the confirmed durable storage/download workflow, then stop the arena and explicitly terminate the compute allocation. A stopped Python process does not necessarily stop provider billing.

## What can break, and the scene that replaces it

| Risk | Check beforehand | On-stream fallback |
| --- | --- | --- |
| No GPU access, wrong image, or CUDA kernel failure | `doctor`, including an actual CUDA operation. | Run CPU, label it, and measure throughput. Ask the contact to fix GPU access for the next race. |
| Package install or download blocked | Test the exact package path/approved image and required outbound hosts. | Use an approved image or uploaded wheel bundle; otherwise run the same repo locally. No guessed package replacements. |
| GUI window cannot open or preview port is absent | Test the web arena through the actual authenticated route. | Run the shared arena locally and transfer checkpoints through an approved path; remote training can continue. |
| Candidate simulation is the bottleneck | Benchmark full collection plus optimization, not GPU matrix multiply alone. | Keep the time budget, report fewer placements, and turn performance investigation into a later stream. |
| Reward rises but lines stay flat | Inspect official evaluation counters and full replays. | Keep the result. Test a reward revision in a separately named, announced experiment next stream. |
| AI never clears a line or does not improve | Expect this possibility; preserve checkpoint zero. | Finish the fair match anyway. The next episode investigates one hypothesis rather than loading a trained replacement. |
| Session expires, credit runs out, or browser disconnects | Verify lifetime, durable storage, and reconnect behavior. | Restore the latest checkpoint and final action log; continue the same race or mark the match unfinished. |
| W&B or networking fails | Confirm local arena/logs work without cloud tracking. | Use local metrics/replays and sync later. |
| Scores/rules diverge or a seed reproduces incorrectly | `smoke`; use positive seeds; inspect capped game and line-clear accounting. | Stop official scoring, fix the shared adapter, version changed rules, and restart the match openly. |
| Training produces nonfinite values or crashes | A small functionality check, not an off-camera strength run. | Save evidence and restore a valid checkpoint. Announce any changed hyperparameters and new run identity. |
| Human final is interrupted | Verify action-log recovery using a disposable test directory. | Restart the server and reconstruct the same final game. No new attempt on an exposed seed. |
| Secret or private account screen appears | Test capture regions and a face-camera-only scene. | Cut to face camera immediately; revoke an exposed credential off screen before continuing. |

Before the actual broadcast, use the 20-minute functionality preflight in [CONFIRM_BEFORE_LIVE.md](CONFIRM_BEFORE_LIVE.md). Do not use it to optimize performance against Jeremy or accumulate off-camera training.

## Carry into the next stream

Keep the rules ID, source hashes, package versions, checkpoint zero, latest/frozen policy, training/evaluation logs, human actions, final seeds, and replays. The shared scoreboard, independent evaluator, checkpoint labels, storage/recovery path, and secret-safe capture scenes carry into [Episode 2](EPISODE_2_OUTLINE.md).

Primary platform references: [GPU sandboxes](https://docs.coreweave.com/products/sandboxes/gpu-sandboxes), [configuration/network/lifetime](https://docs.coreweave.com/products/sandboxes/client/guides/sandbox-configuration), [public endpoints](https://docs.coreweave.com/products/sandboxes/public-endpoints). These document platform capabilities; they do not confirm Jeremy's allocation.
