#!/usr/bin/env node
// Checks the workflow templates bunshin runs, offline, with no model and no dependency.
//
// A workflow template is JavaScript that only runs inside a host's workflow tool, billed per
// agent. A mistake in one is found by the run that pays for it, often hours in: the run this
// pipeline comes from lost a whole fan-out to `fixes.some is not a function`, because a
// placeholder string reached a script that expected an array. So every template is held to the host's
// contract here, and then executed end to end against stubs:
//
// - it begins with `export const meta = {...}`, and meta is a pure literal (no variable, no
//   call, no operator, no spread, no template string), with a name, a description and phases;
// - it never calls Date.now(), Math.random() or an argless new Date(), which break resume: the
//   patterns are grepped, and Date and Math are also shadowed at run time so no spelling of
//   them slips through;
// - it compiles as the body of an async function, the way the host runs it;
// - with each fixture of scripts/tests/fixtures/workflows/<name>*.args.json it runs to the
//   end: every phase() title is declared in meta.phases, every agent() call has a label, a
//   declared phase and a satisfiable schema (every required key among the properties, no empty
//   or duplicated enum), no prompt contains "undefined", "[object Object]", "NaN" or U+2014,
//   parallel() gets functions, and no thunk or pipeline stage throws. The host swallows those
//   throws into a null; here, with stub agents that never fail, a throw is always a bug;
// - with the same fixtures and every agent() returning null, as the host does when a subagent
//   dies, it ends or stops on a deliberate `throw new Error(...)`: a TypeError is a crash;
// - orchestration/scripts/brief.mjs, which prints the prompts for a host with no workflow
//   tool, prints every call of it;
// - with empty args it throws at once, naming the template, instead of fanning out on nothing;
// - build.js and refine.js carry the isolated-build block byte for byte.
//
// Run: node scripts/check-workflows.mjs            (the templates in the repo)
//      node scripts/check-workflows.mjs --self-test (proves each check can still fail)

import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import vm from 'node:vm'
import { briefs } from '../skills/_jutsu/orchestration/scripts/brief.mjs'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const TEMPLATES = join(ROOT, 'skills', '_jutsu', 'orchestration', 'workflows')
const FIXTURES = join(ROOT, 'scripts', 'tests', 'fixtures', 'workflows')
const EM_DASH = String.fromCharCode(0x2014)
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const HOOKS = ['agent', 'parallel', 'pipeline', 'phase', 'log', 'args', 'budget', 'workflow']

// Split the source into the meta literal and the body. The literal ends at the brace that
// closes the one it opens with; strings and comments are skipped so a brace inside them
// never counts.
export function splitMeta(src) {
  const head = 'export const meta = '
  if (!src.startsWith(head)) throw new Error('must begin with `export const meta = {`')
  let i = head.length
  if (src[i] !== '{') throw new Error('meta must be an object literal')
  let depth = 0
  let quote = null
  for (; i < src.length; i++) {
    const c = src[i]
    if (quote) {
      if (c === '\\') { i++; continue }
      if (c === quote) quote = null
      continue
    }
    if (c === "'" || c === '"' || c === '`') { quote = c; continue }
    if (c === '/' && src[i + 1] === '/') { i = src.indexOf('\n', i); if (i < 0) break; continue }
    if (c === '/' && src[i + 1] === '*') {
      const end = src.indexOf('*/', i + 2)
      if (end < 0) throw new Error('meta has an unterminated comment')
      i = end + 1
      continue
    }
    if (c === '{') depth++
    if (c === '}' && --depth === 0) break
  }
  if (depth !== 0) throw new Error('meta literal is not closed')
  return { metaText: src.slice(head.length, i + 1), body: src.slice(i + 1) }
}

