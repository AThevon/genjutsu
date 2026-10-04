#!/usr/bin/env python3
"""Rebuild data/tide.json for the etale-landing example from NOAA CO-OPS, exactly as NOAA returns it.

    python3 examples/etale-landing/data/fetch.py [YYYYMMDD]

Two NOAA stations, each named in the output with what it measures and where it is:
- 9414290 San Francisco: tide height predictions (6-minute curve and highs/lows, MLLW).
- SFB1204 Alcatraz Island, southwest of: tidal current predictions (slack water and maximum
  flood/ebb), the predicted current station closest to Aquatic Park (about 1.1 km north-west of the cove).
The default date is 2 October 2026. Values are kept as the strings NOAA returned. Standard library only.
"""
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import date

API = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
MDAPI = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{}.json"
TIDE, CURRENT = "9414290", "SFB1204"


def url(**params):
    base = {"time_zone": "lst_ldt", "format": "json", "application": "genjutsu_examples"}
    base.update(params)
    return API + "?" + urllib.parse.urlencode(base)


# python.org builds of Python on macOS ship without a CA bundle; fall back to the system one.
CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem") if os.path.exists("/etc/ssl/cert.pem") else None


def get(u):
    with urllib.request.urlopen(u, timeout=60, context=CTX) as r:
        data = json.load(r)
    if "error" in data:
        sys.exit(f"NOAA error for {u}: {data['error']}")
    return data


def station(sid):
    s = get(MDAPI.format(sid))["stations"][0]
    return {"id": s["id"], "name": s["name"], "lat": str(s["lat"]), "lon": str(s["lng"])}


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else "20261002"
    d = date(int(day[:4]), int(day[4:6]), int(day[6:]))
    span = {"begin_date": day, "end_date": day}
    urls = {
        "tide_6min_english": url(product="predictions", station=TIDE, datum="MLLW", interval="6", units="english", **span),
        "tide_6min_metric": url(product="predictions", station=TIDE, datum="MLLW", interval="6", units="metric", **span),
        "tide_hilo_english": url(product="predictions", station=TIDE, datum="MLLW", interval="hilo", units="english", **span),
        "tide_hilo_metric": url(product="predictions", station=TIDE, datum="MLLW", interval="hilo", units="metric", **span),
        "current_slack_max_english": url(product="currents_predictions", station=CURRENT, interval="MAX_SLACK", units="english", **span),
        "current_slack_max_metric": url(product="currents_predictions", station=CURRENT, interval="MAX_SLACK", units="metric", **span),
    }
    r = {k: get(u) for k, u in urls.items()}

    curve = [
        {"t": e["t"], "ft": e["v"], "m": m["v"]}
        for e, m in zip(r["tide_6min_english"]["predictions"], r["tide_6min_metric"]["predictions"])
    ]
    hilo = [
        {"t": e["t"], "type": e["type"], "ft": e["v"], "m": m["v"]}
        for e, m in zip(r["tide_hilo_english"]["predictions"], r["tide_hilo_metric"]["predictions"])
    ]
    cur_e = r["current_slack_max_english"]["current_predictions"]["cp"]
    cur_m = r["current_slack_max_metric"]["current_predictions"]["cp"]
    current = [
        {
            "t": e["Time"],
            "type": e["Type"],
            "velocity_knots": str(e["Velocity_Major"]),
            "velocity_cm_s": str(m["Velocity_Major"]),
            "mean_flood_direction_deg": str(e["meanFloodDir"]),
            "mean_ebb_direction_deg": str(e["meanEbbDir"]),
            "depth_ft": e["Depth"],
            "bin": e["Bin"],
        }
        for e, m in zip(cur_e, cur_m)
    ]

    out = {
        "date": d.isoformat(),
        "date_written": f"{d.day} {d.strftime('%B %Y')}",
        "source": "NOAA CO-OPS (Center for Operational Oceanographic Products and Services), Data API, https://api.tidesandcurrents.noaa.gov/api/prod/",
        "fetched_at": date.today().isoformat(),
        "source_urls": urls,
        "stations": {
            "tide": dict(station(TIDE), measures="tide height predictions", where="on the Presidio shore near the Golden Gate, about 3.8 km west of Aquatic Park"),
            "current": dict(station(CURRENT), measures="tidal current predictions", where="in the bay about 1.1 km north-west of Aquatic Park, off the cove, not inside it"),
        },
        "datum": "MLLW (Mean Lower Low Water): tide heights are measured above it",
        "time_zone": "lst_ldt: local standard or daylight time at the stations (on this date, Pacific Daylight Time, UTC-7)",
        "units": {
            "height_english": "feet",
            "height_metric": "metres",
            "current_velocity": "knots and centimetres per second; positive is flood (into the bay), negative is ebb (out of it)",
            "current_depth": "feet below the surface",
        },
        "notes": [
            "Values are copied exactly as NOAA returned them, as strings. Tide heights and currents are predictions.",
            "Slack water is when the current is weakest. It is not the same moment as high or low tide: on this day each slack at SFB1204 comes 10 to 50 minutes after the preceding high or low at 9414290.",
            "Both stations are outside the cove, named above with their distance. The water in the cove itself is not measured.",
        ],
        "tide_curve": curve,
        "highs_lows": hilo,
        "current_slack_and_max": current,
    }
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
