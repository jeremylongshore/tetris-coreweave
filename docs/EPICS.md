# Execution epics: The Race

This is the implementation and live-execution backlog for `jeremylongshore/tetris-coreweave`. The machine-readable source of the backlog is [`planning/beads-plan.json`](../planning/beads-plan.json). It contains **8 epics and 30 open tasks** with explicit blocking dependencies.

## Current evidence boundary

The repository begins with a Tetris environment adapter, trainer, and browser arena prototype. CPU smoke checks and adapter/scoring checks are useful starting evidence. They do not prove Forge account capabilities, GPU access, CUDA compatibility, B40 identity, H100 availability, session persistence, or time to learning success. Tasks remain open until the stated acceptance criteria have recorded evidence for the relevant environment.

No production contestant may be trained or retained off stream. Rehearsal uses random actions, scripted game fixtures, and synthetic tensors without game optimizer updates. The short full-loop benchmark does perform learning updates, so it occurs visibly on air and its state is discarded before the official zero checkpoint.

## How to execute this backlog

1. Start with **TCF-001**, the only task without a blocker. Verify actual Forge access and limits before deciding the execution route.
2. Import the portable plan using the repository importer after checking the installed Beads CLI. `TCF-*` values are stable external references, never fabricated Beads database IDs. Preserve the IDs returned by `bd create` in the importer mapping.
3. Choose work from the dependency-ready queue. Tasks belong to their containing epic; `depends_on` lists blocking task dependencies. Forward references such as TCF-010 depending on TCF-019 are intentional and acyclic.
4. Record source revision, configuration, environment, and observed evidence before closing a task. If a result is blocked or uncertain, leave it open and explain the blocker.
5. Update the portable plan and this document together when scope changes. Keep live results, failures, and named experiments rather than silently replacing them.

**Priority:** P0 blocks a stream gate; P1 is high priority within the episode; P2 is planned follow-on work; P3 is an improvement; P4 is optional. Priority does not override dependencies.

## Stream gates

| Gate | Required outcome |
| --- | --- |
| G0 | Execution route, real hardware, private access, and budget limits verified. |
| G1 | Shared Tetris rules, scoring, deterministic behavior, and licensing frozen. |
| G2 | CPU-verified learner, honest telemetry, UI, persistence, and fallback paths ready. |
| G3 | Zero-training rehearsal completed and explicit go/no-go recorded. |
| G4 | Episode 1 measured, trained, scored fairly, and archived on air. |
| G5 | Chess data rights, rule adjudication, scratch model, and actual H100 route verified. |
| G6 | Chess learning and fair evaluation completed and archived. |

G3 permits opening the stream. TCF-010 is deliberately a G4 task: its real training-loop benchmark happens after go/no-go and before official training. Gate labels identify the operational milestone supported by a task; the task dependency graph determines readiness.

## Epic map

| Epic | Outcome | Priority | Tasks |
| --- | --- | --- | --- |
| TCF-E01 | Prove the Forge execution route | P0 | TCF-001–TCF-004 |
| TCF-E02 | Freeze one fair Tetris game | P0 | TCF-005–TCF-008 |
| TCF-E03 | Make learning visible and restartable | P1 | TCF-009–TCF-012 |
| TCF-E04 | Operate the arena through failures | P0 | TCF-013–TCF-016 |
| TCF-E05 | Rehearse the show without training the contestant | P0 | TCF-017–TCF-019 |
| TCF-E06 | Run and score the first Tetris race | P1 | TCF-020–TCF-022 |
| TCF-E07 | Build the chess learner and data contract | P2 | TCF-023–TCF-026 |
| TCF-E08 | Run the chess race with independent evaluation | P2 | TCF-027–TCF-030 |

## TCF-E01 — Prove the Forge execution route

Resolve the real account capabilities and resource limits before relying on platform marketing or hardware names.

### TCF-001 — Record actual Forge capabilities and operating limits

**Open · P0 · G0 · Depends on:** None; ready to start

Build a dated capability matrix with the CoreWeave contact and direct account observations. Distinguish confirmed, blocked, and unknown.

