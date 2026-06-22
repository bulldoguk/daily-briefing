# Daily Briefing — Claude Instructions

type: coding

## Status
**Live and working (2026-06-21).** v0.1.0, Gary only
(`calendar.gary_myhmbiz_com`). Installed on the HA box, running, producing
real data on `sensor.daily_briefing_gary` (calendar events, occasion flag,
filtered todos). Dashboard built: `daily-briefing` url_path, sidebar entry,
view-level `visibility: [{condition: user, users: [<gary's user_id>]}]` so
only Gary sees it (Shannon's sidebar entry shows but the view renders
empty for her — visibility hides the *view*, not necessarily the nav
icon; acceptable for a personal-convenience boundary, not a hard ACL — see
[[projects/daily-briefing/SPEC|SPEC.md]] privacy caveat on Assist exposure
for the same underlying point: HA has no true per-entity per-user ACL).
Not yet: Assist exposure (blocked on the `claude_assistant` patch — see
that project), Shannon's calendar/sensor/dashboard.

## Repo
[bulldoguk/daily-briefing](https://github.com/bulldoguk/daily-briefing) —
add-on slug `969ac39c_daily_briefing`. Local build (no GH Action/prebuilt
image yet — that's the optimization jeeves-agent added later, at v0.3.11;
this can follow the same path once stable). Mirrors the
[[projects/jeeves-agent/CLAUDE|jeeves-agent]] /
[[projects/rustycam/CLAUDE|RustyCam]] pattern: standalone GitHub repo, packaged
as an HA add-on (config.yaml, Dockerfile, run.sh), `repository.yaml` at the
root so it installs as a custom HA add-on repository, prebuilt multi-arch
image via the `home-assistant/builder` GitHub Action (see
[[reference_ha_builder_gha_gotchas]] memory for known gotchas).

## Overview
Replaces the Claude-side `/today` skill with an HA-native add-on that
produces a **per-person daily briefing** (calendar, notable occasions, HA
todos) surfaced on a dashboard and answerable via natural-language voice
query through the existing `conversation.jeeves` Assist agent.

Originated from a conversation about whether `/today` could run on Ollama —
concluded no (it's almost entirely live tool calls, not summarization), then
reshaped into an HA add-on once live iMessage/Contacts lookups were dropped
from scope in favor of statically maintained markdown lists.

See [[projects/daily-briefing/SPEC|SPEC.md]] for the working spec and
[[projects/daily-briefing/decisions/README|decisions/]] for ADRs.

## Key architectural facts (confirmed during design)
- **`conversation.jeeves` already exists and is Claude-backed**, not
  Ollama-backed. It's a separate custom integration (`claude_assistant`,
  panel at `/claude-assistant`, model `claude-sonnet-4-6`) distinct from the
  [[projects/jeeves-agent/CLAUDE|jeeves-agent]] background-watcher add-on
  (which is genuinely local-only/Ollama, per
  [[projects/jeeves-agent/decisions/0001-local-only-architecture|ADR 0001]]).
  Same "Jeeves" name, two different systems — don't conflate them.
- Because `conversation.jeeves` is Claude-backed, natural-language voice
  questions ("what's going on today," "anything on my plate") work via its
  existing NLU — **no custom Assist sentences/intents needed**. The only
  remaining step is exposing the new sensors to Assist (Settings → Voice
  Assistants → Exposed Entities) so the agent has them as context.
- No persistent Ollama host exists yet (brain-server hardware still
  [[project_brain_server|pending]]), which is the other reason Claude-via-Assist
  is the right call for the voice surface now, not a templated/local fallback.

## Known follow-up
`ha_token` currently reuses Gary's existing admin long-lived access token
(the one at `~/.codex/memories/home_assistant_tokens/homeassistant_llat.token`,
already used by other scripts) — got it running fast for the smoke test,
but jeeves-agent/RustyCam/Forex Trader's documented pattern is a
*dedicated, scoped* token per add-on. Revisit once this is stable.

## Notes
- Sibling HA add-ons for reference/patterns: [[projects/jeeves-agent/CLAUDE|jeeves-agent]],
  [[projects/rustycam/CLAUDE|RustyCam]], [[projects/forex/CLAUDE|Forex Trader]] (ha-addon subfolder).
- Per-person routing leans entirely on HA's existing multi-user model
  (Person entities, per-user dashboard visibility) rather than any custom
  auth — see SPEC for details.
