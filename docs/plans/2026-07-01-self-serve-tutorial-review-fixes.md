# Self-Serve Tutorial Review Fixes — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Dispatch a fresh **sonnet** subagent per task for implementation; run **opus** code review between tasks before committing.

**Goal:** Update `pick-n-place-tutorial-plan.md` so its spec fully incorporates the self-serve review decisions captured in `tutorial-review-notes.md` — fixing one fabricated API, reframing resource configuration as hands-on, building out the prerequisites gate, and expanding each per-phase content spec for the self-serve learner.

**Architecture:** These are content/spec edits to a single Markdown planning document (with `tutorial-review-notes.md` as the decision source of truth). No Hugo content pages are authored in this plan — that is a separate downstream effort. Tasks are ordered by priority: factual correctness → structural reframe → prerequisites gate → per-phase UX specs. Per-phase tasks (4–9) are mutually independent and touch disjoint sections.

**Tech Stack:** Markdown. Verification is by `grep`/read against the review notes, not automated tests.

**Source of truth:** `tutorial-review-notes.md` (per-phase decision checklists + cross-cutting corrections + synthesis).

**Target file:** `pick-n-place-tutorial-plan.md` (unless a task states otherwise).

**Branching:** Repo is currently on `main`. Before Task 1, create a working branch:
```bash
git checkout -b tutorial-review-fixes
```

**Model assignment:** implementation subagents = `sonnet`; review pass between tasks = `opus`.

**Per-task verification convention:** after each edit, re-read the changed section and grep for the anchor to confirm the change landed and no stale text remains. Commit only after opus review passes.

---

### Task 1: Fix the fabricated `FrameSystemClient` module API (Priority 1 — correctness)

**Why first:** The plan prescribes a non-existent API (`FrameSystemClient` injected as a dependency). A solo learner would copy it and hit an ImportError/AttributeError with no facilitator to recover. This is a bug, not a style issue.

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `### `06-inline-module.md`` section, the bullet beginning **`transform_pose` inside a module:** and its fenced code block (currently ~lines 238–254).

**Step 1: Locate the block**

Run: `grep -n "FrameSystemClient" pick-n-place-tutorial-plan.md`
Expected: several hits inside the `06-inline-module.md` spec.

**Step 2: Replace the entire `transform_pose`-in-module bullet + code block**

Replace the bullet that starts with `- **`transform_pose` inside a module:** primary approach is `FrameSystemClient`...` and its full ```python ... ``` block **and** the trailing `Note: this replaces `robot.transform_pose()`...` line with:

````markdown
- **`transform_pose` inside a module:** there is **no** `FrameSystemClient` and no injected frame-system dependency. A module reaches the machine-management API (including `transform_pose`) by creating a **single, reused `RobotClient` from within the module**, authenticated from environment variables (`VIAM_API_KEY`, `VIAM_API_KEY_ID`, `VIAM_MACHINE_FQDN`). Reference: https://docs.viam.com/build-modules/platform-apis/#use-the-machine-management-api-from-a-module
  ```python
  import os
  from viam.robot.client import RobotClient

  async def create_robot_client_from_module():
      opts = RobotClient.Options.with_api_key(
          api_key=os.environ["VIAM_API_KEY"],
          api_key_id=os.environ["VIAM_API_KEY_ID"],
      )
      return await RobotClient.at_address(os.environ["VIAM_MACHINE_FQDN"], opts)

  # in logic — create once, reuse:
  if not self.robot_client:
      self.robot_client = await create_robot_client_from_module()
  world_pose = await self.robot_client.transform_pose(obj_in_cam, "world")
  ```
  Note: this is the recommended in-module RobotClient pattern (exactly one, reused) — do NOT create a new connection per call, and do NOT hardcode credentials.
````

**Step 3: Verify**

Run: `grep -n "FrameSystemClient" pick-n-place-tutorial-plan.md`
Expected: **zero hits.**
Run: `grep -n "VIAM_MACHINE_FQDN\|create_robot_client_from_module" pick-n-place-tutorial-plan.md`
Expected: hits present in the `06-inline-module.md` spec.

