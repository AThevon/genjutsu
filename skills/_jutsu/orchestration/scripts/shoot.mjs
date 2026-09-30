#!/usr/bin/env node
// Captures a static build in headless Chrome, with no site server and no dependency.
//
// Every request to a fake origin (default http://site.test) is answered from the build folder
// on disk through the DevTools protocol. No dev server or preview server runs: the only socket
// is the browser's own DevTools endpoint, on a free local port the OS picks, so nothing
// collides with a server the user is running, and several clones can shoot at once, each with
// its own browser. Requests to any other origin go to the network as usual.
// Needs Node 22 or later (for the built-in WebSocket) and a Chrome or Chromium binary.
//
// Usage:
//   node shoot.mjs --root <static build dir> --shots <shots.json> [--origin http://site.test]
//                  [--chrome <path to the browser binary>]
//   node shoot.mjs --self-test
//
// shots.json is an array. Each shot:
//   path      the route to open, starting with "/", e.g. "/" or "/en/about"      (required)
//   w, h      the viewport, e.g. 390 x 664                                        (required)
//   dpr       device pixel ratio (default 1)
//   out       where to write the PNG (its folder is created); omit it to measure only
//   full      true: the whole page instead of the first screen
//   segment   with full: cut the page into PNGs this many CSS pixels tall, written as
//             <out without .png>-01.png, -02.png, ... (1700 reads well on a phone capture)
//   width     with full: scale the capture to this many pixels wide (1000 for desktop pages)
//   reduced   true: emulate prefers-reduced-motion: reduce
//   prep      false: skip the preparation (lazy images made eager, the page scrolled through
//             so scroll-triggered content loads, images and fonts awaited, back to the top)
//   reveal    a CSS selector whose elements get the class in revealClass (default "is-in"),
//             to force entrance states to their end for a full-page capture
//   scrollTo  a CSS selector to scroll to before the capture (offset: pixels above it)
//   scrollY   a scroll position to set before the capture
//   before    a JavaScript expression evaluated in the page before the capture
//   wait      milliseconds to wait before the capture (default 1200)
//   measure   a JavaScript expression whose value is returned with the result
//
// Prints a JSON array, one entry per shot: the files written, scrollWidth and clientWidth
// (overflow is true when the page scrolls sideways), the page height, the console errors, the
// uncaught exceptions, every request the build could not answer, and `error` when that shot
// failed. A failed shot never stops the others; the exit code is 1 when any shot failed.
// A page expression that does not settle within 30 seconds fails its shot.

import { execFileSync, spawn } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, extname, isAbsolute, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.txt': 'text/plain', '.xml': 'application/xml',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
  '.avif': 'image/avif', '.gif': 'image/gif', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.mp4': 'video/mp4', '.webm': 'video/webm',
}
const SIGNALS = ['SIGINT', 'SIGTERM', 'SIGHUP']
const sleep = ms => new Promise(r => setTimeout(r, ms))

function option(argv, name) {
  const i = argv.indexOf(name)
  return i >= 0 ? argv[i + 1] : undefined
}

