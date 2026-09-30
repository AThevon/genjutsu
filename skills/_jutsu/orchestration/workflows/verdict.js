export const meta = {
  name: 'bunshin-verdict',
  description: 'Score a round of fixes with the finish reviewer, look with cold eyes when asked, and write the next round\'s plan',
  phases: [
    { title: 'Verdict', detail: 'the finish reviewer scores, a cold-eyes art director sees it for the first time' },
    { title: 'Plan', detail: 'the remaining points, by owner, written where refine.js reads them' },
  ],
}

// bunshin phase 10, after refine.js and new captures. Run with Workflow({ scriptPath: '<this
// file>', args }).
//
// args:
//   packet      string, required. The evidence packet of the NEW captures (same shape as the
//               review packet: project, request, contract, captures, sources, already verified).
//   history     string, required. Where the previous round lives: its plan file, the refine
//               results, the decisions file if any. Only the finish reviewer reads it.
//   round       number, required. The round being scored.
//   owners      [{ key, files }], required. Every file owner, as in review.js.
//   planOut     string, required. Absolute path of the next round's plan file, in the shape
//               refine.js reads: { round, disposition, reviews, plan: { fixes } }.
//   finishAgent string, optional. The agent type the host lists for Impeccable's shipped finish
//               reviewer (Claude Code: 'impeccable-finish-reviewer'), spawned fresh.
//   finishRole  string, optional. As in review.js: a role file, such as Impeccable's own
//               reference/degraded/finish-reviewer.md, never its agent definition.
//   freshEyes   boolean, optional. Also run the cold-eyes art director (default false).
//   scenario    string, required when freshEyes. How the site reaches its audience, in one
//               sentence ("the link arrives from a social profile on a phone, then on a laptop").
//
// Returns { finish, fresh, planOut }: fresh is null without freshEyes; planOut is null only when
// the finish reviewer returned nothing twice, asks for a recapture, or the plan could not be
// written. With nothing left to fix, the plan is still written with an empty fixes list, so a
// round that applies a decisions file alone has the file refine.js reads. The cold-eyes notes are
// not in the plan: turning them into rules is the art director's job, in the decisions file.

const A = args || {}
if (!A.packet || !A.history || !A.round || !Array.isArray(A.owners) || !A.owners.length || !A.planOut) {
  throw new Error('verdict.js needs args.packet, args.history, args.round, args.owners[] and args.planOut')
}
if (A.freshEyes && !A.scenario) throw new Error('verdict.js needs args.scenario when args.freshEyes is true')
const ROUND = Number(A.round)
if (!Number.isInteger(ROUND) || ROUND < 1) throw new Error('verdict.js: args.round must be a positive integer')

const OWNER_KEYS = [...new Set([...A.owners.map(o => o.key), 'orchestrator'])]
const ownerLines = A.owners.map(o => `- ${o.key}: ${(o.files || []).join(', ')}`).join('\n') +
  '\n- orchestrator: every file no owner above lists'

const REMAINING = {
  type: 'object',
  properties: {
    severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
    page: { type: 'string' },
    evidence: { type: 'string' },
    issue: { type: 'string' },
    fix: { type: 'string' },
    files: { type: 'array', items: { type: 'string' } },
  },
  required: ['severity', 'page', 'evidence', 'issue', 'fix', 'files'],
}
const VERDICT = {
  type: 'object',
  properties: {
    disposition: { type: 'string', enum: ['ship', 'fix', 'rebuild', 'recapture'] },
    summary: { type: 'string' },
    scored: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          // Impeccable's scoring contract has three statuses; the plain reviewer may also say it
          // could not verify a fix.
          status: { type: 'string', enum: A.finishAgent ? ['resolved', 'partial', 'unresolved'] : ['resolved', 'partial', 'unresolved', 'not-verifiable'] },
          note: { type: 'string' },
        },
        required: ['id', 'status', 'note'],
      },
    },
    remaining: { type: 'array', items: REMAINING },
    recapture: { type: 'array', items: { type: 'string' }, description: 'With disposition recapture only: each missing or invalid capture, and what a valid one shows' },
  },
  required: ['disposition', 'summary', 'scored', 'remaining'],
}
// The finish reviewer's remaining points become the next plan, so each one carries a plan id,
// a priority and its owner.
const FINISH_VERDICT = {
  type: 'object',
  properties: {
    ...VERDICT.properties,
    remaining: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          ...REMAINING.properties,
          id: { type: 'string' },
          priority: { type: 'string', enum: ['P0', 'P1', 'P2'] },
          owner: { type: 'string', enum: OWNER_KEYS },
        },
        required: [...REMAINING.required, 'id', 'priority', 'owner'],
      },
    },
  },
  required: VERDICT.required,
}

