#!/usr/bin/env python3
"""Burndown-Chart fuer ein GitHub-Project (Scrum-Board), generiert aus den Board-Daten.

Datenquelle: GitHub CLI (`gh`), Felder Estimate, Sprints, Status der Items sowie das
Schliessdatum der verknuepften Issues.
Formel: Rest(d) = Summe Estimates im Sprint - Summe Estimates der Issues, die bis Tag d geschlossen wurden.
Ideallinie: Gerade von der Gesamtsumme am Sprintstart auf 0 am Sprintende.

Aufruf:
  python burndown.py --owner MarcoDaquila --project 3 --sprint current
  python burndown.py --demo        # Testlauf ohne GitHub-Zugriff
"""
import argparse
import csv
import json
import subprocess
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

TZ = ZoneInfo("Europe/Berlin")


def gh(*args):
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def load_items(owner, project):
    data = gh("project", "item-list", str(project), "--owner", owner,
              "--format", "json", "--limit", "500")
    return data["items"]


def closed_date(item):
    """Schliessdatum des Issues (lokale Zeit) oder None, wenn offen oder Draft."""
    content = item.get("content") or {}
    if content.get("type") != "Issue":
        return None
    info = gh("issue", "view", str(content["number"]),
              "--repo", content["repository"], "--json", "state,closedAt")
    if info.get("state") != "CLOSED" or not info.get("closedAt"):
        return None
    ts = datetime.fromisoformat(info["closedAt"].replace("Z", "+00:00"))
    return ts.astimezone(TZ).date()


def current_sprint(items):
    """Titel des Sprints, dessen Zeitraum das heutige Datum enthaelt."""
    today = datetime.now(TZ).date()
    for it in items:
        sp = it.get("sprints") or {}
        if sp.get("startDate"):
            s = date.fromisoformat(sp["startDate"])
            if s <= today < s + timedelta(days=int(sp["duration"])):
                return sp["title"]
    raise SystemExit("Kein laufender Sprint gefunden (Items ohne Sprint oder Sprint nicht aktiv).")


def build(items, sprint_name, start_override, days_override, closed_of):
    if sprint_name == "current":
        sprint_name = current_sprint(items)
    sprint_items, start, days = [], None, None
    for it in items:
        sp = it.get("sprints") or {}
        if sp.get("title") != sprint_name:
            continue
        start = start or date.fromisoformat(sp["startDate"])
        days = days or int(sp["duration"])
        sprint_items.append(it)
    if start_override:
        start = start_override
    if days_override:
        days = days_override
    if not sprint_items or start is None:
        raise SystemExit(f"Keine Items im Sprint '{sprint_name}' gefunden. "
                         "Estimate und Sprints bei den Items gesetzt?")
    total = sum(float(it.get("estimate") or 0) for it in sprint_items)
    done = [(closed_of(it), float(it.get("estimate") or 0)) for it in sprint_items]
    rows = []
    today = datetime.now(TZ).date()
    for i in range(days + 1):
        d = start + timedelta(days=i)
        ideal = total * (1 - i / days)
        actual = None
        if d <= today:
            burned = sum(e for c, e in done if c is not None and c <= d)
            actual = total - burned
        rows.append((d, i, ideal, actual))
    return sprint_name, total, rows


def plot(rows, total, sprint_name, outfile):
    xs = [r[1] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(xs, [r[2] for r in rows], "--", color="gray", label="Ideallinie")
    ax.plot([r[1] for r in rows if r[3] is not None],
            [r[3] for r in rows if r[3] is not None],
            marker="o", color="tab:blue", label="Ist")
    ax.set_title(f"Burndown {sprint_name} (Gesamt: {total:g} Story Points)")
    ax.set_xlabel("Sprinttag")
    ax.set_ylabel("Verbleibender Aufwand (Story Points)")
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)


def demo_data():
    start = date.today() - timedelta(days=9)
    closes = {1: 3, 2: 5, 3: 2, 4: 5, 5: 8}
    items = []
    for n, est in {1: 3, 2: 5, 3: 2, 4: 5, 5: 8, 6: 3}.items():
        items.append({"estimate": est,
                      "sprints": {"title": "Sprint 1", "startDate": start.isoformat(), "duration": 14},
                      "content": {"type": "Issue", "number": n}})
    day_of = {1: 2, 2: 4, 3: 5, 4: 8, 5: 10}
    return items, (lambda it: start + timedelta(days=day_of.get(it["content"]["number"], 99))
                   if it["content"]["number"] in day_of else None)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--owner", default="MarcoDaquila")
    p.add_argument("--project", type=int, default=3)
    p.add_argument("--sprint", default="current", help='Sprint-Titel oder "current" (Standard)')
    p.add_argument("--start", type=date.fromisoformat, help="Startdatum ueberschreiben (YYYY-MM-DD)")
    p.add_argument("--days", type=int, help="Sprintlaenge in Tagen ueberschreiben (Standard: aus Board)")
    p.add_argument("--out", default="burndown.png")
    p.add_argument("--demo", action="store_true")
    a = p.parse_args()

    if a.demo:
        items, closed_of = demo_data()
    else:
        items, closed_of = load_items(a.owner, a.project), closed_date

    sprint, total, rows = build(items, a.sprint, a.start, a.days, closed_of)
    plot(rows, total, sprint, a.out)
    with open(a.out.rsplit(".", 1)[0] + ".csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["datum", "sprinttag", "ideal", "ist"])
        for d, i, ideal, actual in rows:
            w.writerow([d, i, round(ideal, 2), "" if actual is None else actual])
    print(f"{a.out} geschrieben (Gesamt {total:g} SP, {len(rows) - 1} Tage)")


if __name__ == "__main__":
    main()