**Step 4: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "fix: correct fabricated FrameSystemClient module API to in-module RobotClient pattern"
```

---

### Task 2: Reframe resource configuration as hands-on; fragment as reference (Priority 2 — structural)

**Why:** The original plan assumes resources can be pre-provisioned via `machine-fragment.json` to "remove friction." Decision: resources are ALWAYS configured by the learner; the fragment only lets them check their work. Touches three anchors.

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `machine-fragment.json` line (~168), the `_index` "two paths" bullet (~186), the `02-configure-resources.md` content bullet (~198).

**Step 1: Correct the fragment characterization**

Replace:
`` `machine-fragment.json` is the highest-priority asset — it removes the "manually add five switches and two vision services" friction from setup. ``
with:
`` `machine-fragment.json` is a **check-your-work reference**, not an import — learners configure every resource by hand, then compare against this known-good config. It is NOT used to skip configuration. ``

**Step 2: Fix the `02` "pre-configured" framing**

Replace:
`- Content: CONFIGURE tab walkthrough, what's pre-configured (resource table), CONTROL tab test cards, 3D scene tab`
with:
`- Content: CONFIGURE tab walkthrough, learner configures each hardware resource by hand (resource table as target state), CONTROL tab test cards, 3D scene tab`

**Step 3: Clarify the `_index` paths distinguish hardware vs resource config**

Replace:
`- Two explicit paths: "Hardware pre-provisioned by instructor → start at Phase 1" / "Provisioning your own hardware → complete the setup guide first"`
with:
`- Two explicit paths (note: only physical hardware + viam-agent/server may be pre-provisioned — resource configuration is always the learner's hands-on work): "Physical hardware ready → start at Phase 1" / "Provisioning your own hardware → complete the setup guide first"`

**Step 4: Verify**

Run: `grep -n "highest-priority asset\|what's pre-configured" pick-n-place-tutorial-plan.md`
Expected: zero hits.
Run: `grep -n "check-your-work reference\|by hand" pick-n-place-tutorial-plan.md`
Expected: hits present.

**Step 5: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "docs: reframe resources as hands-on config, fragment as check-your-work reference"
```

---

### Task 3: Build out the `_index.md` prerequisites gate (Priority 3)

**Why:** In self-serve, the `_index` carries the orientation a facilitator would deliver live. It must include the two-milestone framing, prerequisite resource links, login-as-prereq, hardware-context-via-links, and environment validation.

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `### `pick-and-place/_index.md`` bullet list.

**Step 1: Replace the `_index` bullet list**

Replace the existing `### `pick-and-place/_index.md`` bullets with:

```markdown
### `pick-and-place/_index.md`

- Header image of complete hardware setup
- What you'll build (one paragraph)
- **Two-milestone framing (lifted from workshop slide 0.2):** Phase 4 (drive the robot from your own code) is a real, bankable win; Phase 5 (perception) is milestone two. Everyone should leave with at least the Phase 4 script; the module is optional. This is the safety net that keeps learners from bouncing when perception gets hard.
- Phase list with time estimates (Phases 1–5 core, Phase 6 optional)
- **Prerequisites checklist with verification commands AND helpful links** for completing each: Python 3.10+, `viam-sdk`, a working terminal, and a Viam account with an accessible machine. Include links to install/setup resources for each prerequisite.
- **Login/machine-access is a prerequisite, not an in-tutorial step:** "log in at app.viam.com, find your machine, confirm the green Live indicator" belongs in this checklist so the tutorial body stays focused on doing.
- **Environment validation is part of the prerequisites gate:** confirm a working Python env (uv recommended) that can `import viam` BEFORE Phase 4, so Phase 4 is just connect + run.
- Hardware context is delivered via links (setup guide + hardware-overview), not a separate tour section
- Two explicit paths (see Task 2 wording): physical hardware ready → Phase 1 / provision your own → setup guide first
- Link to setup guide: `/guides/hardware-setup/xarm6-pick-and-place/`
- Link to companion repo
```

**Step 2: Verify**