**Acceptance:**

- Identify the available execution route for arbitrary Python training; do not assume managed post-training accepts this custom environment.
- Record CPU/RAM, reported GPU model and count, CUDA image guidance, pip/egress policy, maximum session/idle lifetime, persistent storage/export, private port or notebook display support, and whether multi-GPU is permitted.
- Record available credits, billing behavior, cancellation/stop method, and agreed resource/time cap; unresolved facts that affect the chosen route block its use.

**Evidence required:**

- Sanitized capability matrix with observation date and source per answer.
- Redacted contact confirmation or account documentation references; no credentials or account IDs.

### TCF-002 — Reproduce the isolated install and CPU smoke in the approved runtime

**Open · P0 · G0 · Depends on:** TCF-001

Use the selected classic tetris-gymnasium backend and recorded package pins while retaining the platform-provided CUDA PyTorch build.

**Acceptance:**

- Install or obtain the approved dependency set without replacing the supplied CUDA PyTorch blindly; document that unused JAX and GUI backends are intentionally omitted.
- Run doctor and game smoke without optimizer updates in the actual chosen runtime; record Python and package versions.
- If installs or downloads are blocked, demonstrate the approved image/wheelhouse route or explicit local CPU fallback; do not bypass network policy.

**Evidence required:**

- Sanitized doctor/smoke transcript and package manifest.
- Reproducible install steps and the tested fallback choice.

### TCF-003 — Verify the reported GPU and a synthetic gradient operation

**Open · P0 · G0 · Depends on:** TCF-002

Confirm the device rather than assuming the label B40 identifies a particular NVIDIA product; establish whether CUDA actually works.

**Acceptance:**

- Record the exact GPU name, visible device count, driver/CUDA/PyTorch versions, and selected device from the running process.
- Run a small synthetic forward/backward calculation and device allocation; this is a hardware check, not game training.
- If no usable GPU is available, record CPU as the active route and label the stream accordingly; multi-GPU remains out of scope unless separately proven.

**Evidence required:**

- Sanitized hardware report and synthetic gradient result.
- Chosen CPU/GPU route with unresolved limits explicitly named.

### TCF-004 — Set private access, budget, and shutdown boundaries

**Open · P0 · G0 · Depends on:** TCF-001

Turn account permissions into an operational contract that the stream can follow safely and predictably.

**Acceptance:**

- Choose an authenticated display path and persistent/export destination actually supported by this account.
- Set a wall-clock cap, known quota boundary, visible shutdown procedure, and trigger for switching to CPU or ending compute.
- Document private login and secret-entry transitions; disallow environment dumps, exposed tokens, public unauthenticated control ports, and credential-containing logs.

**Evidence required:**

- Sanitized access/storage decision and resource budget.
- A short stop-and-switch checklist with the actual platform control names.


## TCF-E02 — Freeze one fair Tetris game

Make the competition reproducible: identical actions, visible information, scoring, limits, and protected evaluation seeds.

### TCF-005 — Freeze Tetris rules and the meaning of starting from zero

**Open · P0 · G1 · Depends on:** TCF-001

Approve one named rules version for Jeremy, the random baseline, and every learned policy.

**Acceptance:**

- Specify 10x20 placement Tetris, identical column/rotation choices and candidate previews, no timed gravity, no hold, no next-piece preview, and a 50-decision cap including the final failed attempt.
- Disclose engineered board features and preview assistance; random learned weights do not mean raw-pixel learning or no supplied rules.
- Define official total lines, 10*L^2 line-clear points as tie-break, ties that remain ties, and the policy for chat coaching in practice versus scored finals.

**Evidence required:**

- Versioned rules document and rules_id tied to the source revision.
- A viewer-facing rules card with assistance and scoring clearly stated.

### TCF-006 — Verify the shared game adapter and action previews

**Open · P0 · G1 · Depends on:** TCF-002, TCF-005

Re-run meaningful checks against the repository adapter; prototype CPU checks are starting evidence, not completion.

**Acceptance:**

