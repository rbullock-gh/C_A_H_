/**
 * Render the proposal to a PDF.
 *
 *     node tools/proposal-pdf.mjs
 *
 * The proposal is an HTML document so it can be read on a phone and kept in
 * version control as text. A PDF is what actually gets emailed and printed, so
 * it is generated rather than maintained separately — edit the HTML, run this,
 * and the two cannot drift.
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
const SRC = path.join(ROOT, 'docs/proposal/columbia-animal-hospital-proposal.html');
const OUT = path.join(ROOT, 'docs/proposal/Columbia-Animal-Hospital-Website-Proposal.pdf');

const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage();
await page.goto('file://' + SRC, { waitUntil: 'networkidle' });
await page.emulateMedia({ media: 'print' });
await page.pdf({
  path: OUT,
  format: 'Letter',
  printBackground: true,
  margin: { top: '0.5in', bottom: '0.5in', left: '0', right: '0' },
});
await browser.close();
console.log('  ' + path.relative(ROOT, OUT));
