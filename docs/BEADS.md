# Beads handoff

The executable plan is `planning/beads-plan.json`. Its keys (for example,
`TCF-001`) are stable plan references, **not fabricated Beads issue IDs**.
Actual issue IDs are assigned by the installed `bd` CLI and saved to
`planning/beads-id-map.json` after each successful create or recovery.

The current working environment did not have `bd` installed when this importer
was authored. No native Beads database is claimed to exist merely because the
plan exists. Check the repository's current status before deciding whether an
import has already happened.

## Bootstrap using the existing toolchain

Use your existing, trusted Beads installation if available. Otherwise choose a
release from the [official Beads repository](https://github.com/steveyegge/beads)
and follow its installation instructions for your platform; inspect the release
and checksum before installing. Do not paste an unreviewed remote installer into
a shell. Current upstream storage uses Dolt; required runtimes and initialization
behavior depend on the selected release. This repo does not manufacture native
storage files or assume that `.beads/issues.jsonl` is the database.

From the repository root, inspect the installed CLI before initializing anything:

```bash
bd --help
```

```bash
bd init --help
```

```bash
python scripts/import_beads.py
```

The last command is a dry run. It validates keys, required text, priorities,
dependency targets, and the complete dependency graph, then prints the plan.
It requires only Python's standard library and performs no `bd` calls or writes.

For a new checkout with **no existing `.beads` directory**, initialize and import:

```bash
python scripts/import_beads.py --apply --init
```

The importer verifies installed help first, then invokes the equivalent of:

```bash
bd init --prefix tcf --skip-hooks --skip-agents
```

It does not rewrite this repository's agent instructions or install git hooks.
If initialization fails because the selected release requires an unavailable
storage runtime, follow that release's documented setup. Do not reinitialize or
delete an existing database to make the importer pass.

For an already initialized project, including a retry after a partial import:

```bash
python scripts/import_beads.py --apply
```

If initialization succeeded but a later import step failed, omit `--init` on the
retry. `--init` deliberately refuses an existing `.beads` directory.

## What the importer actually does

1. Validate the plan before all mutations, including cycles through parent links.
2. Read the installed CLI help for the required create/list/show/dependency flags.
3. Find each issue by exact external reference, including closed issues:
   `the-race:tetris-coreweave:PLAN_KEY`.
4. Create each missing epic, then its children using the real returned parent ID
   and `bd create --parent`. Acceptance criteria, evidence requirements, and stream gates are
   included in the description with the original plan key.
5. Read each issue back to verify its ID, external reference, type, and parent.
6. Add missing blocking relationships with `bd dep add BLOCKED_ID BLOCKER_ID
   --type blocks`, then read them back to verify direction and type.
7. Persist the map atomically and report verified counts.

There is a local process lock to prevent simultaneous importers in one checkout.
Run the importer once at a time across clones as well. It does not promise a
distributed transaction across different computers.

A crash between creation and saving the map is recoverable: the next invocation
searches by the exact external reference and recovers the generated ID. Repeated
imports verify existing work and add missing edges; they do not reset progress,
reopen closed issues, reparent work, or overwrite descriptions. Conflicting maps,
duplicate external references, and incorrect parents cause a clear stop.

Plan edits do not silently rewrite already imported issue text. Review intentional
content/status changes and use `bd update` after inspecting that command's help.
Keep the ID map with the project handoff. Native database synchronization remains
the responsibility of the selected Beads release and your existing workflow;
pushing this source repository alone is not proof that a Dolt database synced.

## Start work and preserve evidence

```bash
bd ready --json
```

Use the real returned ID with `bd show`. Before claiming or closing work, inspect
the installed `bd update --help` and `bd close --help`; record the acceptance
evidence listed in the task. Prototype code being present does not establish that
the Forge GPU, installation policy, display proxy, restore process, or training
improvement has been verified. Those gates stay open until their evidence exists.

## API provenance and test scope

The commands and JSON fields were checked against the official upstream
[CLI reference](https://github.com/steveyegge/beads/blob/main/docs/CLI_REFERENCE.md)
and [issue types](https://github.com/steveyegge/beads/blob/main/internal/types/types.go).
The original repository URL currently redirects to the upstream `gastownhall`
organization. The importer additionally checks **your installed help at runtime**
because upstream changes and local versions may differ.

Verified API assumptions: `create --type epic|task --parent --external-ref
--description --priority --json`; `list --all --limit 0 --external-ref --json`;
`show --json` emits `id`, `issue_type`, `external_ref`, `parent`, and/or typed
`dependencies`; `dep add CHILD PREREQUISITE --type blocks` creates a blocker in
that direction. Unsupported local help or unexpected JSON fails closed.

The importer is source-checked and its dry-run/validation path can run without
Beads. An actual `bd` mutation test is a separate verification gate; do not claim
it passed until it runs against the intended installation.
