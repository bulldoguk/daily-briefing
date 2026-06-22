# Decisions

Architecture Decision Records for daily-briefing, using the shared template
at `shared/templates/adr.md`. Each significant, hard-to-reverse design call
gets its own numbered file here.

Smaller calibration tweaks (refresh intervals, markdown schema tweaks, etc.)
stay as dated entries in [SPEC.md](../SPEC.md) — only decisions that shape
the architecture or would be costly to reverse warrant a full ADR.

| ADR | Title |
|---|---|
| [0001](0001-ha-native-per-person-routing.md) | Route per-person data via HA-native primitives, not custom auth |
| [0002](0002-drop-live-contact-lookup.md) | Drop live iMessage/Contacts DB lookup in favor of static markdown |
| [0003](0003-filter-shared-todo-by-tag.md) | Filter the shared todo list by tag instead of splitting into per-person lists |
| [0004](0004-no-sync-with-today-fallback.md) | Daily-briefing markdown config and /today's knowledge-base copies are allowed to drift |
