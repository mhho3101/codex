---
name: douyin-video-workflow
description: Produce or recut Chinese narrated explainers from a link, article, manuscript, topic, or existing video with a mandatory ChatCut timeline, mandatory HyperFrames keyword motion, synchronized item-by-item SFX, and evidence-based verification. Use for new production, continuing projects, minimal subject substitutions, targeted recuts, voice or sound changes, 3:4 covers, publish packages, cleanup planning, or platform-compliance diagnosis.
---

# Douyin Explainer-Video Workflow

Build around an accepted spoken-audio master clock. Enforce one production standard, preserve approved work, and make each feedback-driven change at the smallest affected stage.

## Start

1. Run `bash scripts/check-environment.sh` before creating project artifacts.
2. If a required tool is missing, report the gap and ask whether to install it. Do not install without approval. Do not create a fallback render.
3. Read [references/workflow.md](references/workflow.md). For feedback or recuts, also read [references/feedback-routing.md](references/feedback-routing.md).
4. For an existing project, read `PROJECT_STATE.md`, `SCRIPT.md`, `ITERATION_FEEDBACK.md`, and the latest verification before changing anything.
5. Detect the requested mode: `new`, `continue`, `recut`, `sound`, `cover`, `publish`, `compliance`, or `cleanup`.
6. For `new`, run:

```bash
bash scripts/new-video-project.sh --title "<title>" --root "<project-root>" --ratio 9:16 --duration 60
```

## Execution contract

- Treat final narration as the timing authority. Retiming narration requires retiming scenes, captions, motion, and sound effects.
- Accept a public link, article, manuscript, or topic as input. Extract/translate first, then separate verified facts from the creator's teaching viewpoint before scripting.
- Lock one canonical main-subject phrase. Show it in full within the first 12 seconds and at its first spoken mention; never reduce the subject to a decorative corner label.
- Make the first three seconds earn attention: open with a sharp problem, contrast, or outcome; pair the first visible landing with a restrained sound cue when sound design is in scope.
- Propagate terminology corrections through the script, captions, on-screen title, cover, filename, and publish copy before export.
- Record inaccessible, paywalled, or login-only sources. Never invent unavailable content.
- Map every factual or illustrative asset to current narration in `MATERIAL_TO_SCRIPT_MAP.md`.
- Distinguish official evidence, user material, public material, generated illustration, and authored graphics.
- Create a new version for material changes. Never overwrite an accepted render.
- Prepare a cleanup list first. Delete only after explicit authorization.
- Treat publishing, external sends, credentials, and account operations as separate authorized actions.

## Tool selection

- ChatCut is mandatory for the editable timeline, narration, captions, sound design, and final export.
- HyperFrames is mandatory for typography, diagrams, process animation, and keyword-timed motion layers.
- Use FFmpeg for technical evidence, source inspection, and final mixing support; never use it as the primary motion-design tool.
- Static PNG slides joined with FFmpeg are prohibited as the primary video implementation.
- Do not substitute Python/Pillow slides, presentation-style stills, or simple zoompan for ChatCut and HyperFrames.
- If ChatCut or HyperFrames is missing, stop and ask whether to install it. Never silently downgrade.

## Synchronization contract

For every list or multi-step process:

1. Start with the list container empty.
2. Reveal each item only when its corresponding spoken keyword begins.
3. Give every item a deliberate HyperFrames entrance animation.
4. Place one synchronized sound-effect cue on every item entrance in ChatCut.
5. Keep the spoken keyword, HyperFrames entrance, and ChatCut SFX within 3 frames.
6. Never display all items before they are spoken.

## Voice, sound, and visual direction

- When the user says the voice sounds robotic, identify the current TTS source and offer a short audition of suitable voices before replacing narration. Do not silently switch the speaker.
- Use the built-in sound-effects library before generating custom sound. Apply sound to editorial events: opening landing, subject reveal, every list step, transitions, warnings, and completion. Do not add effects to filler words.
- When the user provides a reference video, copy its restraint, rhythm, and density rather than duplicating its exact sounds.
- For this creator's technical explainers, default to a near-black / warm-orange editorial system only when no different style reference is supplied. Keep one main subject visually dominant.
- Treat the 3:4 cover as a separate deliverable: the main subject must be legible at thumbnail size; limit it to one dominant title and two short supporting lines.

## Compliance before publish

- Read [references/workflow.md](references/workflow.md) and complete `COMPLIANCE_CHECKLIST.md` before export for a public platform.
- Verify changing product, release, price, access, and capability claims from current primary sources immediately before publishing. Scope claims by account, permission, region, or plan when relevant.
- Declare AI-generated visuals or narration with the platform's AIGC control and add a visible disclosure when required. Do not assume MP4 metadata alone is sufficient.
- Attribute official screenshots and third-party brands as public-page examples; do not imply partnership or official endorsement.
- Avoid unsupported hot-news titles, universal capability claims, and guarantees. Preserve a source-and-claim record for an appeal if moderation occurs.

## Verification

Run the bundled verifier on every final candidate:

```bash
bash scripts/verify-video.sh final.mp4 verify
```

Require readable video and audio streams, a full decode pass, recorded silence and loudness diagnostics, ChatCut editable-project evidence, HyperFrames composition evidence, keyword timing evidence, and SFX evidence. Review the generated report; diagnostics are evidence, not automatic editorial approval.

## Publish package

Prepare:

1. Final MP4.
2. One final title and ready-to-post copy.
3. A finished 3:4 cover image.
4. Platform AIGC declaration, disclosures, source notes, and current topics when requested.
5. Verification evidence.

Copy a confirmed final video without overwriting prior deliveries:

```bash
bash scripts/publish-video.sh --input final.mp4 --title "<title>" --output-dir "<delivery-directory>"
```

Do not mark a video complete if the primary visual track is static slides, a main subject is visually absent, a list appears before its spoken cue, an item entrance lacks its synchronized SFX, a planned sound effect is absent from the final mix, the ChatCut timeline is missing, the HyperFrames composition is missing, or a required disclosure, cover, or evidence item is missing. Do not claim completion until every required artifact and check is recorded in `PROJECT_STATE.md`.
