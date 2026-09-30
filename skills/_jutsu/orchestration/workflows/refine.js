export const meta = {
  name: 'bunshin-refine',
  description: 'Apply a fix plan in parallel, one clone per file owner, the shared owner first',
  phases: [
    { title: 'Shared', detail: 'the owner of the shared files, alone, when it has fixes' },
    { title: 'Fix', detail: 'every other owner in parallel, reading the plan from disk' },
  ],
}

// bunshin phase 10. Run with Workflow({ scriptPath: '<this file>', args }).
//
// The plan is read from disk by each clone, never passed through args: fifty fixes in args is
// how a run once crashed on a placeholder, and a file is also what a clone can re-read.
//
// args:
//   root       string, required. Absolute path of the project.
//   packet     string, required. What to read first (PRODUCT.md, the direction contract, the
//              quality floor) and the rules.
//   planPath   string, required. A plan file: { round, disposition, reviews, plan: { fixes } }, as review.js
//              writes it for round 1 and verdict.js for every later round.
//   decisions  string, optional. The decisions file of this round (Markdown rules). Each clone
//              applies every rule of it within the files it owns, besides its fixes.
//   owners     [{ key, files }], required. The owners that have fixes in the plan, and, with a
//              decisions file, every owner whose files its rules touch.
//   shared     string, optional. The key of the owner that holds shared files. When it is in
//              owners it runs first and alone, and the others see its contracts.
//   build      { cmd, check?, scratch, exclude?, link?, static?, shoot?, routes? }, required.
//              As in build.js.
//
// Returns [{ owner, done, not_done, files_changed, build_ok, notes }], or { owner, failed: true }.

const A = args || {}
if (!A.root || !A.packet || !A.planPath || !Array.isArray(A.owners) || !A.owners.length || !A.build || !A.build.cmd || !A.build.scratch) {
  throw new Error('refine.js needs args.root, args.packet, args.planPath, args.owners[] and args.build { cmd, scratch }')
}

// --- the isolated build: the same block in build.js and refine.js ---
const q = s => `'${String(s).replace(/'/g, `'\\''`)}'`
const PM = /^\s*(pnpm|npm|yarn|bun|npx|pnpx|bunx)\b/
if ([A.build.cmd, A.build.check].some(c => c && PM.test(c))) {
  throw new Error('build.cmd and build.check must be the framework binary (./node_modules/.bin/...), never a package manager: in the copy it reinstalls through the node_modules link')
}
const ROOT_DIR = String(A.root).replace(/\/+$/, '')
if (!ROOT_DIR.startsWith('/') || ROOT_DIR.includes('$')) throw new Error('args.root must be the absolute, resolved project path')
if (A.build.shoot && !String(A.build.shoot).startsWith('/')) throw new Error('build.shoot must be an absolute path')
const SCRATCH = String(A.build.scratch).replace(/\/+$/, '')
if (!SCRATCH.startsWith('/') || SCRATCH.includes('$') || SCRATCH === ROOT_DIR || SCRATCH.startsWith(`${ROOT_DIR}/`)) {
  throw new Error('build.scratch must be an absolute, already resolved directory outside args.root')
}
const KEYS = A.owners.map(o => o && o.key)
if (KEYS.some(k => typeof k !== 'string' || !/^[a-z0-9][a-z0-9-]*$/.test(k)) || new Set(KEYS).size !== KEYS.length) {
  throw new Error('owner keys must be unique, lower-case letters, digits and dashes')
}
const LINK = A.build.link || ['node_modules']
const CACHES = ['.astro', '.vercel', '.next', '.nuxt', '.output', '.svelte-kit', '.turbo', '.cache']
// Agent and tool folders are never needed by a build, and can weigh megabytes each.
const TOOLING = ['.claude', '.agents', '.impeccable']
const EXCLUDE = [...new Set(['node_modules', 'dist', '.git', '.bunshin', ...TOOLING, ...CACHES, ...(A.build.exclude || []), ...LINK])]

function copyDir(prefix, key) {
  return `${SCRATCH}/${prefix}-${key}`
}

function isolatedBuild(prefix, key, tail) {
  const dir = copyDir(prefix, key)
  const links = LINK.map(l => l === 'node_modules'
    ? `mkdir -p "$D/node_modules" && find ${q(`${ROOT_DIR}/node_modules`)} -mindepth 1 -maxdepth 1 ! -name .astro ! -name .vite ! -name .cache -exec ln -s {} "$D/node_modules/" \\;`
    : `ln -s ${q(`${ROOT_DIR}/${l}`)} "$D"/${q(l)}`)
  return [
    `D=${q(dir)}; rm -rf "$D"; mkdir -p "$D"`,
    `rsync -a ${EXCLUDE.map(e => `--exclude ${q(`/${e}`)}`).join(' ')} ${q(`${ROOT_DIR}/`)} "$D/"`,
    ...links,
    `cd "$D" && ${A.build.cmd} > "$D/.bunshin-build.log" 2>&1; echo "build exit code: $?"; tail -${tail} "$D/.bunshin-build.log"`,
    A.build.check ? `cd "$D" && ${A.build.check} > "$D/.bunshin-check.log" 2>&1; echo "check exit code: $?"; tail -${tail} "$D/.bunshin-check.log"` : '',
  ].filter(Boolean).join('\n')
}

// When the build names its static output, the harness and the owner's routes, a clone sees its
// own page: it captures from its own copy, with its own headless browser, and opens the images.
function selfCapture(prefix, key) {
  const routes = ((A.build.routes && A.build.routes[key]) || []).map(r => (String(r).startsWith('/') ? String(r) : `/${r}`))
  if (!A.build.static || !A.build.shoot || !routes.length) return ''
  const dir = copyDir(prefix, key)
  const name = r => (r.replace(/\W+/g, '-').replace(/^-|-$/g, '') || 'home')
  const shots = routes.flatMap(r => [
    { path: r, w: 390, h: 664, out: `${dir}/shots/${name(r)}-390x664.png` },
    { path: r, w: 1440, h: 900, out: `${dir}/shots/${name(r)}-1440x900.png` },
  ])
  return `