Run: `grep -n "Two-milestone framing\|Login/machine-access is a prerequisite\|Environment validation is part" pick-n-place-tutorial-plan.md`
Expected: three hits in the `_index` spec.

**Step 3: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "docs: build out _index prerequisites gate for self-serve (milestones, prereq links, login/env as prereqs)"
```

---

### Task 4: Expand the Phase 1 spec (`01-platform-mental-model.md`)

**Why:** Overturn "no live interactions yet"; add grounding interactions, a self-check, keep the perception-pipeline foreshadow, and clarify builtin-vs-module + the module-download moment. (See `tutorial-review-notes.md` → Phase 1.)

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `### `01-platform-mental-model.md`` bullets.

**Step 1: Replace the `01` bullets** with:

```markdown
### `01-platform-mental-model.md`

- Content: three-layer architecture (cloud/agent/server), SDK connection, config-as-source-of-truth, resource model (components vs services), dependency graph
- **Live grounding interactions throughout (overrides "no live interactions yet"):** have the learner open their own CONFIGURE tab and find `arm-1`, read its `namespace:family:model`, etc. — ground each abstraction in their real machine to keep engagement high.
- **Keep the perception-pipeline preview in the dependency graph** — use `shape-detector` / `vision-segment` as concrete examples of services and composing resources (intentional foreshadowing of what they build in Phase 5).
- **Builtin vs. module-provided resources:** explain that some resources are builtin to viam-server (RDK) and most added functionality comes from modules, and how modules interact with viam-server. Ground it by having the learner watch the module download + start after configuring the uFactory xArm module (the config action itself lands in Phase 2).
- **Self-check** at the end: "you should now be able to answer the three questions from the top — if not, re-skim."
- Estimated reading time + interaction: 15 min
```

**Step 2: Verify**

Run: `grep -n "Live grounding interactions\|Self-check\|Builtin vs" pick-n-place-tutorial-plan.md`
Expected: hits in the `01` spec.

**Step 3: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "docs: expand Phase 1 spec (live grounding, self-check, builtin-vs-module)"
```

---

### Task 5: Expand the Phase 2 spec (`02-configure-resources.md`)

**Why:** Hands-on config of all resources, the module-download moment on xArm config, an active 3D-scene task, and the gripper `IsHoldingSomething` task. (See `tutorial-review-notes.md` → Phase 2. Note: the "pre-configured" wording was already fixed in Task 2 — do not undo it.)

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `### `02-configure-resources.md`` bullets (append/adjust; preserve the Task 2 correction).

**Step 1: Add these bullets to the `02` spec** (after the existing content/vision bullets, before the reading-time line):

```markdown
- **Configuring the `viam:ufactory:xArm6` arm is the module-download moment** (delivers the Phase 1 builtin-vs-module lesson): learner adds the arm and watches viam-server download + start the module live.
- **3D scene tab active task:** "jog joint 1 and watch the `cam-1` frame move with the arm" — this is where the wrist-mounted-camera insight lands (load-bearing for Phase 5's detect-from-home rule).
- **Gripper card active task for `IsHoldingSomething`:** learner places a block between the gripper fingers, presses Grab, and observes the resulting status.
- Add a gripper checkpoint for symmetry with the camera/arm checkpoints.
```

**Step 2: Verify**

Run: `grep -n "module-download moment\|3D scene tab active task\|IsHoldingSomething" pick-n-place-tutorial-plan.md`
Expected: hits in the `02` spec.

**Step 3: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "docs: expand Phase 2 spec (hands-on config, module-download moment, 3D-scene + gripper tasks)"
```

---

### Task 6: Expand the Phase 3 spec (`03-static-positions.md`)

**Why:** Replace facilitator-provided measurements with teaching frame-geometry config + measuring your own workspace; frame safety walls as a production feature; keep problem-isolation as a real workflow; use the app's duplicate feature; keep the SetPosition troubleshooting. (See `tutorial-review-notes.md` → Phase 3.)

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `### `03-static-positions.md`` bullets.

**Step 1: Update/add bullets** so the `03` spec includes:

