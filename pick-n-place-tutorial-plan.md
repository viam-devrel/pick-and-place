# Viam Docs: Tutorials Section — Implementation Plan

## Context

Introducing a `tutorials/` content section to the Viam docs site (Hugo static site, Netlify hosting). The inaugural entry is a self-serve pick-and-place workshop. This plan covers the Hugo infrastructure, file structure, frontmatter schema, shortcodes, and companion repo needed to ship the first tutorial and scaffold the section for future entries.

---

## Decisions

- **Separate hardware provisioning from tutorial content.** Tutorial assumes a live machine. Setup guide is a prerequisite document, not a tutorial phase.
- **Multi-page tutorial.** One Hugo content page per phase. Prev/next navigation hardcoded in frontmatter (not `.PrevInSection`, which is unreliable with `_index.md` in the sequence).
- **File naming.** Numeric prefixes (`01-`, `02-`, ...) for automatic sort order — no reliance on `weight` for page ordering within the tutorial.
- **Module phase framing.** The inline module (now Phase 6) is relabelled "optional" (not "stretch goal") — self-serve learners set their own pace, the facilitated-session framing doesn't apply.
- **Perception is its own phase.** Phase 4 gets the robot moving from Python (static sequence); Phase 5 adds the vision pipeline + perception code. Splitting protects focus on the hardest concepts and banks a guaranteed Phase 4 win. Obstacles stay in the machine config — no runtime WorldState in the tutorial.
- **Shortcodes needed.** `checkpoint`, `tabs` (if not already in theme), `code-file` (embeds from companion repo). `checkpoint` is blocking for Phase 3+; others can follow.
- **GitHub companion repo.** `viam-tutorials/` org or repo, `pick-and-place/` subdirectory. Linked from tutorial prerequisites and Phase 4–5 content.
- **Section landing page.** Hand-authored card for inaugural tutorial. Automatic list template deferred until second tutorial exists.
- **URL slug.** `/tutorials/pick-and-place/` with phase pages at `/tutorials/pick-and-place/01-platform-mental-model/` etc. Confirm with existing Hugo `baseURL` and `contentDir` config before writing any internal links.

---

## Repository Changes

### New content directory

```
content/
  tutorials/
    _index.md                            # section landing page
    pick-and-place/
      _index.md                          # tutorial overview + prerequisites
      01-platform-mental-model.md
      02-configure-resources.md
      03-static-positions.md
      04-control-the-robot-from-python.md
      05-perception-guided-picking.md
      06-inline-module.md
```

### New layout (if not covered by existing theme)

```
layouts/
  tutorials/
    list.html          # renders tutorial card grid from frontmatter
    single.html        # tutorial page: phase nav, prev/next, checkpoint styling
  shortcodes/
    checkpoint.html
    code-file.html
    tabs.html          # skip if theme already provides
```

### New static assets

```
static/
  tutorials/
    pick-and-place/
      hardware-overview.jpg    # photo of complete setup for overview page
```

### New data file (optional, for card grid rendering)

```
data/
  tutorials.yaml    # machine-readable index of all tutorials for landing page
```

---

## Frontmatter Schema

### Tutorial root (`_index.md`)

```yaml
---
title: "Vision-Guided Pick-and-Place with xArm6"
description: "Build a robot that detects, picks, and sorts coloured cubes using computer vision and motion planning."
difficulty: beginner          # beginner | intermediate | advanced
time_estimate: "2 hours"
hardware:
  - uFactory xArm6
  - Intel RealSense D435
  - uFactory finger gripper
  - System76 Meerkat
skills:
  - manipulation
  - perception
  - python-sdk
setup_guide: "/guides/hardware-setup/xarm6-pick-and-place/"
draft: false
weight: 1
---
```

### Phase pages

```yaml
---
title: "Phase 3: Static Positions and Safety Obstacles"
description: "Save arm poses and configure WorldState obstacles before adding perception."
tutorial: "pick-and-place"
phase: 3
time_estimate: "20 minutes"
weight: 30
prev: "/tutorials/pick-and-place/02-configure-resources/"
next: "/tutorials/pick-and-place/04-control-the-robot-from-python/"
---
```

