/**
 * Render both proposals to PDF.
 *
 *     node tools/proposal-pdf.mjs
 *
 * There are two, because they do different jobs. The one-sheet is what gets
 * left on a desk: two pages, printed both sides, about ninety seconds of
 * reading. The long one is the proof, for the reply that says "send me
 * something" — with a stranger, its length is part of the argument.
 *
 * Both are HTML so they can be read on a phone and kept in version control as
 * text. The PDFs are what get emailed and printed, so they are generated rather
 * than maintained separately — edit the HTML, run this, and they cannot drift.
 *
 * Margins are half an inch top and bottom and nothing at the sides: the
 * document sets its own horizontal gutter, and leaving the sides to it lets the
 * masthead run the full width of the sheet while every page still has room to
 * breathe above and below. Backgrounds are printed, because the dark masthead
 * and the amber recommended-option card are doing work.
 *
 * Needs Playwright's Chromium. Set CHROMIUM to point at another install.
 */
import { chromium } from 'playwright';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const JOBS = [
  // walk-in-notes is the sender's own script, not the practice's — it says so
  // across the top of page one, because the worst outcome for it is being
  // handed across a desk by mistake
  ['docs/proposal/walk-in-notes.html',
   'docs/proposal/Walk-In-Notes.pdf'],
  ['docs/proposal/columbia-animal-hospital-one-sheet.html',
   'docs/proposal/Columbia-Animal-Hospital-One-Sheet.pdf'],
  ['docs/proposal/columbia-animal-hospital-proposal.html',
   'docs/proposal/Columbia-Animal-Hospital-Website-Proposal.pdf'],
];

const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
for (const [src, out] of JOBS) {
  const page = await browser.newPage();
  await page.goto('file://' + path.join(ROOT, src), { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'print' });
  await page.pdf({
    path: path.join(ROOT, out),
    format: 'Letter',
    printBackground: true,
    margin: { top: '0.5in', bottom: '0.5in', left: '0', right: '0' },
  });
  await page.close();
  console.log('  ' + out);
}
await browser.close();