```markdown
- **Teach how frame geometries are configured, and have learners measure their own workspace** (replaces facilitator-provided dimensions): spend real time on measuring the table + obstacles and translating measurements into geometry config. This is the self-serve source for obstacle/table dimensions.
- **Safety walls framed as a production-motion feature:** configured to fit the learner's own workspace; pitch virtual safety walls as a demo of the motion system's power for real-world/production deployments, not just classroom safety.
- **Keep the problem-isolation rationale as proof of value:** pose-to-pose motion without perception is a common real operational workflow in production workcells — not filler before perception.
- **Use the app's "duplicate" resource feature** to create poses #2–5 after configuring #1 fully (a nice peek at power-user features). `machine-fragment.json` remains the check-your-work reference.
- Keep the SetPosition `1`=save / `2`=execute callout prominent, PLUS an inline troubleshooting aside for "SetPosition(2) does nothing" (didn't save first) — no facilitator to unstick.
```

Remove any bullet still implying a facilitator provides table dimensions.

**Step 2: Verify**

Run: `grep -n "measure their own workspace\|production-motion feature\|duplicate" pick-n-place-tutorial-plan.md`
Expected: hits in the `03` spec.
Run: `grep -in "facilitator provides" pick-n-place-tutorial-plan.md`
Expected: zero hits.

**Step 3: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "docs: expand Phase 3 spec (measure-your-workspace geometry, safety walls as production feature, duplicate resources)"
```

---

### Task 7: Expand the Phase 4 spec (`04-control-the-robot-from-python.md`)

**Why:** Sell the Python-control advantage concretely (incl. UI→SDK method mapping), reference the Connect-tab boilerplate, add a secrets note, and lean on the prereq-gate env validation + uv + connect checkpoint. (See `tutorial-review-notes.md` → Phase 4.)

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `### `04-control-the-robot-from-python.md`` bullets.

**Step 1: Add/adjust bullets** so the `04` spec includes:

```markdown
- **Sell the advantage of Python control code concretely:** programmability (loops/branches/logic) AND the ease of translating the Control-tab UI controls to SDK method names (the cards map to methods). Make the payoff felt, not just asserted.
- **Reference the Connect-tab boilerplate:** the starter script follows a similar structure to the SDK boilerplate the app generates in the Connect tab — learner reads/understands the connection block rather than authoring it from scratch.
- **Secrets-handling note:** don't commit API keys; use the companion repo `.gitignore` or env vars.
- Environment validation happens in the Phase 0 prerequisites gate (see Task 3), so this phase's budget is connect + run. Keep uv as the primary path (pins Python, reproducible); pip is fallback. Add a "verify your environment connects" checkpoint (`resource_names`) before robot logic.
```

**Step 2: Verify**

Run: `grep -n "translating the Control-tab\|Connect-tab boilerplate\|Secrets-handling" pick-n-place-tutorial-plan.md`
Expected: hits in the `04` spec.

**Step 3: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "docs: expand Phase 4 spec (Python-control advantage, Connect-tab boilerplate, secrets, env-in-prereqs)"
```

---

### Task 8: Expand the Phase 5 spec (`05-perception-guided-picking.md`)

**Why:** The hardest phase. Add the home-pose guard clause, worked approach-offset + learner grasp-offset practice, explicit `motion.move("gripper-1")` frame semantics, symptom→3D-scene debugging with a Phase-3 forward-link, and granular sub-checkpoints. (See `tutorial-review-notes.md` → Phase 5.)

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `### `05-perception-guided-picking.md`` bullets.

**Step 1: Add/adjust bullets** so the `05` spec includes:

```markdown
- **Home-pose guard clause in the perception code:** return to / assert `home-pose` before every detect, so the wrist-camera "detect from home" rule is structurally enforced (prevents the silent plausible-but-wrong pick-point footgun). Make it the FIRST entry in the debugging guide.
- **Worked approach-offset; learner practices the gripper-TCP grasp offset:** walk through computing the approach pose fully as a worked example, then have the learner compute the grasp/gripper-TCP offset themselves (productive struggle). Don't leave both as a bare TODO.
- **Make `motion.move("gripper-1", …)` semantics explicit:** it drives the gripper's coordinate frame to the destination pose in the world — NOT the end of the arm (which is what the UI MoveToPosition / the arm component API move). Contrast the two so the offset math makes sense.
- **Motion-planning debugging maps symptom → 3D scene tab** (what to look for), with a forward-link back to Phase 3 obstacle/safety-wall config (skipping it bites here).
- **Granular sub-checkpoints:** detector works → transform yields sane world coords → approach reachable → grasp succeeds (better self-diagnosis for a stuck solo learner).
```