- Same positive seed and action sequence reproduce piece order, settled boards, lines, and points; seed zero is rejected.
- Legal candidate previews and predicted clear counts match actual steps, including immediate top-out; no hidden queue information enters either player interface.
- Forced single/four-line clears score correctly, cap termination stops bootstrapping, and no extra move is accepted after termination.

**Evidence required:**

- Saved check output with source/dependency versions and number of compared states.
- Representative line-clear, top-out, and cap fixtures plus results.

### TCF-007 — Lock scoring and the final-match protocol

**Open · P0 · G1 · Depends on:** TCF-006

Separate practice metrics from final evidence and prevent checkpoint or seed cherry-picking.

**Acceptance:**

- Training, development evaluation, and fresh final seed sets are disjoint and use positive seeds; final seeds are drawn after checkpoint freeze.
- Freeze and hash the policy before final seeds; Jeremy completes the three paired final rounds before AI final replays reveal their sequences.
- Both sides get the same three piece sequences, rules, cap, and coaching policy; interrupted rounds follow a predeclared recovery rule rather than selecting favorable scores.

**Evidence required:**

- Match manifest schema and an example made without learned race weights.
- Scoring/replay-isolation checks, including duplicate submission and interruption behavior.

### TCF-008 — Record source licenses and distributable provenance

**Open · P0 · G1 · Depends on:** TCF-002

Make the public repository and show reproducible without commercial ROMs or unverifiable assets.

**Acceptance:**

- Verify and retain the actual upstream MIT notices for the selected Tetris version and other redistributed code/assets.
- Record dependency versions and primary source links; clearly identify original adapter/trainer/UI code and any modifications.
- Ensure no commercial ROM, unlicensed game asset, secret, cached account file, or pretrained race checkpoint enters the repository.

**Evidence required:**

- Third-party notices and source/version manifest.
- Repository content review with the reviewed commit ID.


## TCF-E03 — Make learning visible and restartable

Validate the small learner and its evidence trail before the live benchmark and official training run.

### TCF-009 — Validate Double DQN mechanics and bounded run configuration

**Open · P0 · G2 · Depends on:** TCF-006, TCF-008

Audit the implemented afterstate scorer and training loop with synthetic transitions and CPU-only checks before any live race training.

**Acceptance:**

- Record the random initialization, 16 input features, network size, replay/update schedule, discount, optimizer, exploration schedule, and target-update method.
- Verify Double DQN selection/evaluation separation, legal masking, terminal targets at top-out/cap, finite gradients, and the declared reward formula.
- No alive bonus or official-score substitution is introduced; CPU synthetic checks do not claim B40 learning speed or learned ability.

**Evidence required:**

- Mechanics-check transcript and exact run configuration.
- Explicit list of prototype behavior verified and remaining platform-dependent assumptions.

### TCF-010 — Measure full-loop throughput visibly on the actual device

**Open · P1 · G4 · Depends on:** TCF-003, TCF-009, TCF-019

Run the short gradient-bearing benchmark on air after the go/no-go gate, then discard all benchmark state.

**Acceptance:**

- Measure environment placements, optimizer updates, and wall time on the confirmed device, including the selected collection/update schedule.
- Compute time-to-step-budget from measured throughput and account for evaluation/checkpoint overhead; label time-to-skill as unknown.
- Discard benchmark weights/replay and create a separately identified random-initialization official run; switch to the demonstrated fallback if throughput is too low.

**Evidence required:**

- On-air benchmark log, device/config identity, and measured rate.
- Budget calculation, fallback decision, and evidence of a distinct official zero checkpoint.

### TCF-011 — Show honest development metrics and labeled replays

**Open · P0 · G2 · Depends on:** TCF-007, TCF-009

Connect local metrics to the broadcast and make cloud tracking optional.

**Acceptance:**

- Show official evaluation mean/median/max lines, zero/random baselines, training placements, updates, elapsed time, epsilon, throughput, and checkpoint identity.
- Evaluate frozen snapshots without exploration on fixed development seeds; keep training reward visually separate from official scoring.
- Mark each game feed LIVE or REPLAY with checkpoint/seed context; no replay is presented as the currently learning policy. Local logs work without W&B.

