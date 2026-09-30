#!/usr/bin/env bash
# Scaffold for the bunshin-escalates eval case, run by `claude plugin eval --scaffold`
# in the run's empty workspace. The same Next.js app-router skeleton as the
# landing cases (dependencies declared, never installed: the run has no
# network), plus the client's material: a text export of her public Instagram
# profile, the kind of source the escalation looks for. The page starts empty,
# so a run that writes nothing fails the page-has-content guard. .gitignore is
# written so that gitignore-has-no-bunshin has a file to read. package.json is
# named after the business, not the case: the scan reads it, and a name that
# says bunshin would put the word in the report that bunshin-named reads.
set -euo pipefail

mkdir -p app material

cat > package.json <<'JSON'
{
  "name": "atelier-oudemans",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "motion": "^13.4.0",
    "next": "^16.3.0",
    "react": "^19.3.0",
    "react-dom": "^19.3.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4.3.0",
    "@types/node": "^24.0.0",
    "@types/react": "^19.3.0",
    "tailwindcss": "^4.3.0",
    "typescript": "^5.9.0"
  }
}
JSON

cat > tsconfig.json <<'JSON'
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "strict": true,
    "noEmit": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
JSON

cat > .gitignore <<'TXT'
node_modules
.next
TXT

cat > postcss.config.mjs <<'JS'
export default { plugins: { "@tailwindcss/postcss": {} } };
JS

cat > app/globals.css <<'CSS'
@import "tailwindcss";
CSS

cat > app/layout.tsx <<'TSX'
import type { ReactNode } from "react";
import "./globals.css";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX

: > app/page.tsx

cat > material/profile.md <<'MD'
# Public Instagram profile of Atelier Oudemans, exported by the client

Name on the profile: Atelier Oudemans
Bio: Steel bicycle frames, built by hand in Utrecht. Restorations of old road bicycles. Visits by appointment only.
Posts in the export: the twelve most recent, newest first. Each entry is the caption, then what the photo shows.

1. "Lugs brazed, tubes cleaned up. This one goes to a rider in Deventer who wants to carry a camera bag on the front."
   Photo: a bare steel frame clamped in the jig, brass visible at the head tube joint.
2. "Before and after. A Dutch road bike from the seventies, stripped, straightened and painted cream again, as it left the factory."
   Photo: two halves of one image, the rusted frame on the left, the same frame freshly painted on the right.
3. "Measuring day. Saddle height, reach, the bag you carry to work. Everything I build starts on this sheet."
   Photo: a hand-drawn geometry sheet on the bench, a tape measure and a pencil on it.
4. "Mitring the top tube. Two millimetres of file work nobody will ever see."
   Photo: close-up of a tube end cut to fit against another tube.
5. "New decals printed from a scan of the old ones. The owner's father raced this bike."
   Photo: a sheet of fresh decals next to a faded original on a down tube.
6. "Workshop in the morning."
   Photo: the bench, the jig and a window with low light; three frames hanging from the ceiling.
7. "Fork crown, before brazing."
   Photo: a fork crown and two fork blades laid out on a cloth.
8. "A restoration is mostly patience: this headset took four evenings to free."
   Photo: a seized headset, penetrating oil and a soft-faced hammer.
9. "Delivered. A touring frame for someone who rides from Utrecht to the coast every summer."
   Photo: a finished dark green bicycle with front and rear racks, leaning on a brick wall.
10. "Paint is sent to a small powder coater two streets away. Chrome I do not do; I send it to a plater in Belgium."
    Photo: three frames in grey primer on a rack.
11. "Questions I get most: yes, I restore frames I did not build; no, I do not sell complete bikes off the shelf."
    Photo: a handwritten note pinned above the bench.
12. "Open for two new custom frames this spring. Write to me first, then we set a measuring appointment."
    Photo: the jig, empty.
MD
