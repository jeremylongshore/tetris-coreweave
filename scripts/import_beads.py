#!/usr/bin/env python3
"""Validate the checked-in plan; import through the installed bd CLI only.

Dry-run is the default. No Beads database files or issue IDs are fabricated.
SPDX-License-Identifier: MIT
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


class ImportFailure(RuntimeError):
    pass


def load_plan(path):
    plan = json.loads(path.read_text())
    if str(plan.get("schema_version")) not in {"1", "1.0"}:
        raise ImportFailure("Unsupported plan schema_version (expected 1 or 1.0).")
    project = plan.get("project")
    if not isinstance(project, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", project):
        raise ImportFailure("project must be a stable slug containing letters, digits, _, . or -.")
    nodes = {}
    epics = plan.get("epics")
    if not isinstance(epics, list) or not epics:
        raise ImportFailure("Plan must contain a nonempty epics array.")
    for epic in epics:
        for item, kind, parent in [(epic, "epic", None)] + [
                (task, "task", epic.get("key")) for task in epic.get("tasks", [])]:
            key = item.get("key")
            if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", key):
                raise ImportFailure(f"Invalid symbolic key: {key!r}")
            if key in nodes:
                raise ImportFailure(f"Duplicate key: {key}")
            for field in ("title", "description"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    raise ImportFailure(f"{key}: {field} must be nonempty text.")
            priority = item.get("priority", 2)
            if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 4:
                raise ImportFailure(f"{key}: priority must be an integer 0..4.")
            for field in ("depends_on", "acceptance", "evidence"):
                if not isinstance(item.get(field, []), list) or any(
                        not isinstance(v, str) or not v.strip() for v in item.get(field, [])):
                    raise ImportFailure(f"{key}: {field} must be an array of nonempty strings.")
            nodes[key] = {**item, "kind": kind, "parent_key": parent,
                          "priority": priority, "depends_on": item.get("depends_on", [])}
    # Include containment in the cycle check: blocking one's own epic is unsafe.
    edges = {key: node["depends_on"] + ([node["parent_key"]] if node["parent_key"] else [])
             for key, node in nodes.items()}
    for key, targets in edges.items():
        if len(targets) != len(set(targets)):
            raise ImportFailure(f"{key}: repeated dependency or dependency duplicates its parent.")
        for target in targets:
            if target not in nodes:
                raise ImportFailure(f"{key}: unknown dependency {target}")
    visited, visiting = set(), set()

    def visit(key):
        if key in visiting:
            raise ImportFailure(f"Dependency cycle includes {key}.")
        if key in visited:
            return
        visiting.add(key)
        for target in edges[key]:
            visit(target)
        visiting.remove(key)
        visited.add(key)

    for key in nodes:
        visit(key)
    return project, nodes


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


def rows(value):
    if value is None:
        return []
    if isinstance(value, list) and all(isinstance(v, dict) for v in value):
        return value
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return [value]
    raise ImportFailure("Unexpected bd JSON shape; inspect installed bd help/schema before proceeding.")


class Beads:
    def __init__(self, executable, root):
        self.executable, self.root = executable, root

    def run(self, *args, json_output=False):
        command = [self.executable, *args] + (["--json"] if json_output else [])
        try:
            result = subprocess.run(command, cwd=self.root, text=True,
                                    capture_output=True, timeout=90, check=False)
        except subprocess.TimeoutExpired as exc:
            raise ImportFailure("bd timed out. A write may have committed; rerun this importer to recover by external reference.") from exc
        if result.returncode:
            raise ImportFailure(f"bd {args[0] if args else ''} failed (exit {result.returncode}). "
                                "Inspect the command privately; a write may already have committed. "
                                "Rerun safely after resolving it. CLI output is withheld to avoid exposing credentials.")
        if not json_output:
            return result.stdout
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ImportFailure("bd did not return JSON. If a write committed, rerun to recover its external reference.") from exc

    def preflight(self, initialize):
        # Read local help before every possible database mutation, not a guessed version API.
        checks = [(("--help",), ["--json"]),
                  (("create", "--help"), ["--parent", "--external-ref", "--description", "--type", "--priority"]),
                  (("list", "--help"), ["--all", "--limit", "--external-ref"]),
                  (("show", "--help"), []),
                  (("dep", "add", "--help"), ["--type"])]
        if initialize:
            checks.append((("init", "--help"), ["--prefix", "--skip-hooks", "--skip-agents"]))
        for command, required in checks:
            help_text = self.run(*command)
            missing = [flag for flag in required if flag not in help_text]
            if missing:
                raise ImportFailure(f"Installed bd {' '.join(command)} lacks required flags: {', '.join(missing)}")

    def show(self, bead_id):
        result = rows(self.run("show", bead_id, json_output=True))
        exact = [item for item in result if item.get("id") == bead_id]
        if len(exact) != 1:
            raise ImportFailure(f"bd show did not return exactly the requested ID {bead_id}.")
        return exact[0]

    def by_ref(self, reference):
        result = rows(self.run("list", "--all", "--limit", "0", "--external-ref", reference, json_output=True))
        if any(item.get("external_ref") != reference for item in result):
            raise ImportFailure("bd exact external-ref filter returned unexpected records; stopping.")
        if len(result) > 1:
            raise ImportFailure(f"Duplicate external reference {reference}; resolve existing duplicates before retrying.")
        return result[0] if result else None


def parents(issue):
    result = {dep["id"] for dep in issue.get("dependencies", [])
              if dep.get("dependency_type") == "parent-child"}
    if issue.get("parent"):
        result.add(issue["parent"])
    return result


def blocked_by(issue):
    return {dep["id"] for dep in issue.get("dependencies", [])
            if dep.get("dependency_type") == "blocks"}


@contextlib.contextmanager
def import_lock(root):
    # Keep our lock out of both git and bd's native storage.
    import fcntl
    lock_path = Path(tempfile.gettempdir()) / ("race-beads-" + hashlib.sha256(str(root).encode()).hexdigest()[:16] + ".lock")
    with lock_path.open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ImportFailure("Another importer is already running for this checkout.") from exc
        yield


def apply(args, project, nodes):
    executable = shutil.which(args.bd)
    if not executable:
        raise ImportFailure("bd is not installed. See docs/BEADS.md; dry-run requires only Python.")
    bd = Beads(executable, ROOT)
    bd.preflight(args.init)
    if args.init:
        if (ROOT / ".beads").exists():
            raise ImportFailure(".beads already exists. Do not reinitialize it; rerun --apply without --init.")
        bd.run("init", "--prefix", "tcf", "--skip-hooks", "--skip-agents")
    # Fail before creating anything if the project database is unavailable.
    bd.run("list", "--all", "--limit", "1", json_output=True)
    mapping = {"schema_version": 1, "project": project, "ids": {}}
    if args.map.exists():
        mapping = json.loads(args.map.read_text())
        if mapping.get("project") != project or not isinstance(mapping.get("ids"), dict):
            raise ImportFailure("ID map does not belong to this project or is malformed.")
    ids = mapping["ids"]
    created = recovered = 0
    # Enclosing epics occur before their children, so --parent uses an actual verified ID.
    for key, node in nodes.items():
        reference = f"the-race:{project}:{key}"
        found = bd.by_ref(reference)
        if key in ids:
            mapped = bd.show(ids[key])
            if mapped.get("external_ref") != reference or not found or found["id"] != ids[key]:
                raise ImportFailure(f"{key}: ID map and database disagree; refusing to create or relink anything.")
        elif found:
            ids[key] = found["id"]
            recovered += 1
            write_json(args.map, mapping)
        else:
            description = node["description"]
            for field, heading in (("acceptance", "Acceptance criteria"), ("evidence", "Required evidence")):
                if node.get(field):
                    description += "\n\n## " + heading + "\n" + "\n".join("- " + line for line in node[field])
            if node.get("stream_gate"):
                description += "\n\nStream gate: " + node["stream_gate"]
            description += f"\n\nPlan key: {key}\nSource: planning/beads-plan.json"
            command = ["create", node["title"], "--type", node["kind"],
                       "--priority", str(node["priority"]), "--description", description,
                       "--external-ref", reference]
            if node["parent_key"]:
                command += ["--parent", ids[node["parent_key"]]]
            result = rows(bd.run(*command, json_output=True))
            if len(result) != 1 or not isinstance(result[0].get("id"), str):
                raise ImportFailure(f"{key}: create returned no unique real ID. Rerun for external-ref recovery.")
            ids[key] = result[0]["id"]
            write_json(args.map, mapping)  # Durable immediately after each successful create.
            created += 1
        issue = bd.show(ids[key])
        expected_parent = {ids[node["parent_key"]]} if node["parent_key"] else set()
        if issue.get("external_ref") != reference or issue.get("issue_type") != node["kind"]:
            raise ImportFailure(f"{key}: existing bead identity/type differs from this plan.")
        if parents(issue) != expected_parent:
            raise ImportFailure(f"{key}: parent mismatch; refusing to reparent existing work.")
        print(f"{key} -> {ids[key]} ({node['kind']})")
    added = 0
    for key, node in nodes.items():
        for prerequisite in node["depends_on"]:
            if ids[prerequisite] not in blocked_by(bd.show(ids[key])):
                bd.run("dep", "add", ids[key], ids[prerequisite], "--type", "blocks", json_output=True)
                added += 1
            if ids[prerequisite] not in blocked_by(bd.show(ids[key])):
                raise ImportFailure(f"Dependency did not verify: {key} is blocked by {prerequisite}.")
    mapping["plan_sha256"] = hashlib.sha256(args.plan.read_bytes()).hexdigest()
    write_json(args.map, mapping)
    print(f"Verified {len(nodes)} real beads; created {created}, recovered {recovered}, added {added} blocking edges.")
    print("Existing descriptions, status, owners, and extra dependencies were preserved. Run bd ready --json next.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=ROOT / "planning/beads-plan.json")
    parser.add_argument("--map", type=Path, default=ROOT / "planning/beads-id-map.json")
    parser.add_argument("--bd", default="bd", help="Installed Beads executable name or path")
    parser.add_argument("--apply", action="store_true", help="Create/verify actual beads and dependencies")
    parser.add_argument("--init", action="store_true", help="With --apply only: initialize a new .beads database first")
    args = parser.parse_args()
    try:
        project, nodes = load_plan(args.plan)
        edges = sum(len(n["depends_on"]) for n in nodes.values())
        print(f"VALID {project}: {sum(n['kind'] == 'epic' for n in nodes.values())} epics, "
              f"{sum(n['kind'] == 'task' for n in nodes.values())} tasks, {edges} blocking edges; no cycles.")
        if not args.apply:
            if args.init:
                raise ImportFailure("--init requires --apply. No changes made.")
            for key, node in nodes.items():
                print(f"{key} [{node['kind']}, P{node['priority']}] parent={node['parent_key'] or '-'} "
                      f"blocked_by={','.join(node['depends_on']) or '-'}: {node['title']}")
            print("DRY RUN: no bd commands executed, no database changed, and no IDs invented.")
            return 0
        with import_lock(ROOT):
            apply(args, project, nodes)
        return 0
    except (ImportFailure, OSError, ValueError, TypeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