// The meta literal with every string and comment removed: what is left may only be literal
// syntax (braces, brackets, keys, colons, commas, numbers, true, false, null).
function outsideStrings(text) {
  return text
    .replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"/g, "''")
    .replace(/\/\/[^\n]*/g, '')
    .replace(/\/\*[\s\S]*?\*\//g, '')
}

export function checkMeta(metaText) {
  const errors = []
  const bare = outsideStrings(metaText)
  if (bare.includes('`')) errors.push('meta uses a template string: it must be a pure literal')
  if (bare.includes('...')) errors.push('meta uses a spread: it must be a pure literal')
  if (/[()]/.test(bare)) errors.push('meta calls something: it must be a pure literal')
  else if (/[^\w\s{}[\]:,.'"-]/.test(bare)) errors.push('meta uses an operator: it must be a pure literal')
  let meta = null
  try {
    // An empty context: any identifier that is not literal syntax is a ReferenceError here.
    meta = vm.runInNewContext(`(${metaText})`, Object.create(null), { timeout: 1000 })
  } catch (e) {
    errors.push(`meta is not a pure literal: ${e.message}`)
    return { meta: null, errors }
  }
  if (!meta || typeof meta.name !== 'string' || !meta.name) errors.push('meta.name is missing')
  if (!meta || typeof meta.description !== 'string' || !meta.description) errors.push('meta.description is missing')
  if (!meta || !Array.isArray(meta.phases) || !meta.phases.length) errors.push('meta.phases is missing')
  else if (meta.phases.some(p => !p || typeof p.title !== 'string' || !p.title)) errors.push('every meta.phases entry needs a title')
  return { meta, errors }
}

export function checkBody(body) {
  const errors = []
  if (/\bDate\s*(\.\s*now|\[\s*['"]now['"]\s*\])/.test(body)) errors.push('reads Date.now, which breaks resume')
  if (/\bMath\s*(\.\s*random|\[\s*['"]random['"]\s*\])/.test(body)) errors.push('reads Math.random, which breaks resume')
  if (/\bnew\s+Date\s*(\(\s*\)|(?![\s(]))/.test(body)) errors.push('calls new Date() with no argument, which breaks resume')
  let fn = null
  try {
    // Date and Math are parameters, so the run below can shadow them.
    fn = new AsyncFunction(...HOOKS, 'Date', 'Math', body)
  } catch (e) {
    errors.push(`does not compile as a workflow body: ${e.message}`)
  }
  return { fn, errors }
}

// A value that satisfies a JSON schema, the way a subagent forced through a schema answers.
export function fake(schema) {
  if (!schema || typeof schema !== 'object') return 'a subagent answer'
  if (schema.enum) return schema.enum[0]
  switch (schema.type) {
    case 'object': {
      const out = {}
      for (const [k, s] of Object.entries(schema.properties || {})) out[k] = fake(s)
      return out
    }
    case 'array': return [fake(schema.items)]
    case 'string': return 'text'
    case 'boolean': return true
    case 'number':
    case 'integer': return 1
    default: return null
  }
}

// The host refuses a schema it cannot satisfy, inside agent(), and parallel() then turns the
// whole fan-out into nulls. Catch it here instead.
export function schemaErrors(s, at = 'schema') {
  const out = []
  if (!s || typeof s !== 'object') return out
  if (s.enum && (!s.enum.length || new Set(s.enum).size !== s.enum.length)) out.push(`${at}: enum is empty or has duplicates`)
  if (s.type === 'object') {
    const props = s.properties || {}
    for (const r of s.required || []) if (!(r in props)) out.push(`${at}: required "${r}" is not in properties`)
    for (const [k, v] of Object.entries(props)) out.push(...schemaErrors(v, `${at}.${k}`))
  }
  if (s.type === 'array') out.push(...schemaErrors(s.items, `${at}[]`))
  return out
}

// Stand-ins for the globals a template must not use: a call fails the run with its name.
function stubDate() {
  function StubDate(...a) {
    if (!new.target || !a.length) throw new Error('new Date() without an argument breaks resume')
    return new globalThis.Date(...a)
  }
  StubDate.now = () => { throw new Error('Date.now() breaks resume') }
  StubDate.parse = globalThis.Date.parse
  StubDate.UTC = globalThis.Date.UTC
  return StubDate
}
const stubMath = () => Object.create(Math, { random: { value: () => { throw new Error('Math.random() breaks resume') } } })

// Run a compiled template against stubs. Returns the list of problems found.
// With nulls, every agent() answers null, the way the host answers for a subagent that died.
export async function run(fn, meta, args, { nulls = false } = {}) {
  const errors = []
  const titles = new Set((meta.phases || []).map(p => p.title))
  const calls = []
  const hooks = {
    agent: async (prompt, opts = {}) => {
      calls.push({ prompt, opts })
      if (opts.schema && (typeof opts.schema !== 'object' || opts.schema.type !== 'object')) {
        errors.push(`agent "${opts.label}": a schema must be an object schema at its root`)
      }
      for (const e of schemaErrors(opts.schema)) errors.push(`agent "${opts.label}": ${e}`)
      if (nulls) return null
      return opts.schema ? fake(opts.schema) : 'a subagent answer'
    },
    parallel: async thunks => {
      if (!Array.isArray(thunks)) { errors.push('parallel() takes an array of functions'); return [] }
      return Promise.all(thunks.map((t, i) => {
        if (typeof t !== 'function') {
          errors.push(`parallel() item ${i} is not a function: pass () => agent(...), not agent(...)`)
          return null
        }
        return Promise.resolve().then(t).catch(e => { errors.push(`a parallel() thunk threw: ${e.message}`); return null })
      }))
    },
    pipeline: async (items, ...stages) => Promise.all(items.map(async (item, i) => {
      let v = item
      try {
        for (const s of stages) v = await s(v, item, i)
      } catch (e) {
        errors.push(`a pipeline() stage threw on item ${i}: ${e.message}`)
        return null
      }
      return v
    })),
    phase: title => { if (!titles.has(title)) errors.push(`phase("${title}") is not declared in meta.phases`) },
    log: () => {},
    args,
    budget: { total: null, spent: () => 0, remaining: () => Infinity },
    workflow: async () => { throw new Error('a template must not nest another workflow') },
  }
  let result
  try {
    result = await fn(...HOOKS.map(h => hooks[h]), stubDate(), stubMath())
  } catch (e) {
    // With every agent null, a template may stop on purpose; a TypeError is a crash.
    if (!nulls || e instanceof TypeError || e instanceof ReferenceError) errors.push(`throws with these args: ${e.message}`)
    return errors
  }
  if (!calls.length) errors.push('runs without a single agent() call')
  for (const { prompt, opts } of calls) {
    const who = opts.label || '(no label)'
    if (!opts.label) errors.push('an agent() call has no label')
    if (!opts.phase || !titles.has(opts.phase)) errors.push(`agent "${who}": phase "${opts.phase}" is not declared in meta.phases`)
    if (typeof prompt !== 'string' || !prompt.trim()) { errors.push(`agent "${who}": empty prompt`); continue }
    for (const bad of ['undefined', '[object Object]', 'NaN']) {
      if (prompt.includes(bad)) errors.push(`agent "${who}": the prompt contains "${bad}", an argument did not reach it`)
    }
    if (prompt.includes(EM_DASH)) errors.push(`agent "${who}": the prompt contains U+2014`)
  }
  if (result === undefined) errors.push('returns nothing')
  return errors
}

export async function checkTemplate(name, src, fixtures) {
  const errors = []
  let parts
  try {
    parts = splitMeta(src)
  } catch (e) {
    return [`${name}: ${e.message}`]
  }
  const { meta, errors: metaErrors } = checkMeta(parts.metaText)
  errors.push(...metaErrors.map(e => `${name}: ${e}`))
  const { fn, errors: bodyErrors } = checkBody(parts.body)
  errors.push(...bodyErrors.map(e => `${name}: ${e}`))
  if (!meta || !fn) return errors
  if (src.includes(EM_DASH)) errors.push(`${name}: contains U+2014`)

  if (!fixtures.length) errors.push(`${name}: no fixture in scripts/tests/fixtures/workflows/ (${name.replace(/\.js$/, '')}.args.json)`)
  for (const [fixture, args] of fixtures) {
    for (const e of await run(fn, meta, args)) errors.push(`${name} with ${fixture}: ${e}`)
    for (const e of await run(fn, meta, args, { nulls: true })) {
      // With nulls there are no answers to hold the prompts against, only the crash to find.
      if (e.startsWith('throws with these args')) errors.push(`${name} with ${fixture}, every agent() returning null: ${e}`)
    }
  }
  // Empty args must fail at once rather than fan out on nothing.
  const empty = await run(fn, meta, {})
  if (!empty.some(e => e.startsWith('throws with these args'))) {
    errors.push(`${name}: runs with empty args; it must throw, naming the args it needs`)
  }
  return errors
}

function loadFixtures(base) {
  return readdirSync(FIXTURES)
    .filter(f => f === `${base}.args.json` || (f.startsWith(`${base}.`) && f.endsWith('.args.json')))
    .sort()
    .map(f => [f, JSON.parse(readFileSync(join(FIXTURES, f), 'utf8'))])
}

async function main() {
  const names = readdirSync(TEMPLATES).filter(f => f.endsWith('.js')).sort()
  if (!names.length) {
    console.log(`FAIL: no template under ${TEMPLATES}`)
    return 1
  }
  let status = 0
  // build.js and refine.js carry the same isolated-build block: a fix to one must reach both.
  const block = n => {
    const t = readFileSync(join(TEMPLATES, n), 'utf8')
    const a = t.indexOf('// --- the isolated build: the same block in build.js and refine.js ---')
    const b = t.indexOf('// --- end of the isolated build block ---')
    return a >= 0 && b > a ? t.slice(a, b) : null
  }
  const [bb, rb] = [block('build.js'), block('refine.js')]
  if (!bb || !rb) { status = 1; console.log('FAIL the isolated build block markers are missing in build.js or refine.js') }
  else if (bb !== rb) { status = 1; console.log('FAIL the isolated build block drifted between build.js and refine.js') }
  else console.log('OK   [isolated build]: the block is identical in build.js and refine.js')
  for (const name of names) {
    const base = name.replace(/\.js$/, '')
    const errors = await checkTemplate(name, readFileSync(join(TEMPLATES, name), 'utf8'), loadFixtures(base))
    // brief.mjs prints these prompts for a host without a workflow tool: it must see every call.
    for (const [fixture, args] of loadFixtures(base)) {
      try {
        const calls = await briefs(readFileSync(join(TEMPLATES, name), 'utf8'), args)
        if (!calls.length || calls.some(c => !c.label || !c.prompt)) errors.push(`${name} with ${fixture}: brief.mjs printed no call, or a call without label or prompt`)
      } catch (e) {
        errors.push(`${name} with ${fixture}: brief.mjs fails: ${e.message}`)
      }
    }
    if (errors.length) {
      status = 1
      for (const e of errors) console.log(`FAIL ${e}`)
    } else {
      console.log(`OK   [${base}]: pure meta, compiles, runs to the end on ${loadFixtures(base).length} fixture(s), survives null agents, refuses empty args, briefs print`)
    }
  }
  return status
}

// Each broken template must be caught by the check named beside it. If one is not, the
// check has gone inert, and a template with that defect would pass.
async function selfTest() {
  const good = "export const meta = { name: 't', description: 'd', phases: [{ title: 'P' }] }\n" +
    "if (!args.x) throw new Error('t needs args.x')\nphase('P')\nconst r = await agent(`go ${args.x}`, { label: 'a', phase: 'P' })\nreturn r\n"
  const cases = [
    ['a variable in meta', good.replace("name: 't'", 'name: NAME'), 'pure literal'],
    ['a call in meta', good.replace("name: 't'", "name: String('t')"), 'pure literal'],
    ['an operator in meta', good.replace("description: 'd'", "description: 'a' + 'b'"), 'operator'],
    ['a template string in meta', good.replace("name: 't'", 'name: `t`'), 'template string'],
    ['a spread in meta', good.replace("phases: [{ title: 'P' }]", "phases: [...[{ title: 'P' }]]"), 'spread'],
    ['an unterminated comment in meta', good.replace("name: 't',", "name: 't', /* open"), 'unterminated comment'],
    ['an undeclared phase', good.replace("phase('P')", "phase('Q')"), 'not declared'],
    ['Date.now()', good.replace('return r', 'return Date.now()'), 'Date.now'],
    ["Date['now']()", good.replace('return r', "return Date['now']()"), 'Date.now'],
    ['Math.random()', good.replace('return r', 'return Math.random()'), 'Math.random'],
    ['an argless new Date()', good.replace('return r', 'return new Date()'), 'new Date()'],
    ['a missing argument in a prompt', good.replace('${args.x}', '${args.y}'), '"undefined"'],
    ['an object in a prompt', good.replace('${args.x}', '${args}'), '[object Object]'],
    ['NaN in a prompt', good.replace('${args.x}', '${Number(args.x)}'), '"NaN"'],
    ['U+2014 in a prompt', good.replace('go ', `go ${EM_DASH} `), 'U+2014'],
    ['a runtime error', good.replace('return r', 'return args.x.some(Boolean)'), 'throws with these args'],
    ['a thunk that throws', good.replace('const r = await agent(`go ${args.x}`, { label: \'a\', phase: \'P\' })', "const [r] = await parallel([() => agent(`go ${args.x}`, { label: 'a', phase: 'P' }).then(v => v.nope.length)])"), 'thunk threw'],
    ['promises passed to parallel()', good.replace('const r = await agent(`go ${args.x}`, { label: \'a\', phase: \'P\' })', "const [r] = await parallel([agent(`go ${args.x}`, { label: 'a', phase: 'P' })])"), 'is not a function'],
    ['a crash when an agent returns null', good.replace('return r', "return r.length"), 'returning null'],
    ['an unsatisfiable schema', good.replace("{ label: 'a', phase: 'P' }", "{ label: 'a', phase: 'P', schema: { type: 'object', properties: { y: { type: 'string' } }, required: ['z'] } }"), 'required "z"'],
    ['a duplicated enum', good.replace("{ label: 'a', phase: 'P' }", "{ label: 'a', phase: 'P', schema: { type: 'object', properties: { k: { type: 'string', enum: ['a', 'a'] } } } }"), 'duplicates'],
    ['no label', good.replace("label: 'a', ", ''), 'no label'],
    ['nothing returned', good.replace('return r', ''), 'returns nothing'],
    ['empty args accepted', good.replace("if (!args.x) throw new Error('t needs args.x')\n", ''), 'empty args'],
    ['no meta first', `// a comment first\n${good}`, 'must begin with'],
  ]
  let status = 0
  const clean = await checkTemplate('good.js', good, [['good.args.json', { x: 'value' }]])
  if (clean.length) {
    status = 1
    console.log(`FAIL [self-test]: a correct template is rejected: ${clean.join('; ')}`)
  }
  for (const [what, src, expect] of cases) {
    if (src === good) {
      status = 1
      console.log(`FAIL [self-test]: the "${what}" mutation changed nothing`)
      continue
    }
    const errors = await checkTemplate('broken.js', src, [['broken.args.json', { x: 'value' }]])
    if (errors.some(e => e.includes(expect))) {
      console.log(`OK   [self-test]: ${what} is caught`)
    } else {
      status = 1
      console.log(`FAIL [self-test]: ${what} is NOT caught (expected "${expect}", got: ${errors.join('; ') || 'nothing'})`)
    }
  }
  return status
}

// Run only when invoked, so the checks can be imported by a test or a one-off script. Compared
// through realpath: the module URL is percent-encoded with symlinks resolved, argv is neither.
const sameFile = (a, b) => { try { return realpathSync(a) === realpathSync(b) } catch { return false } }
if (process.argv[1] && sameFile(process.argv[1], fileURLToPath(import.meta.url))) {
  const code = process.argv.includes('--self-test') ? await selfTest() : await main()
  process.exit(code)
}