Then look at what you built, from your own copy, with your own headless browser (never the
shared one): write this JSON to ${dir}/shots.json, run the harness, and open every image it lists
with your file-reading tool. Fix what you see before you return: overflow, a broken first screen,
a console error, a file of your build reported missing. Two missing entries are expected and are
not yours: an analytics script the host injects at deploy time (such as /_vercel/insights/...),
and /favicon.ico when the site ships another icon.
${JSON.stringify(shots)}
node ${q(A.build.shoot)} --root ${q(`${dir}/${A.build.static}`)} --shots ${q(`${dir}/shots.json`)}
`
}
// --- end of the isolated build block ---

const RESULT = {
  type: 'object',
  properties: {
    done: { type: 'array', items: { type: 'string' }, description: 'fix id (or decision) and one line on what changed' },
    not_done: { type: 'array', items: { type: 'string' }, description: 'fix id (or decision) and the reason' },
    files_changed: { type: 'array', items: { type: 'string' } },
    build_ok: { type: 'boolean', description: 'true only when every exit code the recipe printed is 0' },
    notes: { type: 'string', description: 'Contracts you changed that other owners rely on, and anything the next round must know' },
  },
  required: ['done', 'not_done', 'files_changed', 'build_ok', 'notes'],
}

function prompt(o, sharedNotes) {
  return `${A.packet}

You apply fixes, as the owner "${o.key}".
YOU WRITE ONLY THESE FILES: ${(o.files || []).join(', ')}. Other clones change other files at the
same time. A fix that needs a file outside that list: leave it, and say so in not_done.
${sharedNotes ? `\nThe shared owner already ran. What it changed, which you may rely on:\n${sharedNotes}\n` : ''}
YOUR FIXES: read ${A.planPath}, key plan.fixes, and apply every entry whose owner is "${o.key}",
P0 first, then P1, then P2. Each entry has id, priority, files, what, why and sources; the key
reviews of the same file points to the original evidence when you need it. Apply each "what" as
written and keep its "why". When a fix turns out wrong once you read the code, do not apply it:
say why in not_done.
${A.decisions ? `\nTHE RULES OF THIS ROUND: read ${A.decisions}. They are the art director's decisions, and they bind\nwherever they apply. Apply every rule that concerns the files you own, even where no fix names it,\nand list each one you applied in done.\n` : ''}
Never start a server, never drive the shared browser, never run the package manager. Verify in
an isolated copy, exactly, and fix until every exit code it prints is 0. An error from a file
you do not own is not yours: retry once later.
${isolatedBuild('fix', o.key, 20)}
${selfCapture('fix', o.key)}`
}

const shared = A.shared ? A.owners.find(o => o.key === A.shared) : null
const rest = A.owners.filter(o => o !== shared)
const results = []

phase('Shared')
let sharedNotes = ''
if (shared) {
  const r = await agent(prompt(shared, ''), { label: `fix:${shared.key}`, phase: 'Shared', schema: RESULT }).catch(() => null)
  results.push(r ? { owner: shared.key, ...r } : { owner: shared.key, failed: true })
  sharedNotes = r ? `${r.notes}\nFiles: ${(r.files_changed || []).join(', ')}` : '(the shared clone failed: do not rely on any new shared contract)'
} else {
  log('no shared owner in this plan')
}

phase('Fix')
const others = await parallel(rest.map(o => () =>
  agent(prompt(o, sharedNotes), { label: `fix:${o.key}`, phase: 'Fix', schema: RESULT })
    .catch(() => null).then(r => (r ? { owner: o.key, ...r } : { owner: o.key, failed: true }))
))
results.push(...others)

const done = results.reduce((n, r) => n + ((r && r.done) || []).length, 0)
const notDone = results.reduce((n, r) => n + ((r && r.not_done) || []).length, 0)
log(`${done} fixes applied, ${notDone} not applied, ${results.filter(r => r && r.build_ok).length}/${results.length} builds green`)
return results
