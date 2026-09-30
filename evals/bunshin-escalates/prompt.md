---
description: A whole site for an independent workshop, asked of /genjutsu:paint with nobody answering. paint names bunshin in one line and in its final report, carries on with the home page, and never spawns a subagent.
tags: [web, bunshin, routing]
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Use the /genjutsu:paint skill to build the website of this project. If that skill is not available in this session, build it directly.

The brief, which is everything the client has given us:

- Atelier Oudemans is Sanne Oudemans, who builds steel bicycle frames by hand in a workshop in Utrecht and restores old road bicycles.
- She has two kinds of clients, and the site has to work for both: riders who order a custom frame made to their measurements, and owners who bring an old bicycle to be restored.
- She wants the whole site: a home page, a page for custom frames, a page for restorations, a page about the workshop, a journal made from her Instagram posts, and a contact page that explains how an appointment works.
- Her only material is her public Instagram profile, exported in material/profile.md. There is no current site and no logo.
- This is a first version, to show her before she decides to go ahead.
- Contact: sanne@oudemans-frames.test.

Nobody is available to answer questions during this session, so here are the answers to the gates up front:

- Preview mode: C, inline. Write previews out in the conversation.
- Brainstorm: the brief and material/profile.md are all there is. Do not wait for more answers; where a domain is not covered, make the assumption and name it in the thesis.
- Visual thesis and interaction thesis: validated as you propose them.
- Design system: validated as you propose it.
- Existing design: none. The scaffold is an empty Next.js skeleton with no look to preserve; if asked for a mode, treat it as a redesign.
- Scope of this session: the home page only; the other pages come in later sessions. Put the whole home page in app/page.tsx. You may also write a MASTER.md at the root and design tokens in app/globals.css; create no other file.
- Dependencies: package.json already declares next, react, tailwindcss and motion. Install nothing; there is no network.
- Do not start a dev server.

Finish with the final report the pipeline asks for.
