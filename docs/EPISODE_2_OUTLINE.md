# Episode 2 — The Chess Race

**Premise:** Jeremy learns chess with chat while a small, randomly initialized model learns from human game records. Early illegal proposals are visible. The series measures whether the model learns legal moves and whether its actual play improves; those are separate questions.

This is a proposed three-stream arc. Chess training and its interface are not implemented in the Tetris starter. H100 access, package availability, data transfer, and training throughput remain to be confirmed.

## Three-stream arc

| Stream | On-screen story | Build in public | Honest closing result |
| --- | --- | --- | --- |
| 2A · “Can either of us move a knight?” | Jeremy learns piece movement. Show raw move proposals from random weights; illegal moves receive a visible explanation. | Verify the game-data license, parse a bounded sample, build train/validation splits, initialize the small model, and begin the first real training run. | Raw legality rate before/after training, a few complete attempts, and a saved checkpoint. |
| 2B · “Knowing the rules isn't winning” | Alternate chat-coached human practice with checkpoint games. Show cases where the model's favorite move is legal but poor. | Continue the disclosed run, inspect held-out losses and raw legality, and introduce a clearly labeled legal-move mask for complete gameplay. | A first human-versus-model match and fixed-opponent results. No guaranteed “decent” milestone. |
| 2C · “The rematch” | Freeze a checkpoint. Jeremy and the AI each face the fixed opponent with swapped colors; then play each other. | Run the predeclared evaluation schedule, record PGNs and clocks, and review complete games. | Wins/draws/losses and raw legality, with training volume and human practice shown alongside. No Elo claim from a handful of games. |

Plan two to three hours per stream. Benchmark the actual data/training loop on the allocated H100 before stating epochs/hour or a learning-time estimate. “It learns the rules, then gets decent” is the hoped-for story, not a result to stage.

## Small-model default

Use supervised next-move learning from **human-played standard chess PGNs**, with random initial weights. A concrete first architecture is a six-layer, width-256 transformer that reads board-square tokens plus side-to-move, castling, and en-passant metadata, then predicts a source-square/target-square/promotion action. Expect roughly ten million parameters depending on the implemented output head; count and print the real number before training.

Train cross-entropy against the next recorded human move. This is imitation learning, not AlphaZero-style self-play. Start with a bounded 50,000-game sample so parsing, filtering, and splitting remain visible; enlarge it only after the pipeline works. These are proposed implementation settings, not measured performance claims.

Use `python-chess` to parse PGNs and validate game state. Its rule adjudication does not supply strategic recommendations. Do not feed engine evaluations, engine-generated moves, searches, opening-book recommendations, or tablebase results into model training. Omit comments, variations, and analysis annotations when producing examples.

Split by whole game before extracting positions; deduplicate games and inspect repeated positions across splits. Record the dataset source, checksum, filters, game counts, and split seed. A temporal holdout is preferable when the chosen export permits one. Common opening-position overlap must not be mistaken for novel-position generalization.

## Two scoreboards for two claims

**Learning the rules:** On a fixed held-out position set, log the raw, unmasked top-choice legality rate and the probability assigned to legal moves. Show illegal proposals on a diagnostic board. Do not silently replace them and report the replacements as evidence that the model learned legality.

**Playing a full game:** Apply a rule-based legal-move mask to the AI's action scores. Give Jeremy the same legal-move enforcement and visible legal choices. Label this as assisted legal gameplay. The mask prevents illegal actions; the network still chooses among the remaining moves. Report raw legality beside game results so the assistance remains visible.

## Fixed opponent and fair matches

Stockfish can be the **evaluation opponent only**. Pin its executable/version/hash, settings, search budget, and starting positions. It must never suggest moves to either contestant or generate training labels. Keep its move/evaluation process separate from the data/training process.

For the first comparison, propose `Skill Level = 0`, one thread, a fixed hash size, and an explicit node budget, **after verifying the options exposed by the installed binary**. Keep `UCI_LimitStrength` off when using `Skill Level`; if instead choosing `UCI_Elo`, enable `UCI_LimitStrength` and use a value actually supported by that binary. Weak-mode settings introduce randomness and do not establish a certified playing strength. [Stockfish option behavior](https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html)

Each contestant plays the same two color-swapped starting positions with the same clocks and draw/adjudication rules. Start with two games each and expand later. Suggested beginner clocks are ten minutes plus five seconds per move; include AI inference latency in its clock. Score a win as 1, draw as 0.5, and loss as 0. Show all outcomes and sample size. Head-to-head games form a separate result.

If the fixed engine defeats both immediately, retain those results. Add a separately labeled seeded random-legal opponent or beginner position challenge; do not lower the official opponent between Jeremy's and the AI's games.

## Open-source/data choices and caveats

| Component | License and use |
| --- | --- |
| [Lichess standard rated game database](https://database.lichess.org/) | Standard game exports are CC0. Use this section, not the separately licensed broadcast collection. Exclude marked BOT games where possible. A public human-game archive cannot prove every game was free of undisclosed human cheating; document that limitation. |
| [python-chess](https://python-chess.readthedocs.io/en/stable/) | GPL-3.0-or-later. Appropriate for PGN parsing and rule validation. Preserve its license and address GPL obligations when distributing code that incorporates it; do not relabel that dependency MIT. |
| [Stockfish](https://github.com/official-stockfish/Stockfish/blob/master/Copying.txt) | GPLv3. Pin the binary/source and retain relevant notices/source availability when redistributing. It is an opponent, not the learner or its coach. |

Do not download the entire current monthly archive on air. Stream/decompress a bounded sample or use an appropriately sized export; if egress is blocked, upload a documented raw sample through the approved channel and disclose that transport preparation. Parsing and all learning still happen live.

## What Episode 1 should leave ready

- A checked compute image and repeatable capability probe, with H100 verification still required.
- Durable checkpoints, a tested resume path, and local logging that does not depend on W&B availability.
- A shared game-state/rules boundary for human, model, and evaluator.
- A broadcast layout separating practice, raw diagnostics, checkpoint replays, and final results.
- Frozen-model evaluation, held-out inputs, recorded actions/PGNs, and an explicit experience counter.
- A five-minute troubleshooting limit before switching to a playable scene.

The next implementation should reuse those operational patterns without presenting the Tetris model, rewards, or action representation as a chess solution.
