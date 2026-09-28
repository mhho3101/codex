# Narrated Short-Video Workflow

## Contents

1. Project modes
2. Production stages
3. Recut boundaries
4. Completion gates

## Project modes

- `new`: create a project from a manuscript, link, or source package.
- `continue`: resume the first incomplete stage recorded in `PROJECT_STATE.md`.
- `recut`: return to the smallest stage affected by feedback.
- `substitute`: replace a subject or term while preserving approved structure, teaching points, rhythm, and unrelated scenes.
- `rebuild`: recheck facts and rebuild the script only when the user requests a new work or the factual foundation changed.
- `publish`: assemble final video, cover, copy, disclosures, and verification.
- `cleanup`: inventory candidates and request approval before deletion.

## Production stages

Before stage 0, run `scripts/check-environment.sh`. If it reports a missing dependency, stop and ask the user whether to install it. Do not install without approval and do not generate a downgraded video.

### 0. Brief and subject lock

Lock the audience, one main subject, promise, aspect ratio, duration, source type, and deliverables. Write the canonical subject phrase exactly as it should appear in narration, captions, titles, cover, and publish copy. Create `PROJECT_BRIEF.md` and `PROJECT_STATE.md`.

Decide whether the request is a minimal substitution or a new creation. When the user says “replace A with B and keep everything else,” preserve the approved structure, teaching points, materials, rhythm, and unrelated narration. Change only subject-dependent wording, facts, visuals, captions, voice segments, and motion. If the boundary is ambiguous, restate the intended preservation boundary in one sentence before execution.

### 1. Sources and facts

Separate facts, opinions, and methods. Verify changing claims with current primary sources. Record access restrictions and attribution in `SOURCE_AND_FACTS.md`.

For a link or article, create a Chinese working summary before scripting. Preserve the source claim separately from the creator's practical interpretation. Do not turn an article's anecdote, model availability, pricing, or release timing into an unqualified fact.

### 2. Script

Use hook, problem, mechanism, example or method, conclusion, and call to action. Put a tangible hook in the first three seconds; state the exact main subject in full within the first 12 seconds. Make the viewer feel the promise before explaining the method. Write `SCRIPT.md`.

Use short spoken sentences with one idea each. Give list keywords distinct spoken landings. Resolve one consistent pronunciation for Chinese and English names. End with a concrete interaction question.

### 3. Narration

Prefer one continuous narration generation for one speaker. If chunking is unavoidable, hold voice, model, speed, and performance settings constant, then listen across every join.

If the voice is judged robotic, audition alternative voices first. Change only narration and dependent timing after the user chooses a voice; do not recut visuals prematurely.

### 4. Audio clock

Record narration start, end, semantic-block boundaries, keyword timestamps, caption timing, SFX timing, motion completion timing, and 30fps frame numbers. Do not lock motion before narration is accepted. Keep motion within 3 frames, captions within 100ms, and unintended mid-video silence below 0.8 seconds. Typical intentional pauses should be about 0.15–0.5 seconds.

### 5. Materials

Prioritize user material, official evidence, real workflow artifacts, reliable public material, generated illustration, then authored graphics. Record every choice in `MATERIAL_TO_SCRIPT_MAP.md`.

Every material must answer which spoken sentence it proves or explains. Reject decorative material that cannot be mapped. Generated illustrations must never impersonate official interfaces, customer data, cases, or news evidence.

### 6. Storyboard and edit

Build the editable narration, captions, sound design, and export timeline in ChatCut. Build typography, diagrams, process animation, and keyword-timed motion in HyperFrames. Give each scene a spoken purpose. Keep titles, evidence, explanation, and captions in separate safe zones. Explain foreign-language interfaces with Chinese summaries, callouts, crops, or animated guidance.

For every list or process, begin with an empty container. Reveal each item on its corresponding spoken keyword with a deliberate HyperFrames entrance and a ChatCut SFX cue. Keep the spoken keyword, motion entrance, and SFX hit aligned within 3 frames. Never reveal later items early.

