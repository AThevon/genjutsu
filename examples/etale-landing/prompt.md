---
description: Example run. Landing page for Étale, a fictional cold-water swimming app for Aquatic Park in San Francisco, built with /genjutsu:paint from one real day of NOAA tide and current predictions (2 October 2026).
tags: [example, web, paint]
runs: 1
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill]
---

/genjutsu:paint build the landing page for Étale.

The brief. Étale is a fictional product made up for this example, and this is everything its founders have given us:

- Étale is an iPhone app for people who swim in the cold water of Aquatic Park, San Francisco, all year round. It answers one question before you walk down to the beach: when is the water slack (étale is the French word for slack water, the still moment between ebb and flood, when the current is weakest), and how strong the current runs between two slacks.
- Its numbers come from two NOAA CO-OPS stations, and data/tide.json holds one real day of both, 2 October 2026, as fetched from NOAA: the tide predictions of station 9414290 San Francisco, and the slack water and current predictions of station SFB1204 (Alcatraz Island, southwest of, the closest predicted current station, in the bay off the cove). The file names each station, where it is, its datum and its units. Use those numbers and label each one with its date and its station. Slack water is not high or low tide: take the slack times from the current predictions. The app shows no water temperature, so the page must not either. Do not invent any other figure.
- The swimmers it is for train there before work, mostly without a wetsuit. They already know the cove and read the tide themselves on a printed table or a weather site. They want the next slack window at a glance, and an alert the evening before.
- What exists: an iOS beta on TestFlight. No Android, no web app, no prices, no user numbers, no testimonials. The page has one job: get a swimmer onto the TestFlight beta, at /beta.

Nobody is available to answer questions during this session. Up-front answers to the gates:
- Preview mode: A. Write each preview as a standalone HTML file under preview/ in the project.
- Scope: the landing page. You may write src/, index.html, public/, preview/ and MASTER.md; create nothing outside the project.
- Dependencies are installed (node_modules is present) and `npm run build` works. There is no network: install nothing. Do not start a dev server.

Finish with the final report the pipeline asks for.
