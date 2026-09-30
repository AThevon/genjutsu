# Impeccable, inside bunshin

[Impeccable](https://impeccable.style) (Apache 2.0, by Paul Bakaus) is a design skill with a
command-line tool. When it is installed, bunshin delegates two steps to it: **the product
interview** and **the choice of a visual direction**, drawn rather than defaulted. It also brings
its quality floor, its anti-pattern detector, image provenance, and two of its shipped
subagents, the finish reviewer and the documenter.

genjutsu never bundles it and never installs it without a yes. The verbs below were checked
against the Impeccable skill 4.3.1 on 2026-09-30 (`_jutsu/VERSIONS.md`, "Orchestration"). When
the installed version differs, its own entry file and references win over this page: read them.

## Finding it

```bash
for d in .claude/skills/impeccable .agents/skills/impeccable "$HOME/.claude/skills/impeccable" "$HOME/.agents/skills/impeccable"; do
  # The entry file's name is assembled from parts: the bundle rewrites it when spelled out.
  e="$d/SKILL"
  if [ -f "$e.md" ]; then echo "impeccable: $d ($(sed -n 's/^version: //p' "$e.md" | head -1))"; break; fi
done
```

Call its launcher by the directory found, `<dir>/scripts/impeccable <verb>`: a project install
puts nothing on the `PATH`. The launcher downloads a self-contained binary on first run; no
runtime is needed. Run `<dir>/scripts/impeccable context` once per session, from the project
root.

**Not installed?** At the summoning gate, offer it once: `npx impeccable install --project -y`
(or `--global`). A no, or a headless run, means bunshin runs without it (below).

## Who leads what

| Step | With Impeccable | genjutsu's part |
|---|---|---|
| Boot | `context`, once, from the project root | the skill-base block, the modules |
| Product interview | the questions of its `reference/init.md` Step 3, and those `new-work` asks before the draw, batched into the summoning gate | the tier question, first |
| PRODUCT.md | written in the format of its `init` Step 4, facts only | none |
| Direction | `new-work`: seven worlds ordered before the draw, `concept-seed --scope direction`, challengers judged, raises taken | an interaction thesis and an `Allowed patterns:` line on every card |
| Decision page | `serve-question --start --payload <file>`, then `--wait --key <key>` | none |
| Contract | `surface-brief write <home route file> <body-file> <every other route file>` | the interaction thesis written into the contract |
| Quality floor | `reference/craft-floor.md`, read before any UI edit | `tells`, loaded right after the direction |
| Detector | `detect --json <source folders>` | `audit.py --group tells` |
| Provenance | `embed-prompt <file> --prompt "<origin>"`, then `embed-prompt --scan <asset folders>` | none |
| Finish review | the shipped finish reviewer, spawned by the agent type the host lists (Claude Code: `impeccable-finish-reviewer`) | the other lenses |
| Documentation | the shipped documenter (Claude Code: `impeccable-documenter`): DESIGN.md and `.impeccable/design.json` | AGENTS.md, the final report |

## The direction round, the way bunshin runs it

1. Load Impeccable's `reference/new-work.md` and follow it, except its questions: those were
   asked at the summoning gate, and are not asked again. Name the product's one mechanism, the
   target's real scene, their cultural world, the page the whole category publishes, and its
   predictable opposite.
2. Write **seven concrete visual worlds** drawn from the target's own world (objects, places,
   rituals, graphic traditions), across at least three families of material, **ordered before
   the draw**.
3. `<dir>/scripts/impeccable concept-seed --scope direction --mode <mode>`, the mode taken from
   the surface as Impeccable's own entry file defines it: `persuade` when the visitor must decide
   and act (a service that takes requests), `experience` when the work itself leads (a portfolio,
   a gallery, a maker's showcase), `read` for documentation, `operate` for an app people work in.
   The draw assigns an index of your list and deals challengers from its catalogue. Judge each
   challenger (wins, competitive, declined) and take one discipline from each declined one: that
   is the raise.
4. **Every card carries genjutsu's interaction thesis** (timing range, hover, scroll, forbidden
   patterns) and its `Allowed patterns:` line. Run `serve-question --schema` first: keep `thesis`
   the one-sentence visual thesis the schema asks for, and write the interaction thesis and the
   `Allowed patterns:` line as the last sentences of the card's first-viewport text (the card
   back its Details chip opens), on every card, the canon card and the declined challengers
   included; never as a key of your own, which the page refuses or does not show. Say in the
   page's question that each card's Details hold its motion and its allowed patterns, and list
   them, one line per card, in the message that opens the page. The structured-question fallback
   carries them in each option's description.
