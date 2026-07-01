# Tutorial Read-Through Review Notes

Working notes from a phase-by-phase review of the **self-serve** pick-and-place tutorial.
Decisions captured here for later application — not yet applied to the source docs
(`viam-workshop-slides-outline.md`, `pick-n-place-tutorial-plan.md`).

Focus: **self-serve learner experience** (the Hugo tutorial), not the facilitated workshop.

---

## Phase 0 — Orientation / `_index.md` (entry experience)

Context: Phase 0 exists for the facilitated workshop; the self-serve equivalent is the
tutorial `_index.md` (overview + prerequisites gate + entry paths). Orientation content
that a presenter delivers live must be carried by the `_index` prose for self-serve.

**Decisions / action items:**
- [x] **Lift the two-milestone framing into `_index`.** Make explicit that Phase 4 (drive the
  robot from code) is a real, bankable win and Phase 5 (perception) is milestone two. This is
  the psychological safety net for learners who might bounce when perception gets hard.
- [x] **Add helpful links for completing the prerequisites** (Python 3.10+, viam-sdk, terminal,
  account/machine access) directly in the `_index` prerequisites section.
- [x] **Hardware context is handled by links, not a tour.** The self-serve learner gets hardware
  context from the setup-guide link and hardware-overview resources already planned — no separate
  "hardware tour" section needed in `_index`. (Resolves the "0.3 has no self-serve home" gap.)
- [x] **Make login/machine-access a prerequisite.** Move "log in, find your machine, confirm Live"
  into the prerequisites checklist rather than an in-tutorial step — keeps the tutorial body focused
  on doing, and mirrors how login-as-prereq helps timing in the facilitated version.

---

## Phase 1 — Platform Mental Model / `01-platform-mental-model.md`

Context: pure-concept phase. Biggest self-serve risk is a wall of theory with no interaction
before any hands-on payoff. Plan currently says "no checkpoints (no live interactions yet)" —
we are overturning that stance for self-serve.

**Decisions / action items:**
- [x] **Add live "click around the app" interactions.** Ground each concept in the learner's real
  machine (e.g. open CONFIGURE, find `arm-1`, read its `namespace:family:model`). Live interaction
  is necessary to keep engagement high in self-serve — overrides the "no live interactions yet" note.
- [x] **Keep the perception-pipeline preview in the dependency graph (1.7).** Use `shape-detector`
  and `vision-segment` as concrete examples of services / composing resources, grounding the abstract
  "services" idea in something real they'll build later. Foreshadowing is intentional and fine.
- [x] **Add a self-check.** Close the loop with "you should now be able to answer the three questions
  from the top — if not, re-skim." Lets self-serve learners gauge readiness before Phase 2.
- [x] **Clarify builtin (RDK/viam-server) models vs. module-provided models.** Explain that some
  resources are builtin to viam-server and most additional functionality comes from modules, and how
  modules interact with viam-server. Ground it by having the learner watch the module download + start
  after configuring the uFactory xArm module. (Sequencing/home for this "watch the module download"
  moment is an open question — see Phase 2 notes.)

---

## Cross-cutting correction — resource configuration is hands-on (NOT pre-provisioned via fragment)

This overturns an assumption baked into the original `pick-n-place-tutorial-plan.md`. Apply everywhere:

- [x] **Resources are NEVER pre-configured.** Learners configure every resource themselves, by hand —
  this is core hands-on Viam skill-building, not friction to remove. Fix any "what's pre-configured" /
  "pre-provisioned resources" framing.
- [x] **Reframe `machine-fragment.json` as a reference, not an import.** It exists so learners can
  **check their work** against a known-good config — NOT to skip configuration by importing it. Correct
  the plan's "highest-priority asset — removes the manually-add-resources friction" characterization.
- [x] **Distinguish hardware provisioning from resource configuration** in `_index`/paths. Physical
  hardware + viam-agent/server running may be pre-provisioned (or done via setup guide), but component/
  service configuration is always the learner's hands-on work.

---

## Phase 2 — Configure Resources + Explore the App / `02-configure-resources.md`

Context: first hands-on phase; should feel like relief after Phase 1 theory. Test cards are strong
self-serve material (click → observe → verify).

**Decisions / action items:**
- [x] **Learner configures all hardware resources by hand** (`arm-1`, `gripper-1`, `cam-1`). Retitle/
  reframe away from "what's pre-configured." This phase teaches the add-a-resource flow, not a tour.