---

## Shortcodes

### `checkpoint.html` — blocking for Phase 3+

Renders a visually distinct "verify this before continuing" callout. Does not exist in most Hugo themes; must be implemented.

```html
<!-- layouts/shortcodes/checkpoint.html -->
<div class="docs-checkpoint">
  <span class="docs-checkpoint__label">Checkpoint</span>
  <div class="docs-checkpoint__body">{{ .Inner | markdownify }}</div>
</div>
```

Needs accompanying CSS. Usage:

```markdown
{{</* checkpoint */>}}
Run `uv run python -c "import viam; print(viam.__version__)"`.
You should see a version number. If you see `ModuleNotFoundError`, return to Prerequisites.
{{</* /checkpoint */>}}
```

### `code-file.html` — deferred, not blocking

Embeds code from companion GitHub repo rather than duplicating it in docs. Prevents drift between tutorial content and actual working code. Implement before launch if possible; fall back to inline fenced code blocks if not.

### `tabs.html`

Check whether the existing theme provides a tabs shortcode before implementing. Used for OS-specific commands (macOS vs Linux).

---

## Companion GitHub Repository

**Repo:** `github.com/viam-devrel/tutorials` (or similar — confirm naming convention with DevRel team)

**Subdirectory for this tutorial:** `pick-and-place/`

```
pick-and-place/
  README.md                          # brief description + link to docs tutorial
  config/
    machine-fragment.json            # known-good machine config for checking your work (not an import)
    obstacles-template.json          # WorldState geometry with placeholder measurements
  scripts/
    pyproject.toml                   # uv project file, viam-sdk dependency declared
    .python-version                  # pins Python version (3.10+)
    starter-script.py                # Phase 4–5 starting point — TODOs in place
    reference-solution.py            # complete working script — no TODOs
  setup/
    frame-calibration-worksheet.md   # guided measurement doc for camera + gripper frames
```

`machine-fragment.json` is a **check-your-work reference**, not an import — learners configure every resource by hand, then compare against this known-good config. It is NOT used to skip configuration.

---

## Content Pages: Key Requirements Per Page

### `tutorials/_index.md`

- One-paragraph description of the tutorials section and how it differs from how-to guides (learning by doing, explicit time estimates, verifiable end states)
- Hand-authored tutorial card for the inaugural entry (title, description, hardware tags, time, difficulty, link)
- Note: automatic card rendering from `data/tutorials.yaml` or frontmatter deferred until second tutorial

### `pick-and-place/_index.md`