Keep the main subject visually present where it matters: the opening, first definition, and the moment the speaker names it. A small persistent label never substitutes for a full subject reveal.

Create one effective visual event every 1.5–2.5 seconds. An effective event must add understanding, evidence, or emotion rather than decorative movement. Give every scene one primary visual focus, emphasized through size, position, color, motion, and sound. Do not treat enlarged captions as the primary visual.

### 7. Risk preview

Preview the opening, dense lists, complex processes, scene boundaries, and previously reported problem areas before rendering the full video.

### 8. Sound and render

Use sound effects for the opening landing, subject reveal, material entrances, every list item, transitions, warnings, completion events, conclusion, and CTA. Keep narration intelligible. For an attention-focused opener, use a short impact, rise, or whoosh only where the visual lands; do not turn the whole first sentence into an effects demo. Keep ordinary cues roughly 14–18dB below narration peaks. Target about -16 LUFS integrated loudness and no more than -1.5dBTP true peak. Confirm that every `SFX_PLAN.md` cue exists in both the ChatCut timeline and final mix. Save new material versions instead of overwriting accepted files. Do not use static PNG slides joined with FFmpeg, Python/Pillow presentation frames, or simple zoompan as the primary video implementation.

### 9. Compliance and technical checks

Use the current platform AIGC declaration flow and add a visible disclosure when required. Check current official sources for changing factual claims; scope capability claims to supported plans, regions, permissions, or examples. Add a non-endorsement/source note where official screenshots or third-party brands appear. Check layout, captions, contrast, cover copy, H.264/AAC encoding, resolution, frame rate, full decode, silence, loudness, true peak, narration continuity, and the final frame. Record ChatCut evidence, HyperFrames evidence, keyword timing, and SFX evidence. A contact sheet checks composition and density only; it never replaces waveform and synchronization review.

### 10. Publish package

Deliver the final video, a finished 3:4 cover, final title and copy, requested topics, AIGC/platform disclosures, source notes, and verification evidence. Use a new filename for every accepted export.

## Recut boundaries

- Copy or cover feedback: change only the publish package.
- “Hook is weak”: change opening wording, opening visual, and first-three-second sound design; preserve later accepted scenes.
- “Main subject is missing”: add or strengthen full subject reveals; do not rewrite the whole script unless the terminology itself is wrong.
- Terminology correction: update every public-facing text occurrence before export.
- Voice feedback: audition then replace narration; rebuild only timing-dependent scenes, captions, and sound cues.
- Sound feedback: change sound design and mix; preserve accepted narration and visuals.
- Material or motion feedback: preserve accepted script and narration when possible.
- “Replace A with B; keep the rest”: perform minimal substitution; preserve approved structure, general teaching content, rhythm, and unrelated scenes.
- Narration wording or speed: rebuild all dependent timing, captions, motion, and sound cues.
- Factual, platform, or moderation risk: return to sources, claims, title, disclosures, and compliance before republishing.

See [feedback-routing.md](feedback-routing.md) for the working table used to convert a user's plain-language feedback into the smallest safe revision.

## Completion gates

- Artifact existence is not enough; update `PROJECT_STATE.md` with evidence.
- A final video must contain readable video and audio streams and pass full decode.
- A final video must have an editable ChatCut timeline and HyperFrames composition or rendered motion-layer source.
- Every narration-bound list item must have a spoken-keyword timestamp, HyperFrames entrance timestamp, ChatCut SFX timestamp, and measured error within 3 frames.
- Every planned sound effect must be audible in the final mix and traceable to the ChatCut timeline.
- Static-slide, presentation-style, or simple zoompan output cannot pass the visual-production gate.
- Review feedback around the named moment, the surrounding 2–3 seconds, and the whole video for the same issue before closing it.
- A publish handoff is incomplete if any explicitly requested video, copy, cover, or evidence item is missing.
- Final acceptance is not deletion authorization.
