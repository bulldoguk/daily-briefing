import re
from datetime import datetime, timedelta, timezone

from .holidays import standard_holiday
from .markdown_sources import contacts_for_occasion, todays_personal_dates

_TODO_TAG_RE = re.compile(r"for:(gary|shannon|both)", re.IGNORECASE)


def _todo_tag(item):
    desc = item.get("description") or ""
    match = _TODO_TAG_RE.search(desc)
    return match.group(1).lower() if match else "both"


def _todos_for_person(items, person):
    return [
        item for item in items
        if item.get("status") == "needs_action" and _todo_tag(item) in (person, "both")
    ]


def _event_sort_key(event):
    start = event.get("start") or {}
    # All-day events carry "date" (no time) — sort them before timed events
    # on the same day by treating them as midnight.
    return start.get("dateTime") or f"{start.get('date', '')}T00:00:00"


def build_briefing(ha_client, person, todo_entity, key_dates, occasion_contacts, today=None):
    """Assemble one person's briefing. Returns (state, attributes) for
    ha_client.set_state.

    `person` is a dict from config: {"name", "calendar_entity", "sensor_entity"}.
    """
    today = today or datetime.now().date()
    tzinfo = datetime.now().astimezone().tzinfo

    day_start = datetime(today.year, today.month, today.day, tzinfo=tzinfo)
    day_end = day_start + timedelta(days=1)

    events = ha_client.get_calendar_events(
        person["calendar_entity"], day_start.isoformat(), day_end.isoformat()
    )
    events_out = sorted(
        (
            {
                "summary": e.get("summary", ""),
                "start": e.get("start"),
                "location": e.get("location", ""),
            }
            for e in events
        ),
        key=_event_sort_key,
    )

    occasion = standard_holiday(today)
    mmdd = today.strftime("%m-%d")
    personal_dates = todays_personal_dates(key_dates, mmdd, person["name"])
    occasions = ([occasion] if occasion else []) + personal_dates

    contacts_to_text = []
    for occ in occasions:
        contacts_to_text.extend(contacts_for_occasion(occasion_contacts, occ, person["name"]))

    try:
        todo_items = ha_client.get_todo_items(todo_entity)
        todos_today = [
            item["summary"] for item in _todos_for_person(todo_items, person["name"])
            if not item.get("due") or item["due"] <= today.isoformat()
        ]
    except Exception as exc:  # noqa: BLE001
        print(f"[daily_briefing] todo fetch failed for {person['name']}: {exc}")
        todos_today = []

    attributes = {
        "events": events_out,
        "occasions": occasions,
        "contacts_to_text": contacts_to_text,
        "todos_today": todos_today,
        "friendly_name": f"Daily Briefing — {person['name'].capitalize()}",
    }
    return str(len(events_out)), attributes


def run_for_all_people(ha_client, people, todo_entity, key_dates, occasion_contacts):
    for person in people:
        state, attributes = build_briefing(ha_client, person, todo_entity, key_dates, occasion_contacts)
        ha_client.set_state(person["sensor_entity"], state, attributes)
        print(f"[daily_briefing] updated {person['sensor_entity']}: {attributes}")
