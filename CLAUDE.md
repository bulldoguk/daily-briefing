# Daily Briefing — Claude Instructions

type: coding

## Status
v0.1.0 scaffolded locally (Gary only — `calendar.gary_myhmbiz_com`). Not
yet pushed to GitHub or installed on the HA box.

## Repo
Not yet pushed. Code lives locally at `daily_briefing/` in this project
folder for now. Will mirror the [[projects/jeeves-agent/CLAUDE|jeeves-agent]] /
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

## Notes
- Sibling HA add-ons for reference/patterns: [[projects/jeeves-agent/CLAUDE|jeeves-agent]],
  [[projects/rustycam/CLAUDE|RustyCam]], [[projects/forex/CLAUDE|Forex Trader]] (ha-addon subfolder).
- Per-person routing leans entirely on HA's existing multi-user model
  (Person entities, per-user dashboard visibility) rather than any custom
  auth — see SPEC for details.