- [x] **Configuring the `viam:ufactory:xArm6` arm is where the module-download moment lands** (delivers
  Phase 1 #4): learner adds the arm, watches viam-server download + start the module live.
- [x] **3D scene tab gets an explicit active task:** "jog joint 1 and watch the `cam-1` frame move with
  the arm" — this is where the wrist-mounted-camera insight lands (load-bearing for Phase 5's detect-
  from-home rule).
- [x] **Gripper card active task for `IsHoldingSomething`:** have the learner place a block between the
  gripper fingers, press Grab, and observe the resulting `IsHoldingSomething` status. Consider adding a
  gripper checkpoint for symmetry with camera/arm.

---

## Phase 3 — Static Positions + Safety Obstacles / `03-static-positions.md`

Context: richest phase so far (design principle + capture/replay workflow + safety config), but also
the tedium-and-gotcha valley (5 hand-built switches, SetPosition 1-vs-2 trap). Delivers the best
tangible outcome yet: a working static pick-and-place sequence.

**Decisions / action items:**
- [x] **Teach how frame geometries are configured, and have learners measure their own workspace.**
  This replaces the facilitator-provided dimensions (self-serve has no facilitator). Spend real time on
  measuring the table + other obstacles and translating those measurements into geometry config. This is
  the self-serve home for the obstacle/table dimensions gap.
- [x] **Frame safety walls as a production-motion feature, modeled as needed per workspace.** Note that
  virtual safety walls are configured to fit the learner's own workspace, and pitch them as a demo of the
  motion system's power for real-world/production robot deployments (not just classroom safety).
- [x] **Keep the problem-isolation rationale (3.1) as proof of value.** Frame pose-to-pose motion without
  perception as a common, real operational workflow in production workcells — not filler before the "cool"
  perception part.
- [x] **Use the app's "duplicate" resource feature to speed up the 5 switches.** Configure pose #1 fully,
  then duplicate for #2–5. Doubles as a nice peek at power-user features. Keep `machine-fragment.json` as
  the check-your-work reference.
