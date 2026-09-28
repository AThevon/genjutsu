---
description: Landing page for an independent design studio, built with /genjutsu:paint. Measures the tells that survive into app/page.tsx.
tags: [web, tells]
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the /genjutsu:paint skill to build the landing page for this project. If that skill is not available in this session, build the page directly.

The brief, which is everything the studio has given us:

- Fenwick is an independent design studio of three people.
- It does brand identity, packaging and small websites, almost only for independent food and drink producers.
- Two recent projects it wants shown: Brasserie Coutant, the identity and can labels of a six-person brewery; and Moulin Vert, the packaging of a stone-ground flour mill.
- The page has one job: get a producer to write to studio@fenwick.test about a project.

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
