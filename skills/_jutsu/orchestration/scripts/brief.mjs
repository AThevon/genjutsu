#!/usr/bin/env node
// Prints the clone briefs a workflow template would send, for a host with a subagent tool and no
// workflow tool. There, the template is the plan, and rebuilding its prompts by hand drifts: the
// quoting of the build recipe, the shot lists, the schemas. This runs the template itself against
// stand-in agents and prints every call it makes, in order: label, phase, agent type, schema and
// the exact prompt. Spawn each clone with its prompt, its schema as the "return exactly this JSON"
// part, and the agent type when one is given.
//
// The stand-ins answer with placeholder values shaped by each schema. So the calls of the first
// phase are exact; a call made after an answer came back (a synthesis, a plan, a retry) carries a
// placeholder where the real answer goes: rebuild that one prompt from the template, with the real
// answers of the clones before it. Such calls are marked "after answers".
//
// Usage: node brief.mjs <template.js> <args.json>
// Needs Node 18 or later. No dependency.

import { readFileSync, realpathSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor

function splitMeta(src) {
  const head = 'export const meta = '
  if (!src.startsWith(head)) throw new Error('a template begins with `export const meta = {`')
  let depth = 0
  let quote = null
  let i = head.length
  for (; i < src.length; i++) {
    const c = src[i]
    if (quote) { if (c === '\\') i++; else if (c === quote) quote = null; continue }
    if (c === "'" || c === '"' || c === '`') { quote = c; continue }
    if (c === '/' && src[i + 1] === '/') { i = src.indexOf('\n', i); if (i < 0) break; continue }
    if (c === '/' && src[i + 1] === '*') { const e = src.indexOf('*/', i + 2); if (e < 0) break; i = e + 1; continue }
    if (c === '{') depth++
    if (c === '}' && --depth === 0) break
  }
  return src.slice(i + 1)
}

function fake(schema) {
  if (!schema || typeof schema !== 'object') return '<answer>'
  if (schema.enum) return schema.enum[0]
  switch (schema.type) {
    case 'object': return Object.fromEntries(Object.entries(schema.properties || {}).map(([k, s]) => [k, fake(s)]))
    case 'array': return [fake(schema.items)]
    case 'string': return '<answer>'
    case 'boolean': return true
    case 'number':
    case 'integer': return 1
    default: return null
  }
}

export async function briefs(src, args) {
  const calls = []
  const hooks = {
    agent: async (prompt, opts = {}) => {
      calls.push({ n: calls.length + 1, label: opts.label, phase: opts.phase, agentType: opts.agentType || null, afterAnswers: false, schema: opts.schema || null, prompt })
      return opts.schema ? fake(opts.schema) : '<answer>'
    },
    parallel: async thunks => Promise.all(thunks.map(t => Promise.resolve().then(t).catch(() => null))),
    pipeline: async (items, ...stages) => Promise.all(items.map(async (item, i) => {
      let v = item
      for (const s of stages) v = await s(v, item, i)
      return v
    })),
    phase: () => {},
    log: () => {},
    args,
    budget: { total: null, spent: () => 0, remaining: () => Infinity },
    workflow: async () => { throw new Error('nested workflows are not supported here') },
  }
  const fn = new AsyncFunction(...Object.keys(hooks), splitMeta(src))
  await fn(...Object.values(hooks))
  // The calls of the first phase go out before any answer comes back; the later ones, and a
  // retry, may carry an answer in their prompt.
  const firstPhase = calls.length ? calls[0].phase : null
  for (const c of calls) c.afterAnswers = c.phase !== firstPhase || /-retry$/.test(c.label || '')
  return calls
}

const sameFile = (a, b) => { try { return realpathSync(a) === realpathSync(b) } catch { return false } }
if (process.argv[1] && sameFile(process.argv[1], fileURLToPath(import.meta.url))) {
  const [template, argsFile] = process.argv.slice(2)
  if (!template || !argsFile) {
    console.error('usage: node brief.mjs <template.js> <args.json>')
    process.exit(2)
  }
  try {
    const calls = await briefs(readFileSync(template, 'utf8'), JSON.parse(readFileSync(argsFile, 'utf8')))
    console.log(JSON.stringify(calls, null, 1))
  } catch (e) {
    console.error(`brief.mjs: ${e.message}`)
    process.exit(1)
  }
}
