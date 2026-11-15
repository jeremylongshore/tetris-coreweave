# Terminal prompt: create the actual Beads backlog

You are working with Jeremy in `jeremylongshore/tetris-coreweave`, a public repository for live human-versus-AI learning races. Your task is to create or safely reconcile the real Beads backlog from the plan already in this repository.

Read `AGENTS.md`, `README.md`, `docs/BEADS.md`, `docs/EPICS.md`, `planning/beads-plan.json`, and `scripts/import_beads.py`. Inspect the current checkout, git status, remotes, existing `.beads` state, installed Beads instructions/skills, and `bd --help`. Preserve Jeremy's existing work. Keep the repository public and CodeRabbit disabled.

The source plan has 8 epics, 30 child tasks, and 57 explicit blocking relationships. All were open when authored. `TCF-*` keys are stable external references; only the installed Beads CLI may assign native issue IDs. Do not create GitHub issues instead of Beads records. Do not invent a `.beads/issues.jsonl` file or assume a storage backend.

First run `python scripts/import_beads.py` and inspect the validated graph. If the trusted `bd` installation is missing, inspect the current official release and platform requirements, then use its documented installation path. Do not run an unreviewed remote installer or request/paste tokens into the chat. If a missing permission, dependency, or authentication step blocks the install, report the exact blocker and a concrete next action.

For a new checkout without `.beads`, inspect `bd init --help`, then use `python scripts/import_beads.py --apply --init` if its options match the installed CLI. For an existing initialized project, use `python scripts/import_beads.py --apply`. If the installed version differs from the checked API, adapt the importer minimally to documented behavior and explain the change. Never delete or reinitialize an existing database to make the import pass.

Verify the actual generated IDs, epic/child relationships, acceptance criteria, evidence requirements, stream gates, and all explicit blockers. Use the saved `planning/beads-id-map.json` and `bd show` output. Check that rerunning the importer does not duplicate records or reset progress. Existing completed tasks stay completed. Extra existing dependencies stay intact. Run `bd ready --json`; in a fresh import, `TCF-001` should be the sole ready leaf, though the CLI may also list epic containers.

Record the installed Beads version and import result. Commit the ID map and appropriate project metadata with a clear message, and push through Jeremy's existing authenticated GitHub workflow. Respect the installed Beads release's native storage and synchronization rules; a git push alone is not evidence of native database sync. Preserve unrelated changes and do not force push. If sync is blocked, retain local work and report exactly what remains.

Stop after the backlog is verified. Do not provision compute, spend credits, train a contestant, fabricate completed gates, enable GitHub Actions or CodeRabbit, or change repository visibility. Return the repository/branch, commit, real epic/task/dependency counts, native ID for the first ready task, and any concrete blocker. State clearly whether both source metadata and the native Beads database have synchronized.
