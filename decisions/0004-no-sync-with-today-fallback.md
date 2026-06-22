# ADR 0004: Daily-briefing markdown config and /today's knowledge-base copies are allowed to drift

## Context
`key_dates.md` and `occasion_contacts.md` are becoming add-on
configuration, living at `/share/daily_briefing/` on the HA box (see SPEC
"Markdown sources — schema and location"). Gary wants to keep the Claude
`/today` skill around as a manual fallback (e.g. for use from a Mac session
when HA is down), which still reads its own copies at
`~/Documents/Claude/shared/key_dates.md` and `occasion_contacts.md`. That
leaves two copies of conceptually the same data in two places.

## Decision
Do not build a sync mechanism between them. The add-on's
`/share/daily_briefing/` copies (tagged per-person per the new schema) and
the knowledge-base `shared/` copies (untagged, `/today`'s original format)
are maintained independently and are allowed to drift. New entries go
wherever is relevant at the time they're added — the add-on's copy for
day-to-day use, the `shared/` copy only if `/today` is actually in use that
day.

## Consequences
- No sync tooling to build or maintain — the simplest option.
- The two lists will diverge over time; `/today` (fallback path) may be
  missing dates/contacts that were only ever added to the add-on's config,
  and vice versa. Accepted, since `/today` is explicitly a fallback, not
  the primary path, once the add-on ships.
- If this drift becomes annoying in practice, revisit — a periodic manual
  reconciliation pass, or a one-way export script, are the likely fixes;
  neither is being built now since it's speculative until real drift is
  observed.
