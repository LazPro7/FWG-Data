#!/usr/bin/env python3
"""Checks data.json before it is published, so a bad update never reaches the app.

Usage: python3 validate_feed.py [path/to/data.json]
Exits with status 0 when the feed is valid and 1 otherwise.
"""
import json
import sys

SCHEMA_VERSION = 1
COMPETITION_IDS = {"women", "u20boys", "u20girls", "u17boys", "u17girls"}
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def require_keys(obj, keys, where):
    for key in keys:
        check(key in obj, f"{where}: missing '{key}'")
    return all(key in obj for key in keys)


def main(path):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        print(f"INVALID: cannot read {path}: {error}")
        return 1

    top = ["schemaVersion", "lastUpdated", "fifaRankingDate", "mens", "confederations", "hostCountries",
           "fixtures", "teams", "honours", "appearances", "appearanceNotes", "competitions"]
    if not require_keys(data, top, "feed"):
        return report()

    check(data["schemaVersion"] == SCHEMA_VERSION, f"schemaVersion must be {SCHEMA_VERSION}")
    check(isinstance(data["lastUpdated"], str) and data["lastUpdated"], "lastUpdated must be a non-empty string")

    # Men's World Cup
    check(len(data["confederations"]) == 6, "expected 6 confederations")
    for conf in data["confederations"]:
        require_keys(conf, ["id", "name", "full", "region", "colorHex", "members", "slots2026", "qualifiedTeams", "qualifyingStatus"], f"confederation {conf.get('name')}")
    check(len(data["hostCountries"]) > 0, "hostCountries is empty")
    check(len(data["teams"]) > 0, "teams is empty")
    names = [t["name"] for t in data["teams"]]
    check(len(names) == len(set(names)), "duplicate team names")
    for team in data["teams"]:
        require_keys(team, ["name", "confederation", "fifaRank", "host", "qualified"], f"team {team.get('name')}")
        check(not team.get("host") or team.get("qualified"), f"team {team.get('name')} is a host but not qualified")
    mens = data["mens"]
    check(len(mens.get("statTiles", [])) == 4, "mens.statTiles must have 4 tiles")
    check(mens.get("plannedTeams", 0) > 0, "mens.plannedTeams must be positive")

    # Fixtures (men's and competitions)
    def check_fixture(fixture, where):
        require_keys(fixture, ["tournament", "stage", "date", "venue", "status", "detail"], where)
        check(fixture.get("status") in ("upcoming", "finished"), f"{where}: status must be 'upcoming' or 'finished'")
        if fixture.get("home") and fixture.get("away") and fixture.get("status") == "finished":
            check("homeScore" in fixture and "awayScore" in fixture, f"{where}: finished match needs both scores")

    for fixture in data["fixtures"]:
        check_fixture(fixture, f"fixture {fixture.get('stage')} {fixture.get('date')}")

    # Competitions
    check(len(data["competitions"]) == 5, "expected 5 competitions")
    check({c.get("id") for c in data["competitions"]} == COMPETITION_IDS, f"competition ids must be {sorted(COMPETITION_IDS)}")
    for comp in data["competitions"]:
        where = f"competition {comp.get('id')}"
        if not require_keys(comp, ["id", "tabLabel", "name", "blurb", "accentHex", "editions", "next", "latestHeadline", "aliases", "results", "groups"], where):
            continue
        years = [e.get("year") for e in comp["editions"]]
        check(len(years) > 0, f"{where}: no editions")
        check(years == sorted(set(years)), f"{where}: editions must be unique and in ascending year order")
        for edition in comp["editions"]:
            require_keys(edition, ["year", "host", "champion", "runnerUp", "third", "fourth", "teams", "summary"], f"{where} edition {edition.get('year')}")
            podium = [edition.get("champion"), edition.get("runnerUp"), edition.get("third"), edition.get("fourth")]
            check(len(set(podium)) == 4, f"{where} edition {edition.get('year')}: champion, runner-up, third and fourth must differ")
        nxt = comp["next"]
        require_keys(nxt, ["title", "dates", "hosts", "teams", "qualifiedCount", "qualified", "status", "venues", "keyDates", "notes"], f"{where} next")
        if nxt.get("qualified"):
            check(nxt["qualifiedCount"] == len(nxt["qualified"]), f"{where}: qualifiedCount must equal the number of qualified teams listed")
        check(nxt.get("qualifiedCount", 0) <= nxt.get("teams", 0), f"{where}: qualifiedCount exceeds teams")
        for fixture in comp["results"] + comp["groups"]:
            check_fixture(fixture, f"{where} fixture {fixture.get('stage')}")

    return report()


def report():
    if errors:
        print(f"INVALID: {len(errors)} problem(s)")
        for message in errors:
            print(f" - {message}")
        return 1
    print("OK: feed is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data.json"))
