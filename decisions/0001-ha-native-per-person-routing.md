# ADR 0001: Route per-person data via HA-native primitives, not custom auth

## Context
The briefing needs Gary to see his stuff and Shannon to see hers (calendar,
todos, occasion flags), both on a dashboard and via voice. The add-on could
have implemented its own user-identity logic, or leaned on what HA already
provides.

## Decision
Use HA's existing multi-user model end to end: one `calendar.*` entity per
person (via HA's native Google Calendar integration, not a custom OAuth
flow in the add-on), one `todo.*` list per person, one output sensor per
person (`sensor.daily_briefing_<name>`), and per-user dashboard visibility
assignment (Settings → Dashboards) to route the right card to the right
person. The add-on itself stays identity-agnostic — it just produces N
sensors, one per configured person — and lets HA's existing user/dashboard
system handle "who sees what."

## Consequences
- No custom auth, OAuth handling, or session logic to build or maintain.
- Adding a third person later is just: connect their calendar in HA,
  create their todo list, add them to the add-on's person config, assign
  them a dashboard. No code changes to the routing logic.
- Hard dependency: each person's Google Calendar must be connected via
  HA's native integration (not just Claude's calendar connector, which is
  a separate auth context the add-on can't reach). This is a one-time
  setup cost per person, tracked as an open question in SPEC.md.