const RULES = 'Review only: modify no file, start no server, drive no browser. Open the captures with your file-reading tool. Every point cites its evidence (capture and region, or file:line).'

const who = A.finishAgent
  ? 'This is a verdict pass on a finish review another reviewer wrote: its findings, and the fixes applied since, are in the history below.'
  : A.finishRole
    ? `You are the finish reviewer, in a verdict pass. Your role: ${A.finishRole}.`
    : 'You are the finish reviewer, in a verdict pass, holding the direction contract.'

const scoring = A.finishAgent
  ? 'resolved, partial or unresolved), then list in "remaining" every point still open and at most three regressions the fixes introduced (a verdict pass: no new hunt).'
  : 'resolved, partial, unresolved, or not-verifiable), then list in "remaining" every point still open and any regression or new material defect.'
const finishPrompt = `${A.packet}\n${RULES}\n\n${who} Read the previous round: ${A.history}. Score every fix of that round against the new captures (id as in its plan; ${scoring} Give each remaining point an id of the form r${ROUND + 1}-N, a priority (P0 before anyone sees it, P1 high value, P2 finish) and the owner of its files:\n${ownerLines}\nDisposition: recapture when the new captures are missing or invalid (then list them in "recapture"); rebuild when whole regions must be redone; ship when nothing material is left within the scope of this version (facts only the project owner can supply do not count as defects); fix otherwise.`
const finishOpts = { phase: 'Verdict', schema: FINISH_VERDICT, ...(A.finishAgent ? { agentType: A.finishAgent } : {}) }

phase('Verdict')
const thunks = [
  // An empty answer from the finish reviewer is asked once more: the loop starts from its disposition.
  () => agent(finishPrompt, { ...finishOpts, label: 'verdict:finish' }).catch(() => null)
    .then(r => r || agent(finishPrompt, { ...finishOpts, label: 'verdict:finish-retry' }).catch(() => null)),
]
if (A.freshEyes) {
  thunks.push(() => agent(
    `${A.packet}\n${RULES}\n\nYou are an art director who sees this site for the first time. Do not read any history, review or plan: your value is that you have seen none of them. ${A.scenario} Without indulgence: does it make you want what it offers, is it credible, does it hold its direction, what still looks amateur or like a template (repeated images, one layout family everywhere, colour fields that talk too much, type that looks generic)? Leave "scored" empty. In "remaining", at most eight points that really change the perception, by impact, each with a precise fix. Disposition: ship when you would show it as is.`,
    { label: 'verdict:cold-eyes', phase: 'Verdict', schema: VERDICT }
  ).catch(() => null))
}
const [finish, fresh] = await parallel(thunks)

const open = v => (v && v.remaining ? v.remaining.filter(r => r.severity !== 'minor').length : 0)
log(`finish: ${finish ? finish.disposition : 'failed'}, ${open(finish)} critical or major left${A.freshEyes ? `; cold eyes: ${fresh ? fresh.disposition : 'failed'}, ${open(fresh)} critical or major` : ''}`)

let planOut = null
if (finish && finish.disposition !== 'recapture') {
  // The plan is built here, not by a model: its shape is exactly what refine.js reads.
  const next = {
    round: ROUND + 1,
    disposition: finish.disposition,
    reviews: [],
    plan: {
      summary: finish.summary,
      fixes: (finish.remaining || []).map(r => ({
        id: r.id, priority: r.priority, owner: r.owner, files: r.files,
        what: r.fix, why: `${r.issue} (${r.evidence})`, sources: ['verdict'],
      })),
      rejected: [],
      questions_for_owner: [],
    },
  }
  phase('Plan')
  const wrote = await agent(
    `Write the JSON below, exactly as it is, to ${A.planOut} (create the directory if needed). Modify no other file. Then answer with the path you wrote.\n\n${JSON.stringify(next, null, 2)}`,
    { label: `plan:round-${ROUND + 1}`, phase: 'Plan', effort: 'low' }
  ).catch(() => null)
  planOut = wrote ? A.planOut : null
  if (!wrote) log(`the plan of round ${ROUND + 1} was not written: write it from finish.remaining yourself`)
}
return { finish: finish || null, fresh: A.freshEyes ? fresh || null : null, planOut }
