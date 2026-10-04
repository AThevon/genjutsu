#!/usr/bin/env bash
# Scaffold for the invoice-mark-paid example, run by `claude plugin eval --scaffold` in the
# run's empty workspace. Folio, a fictional invoicing app for freelance illustrators: React 19 +
# Vite + TypeScript with motion installed and unused, node_modules already in place (the run
# has no network). This is the "before" state: "Mark as paid" flips a row's status with no
# feedback at all. src/InvoiceList.tsx holds no animation of any kind, so a run that leaves
# it untouched fails button-has-interaction.
set -euo pipefail

TEMPLATE=/private/tmp/genjutsu-ex-templates/react-motion

if [ ! -d "$TEMPLATE/node_modules" ]; then
  echo "invoice-mark-paid: template $TEMPLATE is missing or has no node_modules; run examples/make-templates.sh first" >&2
  exit 1
fi

cp -R "$TEMPLATE"/. .

cat > index.html <<'HTML'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Invoices - Folio</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
HTML

cat > src/data.ts <<'TS'
export type InvoiceStatus = "Draft" | "Sent" | "Overdue" | "Paid";

export interface Invoice {
  id: string;
  client: string;
  project: string;
  amount: number;
  issued: string;
  due: string;
  status: InvoiceStatus;
}

export const invoices: Invoice[] = [
  {
    id: "FOL-2026-031",
    client: "Vellumark Studio",
    project: "Autumn catalogue cover",
    amount: 1450,
    issued: "2026-09-01",
    due: "2026-09-15",
    status: "Paid",
  },
  {
    id: "FOL-2026-032",
    client: "Quillfern Press",
    project: "Picture book, 14 spreads",
    amount: 4200,
    issued: "2026-09-03",
    due: "2026-10-03",
    status: "Overdue",
  },
  {
    id: "FOL-2026-033",
    client: "Otterwick Coffee",
    project: "Menu illustrations",
    amount: 680,
    issued: "2026-09-08",
    due: "2026-09-22",
    status: "Overdue",
  },
  {
    id: "FOL-2026-034",
    client: "Gullwhistle Outdoor",
    project: "Trail map poster",
    amount: 1150,
    issued: "2026-09-12",
    due: "2026-10-12",
    status: "Sent",
  },
  {
    id: "FOL-2026-035",
    client: "The Lanternmoth Review",
    project: "Editorial spot, October issue",
    amount: 320,
    issued: "2026-09-18",
    due: "2026-10-02",
    status: "Paid",
  },
  {
    id: "FOL-2026-036",
    client: "Fennico Tea",
    project: "Tea packaging, three boxes",
    amount: 2400,
    issued: "2026-09-24",
    due: "2026-10-24",
    status: "Sent",
  },
  {
    id: "FOL-2026-037",
    client: "Hushwave Records",
    project: "Album sleeve",
    amount: 950,
    issued: "2026-10-01",
    due: "2026-10-31",
    status: "Sent",
  },
  {
    id: "FOL-2026-038",
    client: "Vellumark Studio",
    project: "Winter catalogue, six spots",
    amount: 1800,
    issued: "2026-10-03",
    due: "2026-10-31",
    status: "Draft",
  },
];

const money = new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR" });
const day = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric" });

export function formatAmount(amount: number): string {
  return money.format(amount);
}

export function formatDate(iso: string): string {
  return day.format(new Date(`${iso}T12:00:00`));
}
TS

cat > src/InvoiceList.tsx <<'TSX'
import { formatAmount, formatDate, type Invoice } from "./data";

interface InvoiceListProps {
  invoices: Invoice[];
  onMarkPaid: (id: string) => void;
}

