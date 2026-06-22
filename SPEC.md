# Daily Briefing — Spec (v0.1, draft)

Part of [[projects/daily-briefing/CLAUDE|daily-briefing]]. See
[[projects/daily-briefing/decisions/README|decisions/]] for ADRs on calls
big enough to warrant their own record.

## Goal

An HA add-on that assembles a per-person daily briefing (calendar, notable
occasions, HA todos) and:
1. Surfaces it on a dashboard card per person.
2. Is answerable via natural-language voice query through the existing
   `conversation.jeeves` Assist agent (Claude-backed — see CLAUDE.md).

Replaces the Claude `/today` skill, which required live per-run tool calls
(Google Calendar MCP, HA MCP, iMessage `chat.db`, macOS Contacts DB) — too
much plumbing to reproduce in an add-on for marginal value, and outside an
add-on's reach anyway (no Mac-side DB access from the HA box).

## Scope decisions (carried over from design conversation)

- **No live iMessage / Contacts DB lookups.** That auto-detection ("who do
  I usually text on this day") is dropped. Instead, occasion → contact
  mappings are maintained manually in a markdown file, same spirit as
  `/today`'s existing `occasion_contacts.md` override list, just promoted
  to the only source instead of a fallback.
- **No live Google Calendar API calls from custom code.** Use HA's native
  Google Calendar integration (`calendar.*` entities) so each person's
  calendar is just another HA entity — no separate OAuth/credential
  handling inside the add-on.
- **No live HA Contacts/iMessage entity is needed for the "who to text"
  step** — folded into the static markdown above.

## Per-person routing

HA already has the primitives for this — don't build custom auth/routing:
- **Calendar**: each person's Google Calendar connected via HA's native
  integration → their own `calendar.*` entity (or entities, if they have
  multiple calendars).
- **Todos**: stay on the single existing shared list (`todo.tablet_tasks`)
  rather than splitting into per-person lists — it's an established family
  list (12 active items as of writing) and fragmenting it would be
  disruptive for little gain. Per-person filtering happens via a
  structured tag in the item's `description` field (e.g. `for:gary`,
  `for:shannon`, `for:both`). Untagged items (the current norm — no
  existing item uses this convention yet) default to showing on **both**
  briefings, matching today's de facto "shared list" behavior. Free-text
  name mentions in `summary` (e.g. "Haircut Gary") are NOT parsed — too
  unreliable; only the explicit `description` tag counts.
  **Implementation note:** HA's REST API has no endpoint to read todo item
  contents — only the WebSocket API exposes `todo.get_items` response
  data. This is the one deliberate exception to the REST-only pattern
  jeeves-agent established (ADR 0005 there); calendar reads and the sensor
  write both stay REST.
- **Static occasion/contact files**: tag each entry with who it applies to
  (`gary` / `shannon` / `both`) so a shared anniversary surfaces on both
  briefings but a personal item only shows on the relevant one.
- **Output**: one sensor per person — `sensor.daily_briefing_gary`,
  `sensor.daily_briefing_shannon` — attributes carry the structured data
  (events list, occasion flag, todos due, contacts-to-text list).
- **Dashboard**: per-person HA dashboard, assigned via Settings → Dashboards
  visibility-per-user, each showing a card driven by that person's own
  sensor. HA's per-user login + dashboard assignment handles "Gary sees his
  stuff, Shannon sees hers" — no custom logic needed.
- **Voice**: expose only the output sensors to Assist (Settings → Voice
  Assistants → Exposed Entities) — **never the raw `calendar.*`/`todo.*`
  entities**. The add-on reads those directly via its own scoped HA API
  token (same pattern as jeeves-agent), not via Assist, so they're never in
  the conversation agent's context at all. `conversation.jeeves` then
  answers free-form questions using the sensors as context — no custom
  sentences/intents required, since the NLU is Claude, not a
  sentence-matcher.
  - **Privacy caveat (real, unresolved):** HA's Assist exposure is scoped
    per *conversation agent*, not per *requesting person*. If both Gary's
    and Shannon's voice queries go through the same shared
    `conversation.jeeves`, exposing both `sensor.daily_briefing_gary` and
    `sensor.daily_briefing_shannon` to it means either person's question
    could in principle surface the other's data — HA has no native
    "only answer with the speaker's own entities" boundary. This is the
    same open question already flagged below (does `claude_assistant`
    filter context by requesting user?) — until that's confirmed, treat
    cross-exposure as a real risk, not a hypothetical. Hidden/visible
    toggles don't help here either — they're cosmetic (dashboard display
    only), not an access boundary.

## What it assembles (v1, mirrors `/today`'s sections)

1. **Calendar** — today's events from the person's `calendar.*` entity/
   entities, time + title + location, chronological.
2. **Notable occasion check** — standard US holidays (computed from date,
   same list as `/today`) + personal dates from a markdown file (successor
   to `key_dates.md`), tagged per person/both.
3. **Contacts to text** — static markdown list only (no live lookup),
   tagged per person/both, surfaced only when step 2 found an occasion.
4. **HA tasks for today** — items due today (or undated, if list is short)
   from `todo.tablet_tasks`, filtered to items tagged `for:<person>` or
   `for:both` (untagged = `both` by default — see Per-person routing).

## Pre-build checklist

