---
description: Landing page for an invoicing SaaS, built with /genjutsu:paint. Measures the tells that survive into app/page.tsx.
tags: [web, tells]
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the /genjutsu:paint skill to build the landing page for this project. If that skill is not available in this session, build the page directly.

The brief, which is everything the founders have given us:

- Ledgerline is invoicing software for freelance translators.
- What it does: invoices in any currency with the exchange rate of the invoice date written on the invoice; the EU reverse-charge VAT mention added automatically for business clients in another member state; a polite reminder emailed seven days after the due date, which the translator can switch off per client.
- Pricing: Free for up to three invoices a month. Pro is 9 EUR a month for unlimited invoices and reminders.
- There are no customer numbers, logos or testimonials yet. The product launches with this page.
- The page has one job: get a translator to create a free account. The sign-up lives at /signup.

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
