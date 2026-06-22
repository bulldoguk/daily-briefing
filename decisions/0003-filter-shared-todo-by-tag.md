# ADR 0003: Filter the shared todo list by tag instead of splitting into per-person lists

## Context
[[projects/daily-briefing/decisions/0001-ha-native-per-person-routing|ADR 0001]]
established splitting calendars into per-person HA entities rather than
filtering a shared one. The same question came up for todos: HA only has
one relevant shared list, `todo.tablet_tasks` (12 active items, no
per-person split, already established as the household's task list). Given
the choice between adding new per-person `todo.*` helper lists (mirroring
the calendar approach) or filtering the existing shared list by a tag, Gary
chose filtering — `tablet_tasks` is an established list and fragmenting it
was judged more disruptive than the calendar split (which only *added*
entities, leaving `house_events` untouched).

## Decision
Keep `todo.tablet_tasks` as the single todo source. Add a structured tag in
each item's `description` field — `for:gary`, `for:shannon`, or `for:both`
— to indicate whose briefing it belongs to. Items with no tag (the current
state of all 12 existing items) default to showing on **both** briefings,
preserving today's de facto "shared list" behavior for anyone who doesn't
bother tagging. Free-text name mentions already present in some item
summaries (e.g. "Haircut Gary") are not parsed — too unreliable to use as
the signal.

## Consequences
- The add-on now contains real per-person filtering logic for todos (the
  thing ADR 0001 avoided for calendars) — accepted as a deliberate,
  narrower exception rather than a general pattern.
- No new HA entities or setup required; works against the list as it
  exists today.
- Tagging is manual and opt-in — items stay visible to both people until
  someone adds a tag, so there's no risk of a task silently disappearing
  from a person's view due to a missing tag.