**Evidence required:**

- Sample local metric events and a dashboard screenshot from non-learning fixtures.
- Offline tracker test and explicit replay labels.

### TCF-012 — Prove checkpoint and resume integrity

**Open · P0 · G2 · Depends on:** TCF-004, TCF-009

Recover a bounded run without silently replacing learned state or double-counting progress.

**Acceptance:**

- Save model, target, optimizer, replay, random-generator state, counters, rules/config identity, and enough game state or episode-boundary context for declared resume semantics.
- Write checkpoints atomically; distinguish resume from fresh start; reject incompatible rules or incomplete/corrupt state.
- Demonstrate interruption/restart with synthetic or non-learning fixtures; document maximum possible progress loss and preserve original checkpoint history.

**Evidence required:**

- Checkpoint manifest and interrupted-write/resume verification output.
- Documented recovery boundary and loss window tied to the implementation.


## TCF-E04 — Operate the arena through failures

Deliver a controllable broadcast surface, durable evidence, and concrete fallback paths.

### TCF-013 — Open human controls through the approved private display route

**Open · P0 · G2 · Depends on:** TCF-004, TCF-006

Verify the actual sandbox/browser connection rather than assuming localhost or public port forwarding reaches the audience machine.

**Acceptance:**

- Jeremy can start a practice game, inspect placements, choose a valid action, and read the result through the selected authenticated route.
- Human controls expose the same candidate-line and immediate-top-out information as the policy and never show hidden next pieces.
- Confirm access control and write-request protections; provide a tested local/browser or notebook fallback when sandbox port display is unavailable.

**Evidence required:**

- Observed UI walkthrough and route description with private URLs redacted.
- Control/error-path checks and fallback screenshot.

### TCF-014 — Compose the live scoreboard and OBS scenes

**Open · P1 · G2 · Depends on:** TCF-011, TCF-013

Make the race understandable to ordinary viewers while keeping diagnostics and credentials out of the main game view.

**Acceptance:**

- Show Jeremy, the AI replay/live board, comparable official scores, training age, and the next match/checkpoint without tiny unreadable text.
- Provide gameplay, code/terminal, and private/holding scenes; label synthetic fixtures and development replays.
- Verify source cropping, resolution, readable counters, audio, and control focus in the actual streaming arrangement.

**Evidence required:**

- Scene list and captured layout at stream resolution.
- Short recording of a non-learning fixture sequence and its audio/control check.

### TCF-015 — Recover artifacts after a process or session ends

**Open · P0 · G2 · Depends on:** TCF-004, TCF-012

Verify the chosen persistent destination with an actual restore, not a claim that sandbox files survive.

**Acceptance:**

- Save source/config identity, checkpoints, manifests, local metrics, action traces, and replay files in the verified durable/export path.
- Stop/restart the relevant process or approved disposable session and restore a fixture run; demonstrate data integrity with hashes.
- Exclude credentials and protected account metadata from artifacts; record retention/export limits and the end-of-stream download step.

**Evidence required:**

- Restore transcript and before/after artifact hashes.
- Sanitized artifact index and retention/export procedure.

### TCF-016 — Demonstrate each failure fallback

**Open · P0 · G2 · Depends on:** TCF-003, TCF-013, TCF-015

Keep the show moving when compute, networking, display, or learning fails.

**Acceptance:**

- Demonstrate CPU operation, W&B-offline/local logs, alternate display, and checkpoint recovery under the chosen environment constraints.
- Write the no-improvement branch: show honest evaluation, inspect one failure, change one declared factor in a new run, and keep original scores visible.
- Set short on-air troubleshooting limits and a viewer activity for each delay; never load a secretly trained winner.

**Evidence required:**

- Failure/fallback matrix with observed outcomes for technical paths.
- Named go/no-go and stop-debugging thresholds with the stream continuation beat.


## TCF-E05 — Rehearse the show without training the contestant

Prove the infrastructure and disclosure boundaries while preserving a real on-air start.

### TCF-017 — Run a zero-training end-to-end rehearsal