export default function InvoiceList({ invoices, onMarkPaid }: InvoiceListProps) {
  return (
    <table className="invoices">
      <thead>
        <tr>
          <th scope="col">Invoice</th>
          <th scope="col">Client</th>
          <th scope="col">Project</th>
          <th scope="col" className="num">Amount</th>
          <th scope="col">Issued</th>
          <th scope="col">Due</th>
          <th scope="col">Status</th>
          <th scope="col"><span className="visually-hidden">Actions</span></th>
        </tr>
      </thead>
      <tbody>
        {invoices.map((invoice) => (
          <tr key={invoice.id}>
            <td className="mono">{invoice.id}</td>
            <td>{invoice.client}</td>
            <td className="muted">{invoice.project}</td>
            <td className="num">{formatAmount(invoice.amount)}</td>
            <td>{formatDate(invoice.issued)}</td>
            <td>{formatDate(invoice.due)}</td>
            <td>
              <span className={`status status-${invoice.status.toLowerCase()}`}>{invoice.status}</span>
            </td>
            <td className="actions">
              {invoice.status === "Sent" || invoice.status === "Overdue" ? (
                <button type="button" onClick={() => onMarkPaid(invoice.id)}>
                  Mark as paid
                </button>
              ) : null}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
TSX

cat > src/App.tsx <<'TSX'
import { useState } from "react";
import InvoiceList from "./InvoiceList";
import { formatAmount, invoices as initialInvoices, type Invoice } from "./data";

export default function App() {
  const [invoices, setInvoices] = useState<Invoice[]>(initialInvoices);

  const outstanding = invoices
    .filter((invoice) => invoice.status === "Sent" || invoice.status === "Overdue")
    .reduce((sum, invoice) => sum + invoice.amount, 0);
  const paid = invoices
    .filter((invoice) => invoice.status === "Paid")
    .reduce((sum, invoice) => sum + invoice.amount, 0);
  const overdueCount = invoices.filter((invoice) => invoice.status === "Overdue").length;

  function markPaid(id: string) {
    setInvoices((current) =>
      current.map((invoice) => (invoice.id === id ? { ...invoice, status: "Paid" } : invoice)),
    );
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="brand">Folio</span>
        <nav aria-label="Main">
          <a href="#" aria-current="page">Invoices</a>
          <a href="#">Clients</a>
          <a href="#">Settings</a>
        </nav>
      </header>

      <main className="page">
        <div className="page-head">
          <h1>Invoices</h1>
          <button type="button" className="secondary">New invoice</button>
        </div>

        <dl className="summary">
          <div>
            <dt>Outstanding</dt>
            <dd>{formatAmount(outstanding)}</dd>
          </div>
          <div>
            <dt>Paid</dt>
            <dd>{formatAmount(paid)}</dd>
          </div>
          <div>
            <dt>Overdue</dt>
            <dd>{overdueCount}</dd>
          </div>
        </dl>

        <InvoiceList invoices={invoices} onMarkPaid={markPaid} />
      </main>
    </div>
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
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color: #1f2328;
  background: #f6f7f9;
  line-height: 1.5;
}

body {
  margin: 0;
}

a {
  color: inherit;
}

button {
  font: inherit;
  cursor: pointer;
  border: 1px solid #1f2328;
  background: #1f2328;
  color: #fff;
  border-radius: 6px;
  padding: 0.35rem 0.75rem;
  font-size: 0.875rem;
}

button.secondary {
  background: #fff;
  color: #1f2328;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 0.75rem 2rem;
  background: #fff;
  border-bottom: 1px solid #e3e5e8;
}

.brand {
  font-weight: 700;
  font-size: 1.125rem;
}

.topbar nav {
  display: flex;
  gap: 1.25rem;
  font-size: 0.9375rem;
}

.topbar nav a {
  text-decoration: none;
  color: #59636e;
}

.topbar nav a[aria-current="page"] {
  color: #1f2328;
  font-weight: 600;
}

.page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 2rem;
}

.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-head h1 {
  margin: 0;
  font-size: 1.5rem;
}

.summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}

.summary div {
  background: #fff;
  border: 1px solid #e3e5e8;
  border-radius: 8px;
  padding: 1rem 1.25rem;
}

.summary dt {
  color: #59636e;
  font-size: 0.875rem;
}

.summary dd {
  margin: 0.25rem 0 0;
  font-size: 1.375rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.invoices {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border: 1px solid #e3e5e8;
  border-radius: 8px;
  font-size: 0.9375rem;
}

.invoices th,
.invoices td {
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #eef0f2;
}

.invoices th {
  color: #59636e;
  font-weight: 500;
  font-size: 0.8125rem;
}

.invoices tbody tr:last-child td {
  border-bottom: none;
}

.num {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}

.mono {
  font-family: ui-monospace, "SF Mono", Menlo, monospace;
  font-size: 0.8125rem;
}

.muted {
  color: #59636e;
}

.actions {
  text-align: right !important;
  width: 9rem;
}

.status {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.status-draft {
  background: #eef0f2;
  color: #59636e;
}

.status-sent {
  background: #e7f0fe;
  color: #1d4ed8;
}

.status-overdue {
  background: #fdecec;
  color: #b42318;
}

.status-paid {
  background: #e6f4ea;
  color: #1a7f37;
}
CSS