function findChrome(explicit) {
  const candidates = [
    explicit,
    process.env.CHROME_PATH,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
  ].filter(Boolean)
  for (const c of candidates) if (existsSync(c)) return c
  for (const name of ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome']) {
    try {
      const p = execFileSync('which', [name], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim()
      if (p) return p
    } catch {}
  }
  return null
}

// The file of the build that answers a URL path: the file itself, then <path>/index.html,
// then <path>.html, the three layouts static builds use. Nothing outside the root is served,
// not even a sibling folder whose name starts like it.
export function resolveFile(root, pathname) {
  let p
  try {
    p = decodeURIComponent(pathname)
  } catch {
    return null // a malformed escape is a request the build cannot answer
  }
  const tries = p.endsWith('/') ? [`${p}index.html`] : extname(p) ? [p] : [`${p}/index.html`, `${p}.html`]
  for (const t of tries) {
    const f = join(root, t)
    const rel = relative(root, f)
    if (rel.startsWith('..') || isAbsolute(rel)) continue
    if (existsSync(f) && statSync(f).isFile()) return f
  }
  return null
}

function write(file, data) {
  mkdirSync(dirname(file), { recursive: true })
  writeFileSync(file, data)
}

export async function shoot({ root, shots, origin = 'http://site.test', chrome }) {
  if (typeof WebSocket === 'undefined') throw new Error('shoot.mjs needs Node 22 or later (built-in WebSocket)')
  if (!Array.isArray(shots)) throw new Error('the shots file must hold a JSON array')
  const bin = findChrome(chrome)
  if (!bin) throw new Error('no Chrome or Chromium found: pass --chrome <path> or set CHROME_PATH')
  const base = resolve(root)
  if (!existsSync(base)) throw new Error(`no build folder at ${base}`)

  const profile = mkdtempSync(join(tmpdir(), 'bunshin-shoot-'))
  const flags = [
    '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--no-first-run',
    '--no-default-browser-check', '--hide-scrollbars', '--disable-gpu', '--disable-extensions',
  ]
  // In a container, /dev/shm is small, and Chrome refuses to run as root with its sandbox.
  if (process.platform === 'linux') flags.push('--disable-dev-shm-usage')
  // A CI runner (Ubuntu 24.04 restricts the user namespaces the sandbox needs) serves only the
  // local fixture here, so the sandbox is dropped there too.
  if ((typeof process.getuid === 'function' && process.getuid() === 0) || (process.env.CI && process.platform === 'linux')) flags.push('--no-sandbox')
  flags.push('about:blank')
  const browser = spawn(bin, flags, { stdio: ['ignore', 'ignore', 'pipe'] })

  // A capture killed from outside (a tool timeout, Ctrl-C) must not leave the browser behind.
  const killBrowser = () => { try { browser.kill('SIGKILL') } catch {} }
  const onSignal = () => {
    killBrowser()
    try { rmSync(profile, { recursive: true, force: true }) } catch {}
    process.exit(130)
  }
  process.on('exit', killBrowser)
  for (const s of SIGNALS) process.once(s, onSignal)

  try {
    const wsUrl = await new Promise((res, rej) => {
      let buf = ''
      const timer = setTimeout(() => rej(new Error(`the browser did not start within 20 s: ${buf.slice(-400).trim()}`)), 20000)
      browser.stderr.on('data', d => {
        buf += d
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/)
        if (m) { clearTimeout(timer); res(m[1]) }
      })
      browser.on('error', e => { clearTimeout(timer); rej(new Error(`cannot start ${bin}: ${e.message}`)) })
      browser.on('exit', code => { clearTimeout(timer); rej(new Error(`the browser exited (${code}) before it listened: ${buf.slice(-400).trim()}`)) })
    })
    const ws = new WebSocket(wsUrl)
    await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej) })
    let id = 0
    const pending = new Map()
    const listeners = new Set()
    ws.addEventListener('message', ev => {
      const msg = JSON.parse(ev.data)
      if (msg.id && pending.has(msg.id)) {
        const { res, rej } = pending.get(msg.id)
        pending.delete(msg.id)
        if (msg.error) rej(new Error(JSON.stringify(msg.error)))
        else res(msg.result)
      } else if (msg.method) {
        // A listener that throws must never become an unhandled rejection: that would kill the
        // process before the browser is cleaned up.
        for (const l of listeners) Promise.resolve().then(() => l(msg)).catch(e => console.error(`shoot.mjs: ${e.message}`))
      }
    })
    const send = (method, params = {}, sessionId) => new Promise((res, rej) => {
      const i = ++id
      pending.set(i, { res, rej })
      ws.send(JSON.stringify({ id: i, method, params, sessionId }))
    })

    const results = []
    for (const s of shots) {
      const entry = { path: s && s.path, viewport: s ? `${s.w}x${s.h}` : '', files: [], consoleErrors: [], exceptions: [], missing: [] }
      let targetId = null
      let onEvent = null
      try {
        if (!s || !s.w || !s.h) throw new Error(`a shot needs path, w and h: ${JSON.stringify(s)}`)
        if (typeof s.path !== 'string' || !s.path.startsWith('/')) throw new Error(`a shot path must start with "/": ${JSON.stringify(s.path)}`)
        ;({ targetId } = await send('Target.createTarget', { url: 'about:blank' }))
        const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true })
        const S = (m, p) => send(m, p, sessionId)

        onEvent = async msg => {
          if (msg.sessionId !== sessionId) return
          if (msg.method === 'Fetch.requestPaused') {
            const { requestId, request } = msg.params
            const url = new URL(request.url)
            const f = resolveFile(base, url.pathname)
            if (f) {
              await S('Fetch.fulfillRequest', {
                requestId, responseCode: 200,
                responseHeaders: [{ name: 'Content-Type', value: TYPES[extname(f).toLowerCase()] || 'application/octet-stream' }],
                body: readFileSync(f).toString('base64'),
              }).catch(() => {})
            } else {
              entry.missing.push(url.pathname)
              await S('Fetch.fulfillRequest', { requestId, responseCode: 404, responseHeaders: [], body: '' }).catch(() => {})
            }
          } else if (msg.method === 'Runtime.consoleAPICalled' && msg.params.type === 'error') {
            entry.consoleErrors.push(msg.params.args.map(a => a.value ?? a.description ?? '').join(' ').slice(0, 300))
          } else if (msg.method === 'Runtime.exceptionThrown') {
            const d = msg.params.exceptionDetails
            entry.exceptions.push(((d.exception && d.exception.description) || d.text || '').slice(0, 300))
          }
        }
        listeners.add(onEvent)

        await S('Fetch.enable', { patterns: [{ urlPattern: `${origin}/*` }] })
        await S('Page.enable')
        await S('Runtime.enable')
        const mobile = s.w < 600
        await S('Emulation.setDeviceMetricsOverride', { width: s.w, height: s.h, deviceScaleFactor: s.dpr || 1, mobile })
        if (mobile) await S('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 })
        await S('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: s.reduced ? 'reduce' : 'no-preference' }] })

        const loaded = new Promise(r => {
          const l = msg => { if (msg.sessionId === sessionId && msg.method === 'Page.loadEventFired') { listeners.delete(l); r() } }
          listeners.add(l)
        })
        await S('Page.navigate', { url: origin + s.path })
        await Promise.race([loaded, sleep(15000)])

        const ev = async expr => {
          const r = await Promise.race([
            S('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }),
            sleep(30000).then(() => { throw new Error('the page expression did not settle within 30 s') }),
          ])
          if (r.exceptionDetails) throw new Error(`in the page: ${JSON.stringify(r.exceptionDetails.exception || r.exceptionDetails.text)}`)
          return r.result.value
        }
        if (s.prep !== false) {
          await ev(`(async () => {
            document.documentElement.style.scrollBehavior = 'auto';
            document.querySelectorAll('img[loading="lazy"]').forEach(i => { i.loading = 'eager'; });
            const step = Math.max(200, window.innerHeight * 0.7);
            for (let y = 0; y < document.documentElement.scrollHeight; y += step) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
            window.scrollTo(0, 0);
            await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 4000); })));
            await document.fonts.ready;
          })()`)
        }
        if (s.reveal) await ev(`document.querySelectorAll(${JSON.stringify(s.reveal)}).forEach(el => el.classList.add(${JSON.stringify(s.revealClass || 'is-in')}))`)
        if (s.scrollTo) await ev(`(() => { const el = document.querySelector(${JSON.stringify(s.scrollTo)}); if (!el) throw new Error('scrollTo: no element matches'); window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - ${Number(s.offset) || 0}); })()`)
        if (s.scrollY !== undefined) await ev(`window.scrollTo(0, ${Number(s.scrollY)})`)
        if (s.before) await ev(s.before)
        await sleep(s.wait ?? 1200)

        const info = await ev(`({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, h: document.documentElement.scrollHeight })`)
        Object.assign(entry, { scrollWidth: info.sw, clientWidth: info.cw, overflow: info.sw > info.cw, height: info.h })

        if (s.out) {
          const scale = s.full && s.width ? s.width / s.w : 1
          if (s.full && s.segment) {
            const stem = s.out.replace(/\.png$/i, '')
            for (let y = 0, n = 1; y < info.h; y += s.segment, n++) {
              const clip = { x: 0, y, width: s.w, height: Math.min(s.segment, info.h - y), scale }
              const { data } = await S('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip })
              const file = `${stem}-${String(n).padStart(2, '0')}.png`
              write(file, Buffer.from(data, 'base64'))
              entry.files.push(file)
            }
          } else {
            const params = { format: 'png' }
            if (s.full) Object.assign(params, { captureBeyondViewport: true, clip: { x: 0, y: 0, width: s.w, height: info.h, scale } })
            const { data } = await S('Page.captureScreenshot', params)
            write(s.out, Buffer.from(data, 'base64'))
            entry.files.push(s.out)
          }
        }
        if (s.measure) entry.measure = await ev(s.measure)
      } catch (e) {
        entry.error = String((e && e.message) || e).slice(0, 500)
      } finally {
        if (onEvent) listeners.delete(onEvent)
        if (targetId) await send('Target.closeTarget', { targetId }).catch(() => {})
      }
      results.push(entry)
    }
    ws.close()
    return results
  } finally {
    process.off('exit', killBrowser)
    for (const s of SIGNALS) process.off(s, onSignal)
    // The browser keeps writing its profile for a moment after the kill: wait for it to exit,
    // then remove the profile, best effort.
    const exited = browser.exitCode !== null ? Promise.resolve() : new Promise(r => browser.once('exit', r))
    killBrowser()
    await Promise.race([exited, sleep(5000)])
    try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }) } catch {}
  }
}