**Open · P0 · G3 · Depends on:** TCF-007, TCF-008, TCF-009, TCF-014, TCF-015, TCF-016

Exercise the sequence with random actions, scripted fixtures, and synthetic checkpoint data only.

**Acceptance:**

- Walk through setup, rules card, human input, random AI play, metrics, freeze/draw/final flow, replay, export, and shutdown without game optimizer updates.
- Record known defects and time each segment; any gate-breaking defect receives a blocking task before go-live.
- Retain no learned policy from rehearsal; preserve source/version evidence so the live run can start from an auditable zero checkpoint.

**Evidence required:**

- Rehearsal checklist, segment timings, and source revision.
- A statement of exactly what was tested and confirmation that no game-learning state was retained.

### TCF-018 — Finalize the timed rundown and private transitions

**Open · P1 · G3 · Depends on:** TCF-017

Turn tested operations into a watchable sequence with a fallback for every potentially slow segment.

**Acceptance:**

- Define episode timing, screen/scene, viewer beat, technical command, expected output, and fallback for each segment.
- Include explicit private scenes before login/token/account steps; show only allowlisted diagnostic output.
- Schedule the live benchmark, random baseline, first training update, checkpoint comparisons, frozen final, archive, and shutdown; no promise of an AI win.

**Evidence required:**

- Final run-of-show linked to actual commands and verified UI.
- Secret-transition and contingency cues on the producer sheet.

### TCF-019 — Record the final go/no-go decision

**Open · P0 · G3 · Depends on:** TCF-018

Check the account and stream conditions immediately before opening the race.

**Acceptance:**

- Recheck compute availability, remaining budget, private display access, persistence, broadcast capture, and source/rules identity.
- Choose GPU race, clearly labeled CPU race, or infrastructure-only stream from observed conditions; no unverified hardware claim survives the decision.
- Record a fresh official output location and initial seed plan with no learned policy, plus the owner responsible for shutdown.

**Evidence required:**

- Dated go/no-go record with selected route and unresolved issues.
- Pre-stream source/config digest and empty official-run inventory.


## TCF-E06 — Run and score the first Tetris race

Make the actual stream, checkpoints, and final result the evidence; failures remain part of the record.

### TCF-020 — Launch the official Tetris race from random weights on air

**Open · P1 · G4 · Depends on:** TCF-010, TCF-019

Start the contestant visibly after the disposable benchmark and run the declared budget.

**Acceptance:**

- Show the source/rules/config identity, initialize and retain the zero checkpoint, and show random/zero-policy baseline scores.
- Train while Jeremy practices under the same game rules; take scheduled development snapshots and explain flat or worsening metrics honestly.
- Respect compute/time caps, keep changes as named runs, and preserve local evidence if the cloud tracker fails.

**Evidence required:**

- Stream timestamps for zero initialization, baseline, first update, and checkpoint comparisons.
- Run configuration, metrics, checkpoints, and any named change decisions.

### TCF-021 — Play the frozen paired final and report the actual result

**Open · P1 · G4 · Depends on:** TCF-020, TCF-007

Execute the predeclared final protocol once with the selected frozen checkpoint.

**Acceptance:**

- Freeze/hash before drawing fresh seeds; complete Jeremy finals before revealing AI final play; apply the declared coaching/recovery rules.
- Score all three paired rounds, show total lines and the exact point tie-break, and keep a draw if still tied.
- Do not cherry-pick checkpoints/seeds, reset a losing contestant silently, or claim statistical strength from a small entertainment match.

**Evidence required:**

- Frozen match manifest, human/AI action traces, round scores, and policy hash.
- On-air final summary with any interruption or protocol deviation disclosed.

### TCF-022 — Archive Episode 1 and hand off the next experiment

**Open · P1 · G4 · Depends on:** TCF-021, TCF-015

Leave a reproducible run record and concrete follow-up work for Codex or Claude.

**Acceptance:**

