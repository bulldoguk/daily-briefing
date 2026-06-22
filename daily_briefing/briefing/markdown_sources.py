"""Parsers for the add-on's two markdown config files.

Schema (see daily-briefing SPEC.md "Markdown sources — schema and location"):
  key_dates.md:          - MM-DD — Description [for: gary|shannon|both]
                          (tag omitted = both)
  occasion_contacts.md:  - Occasion: Name (handle) [for: gary|shannon|both]
                          (tag omitted = gary, matching the ~80 untagged
                          legacy-style entries this format was designed around)
"""

import re

_TAG_RE = re.compile(r"\s*\[for:\s*(gary|shannon|both)\s*\]\s*$", re.IGNORECASE)


def _split_tag(text, default):
    match = _TAG_RE.search(text)
    if match:
        return text[: match.start()].strip(), match.group(1).lower()
    return text.strip(), default


def parse_key_dates(path):
    """Returns a list of {"mmdd": "MM-DD", "description": str, "for": str}."""
    entries = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return entries

    for line in lines:
        line = line.strip()
        if not line.startswith("- "):
            continue
        body = line[2:]
        if " — " not in body:
            continue
        mmdd, rest = body.split(" — ", 1)
        mmdd = mmdd.strip()
        if not re.match(r"^\d{2}-\d{2}$", mmdd):
            continue
        description, person = _split_tag(rest, default="both")
        entries.append({"mmdd": mmdd, "description": description, "for": person})
    return entries


def todays_personal_dates(entries, today_mmdd, person):
    return [
        e["description"] for e in entries
        if e["mmdd"] == today_mmdd and e["for"] in (person, "both")
    ]


def parse_occasion_contacts(path):
    """Returns a list of {"occasion": str, "contact": str, "for": str}."""
    entries = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return entries

    for line in lines:
        line = line.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        body = line[2:]
        occasion, rest = body.split(":", 1)
        contact, person = _split_tag(rest, default="gary")
        entries.append({
            "occasion": occasion.strip(),
            "contact": contact.strip(),
            "for": person,
        })
    return entries


def contacts_for_occasion(entries, occasion_name, person):
    return [
        e["contact"] for e in entries
        if e["occasion"] == occasion_name and e["for"] in (person, "both")
    ]