- Header image of complete hardware setup
- What you'll build (one paragraph)
- **Two-milestone framing (lifted from workshop slide 0.2):** Phase 4 (drive the robot from your own code) is a real, bankable win; Phase 5 (perception) is milestone two. Everyone should leave with at least the Phase 4 script; the module is optional. This is the safety net that keeps learners from bouncing when perception gets hard.
- Phase list with time estimates (Phases 1–5 core, Phase 6 optional)
- **Prerequisites checklist with verification commands AND helpful links** for completing each: Python 3.10+, `viam-sdk`, a working terminal, and a Viam account with an accessible machine. Include links to install/setup resources for each prerequisite.
- **Login/machine-access is a prerequisite, not an in-tutorial step:** "log in at app.viam.com, find your machine, confirm the green Live indicator" belongs in this checklist so the tutorial body stays focused on doing.
- **Environment validation is part of the prerequisites gate:** confirm a working Python env (uv recommended) that can `import viam` BEFORE Phase 4, so Phase 4 is just connect + run.
- Hardware context is delivered via the setup-guide link and the header image (`hardware-overview.jpg`) on this page, not a separate tour section
- Two explicit paths (note: only physical hardware + viam-agent/server may be pre-provisioned — resource configuration is always the learner's hands-on work): "Physical hardware ready → start at Phase 1" / "Provisioning your own hardware → complete the setup guide first"
- Link to setup guide: `/guides/hardware-setup/xarm6-pick-and-place/`
- Link to companion repo

### `01-platform-mental-model.md`

- Content: three-layer architecture (cloud/agent/server), SDK connection, config-as-source-of-truth, resource model (components vs services), dependency graph
- **Live grounding interactions throughout (overrides "no live interactions yet"):** have the learner open their own CONFIGURE tab and find `arm-1`, read its `namespace:family:model`, etc. — ground each abstraction in their real machine to keep engagement high.
- **Keep the perception-pipeline preview in the dependency graph** — use `shape-detector` / `vision-segment` as concrete examples of services and composing resources (intentional foreshadowing of what they build in Phase 5).
- **Builtin vs. module-provided resources:** explain that some resources are builtin to viam-server (RDK) and most added functionality comes from modules, and how modules interact with viam-server. Ground it by having the learner watch the module download + start after configuring the uFactory xArm module (the config action itself lands in Phase 2).
- **Self-check** at the end: "you should now be able to answer the three questions from the top — if not, re-skim."
- Estimated reading time + interaction: 15 min

### `02-configure-resources.md`

- Content: CONFIGURE tab walkthrough, learner configures each hardware resource by hand (resource table as target state), CONTROL tab test cards, 3D scene tab
- Vision pipeline is NOT configured here — it moves to Phase 5, right before the perception code that uses it
- Checkpoints after: camera test card, arm test card, gripper test card
- Wrist-mounted camera callout: camera frame moves with arm; must detect from home pose
- **Configuring the `viam:ufactory:xArm6` arm is the module-download moment** (delivers the Phase 1 builtin-vs-module lesson): learner adds the arm and watches viam-server download + start the module live.
- **3D scene tab active task:** "jog joint 1 and watch the `cam-1` frame move with the arm" — this is where the wrist-mounted-camera insight lands (load-bearing for Phase 5's detect-from-home rule).
- **Gripper card active task for `IsHoldingSomething`:** learner places a block between the gripper fingers, presses Grab, and observes the resulting status.
- Estimated reading time + interaction: 20 min

### `03-static-positions.md`

- Content: why static first (problem isolation rationale), the five key poses, arm-position-saver configuration, WorldState obstacles, static sequence test
- **arm-position-saver setup must be explicit:** add module from Registry (`erh:vmodutils:arm-position-saver`), configure one switch component per pose with `arm` attribute pointing to `arm-1`, JSON example for each, all five reference the same arm
- **Use the app's "duplicate" resource feature** to create poses #2–5 after configuring #1 fully (a nice peek at power-user features). `machine-fragment.json` remains the check-your-work reference.
- **Teach how frame geometries are configured, and have learners measure their own workspace** (replaces facilitator-provided dimensions): spend real time on measuring the table + obstacles and translating measurements into geometry config. This is the self-serve source for obstacle/table dimensions.
- **Safety walls framed as a production-motion feature:** configured to fit the learner's own workspace; pitch virtual safety walls as a demo of the motion system's power for real-world/production deployments, not just classroom safety. (Bin obstacles are out of scope.)
- **Keep the problem-isolation rationale as proof of value:** pose-to-pose motion without perception is a common real operational workflow in production workcells — not filler before perception.
- SetPosition API: `1` = save, `2` = execute — callout box, not a footnote — PLUS an inline troubleshooting aside for "SetPosition(2) does nothing" (didn't save first).
- Checkpoints after: each pose saved and verified, full static sequence completes without LOGS errors
- Estimated reading time + interaction: 20 min

### `04-control-the-robot-from-python.md`

- Content: why script before module (comparison table), running the starter script with uv (environment prepared in Prerequisites), Connect tab starter code, static sequence in Python, connection debugging
- Framing: the "clicking buttons → programming the robot" threshold; perception comes next in Phase 5
- **Sell the advantage of Python control code concretely:** programmability (loops/branches/logic) AND the ease of translating the Control-tab UI controls to SDK method names (the cards map to methods). Make the payoff felt, not just asserted.
- **Division of labor with the prerequisites gate:** the gate (see `_index`) already confirmed Python 3.10+/uv and that the env can `import viam`, so this phase is genuinely just connect + run — no fresh `uv init` here.
- **uv is the primary recommended path** — pip is a fallback only. With the env prepared in Prerequisites, this phase just runs the script:
  ```bash
  uv run python starter-script.py
  ```
- **Reference the Connect-tab boilerplate:** the starter script follows a similar structure to the SDK boilerplate the app generates in the Connect tab — learner reads/understands the connection block rather than authoring it from scratch.
- Learners obtain the whole companion `scripts/` project (clone or download — `starter-script.py` plus its `pyproject.toml`/`.python-version`, so `uv run` resolves deps), not just the bare script; use it rather than the Connect tab snippet for Phase 4 (Connect tab snippet used only for the initial connection test in step 1)
- **Secrets-handling note:** don't commit API keys; use the companion repo `.gitignore` or env vars.
- Obstacles are NOT passed in code — they live in the machine config (Phase 3) and apply to every `motion.move` automatically; no runtime WorldState in the tutorial
- Checkpoints after: `resource_names` prints all resources, static sequence runs end-to-end from Python
- Estimated reading time + interaction: 15 min

### `05-perception-guided-picking.md`

- Content: configure the vision pipeline (shape-detector → `vision-segment`, model `detections-to-segments`) + Control-tab test, frame system + `transform_pose`, perception loop, hybrid pick (`motion.move`) + place (saved switch), debugging guide
- Vision pipeline is configured here, right before the code that uses it (not in Phase 2)
- Wrist-mounted camera callout: must detect from `home-pose` or the world-frame transform is wrong — the most common cause of drifting pick points
- **Home-pose guard clause in the perception code:** return to / assert `home-pose` before every detect, so the wrist-camera "detect from home" rule is structurally enforced (prevents the silent plausible-but-wrong pick-point footgun). Make it the FIRST entry in the debugging guide.
- Perception API: use `len(o.point_cloud)` not `o.point_cloud.size`:
  ```python
  objects = await vision.get_object_point_clouds("cam-1")
  if not objects:
      print("No objects detected")
      return
  obj = max(objects, key=lambda o: len(o.point_cloud))
  label = obj.geometries.geometries[0].label
  ```
- **Worked approach-offset; learner practices the gripper-TCP grasp offset:** walk through computing the approach pose fully as a worked example, then have the learner compute the grasp/gripper-TCP offset themselves (productive struggle). Don't leave both as a bare TODO.
- **Make `motion.move("gripper-1", …)` semantics explicit:** it drives the gripper's coordinate frame to the destination pose in the world — NOT the end of the arm (which is what the UI MoveToPosition / the arm component API move). Contrast the two so the offset math makes sense.
- **Motion-planning debugging maps symptom → 3D scene tab** (what to look for), with a link back to Phase 3 obstacle/safety-wall config (skipping it bites here).
- **Granular sub-checkpoints:** detector works → transform yields sane world coords → approach reachable → grasp succeeds (better self-diagnosis for a stuck solo learner).
- Checkpoints after: detector tested in Control tab, detected object label printed from code, full pick-and-place loop completes
- Estimated reading time + interaction: 22 min

### `06-inline-module.md`

- Framed as **optional next step**, not a stretch goal — no time pressure framing
- **Strong "why bother?" framing** since it's optional — explicit "you'd want this when… (survives disconnection, auto-restart, OTA deploy, runs on a schedule)" so learners self-select.
- **Honest framing — "mostly packaging + one real change":** the module is largely a repackage of the Phase 4–5 script, but the `transform_pose` access genuinely changes (in-module RobotClient from env vars) — surface that so a "just packaging" expectation doesn't set a trap.
- **Tier the scope:** a minimal viable module (repackage + `do_command`, trigger manually) is the core optional path; scheduled jobs + autonomous operation are an explicit "level 2" for a low-effort on-ramp.
- Content: script vs module comparison, inline module editor walkthrough, `validate_config` + `reconfigure` (dependency injection), accessing `transform_pose` inside a module (see below), `do_command` + scheduled job
- **`transform_pose` inside a module:** there is **no** `FrameSystemClient` and no injected frame-system dependency. A module reaches the machine-management API (including `transform_pose`) by creating a **single, reused `RobotClient` from within the module**, authenticated from environment variables (`VIAM_API_KEY`, `VIAM_API_KEY_ID`, `VIAM_MACHINE_FQDN`) — values the operator sets in the module's environment config, not auto-injected. Reference: https://docs.viam.com/build-modules/platform-apis/#use-the-machine-management-api-from-a-module
  ```python
  import os
  from viam.robot.client import RobotClient

  async def create_robot_client_from_module():
      opts = RobotClient.Options.with_api_key(
          api_key=os.environ["VIAM_API_KEY"],
          api_key_id=os.environ["VIAM_API_KEY_ID"],
      )
      return await RobotClient.at_address(os.environ["VIAM_MACHINE_FQDN"], opts)

  # self.robot_client is initialized to None in __init__/reconfigure
  # in logic — create once, reuse:
  if not self.robot_client:
      self.robot_client = await create_robot_client_from_module()
  world_pose = await self.robot_client.transform_pose(obj_in_cam, "world")
  ```
  Note: this is the recommended in-module RobotClient pattern (exactly one, reused) — do NOT create a new connection per call, and do NOT hardcode credentials. Close it on module shutdown with `await self.robot_client.close()`.
- Bridge callout: explicit side-by-side of `from_robot` (local script) vs `cast + get_resource_name` (module), with a note that the resource names are identical in both cases
- Cloud build time (~1 min for Python modules) stated upfront, not discovered as a surprise
- Estimated reading time + interaction: 20 min

---

## Separate Prerequisite Document

**Path:** `content/guides/hardware-setup/xarm6-pick-and-place.md`

This is not a tutorial page — it is a how-to guide. Learners who arrive with pre-provisioned hardware skip it entirely.

Key sections:
1. Bill of materials + physical assembly
2. Network configuration (static IP, Ethernet, arm controller port)
3. viam-agent installation + machine registration
4. Module and resource configuration (compare against `machine-fragment.json` to check your work)
5. **Frame calibration** — physical measurement procedure for gripper TCP offset and camera extrinsics:
   - Gripper: measure flange face to finger convergence point with calipers → pure Z translation, identity orientation
   - Camera: measure x/y/z from flange center to optical center, measure orientation with known-angle bracket → fill into `frame-calibration-worksheet.md` from companion repo
   - Verification: AprilTag at known world position, compare detected pose to expected, iterate
6. Verification checklist (matches the tutorial's prerequisites gate)

---

## Implementation Order

1. Confirm URL structure with existing Hugo config (`baseURL`, `contentDir`, permalink settings)
2. Implement `checkpoint` shortcode + CSS
3. Create `tutorials/_index.md` (section landing page, hand-authored card)
4. Create `pick-and-place/_index.md` (overview + prerequisites)
5. Create companion repo skeleton (`README.md`, `pyproject.toml`, placeholder files)
6. Write Phase pages `01` through `05` (core tutorial, highest priority)
7. Write Phase page `06` (optional, but ship with initial release)
8. Write hardware setup guide (can be authored in parallel with phases 4–5)
9. Populate companion repo: `machine-fragment.json`, `starter-script.py`, `reference-solution.py`, `frame-calibration-worksheet.md`
10. Implement `code-file` shortcode and update Phase 4–5 code blocks to embed from repo
11. Add `data/tutorials.yaml` and `layouts/tutorials/list.html` when second tutorial is ready

---

## Open Questions for Claude Code to Flag

- Does the existing Hugo theme already provide `tabs` and `callout`/`note` shortcodes? Audit before implementing duplicates.
- What is the existing permalink configuration? Confirm that numeric-prefixed filenames (`01-platform-mental-model.md`) produce clean URLs without the prefix in the rendered path, or whether Hugo requires additional permalink config.
- Is there an existing `guides/` section, or does that directory also need to be created?
- Does the docs repo use Hugo modules or a vendored theme? Confirm before adding layout overrides — the override path depends on whether the theme is local or remote.