- Publish authorized source/results artifacts with rules/config, device identity, dependency manifest, seeds, metrics, and reconstruction instructions.
- Separate observed learning, measured throughput, actual cost/time when available, and unanswered questions; report CPU/GPU limits honestly.
- Record what should carry into chess and create follow-up tasks for remaining defects; verify compute is stopped.

**Evidence required:**

- Episode report and artifact index tied to the repository revision.
- Shutdown evidence and a dependency-aware handoff with next ready task.


## TCF-E07 — Build the chess learner and data contract

Use openly licensed human game records, a rules-only referee, and random model weights; engine help remains outside learning.

### TCF-023 — Select licensed human chess data and isolate evaluation

**Open · P1 · G5 · Depends on:** TCF-022, TCF-008

Create a small inspectable first dataset before scaling downloads or training.

**Acceptance:**

- Verify primary-source data license and record the exact source/snapshot; start with a small bounded download and parser smoke.
- Exclude bot games and engine annotations/targets under a documented filter; use human move records only and record filter limitations.
- Deduplicate and split by whole game before creating positions; hold final evaluation games/positions out and record dataset hashes.

**Evidence required:**

- Data card with primary license URL, snapshot, filters, counts, and hashes.
- Game-level split and overlap-check output.

### TCF-024 — Implement chess rules and honest illegality accounting

**Open · P1 · G5 · Depends on:** TCF-023, TCF-005

Use a chess rules library to adjudicate legal moves without choosing strategic moves for the model.

**Acceptance:**

- Verify library license and test move legality, side to move, castling, en passant, promotions, game endings, and repetition/draw policy.
- Define the same human/AI attempt, clock, illegal-move, and resignation policy; distinguish raw model output from any legal-action guard.
- Report raw first-choice illegality before correction or masking; never call guarded legality learned-rule performance.

**Evidence required:**

- Versioned chess rules card and legality fixture results.
- Example raw proposal, adjudication, guard behavior, and logged metric fields.

### TCF-025 — Specify and smoke a genuinely scratch chess policy

**Open · P1 · G5 · Depends on:** TCF-023, TCF-024

Choose a small board/context-to-move model whose initialization and training targets are inspectable.

**Acceptance:**

- Record architecture, parameter count, move vocabulary including promotions, input representation, and random initialization; no pretrained weights or engine labels.
- Train only by supervised next-move prediction on the approved game records; keep optional later reinforcement learning as separately scoped work.
- CPU/synthetic smoke verifies tokenization, loss, decoding, and checkpoint format without retaining a secretly trained contestant; define raw-legality and held-out move-loss metrics.

**Evidence required:**

- Model/data configuration, vocabulary checks, and synthetic gradient log.
- Zero-state checkpoint identity and declared success metrics.

### TCF-026 — Confirm H100 access and measure the chess execution route

**Open · P1 · G5 · Depends on:** TCF-003, TCF-025

Treat H100 availability, memory, session length, and throughput as unconfirmed until observed.

**Acceptance:**

- Verify the actual H100 device/allocation and working CUDA build; do not infer access from a next-week promise or a prior B40 session.
- Measure data loading and synthetic model throughput, then set a bounded training budget without promising that the model will become decent in one stream.
- Demonstrate a smaller-model/CPU or deferred-training fallback and the same durable-state/private-display path.

**Evidence required:**

- Dated hardware/compatibility report and throughput measurement method.
- Chess compute budget, quota/session limits, and tested fallback.


## TCF-E08 — Run the chess race with independent evaluation

Keep the engine as a fixed referee/opponent after training choices are frozen, and show raw legality separately from playing strength.

### TCF-027 — Freeze the independent engine and head-to-head protocol

**Open · P1 · G6 · Depends on:** TCF-024, TCF-026

Define a reproducible opponent for Jeremy and the AI without allowing engine assistance into learning or move choice.

**Acceptance:**

- Verify the chosen open-source engine license and pin engine version, options, search limit, start positions, colors, and draw/illegal/clock handling.
- Use identical paired conditions for Jeremy and the AI; separate development tuning positions from fresh final positions.
- Do not feed engine analysis, recommended moves, evaluations, or final match outcomes into training/model selection; do not convert a small match into a claimed Elo rating.

