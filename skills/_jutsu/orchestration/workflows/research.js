export const meta = {
  name: 'bunshin-research',
  description: 'Research a whole-site brief from four angles in parallel, then synthesise one recommendation',
  phases: [
    { title: 'Sweep', detail: 'one clone per angle, structured findings' },
    { title: 'Synthesis', detail: 'site map, conversion, credibility, pitfalls, written to disk' },
  ],
}

// bunshin phase 3. Run with Workflow({ scriptPath: '<this file>', args }).
//
// args:
//   brief     string, required. The product context, facts only: who, what, where, for whom,
//             the main acquisition channel, the answers of the summoning gate.
//   out       string, required. Absolute path of the Markdown synthesis the last clone writes.
//   language  string, optional. Language of the synthesis. Default: the language of the brief.
//   angles    [{ key, prompt }], optional. Replaces the four default angles. Each prompt is
//             appended to the brief, so it names the angle only.
//
// Returns { out, angles, synthesis }: the path, per angle the URLs read and the patterns seen
// (the full findings go to the synthesis clone, not back into your context), and the synthesis.

const A = args || {}
if (!A.brief || !A.out) throw new Error('research.js needs args.brief and args.out')

const LANGUAGE = A.language ? `Write in ${A.language}.` : 'Write in the language of the brief.'

const RULES = `
Rules for every research clone:
- Read real pages. Use the web search tool to find them and the web fetch tool to read them; a
  site you did not open is not a finding.
- Facts only. Every claim names the site it comes from. Never invent a site, a number or a quote.
- Do not modify any file. Do not start a server.
`

const FINDINGS = {
  type: 'object',
  properties: {
    sites_reviewed: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          url: { type: 'string' },
          why_relevant: { type: 'string' },
          pages_and_sections: { type: 'array', items: { type: 'string' } },
          conversion_mechanics: { type: 'string', description: 'CTAs, the exact fields of the contact or quote form, messaging apps, booking, prices shown or not' },
          standout_ideas: { type: 'array', items: { type: 'string' } },
          weaknesses: { type: 'array', items: { type: 'string' } },
        },
        required: ['name', 'url', 'pages_and_sections', 'conversion_mechanics', 'standout_ideas'],
      },
    },
    patterns: { type: 'array', items: { type: 'string' }, description: 'Recurring patterns, with how often they were seen' },
    recommendations: { type: 'array', items: { type: 'string' } },
    pitfalls: { type: 'array', items: { type: 'string' } },
  },
  required: ['sites_reviewed', 'patterns', 'recommendations'],
}

const DEFAULT_ANGLES = [
  {
    key: 'direct',
    prompt: 'Angle: direct competitors. Independents who do the same job, for the same audience, in the same area or market. Read at least eight real sites, not directories or marketplaces. For each: pages and sections, the conversion mechanics with the exact form fields, standout ideas, weaknesses.',
  },
  {
    key: 'premium',
    prompt: 'Angle: the premium end and the design references. The best-designed sites in this category and its neighbours, internationally, including award galleries. Read at least eight. Note how imagery carries the story, how mobile is handled, how credibility is earned without invented testimonials, and how the offer is presented.',
  },
  {
    key: 'adjacent',
    prompt: 'Angle: the adjacent offer or the second audience named in the brief (a B2B side, a second service, a second language market). How do sites that serve two audiences keep both messages clear? If the brief has one audience only, study the categories that audience compares this offer against. Read at least six sites.',
  },
  {
    key: 'acquisition',
    prompt: 'Angle: acquisition and conversion on the main channel named in the brief. The path from that channel to a request on a phone, which contact mechanics convert (form, messaging app, call, booking), the form fields that matter, local or niche SEO queries, the relevant schema.org types, the questions clients ask before booking, and image performance on mobile. Give prioritised, concrete recommendations.',
  },
]

if (A.angles !== undefined && !Array.isArray(A.angles)) throw new Error(`research.js: args.angles must be an array of { key, prompt }, not ${typeof A.angles}`)
const ANGLES = A.angles && A.angles.length ? A.angles : DEFAULT_ANGLES

phase('Sweep')
const sweeps = await parallel(ANGLES.map(a => () =>
  agent(`${A.brief}\n\n${a.prompt}\n${RULES}`, { label: `research:${a.key}`, phase: 'Sweep', schema: FINDINGS })
    .catch(() => null).then(r => (r ? { angle: a.key, ...r } : null))
))
const found = sweeps.filter(Boolean)
log(`${found.length}/${ANGLES.length} angles returned`)
if (!found.length) throw new Error('research.js: every research angle failed, nothing to synthesise; run the sweep again')
if (found.length < ANGLES.length) {
  log(`missing angles: ${ANGLES.map(a => a.key).filter(k => !found.some(f => f.angle === k)).join(', ')}`)
}

phase('Synthesis')
const synthesis = await agent(
  `${A.brief}\n\nHere are ${found.length} independent research sweeps, as JSON:\n${JSON.stringify(found).slice(0, 180000)}\n\n` +
  `Synthesise them into one recommendation for this project and write it as Markdown to ${A.out} (create the directory if needed). ${LANGUAGE} No U+2014 (em dash). Structure:\n` +
  '1. Site map: the pages or routes, and for each one its sections in order, with the reason.\n' +
  '2. What the first version must have, and what can wait, with the evidence for each.\n' +
  '3. Conversion: the primary and secondary call to action, the request form (exact fields, steps, tone), the messaging channel, and how each works on a phone.\n' +
  '4. Two audiences, when there are two: how to serve both without blurring either.\n' +
  '5. Credibility without invention: what can honestly be shown with no testimonial, client name or figure made up.\n' +
  '6. SEO: titles and descriptions, schema.org types, area or niche pages.\n' +
  '7. Ten signature ideas seen on the best sites, adapted to this project.\n' +
  '8. Pitfalls.\n' +
  'Be concrete and cite the source sites. Then return the same Markdown as your final answer.',
  { label: 'research:synthesis', phase: 'Synthesis' }
)

return {
  out: A.out,
  angles: found.map(f => ({ angle: f.angle, read: (f.sites_reviewed || []).map(s => s.url), patterns: f.patterns || [] })),
  synthesis,
}
