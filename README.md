# Daily Briefing

A Home Assistant add-on that builds a per-person daily briefing — today's calendar, notable occasions, and to-dos — once a day, and publishes it as a sensor (`sensor.daily_briefing_<person>`). Dashboard cards and voice assistants read the sensor; neither needs access to the underlying calendars or lists.

## What goes into a briefing

- **Calendar:** today's events from the person's `calendar.*` entities, via HA's native Google Calendar integration. The add-on has no OAuth or credentials of its own.
- **Occasions:** standard US holidays (computed in code), plus birthdays, anniversaries and other personal dates from a markdown file. Each line carries a `[for: <person>|both]` tag, so a shared anniversary appears on both briefings and a personal date on only one — e.g. `- MM-DD — Anniversary [for: both]`.
- **Who to contact:** a second markdown file maps occasions to the people worth messaging that day.
- **To-dos:** items from a shared HA to-do list, filtered per person by a `for:<name>` tag in the item description. Untagged items appear for everyone, so an existing family list works unchanged.

## Design choices

- **HA-native routing, not custom auth.** Each person's data comes from their own HA entities, and per-user dashboard visibility decides who sees which card.
- **Expose only the output sensors to Assist.** The add-on reads calendars and to-dos with its own scoped token, so the raw `calendar.*` and `todo.*` entities never enter a voice assistant's context.
- **REST for everything except to-do contents**, which HA only exposes over the WebSocket API (`todo.get_items`).

Each of these is written up in [`decisions/`](decisions/).

## Installation

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**
2. Open the ⋮ menu → **Repositories** and add `https://github.com/bulldoguk/daily-briefing`
3. Find **Daily Briefing** in the store and click **Install**
4. Copy `key_dates.md.example` and `occasion_contacts.md.example` to `/share/daily_briefing/` (dropping the `.example`), and fill them in

## Configuration

| Option | Description |
|---|---|
| `ha_url` | HA base URL |
| `ha_token` | Long-lived access token: read calendar and to-do entities, write `sensor.daily_briefing_*` |
| `todo_entity` | The shared to-do list to filter |
| `refresh_time` | When to rebuild the briefing each day (`HH:MM`) |
| `people` | One entry per person: `name`, `calendar_entity`, `sensor_entity`. Adding a person is a config change, not a code change |

## Repository layout

| Path | Contents |
|---|---|
| `daily_briefing/` | The add-on: manifest, Dockerfile, Python package, example config files |
| `decisions/` | Architecture decision records |
| `SPEC.md` | Design spec |
