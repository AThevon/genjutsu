export const meta = {
  name: 'bunshin-review',
  description: 'Review a built site through independent lenses, then turn the findings into a plan by file owner',
  phases: [
    { title: 'Review', detail: 'one clone per lens, same evidence packet, no project file changes' },
    { title: 'Plan', detail: 'deduplicate, verify against the code, reject with reasons, group by owner' },
  ],
}

// bunshin phase 9. Run with Workflow({ scriptPath: '<this file>', args }).
//
// args:
//   packet      string, required. The evidence packet: the project and its path, the request and
//               the gate answers, what to read (PRODUCT.md, the direction contract, the quality
//               floor), where the captures and their segments are (and, for Impeccable's finish
//               reviewer, the required ones: .impeccable/review/desktop.png and mobile.png),
//               where the sources and the built output are, and what is ALREADY VERIFIED.
//   round       number, required. The review round, for labels and the plan.
//   lenses      string[], optional. Among finish, mobile, desktop, truth, tech, truth-tech.
//               Default: the five separate lenses. The lean tier passes finish, mobile, truth-tech.
//   modules     { mobile, desktop, motion }, required for the mobile and desktop lenses: the
//               absolute directories of those genjutsu modules (their entry file is SKILL.md, or
//               GUIDE.md inside the bundle).
//   finishAgent string, optional. The agent type the host lists for Impeccable's shipped finish
//               reviewer (Claude Code: 'impeccable-finish-reviewer'). It is spawned fresh with the
//               packet and answers in its own contract (a disposition, then persistence,
//               fidelity, ceiling, material_fixes, keep): never paste its definition into a prompt.
//   finishRole  string, optional. Only when the agent type is not listed: the absolute path of a
//               role file to follow, such as Impeccable's own reference/degraded/finish-reviewer.md
//               (never its agent definition, which Impeccable asks to be spawned, not read).
//               Without either, the finish lens holds the direction contract itself.
//   owners      [{ key, files }], required. Every file owner: the plan assigns each fix to one of
//               them, or to "orchestrator" for a file no owner lists.
//   planOut     string, required. Absolute path of the plan file:
//               { round, disposition, reviews: [paths], plan }. Each lens's review lands beside
//               it, <planOut without .json>.<lens>.json (the plan clone writes the finish one:
//               Impeccable's reviewer edits nothing).
//
// Returns { round, disposition, recapture, lenses, plan }. When the finish lens says recapture
// or rebuild, the plan is not drawn: invalid evidence binds nothing, and a rebuild is followed
// by a full review of its own. The finish lens is asked twice when its first answer is empty.

const A = args || {}
if (!A.packet || !A.round || !Array.isArray(A.owners) || !A.owners.length || !A.planOut) {
  throw new Error('review.js needs args.packet, args.round, args.owners[] and args.planOut')
}
const ROUND = Number(A.round)
if (!Number.isInteger(ROUND) || ROUND < 1) throw new Error('review.js: args.round must be a positive integer')
if (A.lenses !== undefined && !Array.isArray(A.lenses)) {
  throw new Error(`review.js: args.lenses must be an array of lens names, not ${typeof A.lenses}`)
}
const M = A.modules || {}
const entry = dir => `the module in ${dir} (read its entry file: SKILL.md, or GUIDE.md in a bundle)`
const stem = String(A.planOut).replace(/\.json$/, '')
const reviewFile = key => `${stem}.${key}.json`

const RULES = `
Rules for every reviewer:
- Review only. Do not modify any project file, do not start a server, do not drive a browser.
- Open the captures with your file-reading tool. Judge what renders, not what the code intends.
- Every finding cites its evidence: a capture and the region of it, or a file:line.
- Severity: critical breaks conversion, accessibility or credibility; major is visible and hurts
  the perceived quality; minor is finish. Each finding carries one precise, doable fix.
- Do not report what the packet lists as already verified, unless you can show it is wrong.
`

