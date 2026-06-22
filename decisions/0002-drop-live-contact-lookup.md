# ADR 0002: Drop live iMessage/Contacts DB lookup in favor of static markdown

## Context
The original `/today` skill auto-detected "who to text" for an occasion by
querying `~/Library/Messages/chat.db` and the macOS Contacts DB live, on
every run. An HA add-on has no path to either — it doesn't run on the Mac
and has no access to those local databases.

## Decision
Drop the live lookup entirely. The occasion → contacts mapping is
maintained manually in a markdown file (successor to `/today`'s
`occasion_contacts.md` override list), tagged per person, and edited by
Gary/Claude as needed when occasions change — not re-derived every run.

## Consequences
- Loses the "auto-discovers new people I text on this day" behavior of the
  original skill — acceptable since that list is small and changes rarely.
- Removes the single biggest blocker to making this an HA add-on (no
  Mac-side DB access requirement).
- Gary and Claude are responsible for keeping the markdown file current
  going forward, rather than it self-maintaining.
