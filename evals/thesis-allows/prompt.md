---
description: Studio really split between Paris and Tokyo that asks for a two-city time bar. The bar must survive the tells module (over-correction control, P2).
tags: [web, tells, overcorrection]
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the /genjutsu:paint skill to build the landing page for this project. If that skill is not available in this session, build the page directly.

The brief, which is everything the studio has given us:

- Nakamura Roux is a two-person design studio. Aiko Nakamura works from Tokyo, Julien Roux works from Paris. The studio exists because of that split: work handed over at the end of a day in one city is picked up in the morning in the other, so clients see progress overnight.
- It designs interfaces for museum and exhibition apps.
- One project it wants shown: the visitor app of the Musee des Arts Decoratifs exhibition on Japanese lacquer, designed in both cities.
- They ask for one element by name: a thin bar at the very top of the page that shows the current local time in Paris and in Tokyo, side by side. That bar is the point of the studio; keep it.
- The page has one job: get a museum team to write to hello@nakamura-roux.test.

Nobody is available to answer questions during this session, so here are the answers to the gates up front:

- Preview mode: C, inline. Write previews out in the conversation.
- Brainstorm: the brief above is all there is. Do not wait for more answers; where a domain is not covered, make the assumption and name it in the thesis.
- Visual thesis and interaction thesis: validated as you propose them.
- Design system: validated as you propose it.
- Existing design: none. The scaffold is an empty Next.js skeleton with no look to preserve; if asked for a mode, treat it as a redesign.
- Scope: a single page. Put the whole page in app/page.tsx. You may also write a MASTER.md at the root and design tokens in app/globals.css; create no other file.
- Dependencies: package.json already declares next, react, tailwindcss and motion. Install nothing; there is no network.
- Do not start a dev server.

Finish with the final report the pipeline asks for.
