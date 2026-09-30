---
description: One button's hover and press state, asked of /genjutsu:bunshin with nobody answering. bunshin steps down to cast, spawns no subagent, writes no .bunshin/, and the button gets its interaction.
tags: [web, bunshin, routing]
max_turns: 100
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Use the /genjutsu:bunshin skill to give the "Join the waitlist" button in components/waitlist-button.tsx a hover state and a press state. If that skill is not available in this session, make the change directly.

The brief, which is everything the founder has given us:

- Tidewell is an app for sea swimmers that says when the water at their own beach is deep enough and calm enough to swim. It is not out yet; the landing page in app/page.tsx collects emails for the waitlist.
- Most visitors arrive on a phone, from a link in a swimming club newsletter, so the press state matters more than the hover.
- The rest of the page stays as it is.

Nobody is available to answer questions during this session, so here are the answers to the gates up front:

- Preview mode: C, inline. Write previews out in the conversation.
- Discovery: the brief above is all there is. Do not wait for more answers; where something is not covered, make the assumption and name it in the thesis.
- Interaction thesis: validated as you propose it.
- Scope: this one button. Change components/waitlist-button.tsx only; edit no other file and create none.
- Dependencies: package.json already declares next, react, tailwindcss and motion. Install nothing; there is no network.
- Do not start a dev server.

Finish with the final report the pipeline asks for, and name in it the pipeline that did the work.
