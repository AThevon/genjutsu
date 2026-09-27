#!/usr/bin/env bash
# Scaffold for the saas-landing eval case, run by `claude plugin eval --scaffold` in the
# run's empty workspace. A Next.js app-router skeleton whose dependencies are
# declared but never installed: the run has no network. The page starts empty,
# so a run that writes nothing fails the page-has-content guard.
set -euo pipefail

mkdir -p app

cat > package.json <<'JSON'
{
  "name": "saas-landing",
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