// Serves a small fixture and checks what comes back, including what must fail.
async function selfTest() {
  const parent = mkdtempSync(join(tmpdir(), 'bunshin-shoot-fixture-'))
  const dir = join(parent, 'dist')
  const out = join(parent, 'out')
  try {
    mkdirSync(dir)
    mkdirSync(join(parent, 'dist-secret'))
    writeFileSync(join(parent, 'dist-secret', 'secret.txt'), 'SIBLING SECRET')
    writeFileSync(join(dir, 'index.html'), '<!doctype html><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="/s.css"><h1>fixture</h1><div style="height:2400px"></div><script>console.error("fixture error")</script>')
    writeFileSync(join(dir, 's.css'), 'body{margin:0;background:#fff}')
    writeFileSync(join(dir, 'wide.html'), '<!doctype html><meta name="viewport" content="width=device-width"><div style="width:900px;height:10px"></div><img src="/missing.png"><img src="/100%.png"><script>setTimeout(() => { throw new Error("fixture exception") }, 0)</script>')
    writeFileSync(join(dir, 'motion.html'), '<!doctype html><p id="m">x</p>')
    const r = await shoot({
      root: dir,
      shots: [
        { path: '/', w: 390, h: 664, out: join(out, 'nested', 'home.png') },
        { path: '/', w: 390, h: 664, full: true, segment: 1000, out: join(out, 'home-full.png') },
        { path: '/wide', w: 390, h: 664, measure: "fetch('/..%2Fdist-secret/secret.txt').then(r => r.status)" },
        { path: '/', w: 1440, h: 900, full: true, width: 1000, out: join(out, 'desk.png') },
        { path: '/', w: 390, h: 664, scrollTo: '#nope' },
        { path: '/motion', w: 390, h: 664, reduced: true, before: "document.getElementById('m').textContent = matchMedia('(prefers-reduced-motion: reduce)').matches", measure: "document.getElementById('m').textContent" },
        { path: 'no-slash', w: 390, h: 664 },
      ],
    })
    const problems = []
    const png = f => existsSync(f) && readFileSync(f).subarray(1, 4).toString() === 'PNG'
    const pngWidth = f => readFileSync(f).readUInt32BE(16)
    if (!png(join(out, 'nested', 'home.png'))) problems.push('the first-screen capture is not a PNG in its new folder')
    if (r[1].files.length !== 3 || !r[1].files.every(png)) problems.push(`a 2400 px page in 1000 px segments gave ${r[1].files.length} files, expected 3`)
    if (r[0].overflow) problems.push('the narrow page is reported as overflowing')
    if (!r[2].overflow) problems.push('the 900 px wide page is not reported as overflowing')
    if (!r[0].consoleErrors.some(e => e.includes('fixture error'))) problems.push('the console error was not collected')
    if (!r[2].exceptions.some(e => e.includes('fixture exception'))) problems.push('the uncaught exception was not collected')
    if (!r[2].missing.includes('/missing.png')) problems.push('the missing image was not reported')
    if (!r[2].missing.includes('/100%.png')) problems.push('a malformed escape was not answered as missing')
    if (r[2].measure !== 404) problems.push(`a file outside the build root was served (status ${r[2].measure})`)
    if (!png(join(out, 'desk.png')) || pngWidth(join(out, 'desk.png')) !== 1000) problems.push('the desktop capture was not scaled to 1000 px wide')
    if (!r[4].error || !r[4].error.includes('scrollTo')) problems.push('a shot with a missing scrollTo target did not fail on its own')
    if (r[5].measure !== 'true') problems.push('reduced motion was not emulated')
    if (!r[6].error || !r[6].error.includes('must start with')) problems.push('a path without a leading slash was not refused')
    if (r[5].error) problems.push(`a shot after a failed one did not run: ${r[5].error}`)
    // Browsers ask for /favicon.ico on their own; the fixture has none, and that is expected.
    const missing = r[0].missing.filter(m => m !== '/favicon.ico')
    if (missing.length) problems.push(`a file of the build was reported missing: ${missing.join(', ')}`)
    for (const p of problems) console.log(`FAIL [shoot self-test]: ${p}`)
    if (!problems.length) console.log('OK   [shoot self-test]: routes from disk, segments, scaling, reduced motion, overflow, console errors, exceptions and missing files reported; a failed shot fails alone; nothing outside the root is served')
    return problems.length ? 1 : 0
  } finally {
    rmSync(parent, { recursive: true, force: true })
  }
}

// Run only when invoked. Compared through realpath: the module URL is percent-encoded and
// symlinks are resolved in it, argv is neither, and a path with a space or an accent must not
// turn the script into a silent no-op.
const sameFile = (a, b) => { try { return realpathSync(a) === realpathSync(b) } catch { return false } }
if (process.argv[1] && sameFile(process.argv[1], fileURLToPath(import.meta.url))) {
  const argv = process.argv.slice(2)
  try {
    if (argv.includes('--self-test')) process.exit(await selfTest())
    const root = option(argv, '--root')
    const shotsFile = option(argv, '--shots')
    if (!root || !shotsFile) {
      console.error('usage: node shoot.mjs --root <static build dir> --shots <shots.json> [--origin http://site.test] [--chrome <path>]')
      process.exit(2)
    }
    const shots = JSON.parse(readFileSync(shotsFile, 'utf8'))
    const results = await shoot({ root, shots, origin: option(argv, '--origin'), chrome: option(argv, '--chrome') })
    console.log(JSON.stringify(results, null, 1))
    process.exit(results.some(r => r.error) ? 1 : 0)
  } catch (e) {
    console.error(`shoot.mjs: ${e.message}`)
    process.exit(1)
  }
}
