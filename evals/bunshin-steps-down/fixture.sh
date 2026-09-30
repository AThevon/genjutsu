#!/usr/bin/env bash
# Scaffold for the bunshin-steps-down eval case, run by `claude plugin eval --scaffold`
# in the run's empty workspace. The Next.js app-router skeleton of the landing
# cases (dependencies declared, never installed: the run has no network) with a
# finished one-screen landing whose only button has no hover or press state
# yet, so a run that writes nothing fails the button-has-interaction guard.
# .gitignore is written so that gitignore-has-no-bunshin has a file to read.
# package.json is named after the product, not the case: the scan reads it,
# and a name that says "steps down" would tell the run what is expected.
set -euo pipefail

mkdir -p app components

cat > package.json <<'JSON'
{
  "name": "tidewell",
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

cat > app/page.tsx <<'TSX'
import { WaitlistButton } from "@/components/waitlist-button";

export default function Page() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-8 px-6 py-16">
      <h1 className="text-4xl font-semibold leading-tight">
        Know when the water at your beach is right for a swim.
      </h1>
      <p className="text-lg text-neutral-700">
        Tidewell reads the tide and the wind for the beach you swim from, and tells you when it is deep
        enough and calm enough to go in.
      </p>
      <form className="flex flex-col gap-3 sm:flex-row">
        <label htmlFor="email" className="sr-only">
          Email
        </label>
        <input
          id="email"
          type="email"
          name="email"
          required
          placeholder="you@example.com"
          className="flex-1 rounded-md border border-neutral-300 px-4 py-3"
        />
        <WaitlistButton />
      </form>
    </main>
  );
}
TSX

cat > components/waitlist-button.tsx <<'TSX'
export function WaitlistButton() {
  return (
    <button type="submit" className="rounded-md bg-neutral-900 px-5 py-3 font-medium text-white">
      Join the waitlist
    </button>
  );
}
TSX
