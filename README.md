# Viam Pick-and-Place Workshop — Companion Repo

Clone-able config and code for the **Vision-Guided Pick-and-Place** workshop:
build a robot that **detects** blocks by shape, **picks** them up with motion
planning, and **sorts** them into a bin — on a uFactory xArm6 with a
wrist-mounted Intel RealSense depth camera.

This repo holds the supplemental assets the workshop links to. Follow the
step-by-step tutorial in the Viam docs:

> **Tutorial:** [Vision-Guided Pick-and-Place with the xArm6](https://docs.viam.com/tutorials/pick-and-place/)
> *(link goes live when the workshop ships)*

You don't need to read any of this repo cover to cover. The tutorial tells you
which file to grab at each phase.

---

## What's here

```
pick-and-place/
├── config/
│   ├── machine-fragment.json       # reference config for checking your work (you configure resources by hand)
│   └── obstacles-template.json     # table + safety-wall obstacles — measure your workspace, fill in positions
├── scripts/
│   ├── pyproject.toml              # uv project, declares viam-sdk
│   ├── .python-version             # pins Python 3.11
│   ├── uv.lock                     # locked dependency versions (uv)
│   ├── starter-script.py           # Phase 4–5 starting point — TODOs in place
│   └── reference-solution.py       # complete working script — no TODOs
└── setup/
    └── frame-calibration-worksheet.md   # measure the gripper + camera frames
```

> The `obstacles-template.json` safety walls assume a workspace centered on the arm base; if yours isn't, adjust the wall geometry accordingly.

## Hardware

| Component | Role |
|---|---|
| uFactory xArm6 | 6-DOF arm · direct Ethernet to the robot computer |
| uFactory finger gripper | End effector at the flange |
| Intel RealSense D435 | RGB + depth camera · USB · wrist-mounted on the arm |
| System76 Meerkat | Robot computer · x86_64 · Ubuntu · runs `viam-agent` + `viam-server` |

If your hardware is **pre-provisioned** for the session, skip straight to the
tutorial. If you're **provisioning your own**, work through
[`setup/frame-calibration-worksheet.md`](setup/frame-calibration-worksheet.md)
first so the frame system matches physical reality.

---

## Quick start

**1. Clone**

```sh
git clone https://github.com/viam-devrel/pick-and-place.git
cd pick-and-place
```

**2. Add the resources to your machine**

In the Viam app, add the arm, gripper, camera, vision pipeline
(`shape-detector` → `vision-segment`), and the five pose switches by hand.
Use [`config/machine-fragment.json`](config/machine-fragment.json) as a reference
to check your work — compare it against your machine's config, not as an import shortcut.

> Replace every `REPLACE_WITH_...` placeholder (the arm's IP, safety-wall positions)
> with values for your setup. See [Placeholders](#placeholders-to-replace).

**3. Set up the Python environment** (Phase 4)

[`uv`](https://docs.astral.sh/uv/) is the recommended path:

```sh
cd scripts
uv sync                 # creates a venv and installs viam-sdk
uv run python starter-script.py
```

Prefer plain `pip`? `python3 -m venv .venv && source .venv/bin/activate && pip install viam-sdk`.

**4. Paste your connection details**

Open `scripts/starter-script.py` and fill in `MACHINE_ADDRESS`, `API_KEY`, and
`API_KEY_ID` from your machine's **Connect** tab → **Python SDK**. Never commit
these — `.env` and `*.local.py` are gitignored.

---

## The workshop, in phases

| Phase | Topic | Time | This repo |
|---|---|---|---|
| 1 | Platform mental model | ~15 min | — |
| 2 | Configure resources + explore the app | ~20 min | `config/machine-fragment.json` |
| 3 | Static positions + safety obstacles | ~20 min | `config/obstacles-template.json` |
| 4 | Local Python script *(core goal)* | ~30 min | `scripts/starter-script.py` |
| 5 | Inline module *(optional)* | ~15 min | `scripts/reference-solution.py` |

Finishing the local Python script (Phase 4) is a complete success. The module
(Phase 5) is an optional next step.

---

## The assets explained

### `config/machine-fragment.json`

A reference config listing every resource the workshop needs: `arm-1`, `gripper-1`,
`cam-1`, the `shape-detector` and `vision-segment` vision services, and the
`home/approach/grasp/travel/place` pose switches (built on
`erh:vmodutils:arm-position-saver`). Add these resources by hand in the Viam app
and use this file to check your work — do not import it as a shortcut.

### `config/obstacles-template.json`

The Phase 3 **WorldState** geometry — a table surface and two safety walls — that
teaches the motion planner what to avoid. The obstacle components register
through `erh:vmodutils` and present on the API as grippers. Wall positions are
placeholders; you fill them in by measuring your workspace with `GetEndPosition`.

### `scripts/starter-script.py`

The Phase 4–5 starting point. It connects, runs the static pick-and-place sequence,
and leaves numbered `TODO`s for the perception loop. Copy this — not the Connect
tab snippet — once you've confirmed the initial connection.

### `scripts/reference-solution.py`

The completed script with no TODOs: detect → transform to world frame → pick with
a straight-line descent → place at the saved bin pose → repeat until the
workspace is clear. Treat it as a reference to compare against, and **tune the
constants and offsets for your hardware** before running near people.

---

## Placeholders to replace

Search for these tokens after cloning:

| Token | Where | Replace with |
|---|---|---|
| `REPLACE_WITH_ARM_IP` | `config/machine-fragment.json` | Your xArm6 controller IP |
| `REPLACE_WITH_MEASURED_FRONT_Y` / `REPLACE_WITH_MEASURED_SIDE_X` | `config/obstacles-template.json` | Safety-wall positions from `GetEndPosition` |
| `<paste from Connect tab>` | `scripts/*.py` | Machine address + API key + key ID |

The `viam-sdk` version, vision-service tuning (`confidence_threshold_pct`,
`mean_k`, `sigma`), and grasp/approach offsets (`GRIPPER_LENGTH_MM`,
`APPROACH_MM`) are sensible defaults — adjust to your blocks and gripper.

