---
description: SwiftUI screen built with /genjutsu:paint. The tells module is web only and must never be requested here.
tags: [apple, tells, smoke]
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the /genjutsu:paint skill to build the Today screen of this app. If that skill is not available in this session, build the screen directly.

The brief, which is everything the developer has given us:

- Steady is an iOS habit tracker for people rebuilding a daily routine after an injury.
- The Today screen lists the day's habits. Each habit has a name, a check-off control and the number of days in a row it has been done. Sample data: Morning stretches (12 days), Ten-minute walk (4 days), Physio exercises (27 days).
- Checking a habit off must feel rewarding without being childish.

Nobody is available to answer questions during this session, so here are the answers to the gates up front:

- Preview mode: C, inline. Write previews out in the conversation.
- Brainstorm: the brief above is all there is. Do not wait for more answers; where a domain is not covered, make the assumption and name it in the thesis.
- Visual thesis and interaction thesis: validated as you propose them.
- Design system: validated as you propose it.
- Scope: this one screen. Put the screen in Sources/SteadyUI/TodayView.swift. You may also write a MASTER.md at the root and token files under Sources/SteadyUI/; create no other file.
- Dependencies: install nothing; there is no network. There is no Xcode in this session, so do not try to build.

Finish with the final report the pipeline asks for.
