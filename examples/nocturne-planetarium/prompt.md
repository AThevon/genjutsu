---
description: Example run. Landing page for Nocturne, the late program of a fictional planetarium in Lisbon, built with /genjutsu:paint around the real stars and planets over Lisbon at 22:00 on Friday 9 October 2026 (Yale Bright Star Catalogue, JPL Horizons).
tags: [example, web, paint]
runs: 1
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill]
---

/genjutsu:paint build the landing page for Nocturne, the late program of a planetarium in Lisbon.

The brief. The planetarium and its program are fictional, made up for this example: give the planetarium no name and do not name or suggest any real planetarium or venue. This is everything it has given us:

- Nocturne is the planetarium's after-hours program. On Friday and Saturday nights the dome first shows the night sky above Lisbon as it is that evening, with a narrator, then a 40-minute show. Doors 21:30, first show 22:00, last show 23:30. Tickets 12 EUR, 8 EUR for students, booked at /tickets.
- The hero is the sky over Lisbon as the dome will show it at 22:00 on Friday 9 October 2026. data/stars.json holds the brightest stars of the Yale Bright Star Catalogue (public domain) and the one bright planet above the horizon then, Saturn (from NASA JPL Horizons), with their altitude and azimuth already computed for that place and time, their magnitude and, for stars, their proper name when they have one. It also lists the Moon and the other planets, which are below the horizon or too faint at that time: do not draw them. Use it. Do not invent stars, constellation lines, events or claims that are not in the data or in this brief.
- The page scrolls from dusk to the first show: the program, what is in tonight's sky, the practical information.
- It is for adults in their 20s to 40s looking for an evening out, not school groups. There are no reviews and no attendance numbers yet: the program launches with this page.

Nobody is available to answer questions during this session. Up-front answers to the gates:
- Preview mode: A. Write each preview as a standalone HTML file under preview/ in the project.
- Scope: the landing page. You may write src/, index.html, public/, preview/ and MASTER.md; create nothing outside the project.
- Dependencies are installed (node_modules is present) and `npm run build` works. There is no network: install nothing. Do not start a dev server.

Finish with the final report the pipeline asks for.
