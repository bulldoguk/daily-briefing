import json
import os
import time
from datetime import datetime, timedelta

from briefing.build import run_for_all_people
from briefing.ha_client import HomeAssistantClient
from briefing.markdown_sources import parse_key_dates, parse_occasion_contacts

DATA_DIR = "/share/daily_briefing"


def load_config():
    return {
        "ha_url": os.environ["HA_URL"],
        "ha_token": os.environ["HA_TOKEN"],
        "todo_entity": os.environ.get("TODO_ENTITY", "todo.tablet_tasks"),
        "refresh_time": os.environ.get("REFRESH_TIME", "06:00"),
        "people": json.loads(os.environ.get("PEOPLE_JSON", "[]")),
    }


def seconds_until_next(refresh_time):
    hour, minute = (int(x) for x in refresh_time.split(":"))
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def main():
    config = load_config()
    ha_client = HomeAssistantClient(config["ha_url"], config["ha_token"])

    while True:
        key_dates = parse_key_dates(f"{DATA_DIR}/key_dates.md")
        occasion_contacts = parse_occasion_contacts(f"{DATA_DIR}/occasion_contacts.md")

        try:
            run_for_all_people(ha_client, config["people"], config["todo_entity"], key_dates, occasion_contacts)
        except Exception as exc:  # noqa: BLE001
            print(f"[daily_briefing] refresh failed: {exc}")

        sleep_seconds = seconds_until_next(config["refresh_time"])
        print(f"[daily_briefing] next refresh in {sleep_seconds / 3600:.1f}h")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