// bunshin always builds code-led: no comp was approved, whatever the host can generate.
const FINISH_TASK = 'This is a code-led build: there is no approved comp; a decision comp, when the packet names one, is a critique reference only. Judge the render against the request, the gate answers and the direction contract (thesis, the world it lives in, the story, the first viewport, the form, the signature interaction, the finish), and against the quality floor. You have no browser: the captures are your evidence.'
// The finish reviewer has a hard turn ceiling: point it at the captures it needs first.
const FINISH_READ = 'Read first, as your required captures: .impeccable/review/desktop.png, .impeccable/review/mobile.png, and the first-screen captures (390x664 and 1280x720) of each page. The full-page segments are for the other lenses: open one only to check a specific point.'
const LENSES = {
  finish: A.finishAgent
    ? `LENS: the finish review. ${FINISH_TASK} ${FINISH_READ} Answer in your own contract: the disposition, then persistence, fidelity, ceiling, material_fixes and keep; on a recapture, the recapture list alone.`
    : A.finishRole
      ? `LENS: the finish reviewer. Read your role first, ${A.finishRole}, and follow it. ${FINISH_TASK} Give your disposition (ship, fix, rebuild, recapture).`
      : `LENS: the finish reviewer. ${FINISH_TASK} Give your disposition: recapture when the captures are missing or invalid, rebuild when whole regions must be redone, fix when material findings remain, ship otherwise.`,
  mobile: `LENS: mobile, the path of a visitor who arrives from the main channel on a phone, in each language. Load and apply ${entry(M.mobile)}. Judge the first screen in three seconds, the desire the images create, the thumb zone and the calls to action, any sticky bar (when it appears, what it covers, duplicates), page length and rhythm, text over colour fields, touch targets, forms and their keyboard, menus. Read the mobile segments of every page.`,
  desktop: `LENS: desktop, 1280 px and wider. Load and apply ${entry(M.desktop)} and ${entry(M.motion)}. Judge the compositions, how consistently the direction's grammar carries from page to page, type hierarchy, hover states (read the CSS: present and considered on links, cards, buttons?), each page's first screen, layout families repeated across sections, the signature motion and its reduced-motion path (read the CSS and JS). Read the desktop segments of every page.`,
  truth: 'LENS: copy and truth. Read every content file and what the captures display. Judge the voice and its consistency, the same labels and facts across pages, every claim against the sources the packet names (anything invented or unverifiable: capacities, delays, prices, guarantees, clients, names), promises the owner will have to keep, the quality of each language, repetition, jargon, length. Comments that mark facts to confirm are expected: report only visible text that asserts something unverifiable.',
  tech: 'LENS: technical. Read the sources and the built output. Check heading hierarchy per page, image alternatives, form labels and errors (invalid state, descriptions, live announcements), keyboard paths through every control, contrast of the colour pairs in use (compute it), title, description, canonical, alternates, sitemap and structured data per page (validate the JSON-LD), page weight and the first screen\'s images (priority, no lazy loading on the largest one), needless JavaScript, any server endpoint (validation, header injection, size limits, error responses, secrets), behaviour without JavaScript, and every internal link of the built output against the files that exist.',
}
LENSES['truth-tech'] = `${LENSES.truth}\n\nThen, in the same review: ${LENSES.tech.replace('LENS: technical. ', '')}`

const chosen = A.lenses && A.lenses.length ? A.lenses : ['finish', 'mobile', 'desktop', 'truth', 'tech']
const unknown = chosen.filter(k => !LENSES[k])
if (unknown.length) throw new Error(`review.js: unknown lens(es) ${unknown.join(', ')}`)
if (chosen.some(k => k === 'mobile' || k === 'desktop') && !(M.mobile && M.desktop && M.motion)) {
  throw new Error('review.js: the mobile and desktop lenses need args.modules { mobile, desktop, motion }')
}

const FINDING = {
  type: 'object',
  properties: {
    severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
    page: { type: 'string' },
    viewport: { type: 'string', enum: ['mobile', 'desktop', 'both', 'n/a'] },
    evidence: { type: 'string', description: 'capture and region, or file:line' },
    issue: { type: 'string' },
    fix: { type: 'string' },
    files: { type: 'array', items: { type: 'string' } },
  },
  required: ['severity', 'page', 'viewport', 'evidence', 'issue', 'fix', 'files'],
}
const DISPOSITION = { type: 'string', enum: ['ship', 'fix', 'rebuild', 'recapture'] }
const FINDINGS = {
  type: 'object',
  properties: {
    overall: { type: 'string', description: 'The verdict in three to six sentences' },
    strengths: { type: 'array', items: { type: 'string' } },
    findings: { type: 'array', items: FINDING },
  },
  required: ['overall', 'strengths', 'findings'],
}
const FINISH_PLAIN = {
  type: 'object',
  properties: { disposition: DISPOSITION, ...FINDINGS.properties },
  required: ['disposition', ...FINDINGS.required],
}
const RECAPTURE = { type: 'array', items: { type: 'string' }, description: 'With disposition recapture only: each missing or invalid capture, and what a valid one shows' }
FINISH_PLAIN.properties.recapture = RECAPTURE
// Impeccable's finish reviewer contract, as fields: its own section names, kept. A recapture
// answer carries only the disposition and its recapture list.
const FINISH_IMPECCABLE = {
  type: 'object',
  properties: {
    disposition: DISPOSITION,
    recapture: RECAPTURE,
    persistence: { type: 'string' },
    fidelity: { type: 'string' },
    ceiling: { type: 'string' },
    material_fixes: { type: 'array', items: FINDING, description: 'Ordered, most material first' },
    keep: { type: 'array', items: { type: 'string' } },
  },
  required: ['disposition'],
}

