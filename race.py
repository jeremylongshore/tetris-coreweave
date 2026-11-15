#!/usr/bin/env python3
"""The Race: inspectable, source-only Tetris training and broadcast starter.

MIT License. Copyright (c) 2026 Jeremy Longshore.
No pretrained policy, game ROM, cloud credential, or hosted-model call.
Run `python race.py --help`. See README.txt before going live.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
DEV_SEEDS = [1000001, 1000002, 1000003, 1000004, 1000005]
RULES_ID = "placement-10x20-v1-cap50-noqueue-nohold"


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as f:
        json.dump(value, f, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
        tmp = f.name
    os.replace(tmp, path)


def read_json(path, fallback=None):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def append_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(value, allow_nan=False) + "\n")


def read_events(path):
    try:
        lines = Path(path).read_text().splitlines()
    except FileNotFoundError:
        return []
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # Ignore only a concurrently written incomplete final line.
    return out


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_torch(path, value):
    import torch
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        tmp = f.name
    try:
        torch.save(value, tmp)
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def make_model(n_features=16):
    import torch.nn as nn
    return nn.Sequential(nn.Linear(n_features, 64), nn.ReLU(),
                         nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 1))


def choose_device(request):
    import torch
    torch.set_num_threads(1)
    if request == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable. Confirm the GPU image or explicitly use --device cpu.")
        a = torch.ones((32, 32), device="cuda")
        _ = a @ a
        torch.cuda.synchronize()
    return torch.device(request)


def doctor(_args):
    """Print selected, nonsecret capabilities; never dump environment or config."""
    print("Python:", sys.version.split()[0])
    print("CPU cores visible (not a quota guarantee):", os.cpu_count())
    for package in ("numpy", "gymnasium", "tetris-gymnasium", "torch", "opencv-python-headless"):
        try:
            print(package + ":", importlib.metadata.version(package))
        except importlib.metadata.PackageNotFoundError:
            print(package + ": NOT INSTALLED")
    if shutil.which("nvidia-smi"):
        try:
            p = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                                "--format=csv,noheader"], capture_output=True, text=True, timeout=10)
            print("GPU inventory:", p.stdout.strip() if p.returncode == 0 else "query failed")
        except subprocess.TimeoutExpired:
            print("GPU inventory: query timed out")
    try:
        import torch
        print("PyTorch CUDA build:", torch.version.cuda)
        print("CUDA available:", torch.cuda.is_available())
        if torch.cuda.is_available():
            choose_device("cuda")
            print("CUDA matrix multiply + synchronization: PASS")
    except ImportError:
        print("PyTorch absent: use the CoreWeave-approved PyTorch image; do not guess its CUDA wheel.")
    except Exception as e:
        print("CUDA test: FAIL (" + type(e).__name__ + ")")
    print("Not tested here: egress, pip permission, lifetime, durable storage, quotas, preview access.")


def load_policy(path, device="cpu"):
    import torch
    torch.set_num_threads(1)
    data = torch.load(path, map_location="cpu", weights_only=True)
    if data.get("rules_id") != RULES_ID:
        raise ValueError("Checkpoint rules do not match this kit.")
    model = make_model(data["n_features"]).to(device)
    model.load_state_dict(data["model"])
    model.eval()
    return model, data


def policy_action(model, features, mask, device):
    import numpy as np
    import torch
    with torch.no_grad():
        q = model(torch.as_tensor(features, dtype=torch.float32, device=device)).squeeze(-1)
        q = q.masked_fill(~torch.as_tensor(mask, dtype=torch.bool, device=device), -float("inf"))
        # argmax is deterministic; no epsilon in scored evaluation.
        action = int(q.argmax().item())
    if not np.asarray(mask)[action]:
        raise RuntimeError("Policy selected an invalid placement.")
    return action


def run_game(model, seed, device="cpu", record=False, random_policy=False):
    import numpy as np
    from race_env import RaceEnv
    game = RaceEnv(seed=int(seed), cap=50)
    rng = np.random.default_rng(int(seed) + 777)
    frames = [game.frame()] if record else []
    actions = []
    while not game.done:
        if random_policy:
            action = int(rng.choice(np.flatnonzero(game.mask)))
        else:
            action = policy_action(model, game.features, game.mask, device)
        actions.append(action)
        game.step(action)
        if record:
            # Playback needs only observed state, not 40 candidate boards per frame.
            frame = game.frame()
            frame.pop("previews", None)
            frames.append(frame)
    result = {"seed": int(seed), "lines": game.lines, "points": game.points,
              "pieces": game.pieces, "actions": actions, "rules_id": RULES_ID}
    return result, frames


def evaluate_model(model, seeds, device, step, out=None):
    import numpy as np
    rounds = []
    replay = None
    for i, seed in enumerate(seeds):
        result, frames = run_game(model, seed, device, record=(i == 0))
        rounds.append(result)
        if i == 0:
            replay = {"label": "REPLAY: development evaluation; checkpoint " + str(step),
                      "step": step, "frames": frames}
    scores = [r["lines"] for r in rounds]
    summary = {"mean_lines": float(np.mean(scores)), "median_lines": float(np.median(scores)),
               "max_lines": int(max(scores)), "rounds": rounds}
    if out:
        atomic_json(Path(out) / "replay.json", replay)
    return summary


class ReplayBuffer:
    def __init__(self, capacity=20000, n_features=16):
        import numpy as np
        self.capacity, self.n_features = capacity, n_features
        self.size = self.pos = 0
        self.x = np.zeros((capacity, n_features), np.float32)
        self.nx = np.zeros((capacity, 40, n_features), np.float32)
        self.mask = np.zeros((capacity, 40), bool)
        self.reward = np.zeros(capacity, np.float32)
        self.done = np.zeros(capacity, bool)

    def add(self, x, nx, mask, reward, done):
        i = self.pos
        self.x[i], self.nx[i], self.mask[i] = x, nx, mask
        self.reward[i], self.done[i] = reward, done
        self.pos = (i + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def state(self):
        import torch
        return {"capacity": self.capacity, "n_features": self.n_features,
                "size": self.size, "pos": self.pos,
                **{key: torch.from_numpy(getattr(self, key)[:self.size].copy())
                   for key in ("x", "nx", "mask", "reward", "done")}}

    @classmethod
    def restore(cls, state):
        result = cls(state["capacity"], state["n_features"])
        result.size, result.pos = state["size"], state["pos"]
        for key in ("x", "nx", "mask", "reward", "done"):
            getattr(result, key)[:result.size] = state[key].cpu().numpy()
        return result


def update(model, target, opt, replay, rng, device):
    import torch
    import torch.nn.functional as F
    indices = rng.integers(0, replay.size, size=256)
    x, nx, mask, reward, done = [torch.as_tensor(getattr(replay, key)[indices], device=device)
                               for key in ("x", "nx", "mask", "reward", "done")]
    q = model(x).squeeze(-1)
    with torch.no_grad():
        online_next = model(nx).squeeze(-1).masked_fill(~mask, -1e9)
        best = online_next.argmax(dim=1, keepdim=True)
        next_value = target(nx).squeeze(-1).gather(1, best).squeeze(1)
        desired = reward + 0.99 * (~done).float() * next_value
    loss = F.smooth_l1_loss(q, desired)
    if not torch.isfinite(loss):
        raise RuntimeError("Non-finite training loss. Keep the last good checkpoint and inspect rewards.")
    opt.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 10)
    opt.step()
    return float(loss.item())


def train(args):
    import numpy as np
    import torch
    from race_env import RaceEnv
    out = Path(args.out)
    if (out / "latest.pt").exists() and not args.resume:
        raise ValueError("Output already contains a run. Use --resume or choose a new --out.")
    out.mkdir(parents=True, exist_ok=True)
    device = choose_device(args.device)
    rng = np.random.default_rng(args.seed)
    torch.manual_seed(args.seed)
    model = make_model().to(device)
    target = copy.deepcopy(model).to(device)
    target.eval()
    opt = torch.optim.Adam(model.parameters(), lr=0.0003)
    replay = ReplayBuffer()
    step = updates = episodes = 0
    prior_elapsed = 0.0
    history = []
    summary = None
    loss_value = 0.0
    run_seed = args.seed
    if args.resume:
        state = torch.load(out / "latest.pt", map_location="cpu", weights_only=True)
        if state["rules_id"] != RULES_ID:
            raise ValueError("Cannot resume a checkpoint with different rules.")
        model.load_state_dict(state["model"])
        target.load_state_dict(state["target"])
        opt.load_state_dict(state["optimizer"])
        for optimizer_state in opt.state.values():
            for key, value in optimizer_state.items():
                if torch.is_tensor(value):
                    optimizer_state[key] = value.to(device)
        replay = ReplayBuffer.restore(state["replay"])
        rng.bit_generator.state = json.loads(state["numpy_rng_json"])
        torch.set_rng_state(state["torch_rng"])
        cuda_rng = state.get("cuda_rng")
        if isinstance(cuda_rng, list):
            cuda_rng = cuda_rng[0] if cuda_rng else None
        if device.type == "cuda" and cuda_rng is not None:
            torch.cuda.set_rng_state(cuda_rng, device=device)
        step, updates, episodes = state["step"], state["updates"], state["episodes"]
        prior_elapsed = state["elapsed_s"]
        history, summary = state["history"], state["eval"]
        run_seed = state.get("seed", read_json(out / "run_config.json", {}).get("seed", args.seed))
    start_step = step
    started = time.monotonic()
    next_eval = started + args.eval_seconds
    next_status = started
    last_save = started
    interrupted = False
    wandb_run = None
    if args.wandb:
        import wandb
        # Authentication belongs in the provider's secret mechanism, off camera.
        # Offline mode is explicit and requires no token.
        wandb_run = wandb.init(project="the-race", mode=args.wandb,
                              config={"rules_id": RULES_ID, "algorithm": "shared-afterstate-double-dqn",
                                      "seed": run_seed, "device": str(device)})

    def policy_payload():
        return {"model": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                "n_features": 16, "step": step, "rules_id": RULES_ID, "seed": run_seed}

    def save():
        # Called only at an episode boundary. Resume starts the next seed; no
        # half-played game is silently reset, and replay/optimizer/RNG survive.
        payload = policy_payload()
        payload.update(target={k: v.detach().cpu() for k, v in target.state_dict().items()},
                       optimizer=opt.state_dict(), replay=replay.state(),
                       numpy_rng_json=json.dumps(rng.bit_generator.state),
                       torch_rng=torch.get_rng_state(),
                       cuda_rng=torch.cuda.get_rng_state(device=device) if device.type == "cuda" else None,
                       updates=updates, episodes=episodes,
                       elapsed_s=prior_elapsed + time.monotonic() - started,
                       history=history, eval=summary)
        atomic_torch(out / "latest.pt", payload)
        atomic_torch(out / "latest_policy.pt", policy_payload())
        atomic_json(out / "run_config.json", {"rules_id": RULES_ID,
                    "algorithm": "shared-afterstate-double-dqn", "seed": run_seed,
                    "device": str(device), "cap": 50, "gamma": 0.99,
                    "lr": 0.0003, "batch_size": 256, "replay_capacity": 20000,
                    "warmup_placements": 1024, "update_every_placements": 4,
                    "target_every_updates": 1000,
                    "epsilon": "1.0 to 0.05 over 50000 placements",
                    "training_seed_range": [1, 999999], "dev_seeds": DEV_SEEDS,
                    "source_sha256": {p.name: digest(p) for p in (ROOT / "race.py", ROOT / "race_env.py")},
                    "packages": {n: importlib.metadata.version(n) for n in
                                 ("torch", "numpy", "gymnasium", "tetris-gymnasium")}})

    if not args.resume:
        atomic_torch(out / "checkpoint_zero.pt", policy_payload())
        summary = evaluate_model(model, DEV_SEEDS, device, step, out)
        random_results = [run_game(None, s, random_policy=True)[0] for s in DEV_SEEDS]
        atomic_json(out / "random_baseline.json", random_results)
        history.append({"step": step, "mean_lines": summary["mean_lines"]})
        save()

    try:
        while step < args.steps:
            game = RaceEnv(seed=int(rng.integers(1, 1000000)), cap=50)
            episode_return = 0.0
            while not game.done:
                epsilon = max(0.05, 1.0 - 0.95 * step / 50000)
                if rng.random() < epsilon:
                    action = int(rng.choice(np.flatnonzero(game.mask)))
                else:
                    action = policy_action(model, game.features, game.mask, device)
                chosen_features = game.features[action].copy()
                nx, mask, reward, done, _ = game.step(action)
                replay.add(chosen_features, nx, mask, reward, done)
                step += 1
                episode_return += reward
                if replay.size >= 1024 and step % 4 == 0:
                    loss_value = update(model, target, opt, replay, rng, device)
                    updates += 1
                    if updates % 1000 == 0:
                        target.load_state_dict(model.state_dict())
                now = time.monotonic()
                if now >= next_status:
                    status = {"step": step, "updates": updates, "episodes": episodes,
                              "elapsed_s": prior_elapsed + now - started,
                              "placements_per_s": (step - start_step) / max(now - started, 1e-6),
                              "device": str(device), "epsilon": epsilon,
                              "loss": loss_value, "eval": summary, "history": history}
                    atomic_json(out / "status.json", status)
                    if wandb_run:
                        wandb_run.log({"training/placements": step, "training/loss": loss_value,
                                       "training/epsilon": epsilon,
                                       "training/placements_per_second": status["placements_per_s"]}, step=step)
                    next_status = now + 2
            episodes += 1
            append_json(out / "training.jsonl", {"step": step, "seed": game.seed,
                        "lines": game.lines, "points": game.points,
                        "pieces": game.pieces, "shaped_return": episode_return})
            now = time.monotonic()
            if now >= next_eval:
                summary = evaluate_model(model, DEV_SEEDS, device, step, out)
                history.append({"step": step, "mean_lines": summary["mean_lines"]})
                append_json(out / "evaluation.jsonl", {"step": step, **summary})
                print(f"step={step} dev_mean_lines={summary['mean_lines']:.2f} epsilon={epsilon:.3f}", flush=True)
                if wandb_run:
                    wandb_run.log({"evaluation/mean_lines": summary["mean_lines"],
                                   "evaluation/median_lines": summary["median_lines"],
                                   "evaluation/max_lines": summary["max_lines"]}, step=step)
                next_eval = time.monotonic() + args.eval_seconds
            if now - last_save >= args.save_seconds:
                save()
                last_save = time.monotonic()
            if args.seconds and time.monotonic() - started >= args.seconds:
                break
    except KeyboardInterrupt:
        # Do not label a mid-episode snapshot as exactly resumable.
        interrupted = True
        print("Interrupted mid-round. Keeping the last complete-episode checkpoint; at most one save interval lost.")
    if not interrupted:
        summary = evaluate_model(model, DEV_SEEDS, device, step, out)
        history.append({"step": step, "mean_lines": summary["mean_lines"]})
        save()
        now = time.monotonic()
        atomic_json(out / "status.json", {"step": step, "updates": updates, "episodes": episodes,
                    "elapsed_s": prior_elapsed + now - started, "placements_per_s": (step-start_step)/max(now-started, 1e-6),
                    "device": str(device), "epsilon": max(.05, 1-.95*step/50000),
                    "loss": loss_value, "eval": summary, "history": history, "finished": True})
        print(f"Saved step={step}; dev mean={summary['mean_lines']:.2f}; {out / 'latest.pt'}", flush=True)
    if wandb_run:
        wandb_run.finish()


def benchmark(args):
    """Warmup then measure complete collection + updates; no policy is retained."""
    import numpy as np
    import torch
    from race_env import RaceEnv
    device = choose_device(args.device)
    rng = np.random.default_rng(99)
    torch.manual_seed(99)
    model = make_model().to(device)
    target = copy.deepcopy(model)
    opt = torch.optim.Adam(model.parameters(), lr=.0003)
    replay = ReplayBuffer(capacity=2048)
    game = RaceEnv(seed=991, cap=50)
    collected = updates = 0
    started = None
    warmup_start = time.monotonic()
    while True:
        if game.done:
            game = RaceEnv(seed=int(rng.integers(1, 1000000)), cap=50)
        # Include inference even during random exploration, so the estimate is
        # not optimistic just because early epsilon is high.
        action = policy_action(model, game.features, game.mask, device)
        if rng.random() < .5:
            action = int(rng.choice(np.flatnonzero(game.mask)))
        x = game.features[action].copy()
        nx, mask, reward, done, _ = game.step(action)
        replay.add(x, nx, mask, reward, done)
        collected += 1
        if replay.size >= 1024 and collected % 4 == 0:
            update(model, target, opt, replay, rng, device)
            updates += 1
            if updates % 1000 == 0:
                target.load_state_dict(model.state_dict())
        if started is None and updates >= 5:
            if device.type == "cuda":
                torch.cuda.synchronize()
            started = time.monotonic()
            measured_start = collected
            update_start = updates
            print("Warmup complete; timing collection + optimization.", flush=True)
        if started is not None and time.monotonic() - started >= args.seconds:
            if device.type == "cuda":
                torch.cuda.synchronize()
            elapsed = time.monotonic() - started
            rate = (collected - measured_start) / elapsed
            result = {"device": str(device), "seconds": elapsed,
                      "warmup_s": started - warmup_start, "placements_per_s": rate,
                      "optimizer_updates_per_s": (updates - update_start) / elapsed,
                      "minutes_per_100k_placements_excluding_eval": 100000 / rate / 60,
                      "warning": "Throughput only; not a prediction of learning or B40 performance elsewhere."}
            print(json.dumps(result, indent=2))
            return


def smoke(_args):
    import numpy as np
    from race_env import RaceEnv
    a, b = RaceEnv(seed=42, cap=50), RaceEnv(seed=42, cap=50)
    rng = np.random.default_rng(42)
    for _ in range(50):
        assert np.array_equal(a.features, b.features)
        assert np.array_equal(a.mask, b.mask)
        assert a.frame()["board"] == b.frame()["board"]
        assert a.features.shape == (40, 16)
        assert np.isfinite(a.features).all()
        if a.done:
            break
        action = int(rng.choice(np.flatnonzero(a.mask)))
        ra, rb = a.step(action), b.step(action)
        assert ra[2:4] == rb[2:4]
    print("PASS: same positive seed + same actions give identical game and official counters.")
    print("Shape: 40 placements x 16 features; headless game works; no learning performed.")


def freeze(args):
    out = Path(args.out)
    destination = out / "frozen_policy.pt"
    if destination.exists():
        raise ValueError("A match is already frozen here. Use a new run directory for another match.")
    source = out / "latest_policy.pt"
    _, data = load_policy(source)
    # Load/save from a single fully loaded snapshot, even if trainer replaces latest.
    atomic_torch(destination, data)
    seeds = [secrets.randbelow(2_000_000_000) + 2_000_001 for _ in range(3)]
    while len(set(seeds)) != 3:
        seeds = [secrets.randbelow(2_000_000_000) + 2_000_001 for _ in range(3)]
    manifest = {"rules_id": RULES_ID, "checkpoint": digest(destination),
                "step": data["step"], "seeds": seeds,
                "score": "total lines; tie-break total line-clear points; remaining ties stand",
                "rounds": 3, "cap": 50}
    atomic_json(out / "match.json", manifest)
    print(f"Frozen checkpoint step {data['step']} before drawing three fresh final seeds.")
    print("Play all human final rounds first; AI final replays are withheld until then.")


def evaluate(args):
    model, data = load_policy(args.checkpoint, args.device)
    choose_device(args.device)
    seeds = [int(s) for s in args.seeds.split(",")]
    if any(s <= 0 for s in seeds):
        raise ValueError("Use positive seeds; upstream treats zero differently.")
    summary = evaluate_model(model, seeds, args.device, data["step"])
    print(json.dumps(summary, indent=2))


def serve(args):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import threading
    from urllib.parse import urlparse
    from race_env import RaceEnv
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    human = RaceEnv(seed=4242, cap=50)
    mode = "practice"
    lock = threading.Lock()
    # Rebuild an interrupted final from its recorded actions. Restarting the
    # preview server must not offer a new attempt on a revealed final seed.
    match_on_start = read_json(out / "match.json", {})
    completed_on_start = {r["seed"] for r in read_events(out / "human.jsonl") if r["mode"] == "final"}
    for final_seed in match_on_start.get("seeds", []):
        if final_seed in completed_on_start:
            continue
        moves = [r for r in read_events(out / "human_actions.jsonl")
                 if r.get("mode") == "final" and r["seed"] == final_seed]
        if moves:
            human, mode = RaceEnv(seed=final_seed, cap=50), "final"
            for expected_piece, move in enumerate(moves, 1):
                if move["piece"] != expected_piece:
                    raise RuntimeError("Final action log is inconsistent; inspect it before continuing the match.")
                human.step(move["action"])
            if human.done:
                append_json(out / "human.jsonl", {"player": "Jeremy", "mode": "final",
                            "seed": human.seed, "lines": human.lines, "points": human.points,
                            "pieces": human.pieces, "rules_id": RULES_ID})
        break

    def results():
        return read_events(out / "human.jsonl") + read_events(out / "matches.jsonl")

    def state():
        frame = human.frame()
        frame["mode"] = mode
        return {"human": frame, "training": read_json(out / "status.json", {}),
                "replay": read_json(out / "final_replay.json", None) or read_json(out / "replay.json", {}),
                "results": results(), "match": read_json(out / "match.json", {})}

    def maybe_score_finals():
        match = read_json(out / "match.json", {})
        if not match:
            return
        completed = {r["seed"] for r in read_events(out / "human.jsonl") if r["mode"] == "final"}
        if not set(match["seeds"]).issubset(completed):
            return
        scored = {r["seed"] for r in read_events(out / "matches.jsonl") if r["mode"] == "final"}
        model, data = load_policy(out / "frozen_policy.pt")
        for i, seed in enumerate(match["seeds"]):
            if seed in scored:
                continue
            result, frames = run_game(model, seed, record=True)
            result.update(player="AI", mode="final", checkpoint=match["checkpoint"], step=data["step"])
            append_json(out / "matches.jsonl", result)
            atomic_json(out / ("final_replay_" + str(i+1) + ".json"),
                        {"label": "REPLAY: final round " + str(i+1) + "; frozen checkpoint " + str(data["step"]),
                         "step": data["step"], "frames": frames})
        # Show first final replay; all three are retained on disk for inspection.
        if (out / "final_replay_1.json").exists():
            atomic_json(out / "final_replay.json", read_json(out / "final_replay_1.json"))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_unused):
            pass  # Never log credential-bearing proxy URLs or HTTP headers.

        def respond(self, code, value, kind="application/json"):
            payload = json.dumps(value).encode() if kind == "application/json" else value
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/", "/arena.html"):
                self.respond(200, (ROOT / "arena.html").read_bytes(), "text/html; charset=utf-8")
            elif path == "/api/state":
                with lock:
                    self.respond(200, state())
            else:
                self.respond(404, {"error": "Unknown route"})

        def do_POST(self):
            nonlocal human, mode
            # This is same-origin CSRF friction, NOT authentication. The service
            # must stay behind a private tunnel or an authenticated Forge proxy.
            if self.headers.get("X-Race-UI") != "1":
                self.respond(403, {"error": "Use the arena UI."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length > 4096:
                    raise ValueError("Request too large")
                value = json.loads(self.rfile.read(length) or b"{}")
                path = urlparse(self.path).path
                with lock:
                    if path == "/api/new":
                        if mode == "final" and not human.done:
                            raise ValueError("Complete the current final round; no retries.")
                        seed = int(value.get("seed", 4242))
                        if not 1 <= seed < 1000000:
                            raise ValueError("Practice seeds must be 1..999999.")
                        human, mode = RaceEnv(seed=seed, cap=50), "practice"
                    elif path == "/api/final":
                        if mode == "final" and not human.done:
                            raise ValueError("A final round is already in progress.")
                        match = read_json(out / "match.json", None)
                        if not match:
                            raise ValueError("First run: python race.py freeze --out " + str(out))
                        completed = {r["seed"] for r in read_events(out / "human.jsonl") if r["mode"] == "final"}
                        remaining = [s for s in match["seeds"] if s not in completed]
                        if not remaining:
                            maybe_score_finals()
                            raise ValueError("All three final rounds are complete. Results are on the scoreboard.")
                        human, mode = RaceEnv(seed=remaining[0], cap=50), "final"
                    elif path == "/api/move":
                        action = int(value["action"])
                        if human.done:
                            raise ValueError("Round finished. Start the next round.")
                        if not 0 <= action < 40 or not human.mask[action]:
                            raise ValueError("That placement is unavailable; choose a highlighted button.")
                        human.step(action)
                        append_json(out / "human_actions.jsonl", {"seed": human.seed, "mode": mode,
                                    "piece": human.pieces, "action": action,
                                    "lines": human.lines, "points": human.points})
                        if human.done:
                            append_json(out / "human.jsonl", {"player": "Jeremy", "mode": mode,
                                        "seed": human.seed, "lines": human.lines,
                                        "points": human.points, "pieces": human.pieces,
                                        "rules_id": RULES_ID})
                            maybe_score_finals()
                    else:
                        raise ValueError("Unknown action route")
                    self.respond(200, state())
            except (ValueError, KeyError, TypeError) as e:
                self.respond(400, {"error": str(e)})

    if args.host not in ("127.0.0.1", "localhost") and not args.behind_auth_proxy:
        raise ValueError("Non-loopback binding requires --behind-auth-proxy and a confirmed protected endpoint.")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    maybe_score_finals()
    print(f"Arena listening on port {args.port}. Use your confirmed private/authenticated preview.", flush=True)
    print("Do not put a bearer token or token-bearing URL on the stream.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Nonsecret package/GPU inspection").set_defaults(fn=doctor)
    sub.add_parser("smoke", help="Verify deterministic shared game without learning").set_defaults(fn=smoke)
    p = sub.add_parser("benchmark", help="Measure full loop; discard benchmark weights")
    p.add_argument("--seconds", type=int, default=60)
    p.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    p.set_defaults(fn=benchmark)
    p = sub.add_parser("train", help="Train random initial weights, or explicitly resume")
    p.add_argument("--out", default="run1")
    p.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--steps", type=int, default=200000, help="Total cumulative placement target")
    p.add_argument("--seconds", type=int, default=5400, help="This invocation's wall-clock budget; 0=steps only")
    p.add_argument("--eval-seconds", type=int, default=300)
    p.add_argument("--save-seconds", type=int, default=120)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--wandb", choices=("offline", "online"), default=None)
    p.set_defaults(fn=train)
    p = sub.add_parser("serve", help="Human controls + replay + scoreboard")
    p.add_argument("--out", default="run1")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--behind-auth-proxy", action="store_true")
    p.set_defaults(fn=serve)
    p = sub.add_parser("freeze", help="Freeze a checkpoint, then draw fresh final seeds")
    p.add_argument("--out", default="run1")
    p.set_defaults(fn=freeze)
    p = sub.add_parser("evaluate", help="Inspect a frozen policy on explicit positive seeds")
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--seeds", default=",".join(map(str, DEV_SEEDS)))
    p.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    p.set_defaults(fn=evaluate)
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