**Step 2: Verify**

Run: `grep -n "guard clause\|Worked approach-offset\|drives the gripper's coordinate frame\|sub-checkpoints" pick-n-place-tutorial-plan.md`
Expected: hits in the `05` spec.

**Step 3: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "docs: expand Phase 5 spec (home guard, worked/practice offsets, gripper-frame semantics, granular checkpoints)"
```

---

### Task 9: Expand the Phase 6 spec — non-API items (`06-inline-module.md`)

**Why:** Beyond the Task 1 API fix, add honest "mostly packaging + one real change" framing, tier the scope, strengthen the "why bother," and adopt the plan time estimate. (See `tutorial-review-notes.md` → Phase 6.) Do NOT touch the Task 1 `transform_pose` block.

**Files:**
- Modify: `pick-n-place-tutorial-plan.md` — the `### `06-inline-module.md`` bullets (the framing/scope/why/time bullets, not the corrected API block).

**Step 1: Add/adjust bullets** so the `06` spec includes:

```markdown
- **Honest framing — "mostly packaging + one real change":** the `transform_pose` access genuinely changes (in-module RobotClient from env vars), so don't let the Phase 4 "same logic, different entry point" line set a trap.
- **Tier the scope:** a minimal viable module (repackage + `do_command`, trigger manually) is the core optional path; scheduled jobs + autonomous operation are an explicit "level 2" for a low-effort on-ramp.
- **Strong "why bother?" framing** since it's optional — explicit "you'd want this when… (survives disconnection, auto-restart, OTA deploy, runs on a schedule)" so learners self-select.
- Estimated reading time + interaction: use the plan's estimate (20 min), not the workshop slides' 13 min.
```

**Step 2: Verify**

Run: `grep -n "mostly packaging\|Tier the scope\|why bother" pick-n-place-tutorial-plan.md`
Expected: hits in the `06` spec.
Run: `grep -n "FrameSystemClient" pick-n-place-tutorial-plan.md`
Expected: still zero (Task 1 preserved).

**Step 3: Commit**

```bash
git add pick-n-place-tutorial-plan.md
git commit -m "docs: expand Phase 6 spec (honest framing, tiered scope, why-bother, plan time estimate)"
```

---

### Task 10: Final consistency sweep

**Files:** `pick-n-place-tutorial-plan.md`, cross-checked against `tutorial-review-notes.md`.

**Step 1:** Re-read `tutorial-review-notes.md` end-to-end and confirm every unchecked action item is reflected in the plan doc. For each, tick the checkbox in `tutorial-review-notes.md` (change `- [ ]` to `- [x]`) as it is applied.

**Step 2: Verify no regressions**

Run: `grep -nE "FrameSystemClient|highest-priority asset|what's pre-configured|facilitator provides" pick-n-place-tutorial-plan.md`
Expected: zero hits.

**Step 3: Commit**

```bash
git add pick-n-place-tutorial-plan.md tutorial-review-notes.md
git commit -m "docs: final consistency sweep; tick applied review items"
```

---

## Out of scope (explicitly deferred)

- Authoring the actual Hugo content pages (`content/tutorials/pick-and-place/*.md`), shortcodes, layouts — a separate downstream effort gated on the plan's own open questions (Hugo config, permalinks, theme).
- Editing the facilitated workshop slides (`viam-workshop-slides-outline.md`). The review was self-serve-scoped; shared factual items (gripper-TCP nuance, PoseInFrame kwargs) are already correct there from earlier work.
- Updating `scripts/starter-script.py` / `reference-solution.py` to add the home-pose guard clause — worth doing when the companion repo code is next touched, but this plan covers the spec only.