function lensCall(key) {
  const impeccable = key === 'finish' && A.finishAgent
  const schema = key !== 'finish' ? FINDINGS : impeccable ? FINISH_IMPECCABLE : FINISH_PLAIN
  const opts = { label: `review:${key}`, phase: 'Review', schema }
  if (impeccable) opts.agentType = A.finishAgent
  // Impeccable's reviewer edits nothing: the plan clone writes its file.
  const save = impeccable ? '' : `\nBefore you answer, write the JSON you return, unchanged, to ${reviewFile(key)} (create the directory if needed): it is the only file you may write.`
  const ask = label => agent(`${A.packet}\n${RULES}\n${LENSES[key]}${save}`, { ...opts, label }).catch(() => null)
  return ask(`review:${key}`)
    .then(r => (r || key !== 'finish' ? r : ask('review:finish-retry')))
    .then(r => {
      if (!r) return null
      if (impeccable) {
        return {
          lens: key, disposition: r.disposition, recapture: r.recapture || [],
          overall: `disposition: ${r.disposition}. persistence: ${r.persistence || ''} fidelity: ${r.fidelity || ''} ceiling: ${r.ceiling || ''}`,
          strengths: r.keep || [], findings: r.material_fixes || [],
        }
      }
      return { lens: key, ...r }
    })
}

phase('Review')
const reviews = await parallel(chosen.map(key => () => lensCall(key)))
const ok = reviews.filter(Boolean)
if (!ok.length) throw new Error(`review.js: every lens of round ${ROUND} failed; no plan is drawn from zero reviews`)
const total = ok.reduce((n, r) => n + ((r.findings || []).length), 0)
const finish = ok.find(r => r.lens === 'finish')
const disposition = finish ? finish.disposition : null
log(`round ${ROUND}: ${ok.length}/${chosen.length} lenses returned, ${total} findings, finish disposition ${disposition || 'none'}`)
if (chosen.includes('finish') && !finish) log(`round ${ROUND}: the finish lens returned nothing twice, this round has no disposition`)
const summary = ok.map(r => ({ lens: r.lens, overall: r.overall, findings: (r.findings || []).length }))
const recapture = (finish && finish.recapture) || []

if (disposition === 'recapture' || disposition === 'rebuild') {
  log(`the finish reviewer says ${disposition}: no plan is drawn from this review`)
  return { round: ROUND, disposition, recapture, lenses: summary, plan: null }
}

const ownerLines = A.owners.map(o => `- ${o.key}: ${(o.files || []).join(', ')}`).join('\n')
const PLAN = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    fixes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          priority: { type: 'string', enum: ['P0', 'P1', 'P2'] },
          owner: { type: 'string', enum: [...new Set([...A.owners.map(o => o.key), 'orchestrator'])] },
          files: { type: 'array', items: { type: 'string' } },
          what: { type: 'string', description: 'The exact change, doable by someone who never read the reviews' },
          why: { type: 'string' },
          sources: { type: 'array', items: { type: 'string' }, description: 'The lenses that raised it' },
        },
        required: ['id', 'priority', 'owner', 'files', 'what', 'why', 'sources'],
      },
    },
    rejected: { type: 'array', items: { type: 'string' }, description: 'Findings set aside, each with the reason: wrong, out of scope, or against the validated direction' },
    questions_for_owner: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'fixes', 'rejected', 'questions_for_owner'],
}

const inline = JSON.stringify(ok)
const reviewsText = inline.length <= 150000
  ? `Here are ${ok.length} independent reviews of round ${ROUND}, as JSON:\n${inline}`
  : `The ${ok.length} reviews of round ${ROUND} are too long to inline: read them from ${ok.filter(r => !(r.lens === 'finish' && A.finishAgent)).map(r => reviewFile(r.lens)).join(', ')}; the finish review is ${JSON.stringify(finish)}.`
if (inline.length > 150000) log(`reviews too long to inline (${inline.length} characters): the plan clone reads them from disk`)

phase('Plan')
const plan = await agent(
  `${A.packet}\n\n${reviewsText}\n\n` +
  'Your job: the fix plan. Deduplicate. Verify every finding against the code and the captures, and reject the ones that are wrong or that contradict the direction the user validated, saying why. Settle contradictions between lenses. Group the fixes by file owner so they can be applied in parallel without two clones touching one file:\n' +
  `${ownerLines}\n- orchestrator: every file no owner above lists (the art director applies those)\n` +
  'Priorities: P0 must be fixed before anyone sees it, P1 is high value, P2 is finish. Every "what" must be applicable as written by someone who never read the reviews. Do not modify any project file.\n' +
  (finish && A.finishAgent ? `Write the finish review, exactly as given above, to ${reviewFile('finish')}. ` : '') +
  `Then write this JSON to ${A.planOut} (create the directory if needed): { "round": ${ROUND}, "disposition": ${JSON.stringify(disposition)}, "reviews": ${JSON.stringify(ok.map(r => reviewFile(r.lens)))}, "plan": <your plan> }, and return the plan as your structured answer.`,
  { label: `plan:round-${ROUND}`, phase: 'Plan', schema: PLAN }
).catch(() => null)
if (!plan) throw new Error(`review.js: the plan clone of round ${ROUND} returned nothing; the reviews are on disk at ${stem}.*.json`)

const perOwner = {}
for (const f of plan.fixes || []) perOwner[f.owner] = (perOwner[f.owner] || 0) + 1
log(`plan: ${(plan.fixes || []).length} fixes (${Object.entries(perOwner).map(([k, n]) => `${k} ${n}`).join(', ') || 'none'}), ${(plan.rejected || []).length} rejected`)
return { round: ROUND, disposition, recapture, lenses: summary, plan }
