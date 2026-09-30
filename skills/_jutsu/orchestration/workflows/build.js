export const meta = {
  name: 'bunshin-build',
  description: 'Build the pages or screens of a site in parallel, one clone per owner, on disjoint files',
  phases: [
    { title: 'Build', detail: 'one clone per page, shared files read-only, isolated builds' },
  ],
}

// bunshin phase 7. Run with Workflow({ scriptPath: '<this file>', args }).
//
// args:
//   root     string, required. Absolute path of the project.
//   packet   string, required. The shared brief every clone reads first: what to read, in
//            order (absolute paths: PRODUCT.md, the direction contract, the quality floor, the
//            design system, the reference surface you built), the file conventions, the
//            non-negotiable rules of the validated theses, the voice.
//   owners   [{ key, mission, files }], required. One clone per entry: the page owners you did
//            not build yourself, never `shared`, never the signature surface. `key` is lower
//            case letters, digits and dashes, unique. `files` lists the paths or globs that
//            clone owns and may write; everything else is read-only to it.
//   build    { cmd, check?, scratch, exclude?, link?, static?, shoot?, routes? }, required.
//              cmd      the framework's own build binary, e.g. './node_modules/.bin/astro build'.
//                       Never the package manager: in a copy it reinstalls through the links.
//              check    optional type check, e.g. './node_modules/.bin/astro check'.
//              scratch  an absolute directory OUTSIDE the project, already resolved (never a
//                       shell expression: it is quoted, and nothing in it is expanded).
//              exclude  extra directories not copied, added to the defaults (node_modules, dist,
//                       .git, .bunshin, the agent folders .claude, .agents, .impeccable, and the
//                       framework caches and outputs .astro, .vercel, .next, .nuxt, .output,
//                       .svelte-kit, .turbo, .cache).
//                       A site with no build step passes cmd 'true', static '.', link [].
//              link     directories linked from the project instead of copied (default:
//                       node_modules, linked entry by entry, without the framework caches kept
//                       inside it, so parallel builds never write into the real one).
//              static   optional, the static output the build writes, relative to the copy
//                       (dist, .vercel/output/static, out). With shoot and routes, each clone
//                       captures its own page from its own copy and looks at it.
//              shoot    optional, the absolute path of orchestration/scripts/shoot.mjs.
//              routes   optional, { <owner key>: [routes] }: what each clone captures.
//
// Returns [{ owner, files, summary, open_questions, shared_change_requests, build_ok }], or
// { owner, failed: true } for a clone that returned nothing.

const A = args || {}
if (!A.root || !A.packet || !Array.isArray(A.owners) || !A.owners.length || !A.build || !A.build.cmd || !A.build.scratch) {
  throw new Error('build.js needs args.root, args.packet, args.owners[] and args.build { cmd, scratch }')
}
if (A.owners.some(o => !o || !o.mission || !Array.isArray(o.files) || !o.files.length)) {
  throw new Error('build.js: every owner needs a mission and a non-empty files list')
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

const INVARIANTS = `
How you work, whatever the page:
- Other clones write other files of this project at the same time. You write only the files you
  own (listed below). Every other file is read-only to you. When you need a change in a file you
  do not own, do not make it: describe it precisely in shared_change_requests.
- Never start a dev server or a preview server. Never drive the shared browser. Never run the
  package manager, in the project or in your copy.
- Honour every rule of the packet. Its rules come from the validated theses and win over taste.
- Nothing invented: no testimonial, client, figure, price or distinction that the packet's
  sources do not state. An unknown fact stays generic in the visible text and is marked for the
  owner of the project in a comment of the content file, never on the page.

Verify before you return, in an isolated copy (the project folder is shared, so never build in
it). Run exactly this, and fix until every exit code it prints is 0. Do not fix another clone's
files: an error that comes from a file you do not own is theirs, retry once later.
`

const RESULT = {
  type: 'object',
  properties: {
    files: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string', description: 'The sections built and the choices made, in a few sentences' },
    open_questions: { type: 'array', items: { type: 'string' }, description: 'Facts only the project owner can confirm' },
    shared_change_requests: { type: 'array', items: { type: 'string' }, description: 'Precise changes needed in files you do not own' },
    build_ok: { type: 'boolean', description: 'true only when every exit code the recipe printed is 0' },
  },
  required: ['files', 'summary', 'open_questions', 'shared_change_requests', 'build_ok'],
}

phase('Build')
const results = await parallel(A.owners.map(o => () =>
  agent(
    `${A.packet}\n${INVARIANTS}\n${isolatedBuild('build', o.key, 30)}\n${selfCapture('build', o.key)}\nYOU OWN: ${(o.files || []).join(', ')}\n\nYOUR MISSION (${o.key}):\n${o.mission}`,
    { label: `build:${o.key}`, phase: 'Build', schema: RESULT }
  ).catch(() => null).then(r => (r ? { owner: o.key, ...r } : { owner: o.key, failed: true }))
))

const green = results.filter(r => r && r.build_ok).length
const failed = results.filter(r => r && r.failed).map(r => r.owner)
const requests = results.reduce((n, r) => n + ((r && r.shared_change_requests) || []).length, 0)
log(`${green}/${A.owners.length} builds green, ${requests} shared change requests${failed.length ? `, no answer from ${failed.join(', ')}` : ''}`)
return results