- [x] (Carry-over) Keep the SetPosition `1`=save / `2`=execute callout prominent, plus an inline
  troubleshooting aside for "SetPosition(2) does nothing" (didn't save first) — no facilitator to unstick.

---

## Phase 4 — Control the Robot from Python / `04-control-the-robot-from-python.md`

Context: conceptually light but operationally the most failure-prone phase for solo learners — the
risk is local Python environment setup (uv/pip/version), not the robot code. Milestone 1.

**Decisions / action items:**
- [x] **Sell the advantage of Python control code concretely** — beyond asserting the milestone, note
  the real advantages: programmability (loops/branches/logic) AND the ease of translating the Control-tab
  UI controls directly to the SDK method names (the cards map to methods). Make the payoff felt.
- [x] **Reference the Connect tab boilerplate for connection code.** Don't emphasize typing the connection
  from scratch — note that the starter script follows a similar structure to the SDK boilerplate the app
  generates in the Connect tab. Learner reads/understands it rather than authoring it.
- [x] **Add a secrets-handling note** — don't commit API keys; use the companion repo `.gitignore` or env
  vars. Cheap, and models the production-minded framing.
- [x] **Move environment validation into the Phase 0 prerequisites gate** so Phase 4's budget is just
  connect + run, not install-debugging. Keep uv as the primary path (pins Python, reproducible); pip is
  fallback only. Add a "verify your environment connects" checkpoint (`resource_names`) before robot logic.

---

## Phase 5 — Perception-Guided Picking / `05-perception-guided-picking.md`

Context: hardest + most valuable phase; cognitive-load peak (segmentation, frames, transforms, motion
planning, pose math in ~22 min). Milestone 2 — the full workshop goal and the "wow." Also the most
likely solo-abandonment point. Internal rhythm (configure+test vision in app → concept → code) is
working and should be preserved.

**Decisions / action items:**
- [x] **Add a home-pose guard clause in the perception code** (return to / assert `home-pose` before
  every detect) so the wrist-camera "detect from home" rule is structurally enforced, not just documented.
  Prevents the silent plausible-but-wrong-pick-point footgun. Also make it the FIRST entry in the 5.7
  debugging guide.
- [x] **Worked explanation for the approach offset; learner practices the gripper-TCP grasp offset.**
  Walk through computing the approach pose fully as a worked example, then have the learner compute the
  grasp/gripper-TCP offset themselves as productive struggle (or vice versa). Don't leave both as a bare TODO.
- [x] **Make `motion.move("gripper-1", …)` semantics explicit:** moving `gripper-1` drives the gripper's
  coordinate frame to the destination pose in the world — NOT the end of the arm (which is what the UI's
  MoveToPosition / the arm component API move). Contrast the two directly so the offset math makes sense.
- [x] **Motion-planning debugging maps symptom → 3D scene tab** (what to look for), with a forward-link
  back to Phase 3 obstacle/safety-wall config (skipping it comes back to bite here).
- [x] **Add more granular sub-checkpoints:** detector works → transform yields sane world coords →
  approach reachable → grasp succeeds. More gates = better self-diagnosis for a stuck solo learner.

---

## Phase 6 — Inline Module / `06-inline-module.md` (optional)

Context: correctly framed as optional; a learner can stop after Phase 5 with the full win. Feedback loop
inverts (instant local runs → ~1 min cloud build). The `from_robot` ↔ `cast + get_resource_name` bridge
callout is the pedagogical centerpiece and should stay front-and-center.

**Decisions / action items:**
- [x] **CRITICAL API CORRECTION — the plan's `transform_pose`-in-module approach is fabricated.**
  There is **no injected `FrameSystemClient`** (that API does not exist). Replace the plan block
  (`pick-n-place-tutorial-plan.md` lines ~238–254) entirely. The correct pattern (per
  https://docs.viam.com/build-modules/platform-apis/#use-the-machine-management-api-from-a-module):
  the module reaches the machine management API by **creating a `RobotClient` from within the module**,
  using credentials from environment variables (`VIAM_API_KEY`, `VIAM_API_KEY_ID`, `VIAM_MACHINE_FQDN`),
  stored as a single reused instance variable:
  ```python
  async def create_robot_client_from_module():
      opts = RobotClient.Options.with_api_key(
          api_key=os.environ["VIAM_API_KEY"],
          api_key_id=os.environ["VIAM_API_KEY_ID"],
      )
      return await RobotClient.at_address(os.environ["VIAM_MACHINE_FQDN"], opts)

  # in logic, reuse a single client:
  if not self.robot_client:
      self.robot_client = await create_robot_client_from_module()
  world_pose = await self.robot_client.transform_pose(obj_in_cam, "world")
  ```
  Note this is the OPPOSITE of the plan's "not a second RobotClient connection" claim — the recommended
  approach IS an in-module RobotClient (just exactly one, reused). Don't hardcode creds; use the env vars.
- [x] **Be honest that it's "mostly packaging + one real change."** The `transform_pose` access genuinely
  changes (env-var RobotClient inside the module), so don't let the Phase 4.1 "same logic, different entry
  point" promise set a trap.
- [x] **Tier the scope.** Minimal viable module (repackage + `do_command`, trigger manually) as the core
  optional path; scheduled jobs + autonomous operation as an explicit "level 2." Gives a tired learner a
  low-effort on-ramp.
- [x] **Strong "why bother?" framing** since it's optional — explicit "you'd want this when… (survives
  disconnection, auto-restart, OTA deploy, runs on a schedule)" so learners self-select instead of trudging.
- [x] **Use the plan's time estimate** (not the slides' 13 min) for the self-serve reading estimate.

---

## Synthesis — recurring self-serve themes

These patterns cut across phases; worth treating as tutorial-wide principles when applying the notes.

1. **Replace every facilitator-ism with a self-serve mechanism.** The facilitated version leans on a human
   to: provide measurements (P3), unstick the SetPosition gotcha (P3), sell the milestone (P4), diagnose
   wrong pick points (P5). Each must become something on the page — measure-your-own-workspace guidance,
   inline troubleshooting asides, guard clauses, worked examples, symptom→tool debugging.
2. **Live interaction is non-negotiable for engagement.** Overturn "no live interactions yet." Every phase
   (including the mental-model phase) needs hands-on grounding in the learner's real machine.
3. **Granular checkpoints double as self-diagnosis.** With no facilitator, gates must localize *where* a
   learner is stuck — most critical at the Phase 5 cognitive-load peak.
4. **The prerequisites gate (`_index`) is load-bearing and under-specified.** Front-load login, environment
   setup, hardware context, and the two-milestone framing here so phase flow isn't blown mid-stream.
5. **Honest framing + motivation.** Self-serve learners self-select and have no one pushing them: milestone
   framing (P4), "why bother" (P6), problem-isolation-as-real-workflow (P3), "mostly packaging + one real
   change" (P6). Set expectations honestly and give reasons to continue.
6. **Factual/API correctness matters more solo.** A facilitator patches errors live; solo learners copy and
   break. Already found: the fabricated `FrameSystemClient` (P6), the gripper-TCP `60`-vs-`105` nuance (P5),
   PoseInFrame kwargs. Audit all code before publishing.
7. **Fragment = reference, resources = hands-on.** Learners configure everything themselves;
   `machine-fragment.json` is only for checking their work.