- [ ] Add Gary's and Shannon's individual personal Google calendars to
      HA's existing Google Calendar integration as additional entities
      (`calendar.gary`, `calendar.shannon` or similar) — Settings →
      Integrations → Google Calendar → add calendar. Leave
      `calendar.house_events` as-is for shared events. Must be done before
      the add-on's calendar reads are wired up.

## Markdown sources — schema and location

`key_dates.md` and `occasion_contacts.md` become **add-on configuration**,
not knowledge-base content with a synced copy. They live at
`/share/daily_briefing/` on the HA box and are read directly by the add-on
— no master-copy-plus-sync step. Edits happen in place via the existing
SCP-edit-SCP pattern already documented in `home-assistant/CLAUDE.md`:
`scp` the file down, edit with the Edit tool, `scp` it back. This is the
same model jeeves-agent already uses for its own runtime state
(`/share/jeeves_agent/`) — config/state for an HA add-on lives on the HA
box, not duplicated into the git-tracked knowledge base.

**`/today` stays as a manual fallback** (e.g. for use from a Mac session
when HA is down), so `shared/key_dates.md` and `shared/occasion_contacts.md`
keep existing independently — they are **not** kept in sync with the
add-on's `/share/daily_briefing/` copies. The two are allowed to drift:
new dates/contacts added going forward get added to whichever surface is
relevant at the time (the add-on's copy for day-to-day use, the `shared/`
copy only if `/today` is actually being used that day). See
[[projects/daily-briefing/decisions/0004-no-sync-with-today-fallback|ADR 0004]].

**Schema additions** (both files currently lack person tagging):
- `key_dates.md`: append an optional tag — `- MM-DD — Description [for:
  gary|shannon|both]`. **Default when omitted: `both`** — personally
  significant dates (anniversaries, etc.) are usually relevant to both
  people, and the file is currently just a template with no real entries
  yet, so this is a clean slate.
- `occasion_contacts.md`: append the same optional tag —
  `- Occasion: Name (handle) [for: gary|shannon|both]`. **Default when
  omitted: `gary`** — the ~80 existing entries are unambiguously Gary's own
  contacts (untagged today, and staying that way rather than rewriting
  them); new entries for Shannon's contacts get an explicit `[for:
  shannon]` tag going forward.

## Refresh schedule

Sensors refresh **once daily at a fixed early-morning time** (time TBD,
likely ~6am) rather than continuously polling like
[[projects/jeeves-agent/CLAUDE|jeeves-agent]]'s watcher loop — a daily
briefing doesn't need to react in real time, and a fixed refresh keeps the
add-on simple (no poll-loop/diffing logic to maintain).

## Deployment

Mirrors [[projects/jeeves-agent/CLAUDE|jeeves-agent]] /
[[projects/rustycam/CLAUDE|RustyCam]]: HA add-on, prebuilt multi-arch image
via the `home-assistant/builder` GitHub Action, config via add-on options
UI, any persisted state under `/share/daily_briefing/`.

## Open questions

- [x] Is HA's native Google Calendar integration already connected? —
      **Yes**, confirmed via `calendar.house_events` (already powers the
      tablet dashboard). But it's a single shared calendar, not split per
      person. **Decision: add Gary's and Shannon's individual personal
      Google calendars as additional entities under the same integration**
      rather than filtering `house_events` by attendee. `house_events`
      continues to exist separately for shared items.
      **Gary's calendar added: `calendar.gary_myhmbiz_com`.** Shannon's
      still needs to be added the same way (Settings → Integrations →
      Google Calendar → add calendar) before her sensor can be wired up.
- [x] Todo source — **decided: stay on the existing shared
      `todo.tablet_tasks` list**, filtered per person via a `for:<person>`
      tag in each item's `description` field (untagged = shown to both).
      See ADR 0003.
- [x] Markdown schema and sync mechanism — **decided**, see "Markdown
      sources — schema and sync" above.
- [x] Refresh interval — **decided: once daily, fixed early-morning time**,
      see "Refresh schedule" above. Exact time still TBD at build time.
- [x] **Investigated and confirmed (2026-06-21):** `claude_assistant`
      (the integration behind `conversation.jeeves`) has **no per-user
      filtering at all** — it doesn't read `context.user_id`, and its
      `get_states` tool bypasses HA's Assist exposure list entirely,
      reading any entity directly. Full write-up now lives at
      [[projects/claude_assistant/CLAUDE|claude_assistant]] (newly
      documented — this integration existed undocumented until this
      investigation).
      **Decision: patch `claude_assistant`** to resolve the requester via
      `person.*.attributes.user_id` and enforce real filtering on personal
      entities (design captured in that project's CLAUDE.md), rather than
      accept unscoped access or skip voice for daily-briefing.
      **Hard blocker on exposing the daily-briefing sensors to Assist**
      until that patch lands — do not flip the exposure toggle for
      `sensor.daily_briefing_gary`/`_shannon` before then.

## Explicitly deferred / out of scope

- Live iMessage history lookup (dropped — see Scope decisions above).
- Live macOS Contacts DB lookup (dropped — see Scope decisions above).
- Custom Assist sentences/intents (not needed — Claude-backed NLU handles
  free-form phrasing already).
- Ollama-based summarization (no persistent Ollama host yet; also not
  needed — output is templated/structured, not generative prose).
