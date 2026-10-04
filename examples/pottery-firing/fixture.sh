#!/usr/bin/env bash
# Scaffold for the pottery-firing example, run by `claude plugin eval --scaffold` in the run's
# empty workspace. A one-page site for Atelier Grès, a fictional pottery studio: React 19 +
# Vite + TypeScript with gsap installed and unused (ScrollTrigger ships in the gsap package),
# node_modules already in place (the run has no network). "The four firings" is four static
# blocks in src/Firings.tsx, which imports nothing and moves nothing, so a run that leaves it
# untouched fails page-has-content.
set -euo pipefail

TEMPLATE=/private/tmp/genjutsu-ex-templates/react-gsap

if [ ! -d "$TEMPLATE/node_modules" ]; then
  echo "pottery-firing: template $TEMPLATE is missing or has no node_modules; run examples/make-templates.sh first" >&2
  exit 1
fi

cp -R "$TEMPLATE"/. .

cat > index.html <<'HTML'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Atelier Grès - stoneware, fired by hand</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
HTML

cat > src/Firings.tsx <<'TSX'
const stages = [
  {
    name: "Drying",
    measure: "About a week",
    text: "Freshly thrown pieces dry slowly, first under plastic, then in the open air, until they are bone dry. Water left in the clay turns to steam in the kiln and can burst a pot.",
  },
  {
    name: "Bisque firing",
    measure: "Around 950 °C",
    text: "The first firing turns dry clay into ceramic for good. The pieces come out hard but still porous, so they can take up the glaze.",
  },
  {
    name: "Glaze firing",
    measure: "Around 1280 °C, in reduction",
    text: "The second firing melts the glaze and vitrifies the stoneware body. Near the top of the firing the kiln is starved of oxygen; this reduction changes how the iron in the clay and the glazes colours.",
  },
  {
    name: "Cooling",
    measure: "Slowly, over about 24 hours",
    text: "The kiln stays shut while it cools. Opening it too early would crack the work with thermal shock.",
  },
];

export default function Firings() {
  return (
    <section className="firings" aria-labelledby="firings-title">
      <h2 id="firings-title">The four firings</h2>
      <p className="lede">Every piece goes through the same four stages before it leaves the studio.</p>
      <ol className="stages">
        {stages.map((stage, index) => (
          <li key={stage.name} className="stage">
            <span className="stage-index">{index + 1}</span>
            <h3>{stage.name}</h3>
            <p className="stage-measure">{stage.measure}</p>
            <p>{stage.text}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
TSX

cat > src/App.tsx <<'TSX'
import Firings from "./Firings";

export default function App() {
  return (
    <>
      <header className="hero">
        <p className="brand">Atelier Grès</p>
        <h1>Stoneware, thrown and fired by hand.</h1>
        <p className="hero-text">
          Bowls, cups and plates for everyday use, made in small batches and fired in our own gas kiln.
        </p>
      </header>

      <main>
        <Firings />
      </main>

      <footer className="footer">
        <p>Atelier Grès. Stoneware, thrown and fired by hand.</p>
      </footer>
    </>
  );
}
TSX

cat > src/index.css <<'CSS'
*,
*::before,
*::after {
  box-sizing: border-box;
}

:root {
  font-family: Georgia, "Times New Roman", serif;
  color: #2b2621;
  background: #f4efe8;
  line-height: 1.6;
}

body {
  margin: 0;
}

.hero {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 960px;
  margin: 0 auto;
  padding: 4rem 2rem;
}

.brand {
  margin: 0 0 2rem;
  font-size: 0.875rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0;
  font-size: clamp(2.25rem, 5vw, 3.75rem);
  font-weight: 400;
  line-height: 1.1;
  max-width: 14ch;
}

.hero-text {
  max-width: 38ch;
  font-size: 1.125rem;
  color: #5b5148;
}

.firings {
  max-width: 960px;
  margin: 0 auto;
  padding: 4rem 2rem 6rem;
}

.firings h2 {
  margin: 0;
  font-size: 2rem;
  font-weight: 400;
}

.lede {
  color: #5b5148;
  margin: 0.5rem 0 2.5rem;
}

.stages {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 1.5rem;
}

.stage {
  background: #fbf8f4;
  border: 1px solid #e2d8cc;
  border-radius: 4px;
  padding: 1.75rem 2rem;
}

.stage-index {
  font-size: 0.875rem;
  color: #8a6f57;
}

.stage h3 {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 400;
}

.stage-measure {
  margin: 0.25rem 0 0.75rem;
  font-style: italic;
  color: #8a6f57;
}

.stage p:last-child {
  margin-bottom: 0;
  max-width: 60ch;
}

.footer {
  border-top: 1px solid #e2d8cc;
  padding: 2rem;
  text-align: center;
  font-size: 0.875rem;
  color: #5b5148;
}
CSS