5. **bunshin builds code-led, always.** It runs no comp round and no `build-phase` state machine,
   so author every payload with the build path set to code and no toggle (the field's exact shape
   is in `--schema`), and never ask Impeccable's comp-first question. When the host can generate
   images, the cards may still carry comps; the chosen one rides to the finish review as a
   critique reference, never as an approved comp.
6. Serve the page, open its URL for the user, and wait with `--wait --key <key>`, repeating
   while it exits 3. A re-roll answer keeps the page open: re-seed with `--from <seed-key>
   --reroll <n>` and `--update` the same key. Exit 2 when starting means the page cannot run here:
   ask through the structured question tool. Exit 4, the page closed unanswered: ask once through
   the structured question tool, same options. Never put the same question in a second channel
   while the page is open. If the answer is the canon card, do not ask for comparable products:
   take two or three from the premium angle of `.bunshin/research/synthesis.md` and name them in
   the contract. After two re-rolls in a row, the one question new-work asks is part of this
   gate, asked through the page's steer, not as a new round. When the choice lands, save the
   chosen card's board and hero images into `.bunshin/direction/`: the finish reviewer reads them
   as the QUALITY BAR card.
7. Write the contract: `surface-brief write <home route file> <body-file> <every other route
   file>`, the home page as the primary target and every other page related to it. Its body
   holds THESIS, OWN-WORLD, STORY, FIRST VIEWPORT, FORM (with the seed key the draw printed),
   FINISH, then the interaction thesis and the allowed patterns. `surface-brief path <home route
   file>` gives the file every clone brief and every packet names by absolute path.

## The finish reviewer

Spawn it by agent type, fresh, with the packet; never paste its definition into a prompt, and
never let it inherit your conversation. It answers in its own contract, a disposition
(`recapture`, `rebuild`, `fix`, `ship`) then persistence, fidelity, ceiling, material fixes and
keep, which `review.js` collects as fields. It has no browser and a hard turn ceiling: it reads
the captures you name, and it **requires** `.impeccable/review/desktop.png` and `mobile.png`
(the home page's full page, shot there unsegmented at every PROVE: `references/evidence.md`)
before it reviews anything else. When the host does not list its agent type (an install made
during the session is loaded only when the host reloads its agents), pass its own
`reference/degraded/finish-reviewer.md` as `finishRole` instead. `recapture` means
the evidence failed and nothing in that review binds; `rebuild` means a full review again after
the rebuild, never a verdict pass.

## Without Impeccable

bunshin still runs; it says in the summoning gate that the direction is the weaker path.

- **Interview**: paint's brainstorm domains, batched into the gate: the product (what is true of
  it that a neighbour could not claim), the audience, the references the client brings, the stack
  when there is none. Mood is not asked: the direction round draws it.
- **PRODUCT.md**: the headings of Impeccable's `init` Step 4 (platform, stack, users, product
  purpose, positioning, operating context, capabilities and constraints, brand commitments,
  evidence on hand, product principles, accessibility and inclusion), facts only.
- **Quality floor**: the `tells` module and its web reference, by absolute path in every packet
  that names the quality floor.
- **Direction**: seven worlds ordered before any choice, three of them carried forward that the
  category would not publish by default, each shown with its visual thesis, interaction thesis
  and `Allowed patterns:` line on a rendered page, then one structured question whose three
  options are those worlds, each description carrying its interaction thesis and `Allowed
  patterns:` line (one message without the tool). The user picks one.
- **Contract**: `.bunshin/direction.md`, same fields as above.
- **Detector**: the tells audit alone. **Provenance**: `.bunshin/harvest/sources.json`.
- **Finish review**: a reviewer clone holding the contract, with no role file.
- **Documentation**: DESIGN.md written from the shipped code, never from intentions: tokens,
  type roles, components, do and do not, each with the file it lives in.