**Evidence required:**

- Engine/license/config manifest and paired-match schedule.
- A dry-run result record and evidence that training data flow excludes engine outputs.

### TCF-028 — Show the chess model learning from human games on air

**Open · P1 · G6 · Depends on:** TCF-025, TCF-026, TCF-027

Make the progression from invalid proposals to legal moves a measured outcome rather than a scripted promise.

**Acceptance:**

- Initialize the official model visibly from random weights and retain its baseline raw first-choice illegality and held-out loss.
- Train with scheduled frozen snapshots; show raw legality, complete-game outcomes, and any guarded-play mode with explicit labels.
- If progress is slow, reduce the declared experiment in a named new run or continue across streams; retain failed results and make no guaranteed-strength claim.

**Evidence required:**

- On-air initialization/training timestamps and zero/current checkpoint identities.
- Dataset/config hashes, raw-legality traces, held-out metrics, and named change log.

### TCF-029 — Play Jeremy-versus-AI and paired engine finals

**Open · P1 · G6 · Depends on:** TCF-028, TCF-027

Score the agreed chess contests without hidden move correction or engine coaching.

**Acceptance:**

- Freeze the policy and selected guarded/raw mode before fresh final positions; apply the same published move/clock/assistance rules.
- Record Jeremy-versus-AI games and both contestants against the fixed engine with balanced colors and complete outcomes.
- Show illegal-attempt rate separately from wins/draws/losses; disclose forfeits, guards, interruptions, and uncertainty from the small sample.

**Evidence required:**

- Final policy/engine manifests, PGNs/action logs, and paired result table.
- Stream timestamps and protocol-deviation record.

### TCF-030 — Archive chess and extract the reusable Race scaffold

**Open · P2 · G6 · Depends on:** TCF-029, TCF-022

Leave the next episode with a stable competition/evidence pattern and a clean operational handoff.

**Acceptance:**

- Archive authorized source, data references/hashes, model configuration, checkpoints, metrics, and final records without redistributing unlicensed material.
- Separate reusable game/referee, contestant, scorer, broadcaster, checkpoint, and provenance interfaces based on what both episodes proved.
- Update the dependency backlog with observed lessons and next ready work; stop compute and verify recoverable artifacts.

**Evidence required:**

- Chess episode report and replay/reproduction index.
- Reusable-interface note, updated task references, and shutdown/restore evidence.

## Primary sources to verify at the relevant tasks

- [Tetris Gymnasium 0.3.1](https://pypi.org/project/tetris-gymnasium/0.3.1/) and its [MIT license](https://github.com/Max-We/Tetris-Gymnasium/blob/main/LICENSE). Use the exact installed version and license notices, not a floating repository assumption.
- [Grouped placement source](https://max-we.github.io/Tetris-Gymnasium/_modules/tetris_gymnasium/wrappers/grouped/) and [classic environment source](https://max-we.github.io/Tetris-Gymnasium/_modules/tetris_gymnasium/envs/tetris/). Pin behavior with local acceptance evidence.
- [CoreWeave Forge](https://www.coreweave.com/products/coreweave-forge) and [CoreWeave Sandboxes](https://www.coreweave.com/products/coreweave-sandboxes). Product pages do not establish the permissions, hardware, lifetime, or quotas of this account.
- [Lichess database](https://database.lichess.org/) for the chess data selection/license check; inspect the actual selected dataset and metadata before choosing filters or download commands.
- [python-chess](https://python-chess.readthedocs.io/) for a rules-only referee candidate, and [Stockfish](https://github.com/official-stockfish/Stockfish) for an independent evaluation-opponent candidate. Their use and license obligations must be verified in the chess tasks; no engine output belongs in training.

## Handoff contract

Codex or Claude should read the repository instructions, inspect the current task state, take one dependency-ready task, and produce its acceptance evidence. An agent may prepare source, tests, and operational instructions autonomously. Actual authenticated account actions, live training, broadcast operation, and resource spending must follow Jeremy’s current authorization and the verified limits. Never treat this plan as proof that an external account operation has occurred.
