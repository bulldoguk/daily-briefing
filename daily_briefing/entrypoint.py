import json
import time
from datetime import datetime, timedelta

from briefing.build import run_for_all_people
from briefing.ha_client import HomeAssistantClient
from briefing.markdown_sources import parse_key_dates, parse_occasion_contacts

DATA_DIR = "/share/daily_briefing"
OPTIONS_PATH = "/data/options.json"


def load_config():
    # Read the add-on's options directly rather than via bashio env-var
    # export — bashio::config doesn't cleanly serialize the nested
    # "people" list-of-objects to a shell-safe JSON string.
    with open(OPTIONS_PATH, encoding="utf-8") as f:
        options = json.load(f)
    return {
        "ha_url": options["ha_url"],
        "ha_token": options["ha_token"],
        "todo_entity": options.get("todo_entity", "todo.tablet_tasks"),
        "refresh_time": options.get("refresh_time", "06:00"),
        "people": options.get("people", []),
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
