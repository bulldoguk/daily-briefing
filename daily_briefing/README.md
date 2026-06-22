# Daily Briefing — Home Assistant Add-on

Add-on package for [[projects/daily-briefing/CLAUDE|daily-briefing]] — see
[[projects/daily-briefing/SPEC|SPEC.md]] for the full design.

Assembles a per-person daily briefing (calendar events, notable occasions,
todos due) once a day and writes it to a sensor (`sensor.daily_briefing_<person>`)
for dashboard cards and voice queries to read.

## First-time setup
1. Copy `key_dates.md.example` → `/share/daily_briefing/key_dates.md` and
   `occasion_contacts.md.example` → `/share/daily_briefing/occasion_contacts.md`
   on the HA box (these are config, not committed to this repo with real
   content — see daily-briefing ADR 0002/0004 for why they're kept separate
   from the knowledge-base copies used by `/today`).
2. Set `ha_token` in the add-on options to a long-lived access token
   (read access to calendar/todo, write access to `sensor.daily_briefing_*`).
3. Confirm `people` config matches real calendar/sensor entity IDs.

## Status
v0.1.0 — Gary only (`calendar.gary_myhmbiz_com`). Add Shannon by adding a
second entry to the `people` config option once her personal calendar is
connected in HA — no code change needed.
